# Build Audit — Wrapper Evolution Pass 4

This audit covers the fourth wrapper-evolution pass focused on project context, richer workspace-aware recipes, and stronger command-center panels.

## Goals targeted
- improve wrapper and recipe branching with workspace context
- expose project context directly in the console and API
- make wrapper state reset/reuse more practical
- reinforce the terminal as the prototype of the future JARVIS desktop shell

## Added / expanded behavior

### `app/services/app_wrapper_service.py`
Added:
- preferred project-target helper
- project context summary method
- smarter recipe defaults using remembered project paths/targets
- new recipes and improved branching:
  - `vscode.readme`
  - `project.inspect`
  - `project.resume`
- improved browser fallback behavior for recipes
- improved terminal command behavior with remembered path/command reuse
- wrapper reset support remains available and integrated

### `app/api/routes/apps.py`
Added:
- `GET /tools/apps/project-context`
- action aliases for project/context support

### `app/agents/orchestrator.py`
Added CLI command handling for:
- `app project`
- `app project: <path>`
- `app context`
- `app context: <path>`

### `app/cli.py`
Added:
- `/projects` slash command
- project context panel in dashboard
- updated help text for project/context commands

### `app/services/wrapper_state_service.py`
Added:
- wrapper reset helpers for one/all wrappers

## Documentation updated
- `docs/APP_WRAPPERS.md`
- `docs/USAGE.md`
- `docs/CONTROL_PHASES.md`
- `docs/ROADMAP_V1.md`
- `docs/JARVIS_CONSOLE_UI.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime checks succeeded for:
  - `app recipe: project.inspect ::: .`
  - `app status: vscode`
  - `app reset: vscode`
- expected sandbox limitations remain for Windows-specific GUI actions and missing Playwright runtime

## Remaining gaps
- richer live branching still depends on actual Windows GUI/browser state on target machine
- wrapper state is useful but still lightweight
- project context is local and static; it is not yet a full project graph/memory system
