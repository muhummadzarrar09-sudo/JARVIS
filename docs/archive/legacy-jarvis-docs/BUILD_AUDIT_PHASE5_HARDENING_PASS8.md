# Build Audit — Phase 5 Hardening Pass 8

## Implemented

### Recovery-pack export / import layer
- added `app/services/recovery_service.py`
- added `app/api/routes/maintenance.py`
- added:
  - `GET /maintenance/packs`
  - `GET /maintenance/pack-file`
  - `POST /maintenance/export-pack`
  - `POST /maintenance/import-pack`
- added PowerShell helpers:
  - `scripts/export-recovery-pack.ps1`
  - `scripts/import-recovery-pack.ps1`
- recovery packs now bundle the current DB, audit log, wrapper state, recent validation files, and optionally backups/archives
- import can restore selected local files with safety backups first

### Maintenance drawer + offline/reconnect overlay
- shell now includes a dedicated maintenance drawer
- shell now includes a connection / recovery overlay with a manual reconnect action
- overlay appears when live shell state refresh fails
- banner + cached-state recovery continue to work together during reconnect scenarios

### Cleanup dry-run preview + stronger retention controls
- shell now supports cleanup preview actions for:
  - light
  - normal
  - aggressive
- cleanup execution helpers remain available alongside preview mode
- session cleanup warnings are now surfaced through validation when the session store grows large

### Recovery / archive downloads in the shell
- shell now lets you:
  - download selected DB backups
  - download selected audit archives
  - download selected recovery packs
- shell now lets you import the selected recovery pack back into the local runtime

### Maintenance history + drawer summaries
- maintenance state now includes:
  - recovery pack history
  - recovery pack list
  - session cleanup history
- shell now renders these through maintenance event cards and the new maintenance drawer

## Why this pass matters
This pass pushes the shell closer to a real local command center with:
- exportable recovery checkpoints
- importable runtime recovery packs
- safer cleanup previews
- visible reconnect behavior
- stronger maintenance visibility over longer sessions
