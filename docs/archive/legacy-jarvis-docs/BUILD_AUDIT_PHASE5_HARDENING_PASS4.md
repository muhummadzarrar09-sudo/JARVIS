# Build Audit — Phase 5 Hardening Pass 4

## Implemented

### Database maintenance layer
- added `/database/status`
- added `/database/backup`
- added `/database/vacuum`
- added `scripts/backup-db.ps1`
- added `scripts/vacuum-db.ps1`
- database status now exposes integrity, journal mode, checkpoint state, counts, and file size

### Model runtime operations layer
- added `/models/preload?slot=fast|main`
- model status now exposes loaded-model cache state
- shell now exposes model selectors and model-action controls

### Shell resilience / operator UX
- added localStorage-backed draft/session/cache persistence in the shell
- added cached-state recovery mode when live shell state refresh fails
- added toast notifications for success/failure flows
- added persistent error drawer for captured shell failures
- added in-shell database maintenance buttons
- added in-shell model action buttons

### Packaged shell diagnostics
- `desktop_shell/app.py` now supports `--print-diagnostics`
- `scripts/start-shell.ps1` now supports:
  - `-PrintDiagnostics`
  - `-BrowserOnly`
  - custom host/port
- packaged shell startup diagnostics now print health, validation, and model status before opening the shell when requested

## Why this pass matters
This pass keeps moving Phase 5 from “feature complete” toward “operator-grade local runtime” by making the shell easier to recover, inspect, maintain, and trust over longer real-world use.
