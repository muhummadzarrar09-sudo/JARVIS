# Phase 5.11 — Real-Use Stabilization Plan

## Goal
Make the current JARVIS shell + local runtime dependable enough for real daily personal use.

## Build principles
- keep the system clean and modular
- stabilize before expanding
- do not introduce Laravel/PHP into the runtime path right now
- defer AirLLM-style layer/offload inference exploration until **after Phase 11**

## Explicitly out of scope for 5.11
- Phase 6 mobile companion work
- major voice/orb expansion
- Laravel/PHP integration
- AirLLM-style inference re-architecture
- aesthetic-only UI redesigns

---

## Phase 5.11.X sequence

### 5.11.1 — Shell reliability + state correctness
Status: **complete**
Percent: **100.0%**

#### Focus
- fix send/enter edge cases
- eliminate boot-stuck / partial-loading behavior
- remove stale remembered-state contamination
- keep shell state hydration predictable

#### Tasks
1. verify `/ui/app-shell` boot path end-to-end
2. remove malformed remembered browser/project path pollution
3. normalize maintenance/settings state shown in shell
4. ensure shell fallback/recovery UI never blocks normal send flow
5. verify shell can call `/chat` cleanly with local GGUF runtime

#### Implemented so far
- wrapper remembered-state hygiene / normalization layer
- shell bootstrap route for lighter preflight state loading
- shell doctor route for shell-specific boot/state diagnostics
- startup sanitation of wrapper remembered state
- root redirect to `/ui/app-shell`
- safer project-context fallback when remembered paths are stale
- shell boot now consumes `/shell/bootstrap` and surfaces hygiene normalization feedback
- shell state now includes shell bootstrap/doctor surfaces
- shell now has a safer bootstrap banner path before full state hydration
- added `/chat/ping` for shell send-path readiness checks
- shell/runtime surfaces now expose combined runtime stability summaries

#### Exit criteria
- shell loads consistently
- Enter/send works reliably
- shell can reach `/chat`
- shell reflects current Windows-local state instead of stale sandbox state

---

### 5.11.2 — Browser + desktop runtime stability
Status: **complete**
Percent: **100.0%**

#### Focus
- real Windows launch behavior
- browser preference correctness
- desktop focus/undo correctness

#### Tasks
1. validate Chrome / Edge / fallback launch order on the real machine
2. verify remembered browser state does not poison new runs
3. verify live browser window detection branches correctly
4. validate desktop focus, focus_handle, and undo flows on real windows
5. tighten browser/desktop fallbacks from real runtime feedback

#### Implemented
- runtime stability service for browser + desktop summaries
- `/runtime/browser`, `/runtime/desktop`, and `/runtime/summary` routes
- `/runtime/browser/validate` and `/runtime/desktop/validate` routes
- shell state now carries runtime stability data
- shell UI now shows shell-path readiness and runtime stability panels
- shell exposes browser and desktop runtime validation actions
- runtime validation harness now includes runtime summary and desktop/browser validation details

#### Exit criteria
- browser launch selection is predictable
- browser status matches reality
- focus behavior is trustworthy on the real Windows desktop

---

### 5.11.3 — Maintenance + recovery correctness
Status: **complete**
Percent: **100.0%**

#### Focus
- backup / restore / archive / cleanup flows must be safe and verifiable

#### Implemented
- maintenance verification summary service
- `/maintenance/verify` route
- backup verification for recent database backups
- archive verification for recent audit archives
- recovery pack verification for recent recovery packs
- session cleanup preview verification tied to stored maintenance settings
- shell maintenance verification panel and verification action
- maintenance history now includes verification-friendly operation traces

#### Exit criteria
- maintenance operations succeed without corrupting runtime state
- recovery flows are reversible and understandable
- maintenance drawer/history are trustworthy

---

### 5.11.4 — Model/runtime integration stability
Status: **complete**
Percent: **100.0%**

#### Focus
- stable local GGUF use through shell, API, preload, and warm-start flows

#### Implemented
- model/runtime consistency summary in `app/services/model_service.py`
- unload-runtime-cache support in `llama_manager` + model service
- `POST /models/verify` for real local GGUF runtime verification
- `POST /models/unload` for provider-transition/cache-reset stability
- `GET /chat/ping` now exposes loaded-model count and consistency data
- shell model runtime panel now shows consistency + loaded count
- shell can verify fast/main runtime paths and unload in-process model cache directly
- configure-provider flow now clears in-process model cache to reduce transition mismatch risk

#### Exit criteria
- local GGUF model works reliably through normal shell usage
- runtime state is accurately reported
- no hidden provider mismatch between shell and backend

---

### 5.11.5 — Actual-use acceptance sweep
Status: **active**
Percent: **100.0%**

#### Focus
- final acceptance based on repeated real usage, not just isolated route checks


#### Implemented
- acceptance state persistence service
- acceptance sweep service with safe/deep modes
- `/acceptance/status`, `/acceptance/history`, `/acceptance/run`, `/acceptance/reset`
- `/acceptance/final-blockers` and `/acceptance/export`
- acceptance sweep result scoring, blocker extraction, blocker delta vs previous run, and readiness-for-5.12 signal
- shell acceptance panel, history actions, blocker summary action, export action, and reset action
- repeated acceptance loop script

#### Tasks
1. run multi-step shell sessions on the real machine
2. test reconnect/recovery behavior during API interruption
3. test maintenance flows after real usage changes state
4. confirm shell remains usable across repeated restarts
5. record final blocker list for 5.12 polish

#### Exit criteria
- no major blocker remains for normal personal use
- remaining issues are polish issues, not trust issues

---

## Acceptance definition for Phase 5.11
Phase 5.11 is complete when:
- shell is reliable enough for normal command use
- local model use is stable through the shell
- browser + desktop flows are trustworthy on the real Windows machine
- maintenance/recovery flows are safe enough to rely on
- remaining work clearly belongs to polish, not stabilization

## Next phase after 5.11
### Phase 5.12 — Daily-Driver Polish
That phase will focus on:
- calmer shell UX
- cleaner maintenance UX
- better defaults
- long-session comfort
- repeated-use polish
