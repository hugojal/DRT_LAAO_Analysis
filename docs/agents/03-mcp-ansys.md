# 03 · `ansys-fluent` MCP server

Code: [tools/fluent_mcp/ansys_fluent_mcp.py](../../tools/fluent_mcp/ansys_fluent_mcp.py) · registered in [.mcp.json](../../.mcp.json) · venv `../mcp/.venv` (shared, outside the repo) (Python 3.14, `mcp<2` FastMCP, `ansys-fluent-core` 0.43 = PyFluent).
Installed Ansys: `C:\Program Files\ANSYS Inc\ANSYS Student\v261` (2026 R1, Student).

## Connecting to the user's running Fluent (the "continue from what I'm doing" case)
The user's Fluent was started by the GUI launcher (`fluent -wait 3d -r26.1.0 … -cx HugoLaptop:…`), which does **not** expose a gRPC endpoint by default. The user must do this once in the Fluent console:

```
/server/start-server C:\Users\hugoj\Desktop\UNI\3er\MOs\mcp\server_info.txt
```
(If your build names it differently, search the TUI with `/server/` + Tab; the goal is to write a *server-info file* with address and password.)
Then the agent calls `fluent_connect(server_info_file="…/logs/server_info.txt")`.
**Status: not yet verified on this machine** — try it first; if it fails, use the fallback below. Delete `server_info.txt` afterwards (it contains the session password; it is git/ignore-worthy and must not be shared).

### Fallback: agent-owned session
User saves their case in Fluent (*File > Write > Case…*, e.g. `3_simulation/cases/case_dm_YYYYMMDD.cas.h5`), then `fluent_launch(case_file="3_simulation/cases/case_dm_YYYYMMDD.cas.h5")`. The agent then works on its own Fluent instance. Note `archive/3_simulation/cases/fluent_before_dynamicmesh.cas.h5` does **not** contain the dynamic-mesh setup.

## Tools
| Tool | Use |
|---|---|
| `fluent_connect`, `fluent_launch`, `fluent_disconnect` | Session lifecycle (never `exit_fluent=True` on the user's GUI without asking) |
| `fluent_status` | Transient on/off, viscous model, dynamic mesh flag, background run state |
| `fluent_zones` | Boundary/cell zones by type |
| `fluent_get` / `fluent_set` | Settings API by dotted path (`setup.general.solver.time`); always `get` first |
| `fluent_tui`, `fluent_scheme` | Escape hatches: any TUI command / Scheme expression |
| `fluent_transcript` | Tail of `logs/fluent_mcp_transcript.log` (solver output, residuals, errors) — **check after every action** |
| `fluent_read_profile` | `.prof` transient tables |
| `fluent_mesh_check` | `/mesh/check` + `/mesh/quality` |
| `fluent_initialize` | Standard initialization |
| `fluent_save_case` | Write `.cas.h5` (± data) |
| `fluent_run_start` / `fluent_run_status` / `fluent_interrupt` | Non-blocking transient run (85 steps, dt 0.01, 200 it) |

## Usage guidance for agents
1. `fluent_status`, `fluent_zones`, then `fluent_get("setup.dynamic_mesh")` to **verify the user's dynamic-mesh state against section D of 02** before doing anything.
2. Prefer the settings API; fall back to `fluent_tui` for steps with no settings equivalent (zone separate/merge/scale: `/mesh/modify-zones/…`, `/mesh/scale`).
3. Every state-changing call: read the transcript afterwards and report errors verbatim.
4. Long calculations: only after the user confirms; save case first; poll no more often than every ~60 s.
5. Settings-API names can differ between releases; if a path fails, `fluent_get` the parent to list children (`child_names`) instead of guessing.
6. The server must never write to stdout (stdio transport). Logs go to stderr.

## Known unknowns / to verify
- `/server/start-server` availability and exact syntax in 26.1 Student; whether the Student licence allows PyFluent gRPC attach.
- `dual_time_iterate(time_step_count, iter_count)` argument names in 26.1.
- Transcript capture via `/file/start-transcript` on an attached GUI session.
