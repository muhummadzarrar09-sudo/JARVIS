# Build Audit — Phase 5.11.1 Pass 2 + 5.11.2 Pass 1

## 5.11.1 implemented
- added `GET /chat/ping` so the shell has a lightweight send-path readiness probe
- shell state now includes dedicated shell bootstrap + shell doctor surfaces
- startup sanitation of wrapper state is now enforced before full shell-state hydration
- safer current-project fallback reduces stale remembered-path poisoning during shell boot

## 5.11.2 implemented
- added `app/services/runtime_stability_service.py`
- added:
  - `GET /runtime/browser`
  - `GET /runtime/desktop`
  - `GET /runtime/summary`
- runtime stability now summarizes:
  - browser readiness
  - preferred browser running state
  - managed-browser availability
  - desktop active-window status
  - desktop window-listing status
  - undo-focus support
- runtime validation harness now includes `runtime_summary`

## Why this matters
This keeps Phase 5.11 in sequence:
- finish shell/state correctness first
- immediately begin real-machine browser/desktop runtime stability work on top of that
