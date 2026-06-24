# Build Audit — Phase 5 Hardening Pass 7

## Implemented

### Maintenance event cards
- shell now renders dedicated maintenance-event cards sourced from:
  - database maintenance history
  - audit maintenance history
  - session cleanup history
- maintenance summary text now includes the latest session-maintenance event as well

### Session cleanup helpers
- added `POST /sessions/cleanup`
- shell now exposes cleanup presets:
  - light
  - normal
  - aggressive
- cleanup results are logged as maintenance events and surfaced back into the shell

### Download / export helpers
- added `GET /database/backup-file`
- added `GET /audit/archive-file`
- shell now lets you download the selected database backup or audit archive directly

### Archive preview / maintenance visibility
- shell now supports maintenance snapshot viewing
- shell can preview the selected audit archive in the feed
- shell maintenance state now includes summary counts and maintenance event history

### Reconnect / refresh posture
- shell now refreshes on visibility return
- shell now polls periodically in the background
- cached-state recovery banner remains active when live refresh fails

## Why this pass matters
This pass makes the maintenance side of the shell more operational:
- not just maintaining the system, but also seeing what maintenance happened and exporting recovery artifacts when needed
