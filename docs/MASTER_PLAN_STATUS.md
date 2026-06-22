# JARVIS Master Plan + Status

This is the single top-level planning document for the build.

## Vision
Build a local-first JARVIS-style assistant that can:
- reason locally
- remember sessions/tasks/checkpoints
- operate browser and desktop tools
- wrap common apps with easier workflows
- grow from terminal-first command center into a packaged desktop app shell
- later add voice, orb UI, and mobile handoff

## Current build posture
### Working style
- terminal-first
- command-center UI
- local APIs behind the scenes
- wrappers/recipes for app actions
- audit + replay visibility
- beginner-friendly commands layered on top of technical commands

## Phase map

### Phase 0 — Foundation
Status: mostly done
- FastAPI scaffold
- terminal CLI / REPL
- SQLite persistence
- audit logging
- bootstrap/install scripts
- local folder structure
- local model runtime path scaffolded

### Phase 1 — Brain + Terminal MVP
Status: active / partially complete
- chat endpoint
- local/mock model routing shell
- memory persistence
- shell tools
- file tools
- tasks
- sessions
- checkpoints
- timeline/replay support
- beginner starter/guide flows

Still pending for true Phase 1 completion:
- verified real local llama.cpp inference on target machine
- stronger planning/step execution memory

### Phase 2 — Structured Tool Use
Status: started
- process manager groundwork
- tool registry
- operator-mode risk classification
- replay candidates

Still pending:
- Git tools
- stronger policy/trusted zones
- richer undo semantics

### Phase 3 — Browser Automation
Status: started
- Playwright integration scaffold
- browser open/fill/press/click/screenshot
- selector inspect / force click helpers
- browser wrapper recipes
- browser resume/snapshot/research flows
- browser candidate detection for installed browsers (Chrome/Edge/Brave/Firefox/playwright bundle)
- browser site-scoped search and remembered-browser branching

Still pending:
- multi-tab management
- richer extraction logic
- browser login/session storage abstractions

### Phase 4 — Desktop Control + Wrappers
Status: heavily active
- desktop window listing
- focus by title
- screen info
- screenshot capture
- desktop typing/keypress/hotkeys/clicks
- wrapper doctor diagnostics
- app wrappers
- app recipes
- wrapper remembered state
- project-aware wrapper flows
- terminal command-center panels
- beginner-friendly natural commands
- `/do ...` shortcut
- README, directory, and browser-link fallbacks when local apps are unavailable

Phase 4 completion estimate: **100.0%**

#### Phase 4 mini-task breakdown
- Desktop control primitives: **9/9 complete (100.0%)**
  - done: desktop window listing, active-window inspection, screen-state inspection, focus by title, keyboard typing starter, hotkey + coordinate click starter, desktop screenshots, exact activation hardening beyond title matching, richer desktop safety / undo policies
  - left: none in the current desktop primitives bucket
- Wrappers and recipes: **7/7 complete (100%)**
  - done: app wrapper starter, workflow recipe starter, wrapper remembered state, workspace-aware wrapper flows, browser candidate detection + preference support, deeper live browser branching starter, broader app-specific workflow coverage
  - left: none in the currently tracked wrapper/recipe bucket
- Command-center UX: **6/6 complete (100%)**
  - done: command-center panels, beginner-friendly natural commands + `/do`, timeline/replay/operator surfaces, project-context panels, browser panel / browser option visibility, desktop app shell preparation layer
  - left: none in the currently tracked command-center bucket

Still pending after Phase 4 checklist completion:
- validate exact desktop focus/activation behavior on the real Windows machine
- validate multi-browser launch behavior on the real Windows machine
- continue refining browser/window live-state branching with real runtime feedback

### Phase 5 — Desktop App Shell + Voice/UI
Status: active
- packaged desktop app shell
- visual version of the terminal command center
- local web shell prototype at `/ui/app-shell`
- local STT
- local TTS
- orb/subtitle layer
- action timeline UI
- approval dialogs

Phase 5 completion estimate: **100.0%**

#### Phase 5 mini-task breakdown
- Shell foundation: **4/4 complete (100.0%)**
  - done: static shell preview, live web shell route, live shell panels, in-shell prompt posting to /chat
- Shell UX hardening: **4/4 complete (100.0%)**
  - done: validation panel, phase status visibility, task/session interaction in shell, approval modal / guard UX
- Desktop app transition: **4/4 complete (100.0%)**
  - done: desktop shell packaging plan, runtime validation harness for Windows testing, actual packaged desktop app wrapper starter, voice / orb shell integration starter

### Phase 6 — Android / Handoff
Status: groundwork only
- checkpoints exist
- session continuity primitives exist

Still pending:
- websocket/mobile companion
- paired-device auth
- room-exit / return handoff logic

## What exists right now for the user
### Technical commands
- shell tools
- file tools
- browser tools
- desktop tools
- process tools
- task tools
- session tools
- wrapper tools

### Beginner commands
Examples:
- help me start
- show my project
- show project overview
- review this project
- show my project files
- show my setup blockers
- what should i do next
- show me where to start
- show me today's focus
- show my tasks
- what task should i do next
- what am i doing now
- work on next task
- complete next task
- wrap up current task
- show my sessions
- show me recent work
- resume last session
- open readme
- open code here
- open files here
- open terminal here
- open chrome
- open edge to https://example.com
- use chrome browser
- use default browser
- search for local ai agents
- search this site for pricing
- research local ai agents
- show me the current page
- show browser options
- resume project
- resume browser
- resume code
- start coding
- continue coding
- take screenshot
- write note remember this idea
- start my workday
- show setup
- get me started

### Console helpers
- /starter
- /today
- /progress
- /setup
- /phase4
- /phase5
- /next
- /focus
- /browser
- /status
- /wrappers
- /recipes
- /projects
- /doctor
- /timeline
- /replay
- /palette
- /tasks
- /work
- /done
- /sessions
- /resume
- /use <index|shortid|fullid>
- /find <text>
- /do <goal>

## Immediate next sprint focus
1. validate installed-browser preference launching on the real Windows machine and tune browser-specific fallbacks
2. validate exact desktop focus/activation behavior on the real Windows machine
3. deepen live-state-aware branching from browser/window conditions
4. harden the packaged shell launcher on the real Windows machine
5. add richer one-shot workflows for common everyday goals
6. continue simplifying session/task flows for non-technical users
7. keep improving browser/runtime fallbacks so links and previews are always useful
