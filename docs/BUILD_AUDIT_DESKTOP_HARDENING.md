# Build Audit — Desktop Hardening

This audit covers the desktop hardening pass after the initial desktop phase starter.

## Goals targeted
- safer focus logic
- active-window awareness
- screen-state inspection
- action guard metadata
- screenshot-to-audit improvements

## Added / expanded behavior

### `app/services/desktop_tool.py`
Hardening added:
- `active_window()`
- `screen_info()`
- action guard metadata per desktop action
- safer focus matching / verification
- bounds checking for coordinate clicks
- active-window context for typing, key presses, hotkeys, clicks, and screenshots

### `app/api/routes/desktop.py`
Added endpoints:
- `GET /tools/desktop/active`
- `GET /tools/desktop/screen`

Improved:
- desktop action audit payload now includes guard metadata
- screenshot actions now log returned artifact path when available
- active-window info is logged when returned

### `app/agents/orchestrator.py`
Added CLI command handling for:
- `desktop active`
- `desktop screen`

### `app/cli.py`
Help text updated with:
- desktop active
- desktop screen

### `app/services/tool_registry.py`
Desktop tool metadata updated to reflect:
- active-window inspection
- screen-state inspection
- improved notes around guard-aware desktop control

## Documentation updated
- `docs/DESKTOP_MODE.md`
- `docs/USAGE.md`
- `docs/CONTROL_PHASES.md`
- `docs/ROADMAP_V1.md`

## Validation performed
- Python compile check passed with `python3 -m compileall app`

## Remaining gaps
- app-specific wrappers are still not implemented
- exact activation hardening may still vary depending on Windows behavior
- no full undo layer for desktop actions yet
