# Build Audit — Phase 5 Hardening Pass 5

## Implemented

### Database restore / maintenance
- added `GET /database/backups`
- added `POST /database/restore`
- added `scripts/restore-db.ps1`
- restore flow now:
  - resolves backup paths inside the workspace only
  - can create a safety backup before restore
  - validates restored SQLite integrity after copy

### Audit rotation / pruning
- added `GET /audit/status`
- added `GET /audit/archives`
- added `POST /audit/rotate`
- added `POST /audit/prune`
- added `scripts/rotate-audit.ps1`
- added `scripts/prune-audit.ps1`
- active audit log can now be rotated into an archive folder and old archives pruned by retention count

### Shell startup diagnostics / maintenance center
- added in-shell startup diagnostics banner summarizing:
  - API health
  - model runtime mode
  - DB integrity
  - blocker count
- expanded shell maintenance center with:
  - DB backup
  - DB restore
  - DB vacuum
  - audit rotate
  - audit prune
  - model preload
  - maintenance refresh
- shell now renders backup selection from live maintenance state

### Shell resilience / warm-start
- added auto warm-start behavior for local GGUF mode when no models are loaded yet
- added cached maintenance rendering and maintenance status text
- added `--print-diagnostics` packaged-shell startup support to the desktop launcher script path

## Why this pass matters
This pass moves the shell from a useful operator UI into a more complete local command center with actual maintenance and recovery operations for its runtime state, audit trail, and SQLite store.
