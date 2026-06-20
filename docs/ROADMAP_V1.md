# JARVIS Roadmap v1

This roadmap turns the vision into a build sequence with current status.

## Current status snapshot

### Phase 0 — Foundation
**Status:** mostly done
- [x] FastAPI scaffold
- [x] terminal CLI / REPL
- [x] SQLite memory bootstrap
- [x] audit logging
- [x] PowerShell bootstrap
- [x] browser install helper
- [~] llama.cpp runtime depends on Python 3.11 + successful local install

### Phase 1 — Brain + Terminal MVP
**Status:** actively in progress
- [x] chat endpoint
- [x] mock/local model routing shell
- [x] session memory persistence
- [x] shell tools
- [x] filesystem tools
- [x] task management layer
- [x] session listing + overview endpoints
- [x] checkpoint groundwork
- [ ] verify real llama.cpp inference on target machine
- [ ] add richer planner/step execution memory

### Phase 2 — Structured Tool Use
**Status:** started early
- [x] process manager groundwork
- [x] tool registry endpoint
- [ ] Git tools
- [ ] policy labels + trusted zones
- [ ] replay/undo metadata per action

### Phase 3 — Browser Automation
**Status:** started
- [x] Playwright integration
- [x] browser open/fill/press/click/screenshot
- [x] selector inspect + force click helpers
- [ ] multi-tab management
- [ ] browser workflow recipes
- [ ] login/session storage abstractions

### Phase 4 — Desktop Control
**Status:** started
- [x] window listing
- [x] active-window inspection
- [x] screen-state inspection
- [x] focus by title
- [x] keyboard typing starter
- [x] desktop screenshots
- [x] hotkey + coordinate click starter
- [x] guard metadata on desktop actions
- [x] app-level action wrappers starter
- [x] richer app-specific workflow recipes starter
- [x] wrapper-specific state persistence starter
- [ ] exact window activation hardening beyond title matching
- [ ] richer desktop safety/undo policies
- [ ] smarter wrapper/recipe branching from live app state

### Phase 5 — Voice + Orb UI
**Status:** planned
- [ ] local STT
- [ ] local TTS
- [ ] wake word
- [ ] orb UI + subtitles

### Phase 6 — Android Handoff
**Status:** groundwork only
- [x] local checkpoints
- [ ] websocket session stream
- [ ] mobile-responsive UI
- [ ] paired-device auth

---

## Recommended build order from here

### Step A — Finish Phase 1 hardening
1. Get Python 3.11 working on target machine
2. Rebuild `.venv`
3. Install/import-check `llama-cpp-python`
4. Download GGUF models successfully
5. Switch `.env` to `DEFAULT_MODEL_PROVIDER=llama_cpp`
6. Verify real local responses in CLI/API

### Step B — Expand structured control
1. Add window focus/activation actions
2. Add safer process launch profiles
3. Add file-search / project-search tools
4. Add action replay metadata in audit logs

### Step C — Build desktop control layer
1. harden focus/activate logic on Windows
2. add exact window targeting + safer fallbacks
3. add desktop screenshots into audit/replay loop
4. add active-window aware action guardrails
5. expand wrapper recipes and app-specific workflows
6. later: click coordinates / vision-assisted selection
7. later: wrapper state persistence and smarter app agents

### Step D — Add mobile/UI layer
1. local web dashboard
2. packaged desktop app shell
3. action timeline
4. session/checkpoint viewer
5. mobile companion view

### When the real desktop app happens
The packaged desktop app starts after the control backend is stable enough to wrap.
That means:
- terminal/core agent stable first
- browser + desktop control primitives stable second
- app wrappers third
- then the desktop app shell wraps those capabilities as the main user experience

Practically, that puts the desktop app shell at the boundary between late Phase 4 and early Phase 5.

---

## Phase 1 deliverables now in repo
- `/chat`
- `/health`
- `/audit/recent`
- `/sessions/list`
- `/sessions/overview`
- `/sessions/recent-messages`
- `/tasks`
- `/tasks/status`
- `/tools/registry`
- `/tools/shell`
- `/tools/fs/*`
- `/tools/browser/*`
- `/tools/proc/*`
- `/checkpoints/*`

## CLI commands now available
- shell commands
- filesystem commands
- browser commands
- process commands
- checkpoint commands
- task commands
- session overview commands

## What “Phase 1 complete” means for this project
For your JARVIS specifically, Phase 1 is complete when:
- real local GGUF inference is working
- sessions persist correctly
- tasks and checkpoints persist correctly
- shell/files/browser basics are reliable
- audit trail captures all major actions

That is the bar before moving hard into full desktop control.
