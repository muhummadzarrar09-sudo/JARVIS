# Build Audit — App Wrapper Recipes

This audit covers the recipe expansion layered on top of the initial app-wrapper phase.

## Goals targeted
- move wrappers beyond simple app launch/focus actions
- provide reusable workflow recipes for common app tasks
- keep the build sequence aligned with the desktop-control roadmap

## Added / expanded behavior

### `app/services/app_wrapper_service.py`
Added:
- recipe registry
- recipe listing
- recipe normalization/aliases
- recipe execution handler

New starter recipes:
- `note.quick`
- `explorer.workspace`
- `vscode.project`
- `terminal.project`
- `browser.search`
- `browser.research`
- `project.starter`

### `app/api/routes/apps.py`
Added:
- `GET /tools/apps/recipes`
- `action=recipes`
- `action=recipe`

### `app/agents/orchestrator.py`
Added CLI command handling for:
- `app recipes`
- `app recipe: <name> [::: payload]`

### `app/cli.py`
Help text updated with:
- recipe listing command
- recipe execution command

### `app/services/tool_registry.py`
Updated app-wrapper tool metadata to include recipe commands.

## Documentation updated
- `docs/APP_WRAPPERS.md`
- `docs/USAGE.md`
- `docs/CONTROL_PHASES.md`
- `docs/ROADMAP_V1.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`
- runtime orchestrator test succeeded for `app wrappers`
- recipe/wrapper routing verified at compile level

## Remaining gaps
- recipe success for GUI/browser actions still depends on target-machine Windows runtime
- browser recipes depend on Playwright/browser availability locally
- VS Code wrapper/recipe still depends on `code` being available on PATH locally
