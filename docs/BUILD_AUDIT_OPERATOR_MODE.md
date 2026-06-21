# Build Audit — Operator Mode Starter

This audit covers the operator-mode pass layered on top of deeper Phase 4 work.

## Goals targeted
- add approval prompts for risky terminal actions
- surface replayable commands and timeline visibility
- expose operator-oriented audit summaries and APIs
- strengthen the JARVIS console as a real command center prototype

## Added / expanded behavior

### `app/services/operator_mode.py`
Added:
- command risk classification
- starter command palette categories

### `app/services/audit.py`
Added:
- event filtering
- session timeline helper
- operator summary helper
- replay candidate extraction

### `app/api/routes/audit.py`
Added:
- `GET /audit/operator-summary`
- `GET /audit/replay`
- richer filtering on `/audit/recent`

### `app/services/app_wrapper_service.py`
Expanded:
- `current_browser_context()`
- `wrapper_doctor()`
- richer resume/project-aware branching
- `browser.resume`
- `vscode.resume`

### `app/cli.py`
Added:
- approval prompts for high-risk commands
- `/timeline`
- `/replay`
- `/palette`
- dashboard timeline rendering
- replay table
- command palette panel

## Documentation updated
- `docs/APP_WRAPPERS.md`
- `docs/USAGE.md`
- `docs/CONTROL_PHASES.md`
- `docs/JARVIS_CONSOLE_UI.md`
- `docs/ROADMAP_V1.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime checks succeeded for:
  - `app doctor`
  - `app project`
  - `app recipe: browser.resume`
  - `app recipe: vscode.resume`
- expected sandbox limitations remain for Windows GUI binaries and Playwright runtime
