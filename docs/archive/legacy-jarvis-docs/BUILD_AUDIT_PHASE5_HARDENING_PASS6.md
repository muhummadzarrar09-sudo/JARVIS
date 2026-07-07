# Build Audit — Phase 5 Hardening Pass 6

## Implemented

### Restore history + maintenance summaries
- shell maintenance state now includes:
  - `database_history`
  - `audit_history`
  - maintenance summary counts
  - latest database/audit maintenance events
- shell maintenance panel now surfaces latest maintenance activity rather than only raw counts

### Audit archive viewer
- added `GET /audit/archive-preview`
- shell now lets you select an archived audit log and preview its recent entries directly in the feed

### Database restore flow hardening
- restore path now stays constrained under the workspace
- restore can create a safety backup first
- restored database gets an immediate integrity check
- shell now exposes restore-from-backup controls through the maintenance panel

### Packaged-shell reconnect / recovery posture
- desktop shell launcher now has deeper HTTP readiness checks beyond raw port-open checks
- added launcher controls:
  - `--retry-count`
  - `--retry-delay`
  - `--open-recovery-on-failure`
- `scripts/start-shell.ps1` now exposes:
  - `-RetryCount`
  - `-RetryDelay`
  - `-OpenRecoveryOnFailure`

### Startup banner + longer-session shell resilience
- shell startup banner now acts as a runtime diagnostics summary instead of just a static boot note
- shell now updates the banner during cached-state recovery mode
- shell now refreshes on visibility return and periodic polling
- shell warm-start flow for local GGUF mode remains active and now sits inside a stronger boot sequence

## Why this pass matters
This pass improves the operational side of Phase 5 hardening:
- better recovery from bad runtime states
- better visibility into maintenance history
- safer restore workflows
- stronger packaged-shell readiness and recovery behavior
