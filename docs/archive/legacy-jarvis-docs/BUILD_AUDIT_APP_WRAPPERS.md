# Build Audit — App Wrappers

This audit covers the app-wrapper phase added on top of the desktop/process/browser layers.

## Goals targeted
- add higher-level app entry points
- reduce reliance on low-level raw desktop commands
- establish a bridge toward the eventual packaged desktop app shell

## Added files
- `app/services/app_wrapper_service.py`
  - canonical wrapper metadata
  - app open/focus helpers
  - quick note workflow
  - explorer / VS Code / browser wrapper shortcuts

- `app/api/routes/apps.py`
  - wrapper listing endpoint
  - wrapper action endpoint

- `docs/APP_WRAPPERS.md`
  - wrapper-specific usage and rationale

## Updated files
- `app/main.py`
  - registered app-wrapper API routes

- `app/agents/orchestrator.py`
  - added `app wrappers`
  - added `app open`, `app focus`, `app focusexact`
  - added `app note`, `app explore`, `app code`, `app browse`

- `app/cli.py`
  - help text updated with wrapper commands

- `app/services/tool_registry.py`
  - added app-wrapper tool metadata

- `docs/USAGE.md`
  - added wrapper examples

- `docs/CONTROL_PHASES.md`
  - added app-wrapper phase extension

- `docs/ROADMAP_V1.md`
  - marked app wrappers started/completed in current desktop phase
  - clarified that the packaged desktop app shell comes after wrappers stabilize

- `README.md`
  - added app-wrapper docs reference

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- route/service wiring verified at import/compile level

## Remaining gaps
- wrappers are starter-level, not full app-specific workflow agents yet
- VS Code wrapper depends on `code` being on PATH locally
- terminal/explorer behavior may vary across local Windows setups
