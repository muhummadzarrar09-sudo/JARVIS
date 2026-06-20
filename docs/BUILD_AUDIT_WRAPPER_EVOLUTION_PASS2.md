# Build Audit — Wrapper Evolution Pass 2

This audit covers the second wrapper-evolution pass focused on smarter state, richer recipes, and a stronger console feel.

## Goals targeted
- add lightweight wrapper state persistence
- make `app ensure` smarter by reusing remembered targets
- expand recipe coverage for VS Code, terminal, and browser workflows
- improve the terminal console toward a more command-center UX

## Added files
- `app/services/wrapper_state_service.py`
  - persists remembered wrapper state in local JSON
  - stores last target/path/url/query/recipe/action metadata per wrapper

- `docs/BUILD_AUDIT_WRAPPER_EVOLUTION_PASS2.md`
  - this audit file

## Updated files
- `app/services/app_wrapper_service.py`
  - wrapper state integration
  - smarter `ensure_app()` behavior
  - richer recipes:
    - `vscode.file`
    - `terminal.command`
    - `browser.snapshot`
  - wrapper status now includes remembered state

- `app/api/routes/apps.py`
  - `GET /tools/apps/status`
  - `status/state` action handling
  - `ensure` action support

- `app/agents/orchestrator.py`
  - `app state`
  - `app status`
  - `app ensure`

- `app/cli.py`
  - wrapper status table now shows remembered target
  - help text updated with status/ensure/state usage

- `app/core/config.py`
  - added `WRAPPER_STATE_PATH`

- `.env.example`
  - added `WRAPPER_STATE_PATH`

- `docs/APP_WRAPPERS.md`
- `docs/USAGE.md`
- `docs/CONTROL_PHASES.md`
- `docs/ROADMAP_V1.md`
- `docs/JARVIS_CONSOLE_UI.md`
  - all updated to reflect smarter wrappers and console state awareness

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime orchestrator checks succeeded for:
  - `app status`
  - `app recipes`
- browser-search recipe routing executed correctly up to missing local Playwright runtime in sandbox

## Remaining gaps
- wrapper state is lightweight memory, not yet a full app-agent memory graph
- GUI execution success still depends on the real Windows target environment
- browser/desktop recipes still need more conditional branching based on live app state
