# Build Audit — Phase 5.11.5 Pass 1

## Implemented
- added `app/services/acceptance_state_service.py`
- added `app/services/acceptance_service.py`
- added acceptance routes:
  - `GET /acceptance/status`
  - `GET /acceptance/history`
  - `POST /acceptance/run`
  - `POST /acceptance/reset`
- added `scripts/acceptance_sweep.py`
- added `scripts/run-acceptance.ps1`
- shell now exposes acceptance sweep actions and an acceptance status panel
- acceptance sweep now rolls together:
  - shell bootstrap checks
  - shell doctor checks
  - runtime summary
  - maintenance verification
  - fast/main model runtime verification
  - optional deep browser/desktop validation

## Why this matters
This begins the actual-use acceptance phase with a unified acceptance flow instead of scattered manual checks.
