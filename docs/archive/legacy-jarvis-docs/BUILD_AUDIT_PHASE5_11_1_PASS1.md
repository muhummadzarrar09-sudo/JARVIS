# Build Audit — Phase 5.11.1 Pass 1

## Implemented
- added wrapper remembered-state hygiene and normalization in `app/services/wrapper_state_service.py`
- startup now sanitizes stale remembered wrapper state before normal use
- added `GET /shell/bootstrap`
- added `GET /shell/doctor`
- shell boot now uses `/shell/bootstrap` before the full `/shell/state` refresh
- shell boot now surfaces state-normalization feedback to the operator
- added root redirect from `/` to `/ui/app-shell`
- hardened project-context fallback so stale remembered paths do not poison current workspace context as easily

## Why this matters
This pass targets the first slice of 5.11:
- shell reliability
- state correctness
- stale-state cleanup
- cleaner boot behavior
