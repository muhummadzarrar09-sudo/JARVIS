# Build Audit — One-Shot Workflows Pass 5

## Added / expanded behavior
- added coding resume workflow
- added project files workflow recipe
- added page review workflow recipe
- added more natural commands for coding resume, project files, and setup blockers
- updated beginner docs and master plan coverage

## Code updated
- `app/services/app_wrapper_service.py`
- `app/services/quick_actions_service.py`
- `app/agents/orchestrator.py`

## Docs updated
- `docs/USAGE.md`
- `docs/MASTER_PLAN_STATUS.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime checks succeeded for:
  - `review this project`
  - `show my project files`
  - `start coding`
  - `show me the current page`

## Remaining gaps
- live GUI/browser behavior still needs target-machine validation
- more one-shot everyday workflows can still be added
- deeper browser/window state branching is still pending
