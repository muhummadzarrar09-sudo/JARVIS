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

Still pending:
- deeper live branching from actual Windows GUI state
- stronger exact activation/focus reliability
- richer app-specific workflows
- even smoother local fallbacks everywhere

### Phase 5 — Desktop App Shell + Voice/UI
Status: planned
- packaged desktop app shell
- visual version of the terminal command center
- local STT
- local TTS
- orb/subtitle layer
- action timeline UI
- approval dialogs

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
- search for local ai agents
- research local ai agents
- show me the current page
- resume project
- resume browser
- resume code
- start coding
- take screenshot
- write note remember this idea
- start my workday
- show setup
- get me started

### Console helpers
- /starter
- /today
- /next
- /focus
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
1. add richer one-shot workflows for common everyday goals
2. deepen browser/runtime fallbacks so links and previews are always useful
3. improve live-state-aware branching from browser/window conditions
4. continue simplifying session/task flows for non-technical users
5. keep maturing the terminal command center toward the future desktop app shell
