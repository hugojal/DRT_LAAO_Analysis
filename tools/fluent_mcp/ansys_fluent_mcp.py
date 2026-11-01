"""MCP server that lets a Claude agent drive Ansys Fluent through PyFluent.

Transport: stdio. NEVER print to stdout in this file (it would corrupt the MCP protocol); use `log`.

Two ways to get a session:
  * fluent_connect  -> attach to the Fluent GUI the user already has open (needs a server-info file,
                       see docs/agents/03-mcp-ansys.md).
  * fluent_launch   -> start a fresh Fluent (optionally loading a .cas.h5) controlled only by the agent.
"""
from __future__ import annotations

import json
import logging
import sys
import threading
import time
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("ansys-fluent-mcp")

PROJECT_ROOT = Path(__file__).resolve().parents[2]          # DRT_LAAO_Case3/
TRANSCRIPT = PROJECT_ROOT / "logs" / "fluent_mcp_transcript.log"
MAX_CHARS = 8000

mcp = FastMCP("ansys-fluent")

_solver: Any = None
_run: dict[str, Any] = {"state": "idle"}  # background calculation bookkeeping


def _need_solver() -> Any:
    if _solver is None:
        raise RuntimeError("No Fluent session. Call fluent_connect or fluent_launch first.")
    return _solver


def _clip(text: str) -> str:
    return text if len(text) <= MAX_CHARS else text[:MAX_CHARS] + f"\n...[truncated {len(text) - MAX_CHARS} chars]"


def _tui(solver: Any, command: str) -> None:
    """Run a TUI command through Scheme (stable across PyFluent versions)."""
    escaped = command.replace("\\", "\\\\").replace('"', '\\"')
    solver.scheme.eval(f'(ti-menu-load-string "{escaped}")')


def _start_transcript(solver: Any) -> None:
    try:
        _tui(solver, f"/file/start-transcript \"{TRANSCRIPT.as_posix()}\" yes")
    except Exception as exc:  # transcript is a convenience only
        log.warning("could not start transcript: %s", exc)


def _resolve(solver: Any, path: str) -> Any:
    node = solver.settings
    for part in filter(None, path.split(".")):
        if part.isdigit():
            node = node[int(part)]
        elif part.startswith("[") and part.endswith("]"):
            node = node[part[1:-1]]  # named-object child, e.g. boundary_conditions.velocity_inlet.[inlet]
        else:
            node = getattr(node, part)
    return node


@mcp.tool()
def fluent_connect(server_info_file: str = "", ip: str = "", port: int = 0, password: str = "") -> str:
    """Attach to a running Fluent. Preferred: pass server_info_file (written by Fluent's
    `/server/start-server` TUI command or `-sifile`). Alternatively ip+port+password."""
    global _solver
    import ansys.fluent.core as pyfluent

    kwargs: dict[str, Any] = {"start_transcript": False, "cleanup_on_exit": False}
    if server_info_file:
        kwargs["server_info_file_name"] = server_info_file
    else:
        kwargs.update(ip=ip or "127.0.0.1", port=port, password=password)
    _solver = pyfluent.connect_to_fluent(**kwargs)
    _start_transcript(_solver)
    return "connected: " + str(_solver)


@mcp.tool()
def fluent_launch(case_file: str = "", processors: int = 2, show_gui: bool = True) -> str:
    """Start a new Fluent 3D double-precision-off session (Student licence: <=1 M cells, <=4 cores),
    optionally reading a case file (relative to the project root or absolute)."""
    global _solver
    import ansys.fluent.core as pyfluent

    _solver = pyfluent.launch_fluent(
        mode="solver", dimension=3, precision="single", processor_count=min(processors, 4),
        ui_mode="gui" if show_gui else "no_gui", cwd=str(PROJECT_ROOT / "logs" / "fluent"), start_transcript=False,
        cleanup_on_exit=False,
    )
    _start_transcript(_solver)
    if case_file:
        p = Path(case_file)
        p = p if p.is_absolute() else PROJECT_ROOT / p
        _solver.file.read_case(file_name=str(p))
    return "launched: " + str(_solver)


@mcp.tool()
def fluent_status() -> str:
    """Session summary: connection, mesh size, time settings, background-run state."""
    out: dict[str, Any] = {"connected": _solver is not None, "run": dict(_run)}
    if _solver is not None:
        s = _solver
        for key, getter in {
            "transient": lambda: s.settings.setup.general.solver.time.get_state(),
            "viscous_model": lambda: s.settings.setup.models.viscous.model.get_state(),
            "dynamic_mesh_enabled": lambda: s.settings.setup.dynamic_mesh.enabled.get_state(),
        }.items():
            try:
                out[key] = getter()
            except Exception as exc:
                out[key] = f"n/a ({type(exc).__name__})"
    return json.dumps(out, default=str, indent=2)


@mcp.tool()
def fluent_tui(command: str) -> str:
    """Run any Fluent TUI command (e.g. `/mesh/check`, `/file/write-case x.cas.h5 yes`).
    Output is appended to the transcript; the tail is returned."""
    s = _need_solver()
    _tui(s, command)
    return fluent_transcript(40)


