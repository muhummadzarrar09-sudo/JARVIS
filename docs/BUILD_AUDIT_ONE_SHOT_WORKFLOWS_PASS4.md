# Build Audit — One-Shot Workflows Pass 4

## Added / expanded behavior
- added today-brief helper flow for a simpler daily starting point
- added more one-shot natural commands for setup, focus, browser resume, and project review
- improved browser and coding fallback outputs to carry manual steps and next actions
- expanded docs and master plan with the current one-shot workflow coverage

## Code updated
- `app/services/quick_actions_service.py`
- `app/agents/orchestrator.py`
- `app/services/app_wrapper_service.py`
- `app/cli.py`

## Docs updated
- `docs/USAGE.md`
- `docs/MASTER_PLAN_STATUS.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime checks succeeded for:
  - `show me today's focus`
  - `wrap up current task`
  - `search for local ai agents`
  - `open readme`
  - `review this project`
  - `show my project files`
  - `start coding`
  - `show me the current page`

## Remaining gaps
- actual Windows GUI/browser runtime still needs target-machine validation
- live-state-aware branching can still go deeper
- more one-shot everyday flows can still be layered in
