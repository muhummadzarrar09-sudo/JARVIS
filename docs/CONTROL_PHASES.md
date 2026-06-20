# Control + Continuity Phase Extensions

This document tracks the next layers added on top of the terminal/browser MVP.

## Phase extension A — Process / laptop-control groundwork
Current additions:
- process listing
- windowed-process listing on Windows
- process start
- process kill

CLI examples:
```text
proc list
proc list: chrome
proc windows
proc start: notepad
proc kill: notepad.exe
```

API endpoints:
- `GET /tools/proc/list`
- `GET /tools/proc/windows`
- `POST /tools/proc/start`
- `POST /tools/proc/kill`

## Phase extension B — Session continuity groundwork
Current additions:
- checkpoint create for current session
- checkpoint retrieval
- JSON checkpoint artifacts stored locally

CLI examples:
```text
checkpoint create
checkpoint create: leaving room, continue on phone later
checkpoint get
```

API endpoints:
- `POST /checkpoints/create`
- `GET /checkpoints/get?session_id=...`

## Why this matters
These additions move JARVIS closer to:
- laptop control
- recoverable state
- handoff-aware continuity
- audit-friendly automation

## Phase extension C — Desktop control starter
Current additions:
- desktop window listing
- active-window inspection
- screen state inspection
- focus window by title with verification
- type into focused app
- key press + hotkey support
- coordinate clicks with bounds checks
- desktop screenshots with active-window context

CLI examples:
```text
desktop windows
desktop focus: Notepad
desktop type: hello from jarvis
desktop press: enter
desktop hotkey: ctrl+shift+t
desktop click: 500,300
desktop screenshot
```

API endpoints:
- `GET /tools/desktop/windows`
- `GET /tools/desktop/active`
- `GET /tools/desktop/screen`
- `POST /tools/desktop/action`

## Phase extension D — App wrappers
Current additions:
- higher-level wrappers for Notepad, Calculator, Explorer, VS Code, browser, and terminal
- wrapper open/focus/ensure/status/reset actions
- lightweight remembered wrapper state
- quick note workflow via Notepad
- reusable recipes for search, research, project startup, workspace inspection/resume, terminal commands, and VS Code files
- cleaner wrapper-oriented API surface

CLI examples:
```text
app wrappers
app recipes
app status
app status: vscode
app open: notepad
app ensure: terminal ::: .
app reset: browser
app code: .
app browse: https://example.com
app note: hello from jarvis
app recipe: terminal.command ::: . || python --version
app recipe: browser.search ::: jarvis local assistant
app recipe: project.inspect ::: .
app recipe: project.resume
```

API endpoints:
- `GET /tools/apps/wrappers`
- `GET /tools/apps/recipes`
- `GET /tools/apps/status`
- `POST /tools/apps/action`

## Recommended next build targets
1. exact window activation + safer focus flows
2. desktop screenshots tied to audit/replay
3. keyboard/mouse automation layer with action guards
4. richer app-specific workflow recipes
5. mobile companion consuming checkpoint/session APIs
