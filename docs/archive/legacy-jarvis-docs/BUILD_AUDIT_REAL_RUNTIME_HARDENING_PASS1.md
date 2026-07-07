# Build Audit — Real Runtime Hardening Pass 1

## Implemented

### Browser launch hardening
- upgraded `app/services/browser_tool.py`
- normalized browser aliases like `edge -> msedge`
- added richer browser availability metadata:
  - display names
  - preference rank
  - fallback flag
  - default selected candidate
- added launch-attempt diagnostics:
  - requested browser
  - attempted candidates
  - selected candidate rank
  - fallback-used signal
- added safer cleanup between failed launch attempts so one bad candidate does not poison the next attempt

### Browser wrapper state / fallback hardening
- upgraded `app/services/app_wrapper_service.py`
- browser wrapper status now detects any supported browser window instead of only Chrome-like title matching
- browser context now exposes:
  - default candidate
  - running browser names
  - preferred browser running state
  - preferred browser window
  - selected live browser
- browser wrapper now remembers the actual browser that launched, not just the requested one
- browser URL flows now fall back to a manual link pack when browser automation launch fails at runtime

### Desktop focus verification hardening
- upgraded `app/services/desktop_tool.py`
- improved title normalization for fuzzy matching
- added stronger focus verification with retry polling after activation
- focus results now include `focus_verification` diagnostics showing how focus was verified
- window matching now slightly prefers already-active and non-minimized candidates during ambiguous fuzzy matches

### Validation + shell launcher support
- upgraded `app/services/validation_service.py`
- validation report now includes:
  - browser context
  - desktop active/window state
  - shell launcher readiness
  - Phase 5 progress snapshot
- upgraded `scripts/runtime_validation.py`
- upgraded `scripts/validate-runtime.ps1`
- runtime validation can now:
  - test specific browsers
  - attempt browser open-to-URL flows
  - test desktop focus with a chosen match index
  - capture shell launcher readiness in the report

### Shell refinement
- upgraded `app/api/routes/ui.py`
- live shell now refreshes from `/shell/state` as the main command-center snapshot
- shell now surfaces:
  - session summary
  - recommended commands
  - validation block
  - operator risk block
  - recent timeline block
  - richer browser state block
- added left-rail snapshot actions for today, browser, validation, and timeline
- upgraded `desktop_shell/app.py`
- packaged shell starter now supports:
  - `--browser-only`
  - custom host/port/path
  - clearer browser fallback messaging
  - safer no-stdin keep-alive behavior

## Why this sprint matters
This pass makes the project much better prepared for the next real Windows validation loop:
- browser launch behavior is easier to inspect
- browser fallbacks are more resilient when automation cannot attach or launch
- desktop focus results are easier to trust and debug
- the shell is more state-driven and closer to a real packaged command center

## Remaining live validation work
- confirm actual launch behavior for Chrome / Edge / Brave / Firefox on the user’s Windows machine
- confirm which browser-specific launch errors still occur in real life
- confirm desktop focus verification against real active-window behavior and undo flows
- run the packaged shell on the real Windows machine and polish anything surfaced there
