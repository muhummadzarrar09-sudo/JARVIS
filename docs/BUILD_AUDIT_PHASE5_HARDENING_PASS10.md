# Build Audit — Phase 5 Hardening Pass 10

## Implemented

### Maintenance doctor panel
- added `app/services/maintenance_service.py`
- added `GET /maintenance/doctor`
- doctor now reports pass/warn/fail checks with evidence for:
  - database integrity
  - audit size
  - model runtime
  - browser readiness
  - recovery-pack availability
  - validation blockers
- shell now surfaces the doctor summary directly in the right rail and maintenance drawer

### Maintenance history + backend settings
- added `GET /maintenance/history`
- added `GET /maintenance/settings`
- added `POST /maintenance/settings`
- added `app/services/maintenance_settings_service.py`
- maintenance preferences can now be saved to backend storage instead of living only in local browser storage

### Recovery-pack preview / import tooling
- added `GET /maintenance/pack-preview`
- shell now supports previewing the selected recovery pack before import
- recovery history is included in maintenance state and surfaced to the shell

### Delete operations for maintenance artifacts
- added `POST /database/backup-delete`
- added `POST /audit/archive-delete`
- added `POST /maintenance/pack-delete`
- added PowerShell helpers:
  - `scripts/delete-db-backup.ps1`
  - `scripts/delete-audit-archive.ps1`
  - `scripts/delete-recovery-pack.ps1`
- shell now supports deleting selected DB backups, audit archives, and recovery packs

### Custom cleanup + retention UX
- shell now supports custom cleanup previews and custom cleanup execution
- shell now exposes an audit retention field for prune count
- shell now persists maintenance preferences and uses them across sessions

### Reconnect / maintenance histories
- shell now keeps reconnect history and maintenance-operation result history in local storage
- maintenance drawer now shows:
  - doctor summary
  - recovery packs
  - DB backups
  - audit archives
  - reconnect timeline
  - maintenance result history

## Why this pass matters
This pass makes Phase 5 more viable for real everyday use by giving the operator more visibility, cleaner retention controls, backend-persisted maintenance settings, and actual delete/cleanup workflows for local maintenance artifacts.
