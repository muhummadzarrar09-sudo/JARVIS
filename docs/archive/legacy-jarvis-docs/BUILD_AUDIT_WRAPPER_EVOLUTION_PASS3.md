# Build Audit — Wrapper Evolution Pass 3

This audit covers the third wrapper-evolution pass focused on workspace-aware recipes, wrapper reset/state flows, and more useful command-center behavior.

## Goals targeted
- expand wrapper recipes into more project-aware workflows
- make wrapper state more usable through reset/status flows
- improve remembered-target reuse for wrappers
- reinforce the JARVIS console as a practical command center

## Added files
- `docs/BUILD_AUDIT_WRAPPER_EVOLUTION_PASS3.md`
  - this audit file

## Updated files
- `app/services/wrapper_state_service.py`
  - added single-wrapper reset
  - added clear-all support

- `app/services/app_wrapper_service.py`
  - added workspace path resolution helpers
  - added project summary / README detection
  - added wrapper state reset support
  - expanded recipes:
    - `vscode.readme`
    - `project.inspect`
    - `project.resume`
  - improved existing recipes:
    - `terminal.command` now supports `path || command`
    - `browser.research` now includes title + screenshot steps
    - `browser.snapshot` now includes title + screenshot steps
  - smarter remembered-target reuse in `ensure_app()`

- `app/api/routes/apps.py`
  - added `reset` action support

- `app/agents/orchestrator.py`
  - added `app reset`
  - added `app reset: <name>`

- `app/cli.py`
  - help text updated with reset examples

- `docs/APP_WRAPPERS.md`
- `docs/USAGE.md`
- `docs/CONTROL_PHASES.md`
- `docs/ROADMAP_V1.md`
  - updated to reflect workspace-aware wrapper evolution

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime orchestrator checks succeeded for:
  - `app status`
  - `app ensure: browser ::: https://example.com`
  - `app recipe: terminal.command ::: python --version`
- expected sandbox limitations remain for Windows-specific GUI actions and missing Playwright runtime

## Remaining gaps
- wrapper state is still lightweight and local, not yet a full long-horizon app memory graph
- GUI workflows still need target-machine Windows validation
- recipe branching is improved but still not fully adaptive based on rich live app state
