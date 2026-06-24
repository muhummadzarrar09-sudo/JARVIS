# Build Audit — Phase 5 Hardening Pass 3

## Implemented

### API / security posture
- restricted CORS to configured local origins instead of wildcard-with-credentials behavior
- added trusted-host protection using `APP_ALLOWED_HOSTS`
- added request-size guard using `APP_REQUEST_MAX_BYTES`
- added response security headers:
  - CSP
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
  - Permissions-Policy
- added a generic unhandled-exception handler that logs failures and returns a clean JSON error

### Server-side approval enforcement
- chat payload now supports `confirmed`
- chat responses now support `requires_confirmation` and `confirmation`
- JARVIS now enforces approval on the server before high-risk commands execute
- this closes the loophole where a client could bypass the UI approval modal and call `/chat` directly

### Operator classification hardening
- expanded high-risk coverage to include:
  - `proc start:`
  - `desktop press:`
  - natural write-note flows
- expanded natural-language medium-risk detection for app/browser/tool-launch commands

### Database hardening
- added `app/services/sqlite_service.py`
- SQLite connections now use:
  - WAL mode
  - NORMAL sync
  - busy timeout
  - foreign keys on
  - temp store memory
- added indexes for sessions/messages/tasks query patterns
- added `app/services/database_service.py`
- database status now reports:
  - path
  - size
  - journal mode
  - integrity check
  - session/message/task counts

### Audit hardening
- audit payloads are now truncated before logging
- audit log parsing now skips malformed lines instead of crashing readers
- this reduces log-bloat risk and makes timeline/replay more resilient

### Route / payload validation
- chat payload now has explicit message/session limits
- task create/status payloads now have tighter bounds
- session routes now validate session-id length
- task service now validates allowed statuses and priorities server-side

### Shell UX hardening
- live shell now handles server-side confirmation-required responses
- confirmation modal can now be triggered either before send or after a server-enforced block
- added database panel + database snapshot surface in the shell

## Why this matters
This pass hardens the project beyond feature completion:
- safer local API exposure
- fewer silent shell failures
- stronger protection against accidental system-control execution
- better SQLite resilience for real ongoing usage
- stronger runtime introspection for debugging

## Remaining real-machine work
- confirm the new security headers and trusted-host setup behave cleanly in the user’s Windows shell/browser workflow
- confirm server-enforced approval behaves correctly in the packaged shell
- validate database integrity reporting and performance on the user’s real machine over longer sessions
