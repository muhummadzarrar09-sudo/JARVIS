# BRAVO-1 UI Plan v1

## Short answer
Yes — the UI is planned.

BRAVO-1 is not meant to stay a raw Python CLI forever.
The UI roadmap is intentionally layered so we can move fast without overbuilding too early.

---

## UI evolution plan
### Layer 1 — Terminal shell
Purpose:
- fastest iteration loop
- direct operator testing
- lowest dependency burden
- best for debugging the core brain

Current status:
- live

### Layer 2 — Thin local web shell
Purpose:
- quick visual shell
- easy state inspection
- browser-accessible local operator surface
- bridge between CLI and polished app shell

Current status:
- live bootstrap

### Layer 3 — Full calm BRAVO-1 shell
Target feel:
- Claude-like chat-first surface
- one primary action
- tiny status strip
- current project, tasks, next actions
- hidden ops by default
- premium, low-noise shell

Status:
- planned, not yet built in final form

### Layer 4 — Packaged desktop shell
Purpose:
- installer-ready local product
- shortcuts, startup, runtime checks
- proper end-user entrypoint

Status:
- later hardening phase

---

## UI rules we are keeping
- chat-first
- low noise
- one primary action
- no dashboard overload
- status visible but quiet
- project continuity visible
- advanced tools hidden until needed

---

## Immediate next UI goals
1. strengthen the thin web shell state model
2. add better structured session/project/runtime cards
3. keep command surfaces simple while capability layers deepen
4. only then move toward the full calm operator shell
