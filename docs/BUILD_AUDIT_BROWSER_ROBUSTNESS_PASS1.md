# Build Audit — Browser Robustness Pass 1

## Added / expanded behavior
- browser runtime now detects multiple installed browser candidates
- candidate preference order is configurable through `.env`
- browser state now reports active browser name and engine
- browser doctor now surfaces available browser candidates and preference order

## Code updated
- `app/services/browser_tool.py`
- `app/services/app_wrapper_service.py`
- `app/core/config.py`
- `.env.example`

## Docs updated
- `docs/USAGE.md`
- `docs/MASTER_PLAN_STATUS.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- browser candidate detection path compiled successfully

## Remaining gaps
- actual target-machine validation is still needed for installed browser discovery on Windows
- live automation behavior can still vary by browser family and version
