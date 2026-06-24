# Build Audit — Phase 5 Hardening Pass 9

## Implemented

### Maintenance doctor API
- added `app/services/maintenance_service.py`
- added `GET /maintenance/doctor`
- doctor now summarizes pass/warn/fail checks across:
  - database integrity
  - audit log size
  - model runtime mode
  - browser readiness
  - recovery-pack availability
  - validation blockers

### Recovery-pack verification panel support
- added `GET /maintenance/pack-preview`
- shell can now preview the selected recovery pack before import
- pack preview exposes manifest, entry list, and required-entry presence checks

### Custom cleanup preset UI
- shell now includes custom cleanup inputs for:
  - keep recent sessions
  - drop-empty days
  - drop-inactive days
- shell now supports:
  - preview custom cleanup
  - run custom cleanup
  - save maintenance preferences locally

### Maintenance retention controls
- shell now exposes an audit retention input for prune count
- maintenance preferences are persisted in local storage and restored on boot

### Reconnect status timeline + maintenance result history
- shell now stores reconnect events locally and renders them in the maintenance drawer
- shell now stores maintenance-operation result history locally and renders it in the maintenance drawer
- this gives a simple operator-visible history of reconnects, pack ops, cleanup ops, and maintenance actions

### Connection / recovery overlay
- overlay now acts as a real offline/reconnect surface instead of a passive message only
- reconnect attempts are logged into reconnect history
- successful live refreshes now also update reconnect history

### Maintenance drawer expansion
- maintenance drawer now shows:
  - doctor summary
  - recovery packs
  - DB backups
  - audit archives
  - reconnect timeline
  - maintenance result history

## Why this pass matters
This pass pushes Phase 5 hardening farther into operator-grade territory by making maintenance and recovery not just possible, but inspectable and reviewable from inside the shell itself.
