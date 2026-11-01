# ansys-fluent MCP

MCP server that lets a Claude Code agent drive Ansys Fluent through PyFluent (launch a solver, read cases, run TUI/settings commands, save new case files).

Setup (already done on this machine; the virtual environment lives outside the repo, in `MOs/mcp/.venv`, and is shared with the other course project):
```
python -m venv ..\mcp\.venv
..\mcp\.venv\Scripts\python -m pip install -r tools\fluent_mcp\requirements.txt
```
Claude Code picks the server up from `.mcp.json` in the project folder (approve it on first use). Test: `..\mcp\.venv\Scripts\python tools\fluent_mcp\smoke_test.py`.
Relative paths given to the tools are resolved from the project folder (`DRT_LAAO_Case3/`); Fluent runs with `logs/fluent/` as working directory.
See `docs/agents/03-mcp-ansys.md` for the connection procedure and tool list.