@mcp.tool()
def fluent_scheme(expression: str) -> str:
    """Evaluate a Scheme expression in Fluent (advanced; e.g. `(rp-var-value 'flow-time)`)."""
    return _clip(repr(_need_solver().scheme.eval(expression)))


@mcp.tool()
def fluent_transcript(lines: int = 60) -> str:
    """Tail of the Fluent transcript file (solver messages, residuals, errors)."""
    if not TRANSCRIPT.exists():
        return "(no transcript yet)"
    return _clip("\n".join(TRANSCRIPT.read_text(errors="replace").splitlines()[-lines:]))


@mcp.tool()
def fluent_get(path: str) -> str:
    """Read a settings-API node, dotted path from root, e.g. `setup.general.solver.time`,
    `setup.boundary_conditions.pressure_inlet`, `setup.dynamic_mesh`. Use `[name]` for named objects."""
    node = _resolve(_need_solver(), path)
    try:
        value = node.get_state()
    except Exception:
        value = {"children": list(getattr(node, "child_names", []))}
    return _clip(json.dumps(value, default=str, indent=2))


@mcp.tool()
def fluent_set(path: str, value_json: str) -> str:
    """Set a settings-API node to a JSON value, e.g. path `setup.general.solver.time`, value `"unsteady-2nd-order"`.
    Read the node with fluent_get first and mirror its structure."""
    node = _resolve(_need_solver(), path)
    node.set_state(json.loads(value_json))
    return "set " + path


@mcp.tool()
def fluent_zones() -> str:
    """List boundary and cell zones with their types."""
    s = _need_solver()
    bc = s.settings.setup.boundary_conditions
    result: dict[str, list[str]] = {}
    for t in getattr(bc, "child_names", []):
        try:
            names = list(getattr(bc, t).keys())
        except Exception:
            continue
        if names:
            result[t] = names
    try:
        result["cell_zones"] = list(s.settings.setup.cell_zone_conditions.fluid.keys())
    except Exception:
        pass
    return json.dumps(result, indent=2)


@mcp.tool()
def fluent_read_profile(profile_file: str) -> str:
    """Read a transient table (.prof): TUI `/file/read-transient-table`. Path relative to project root."""
    p = Path(profile_file)
    p = p if p.is_absolute() else PROJECT_ROOT / p
    _tui(_need_solver(), f'/file/read-transient-table "{p.as_posix()}"')
    return f"read {p}"


@mcp.tool()
def fluent_mesh_check() -> str:
    """Run mesh check + quality report; returns the transcript tail."""
    s = _need_solver()
    _tui(s, "/mesh/check")
    _tui(s, "/mesh/quality")
    return fluent_transcript(60)


@mcp.tool()
def fluent_save_case(file_name: str, with_data: bool = False) -> str:
    """Write case (and optionally data) to file_name (.cas.h5 / .dat.h5), relative to project root."""
    p = Path(file_name)
    p = p if p.is_absolute() else PROJECT_ROOT / p
    s = _need_solver()
    (s.file.write_case_data if with_data else s.file.write_case)(file_name=str(p))
    return f"saved {p}"


@mcp.tool()
def fluent_initialize() -> str:
    """Standard initialization (required again whenever you stop and change parameters)."""
    _need_solver().solution.initialization.initialize()
    return "initialized"


@mcp.tool()
def fluent_run_start(time_steps: int, time_step_size: float | None = None, max_iter_per_step: int | None = None) -> str:
    """Start a transient calculation in a background thread and return immediately.
    Poll with fluent_run_status. Reference case: 85 steps, dt 0.01 s, 200 iterations/step."""
    s = _need_solver()
    if _run.get("state") == "running":
        return "a run is already in progress"
    rc = s.settings.solution.run_calculation
    if time_step_size is not None:
        rc.transient_controls.time_step_size = time_step_size
    kwargs: dict[str, Any] = {"time_step_count": time_steps}
    if max_iter_per_step is not None:
        kwargs["iter_count"] = max_iter_per_step

    def work() -> None:
        _run.update(state="running", started=time.time(), steps=time_steps, error=None)
        try:
            rc.dual_time_iterate(**kwargs)
            _run.update(state="finished", ended=time.time())
        except Exception as exc:
            _run.update(state="failed", error=f"{type(exc).__name__}: {exc}", ended=time.time())

    threading.Thread(target=work, daemon=True).start()
    return "run started"


@mcp.tool()
def fluent_run_status() -> str:
    """State of the background run plus transcript tail (residuals)."""
    return json.dumps(_run, default=str) + "\n" + fluent_transcript(25)


@mcp.tool()
def fluent_interrupt() -> str:
    """Ask Fluent to stop the current calculation."""
    _need_solver().scheme.eval("(interrupt-iterations)")
    return "interrupt requested"


@mcp.tool()
def fluent_disconnect(exit_fluent: bool = False) -> str:
    """Drop the session. exit_fluent=True also closes Fluent (never do this on the user's GUI without asking)."""
    global _solver
    if _solver is not None:
        try:
            if exit_fluent:
                _solver.exit()
        finally:
            _solver = None
    return "disconnected"


if __name__ == "__main__":
    mcp.run()
