# Build Audit — Browser Multi-Candidate Sprint

## Added / expanded behavior
- browser runtime now detects multiple installed browser candidates
- browser candidate preference is configurable through `.env`
- browser doctor now surfaces candidate list and preference order
- browser context now exposes remembered URL and plain-English next actions
- `/browser` console panel added for quick browser visibility

## Code updated
- `app/services/browser_tool.py`
- `app/services/app_wrapper_service.py`
- `app/core/config.py`
- `.env.example`
- `app/cli.py`

## Docs updated
- `docs/USAGE.md`
- `docs/MASTER_PLAN_STATUS.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime checks succeeded for:
  - `browser_tool.available_browsers()`
  - `app_wrapper_service.wrapper_doctor('browser')`
  - browser context rendering in CLI helpers

## Remaining gaps
- target-machine Windows validation is still needed for real installed-browser launch behavior
- per-browser quirks may still need additional handling
