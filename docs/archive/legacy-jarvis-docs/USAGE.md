# Terminal MVP Usage

## Start the API
```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Start terminal JARVIS
```powershell
.\.venv\Scripts\Activate.ps1
python -m app.cli repl
```

Useful console panels:
```text
/starter
/today
/progress
/setup
/phase4
/phase5
/next
/focus
/browser
/status
/wrappers
/recipes
/projects
/doctor
/timeline
/replay
/palette
/tasks
/work
/done
/sessions
/tools
```

Quick beginner shortcut:
```text
/do open readme
/do show my tasks
/do work on next task
/do show me today's focus
```

## CLI examples

### Normal chat
```text
Design me a roadmap for my Python project
```

### Shell command
```text
shell: dir
```

### List files
```text
fs list: .
```

### Read a file
```text
fs read: README.md
```

### Write a file
```text
fs write: notes/todo.txt ::: Build JARVIS phase 1 today
```

### Append to a file
```text
fs append: notes/todo.txt ::: Add browser automation later
```

### Make a directory
```text
fs mkdir: notes/archive
```

## Browser mode examples

### Install browser support
```powershell
.\scripts\install-browser.ps1
```

Browser startup now tries installed browsers in preference order from `.env`:
```env
BROWSER_CHANNEL_PREFERENCE=chrome,msedge,brave,firefox,playwright_chromium
```

### Start browser
```text
browser start
```

### Open a page
```text
browser open: https://example.com
```

### Get title
```text
browser title
```

### Read page text
```text
browser text
```

### Fill and submit a search field
```text
browser fill: input[name='q'] ::: jarvis local agent
browser press: input[name='q'] ::: Enter
```

### Click by visible text
```text
browser click I'm Feeling Lucky
```

### Inspect a browser selector when click fails
```text
browser inspect: text=I'm Feeling Lucky
```

### Force-click a matched element
```text
browser forceclick: text=I'm Feeling Lucky
```

### Screenshot
```text
browser screenshot: data/browser/example.png
```

### Close browser
```text
browser close
```

## Process / desktop-control groundwork

### List processes
```text
proc list
proc list: chrome
```

### List windowed apps
```text
proc windows
```

### Start an app
```text
proc start: notepad
```

### Kill a process
```text
proc kill: notepad.exe
```

## App wrappers

### Beginner-friendly natural commands
```text
help me start
show my project
show project overview
review this project
show my project files
show my setup blockers
what should i do next
show me where to start
show me today's focus
show my tasks
what task should i do next
what am i doing now
work on next task
complete next task
wrap up current task
add task finish setup
done with task 1
show my sessions
show me recent work
resume last session
open browser
open chrome
open edge to https://example.com
use chrome browser
use default browser
open browser to https://example.com
search for local ai agents
search this site for pricing
research local ai agents
show me the current page
show browser options
open code here
open files here
open terminal here
open readme
resume project
resume browser
resume code
start coding
continue coding
take screenshot
write note remember this idea
start my workday
show setup
get me started
```

Examples of easy one-shot goals:
```text
/do review this project
/do show my project files
/do start coding
/do show me the current page
/do show me today's focus
```

### List wrappers, recipes, diagnostics, and project context
```text
app wrappers
app recipes
app status
app status: vscode
app state: browser
app doctor
app doctor: browser
app project
app project: .
```

### Safety / operator flow
High-risk commands now ask for confirmation in the shell UI before execution.
There is also a server-side confirmation gate on `/chat`, so direct API calls cannot silently bypass the approval step for high-risk commands.

### Open, ensure, or reset higher-level wrappers
```text
app open: notepad
app open: explorer ::: .
app open: vscode ::: .
app open: browser ::: https://example.com
app ensure: terminal ::: .
app ensure: browser ::: https://example.com
app reset: browser
```

### Wrapper shortcuts
```text
app note: hello from jarvis
app explore: .
app code: .
app browse: https://example.com
```

### Wrapper recipes
```text
app recipe: note.quick ::: hello from jarvis
app recipe: explorer.workspace ::: .
app recipe: vscode.project ::: .
app recipe: vscode.file ::: README.md
app recipe: vscode.readme ::: .
app recipe: terminal.project ::: .
app recipe: terminal.command ::: python -m uvicorn app.main:app --reload
app recipe: terminal.command ::: . || python --version
app recipe: browser.search ::: jarvis local assistant
app recipe: browser.research ::: local ai agents
app recipe: browser.snapshot ::: https://example.com
app recipe: browser.resume
app recipe: project.inspect ::: .
app recipe: project.starter ::: .
app recipe: project.resume
```

## Desktop control starter

### Install desktop support
```powershell
.\scripts\install-desktop.ps1
```

### List focusable windows and inspect focus/screen state
```text
desktop windows
desktop active
desktop screen
```

### Focus a window
```text
desktop focus: Notepad
desktop focusexact: Calculator
```

### Type or press keys
```text
desktop type: hello from jarvis
desktop press: enter
desktop hotkey: ctrl+shift+t
```

### Click coordinates
```text
desktop click: 500,300
desktop click: 500,300 ::: right
```

### Capture desktop screenshot
```text
desktop screenshot
desktop screenshot: data/desktop/desk.png
```

## Session continuity groundwork

### Create a checkpoint for current session
```text
checkpoint create
checkpoint create: leaving room, continue on mobile later
```

### Load the latest saved checkpoint for current session
```text
checkpoint get
```

## Task + session management

### Create and manage tasks
```text
task create: Finish JARVIS phase 1
task list
task open
task done: 1
task reopen: 1
```

### Inspect stored sessions
```text
session list
session overview
```

## Switching between mock mode and real GGUF inference

### Easiest way
```powershell
.\scripts\use-local-models.ps1
.\scripts\use-mock-models.ps1
```

### Natural-language commands
```text
show model status
use local models
use mock mode
```

### Model API / preload
```text
POST /models/preload?slot=fast
POST /models/preload?slot=main
```

### Manual `.env` mode
```env
DEFAULT_MODEL_PROVIDER=auto
```

`auto` will use local GGUF models when `llama-cpp-python` is available and a model is found in `data/models`, then fall back safely to mock mode if not.

You can still force direct llama.cpp mode if you want:
```env
DEFAULT_MODEL_PROVIDER=llama_cpp
```

Optional llama runtime tuning:
```env
LLAMA_N_CTX=4096
LLAMA_N_THREADS=0
LLAMA_N_GPU_LAYERS=0
LLAMA_MAX_TOKENS=384
```

## Notes
- current tool use is explicit/prefix-based for reliability
- later phases can let the planner decide tools automatically
- workspace_root is restricted so file operations stay inside the project scope
- browser mode is currently single-session and Chromium-based
- if browser start fails, run `python -m playwright install chromium` inside the venv

## Database maintenance

### API
```text
GET /database/status
GET /database/backups
GET /database/backup-file
POST /database/backup
POST /database/backup-delete
POST /database/restore
POST /database/vacuum
```

### PowerShell
```powershell
.\scripts\backup-db.ps1 -Label before-upgrade
.\scripts\restore-db.ps1 -BackupPath data/backups/<backup-file>.sqlite3
.\scripts\vacuum-db.ps1
.\scripts\rotate-audit.ps1 -Label maintenance
.\scripts\prune-audit.ps1 -KeepArchives 10
```

## Shell launcher diagnostics
```powershell
.\scripts\start-shell.ps1 -PrintDiagnostics
.\scripts\start-shell.ps1 -BrowserOnly
.\scripts\start-shell.ps1 -PrintDiagnostics -OpenRecoveryOnFailure -RetryCount 12 -RetryDelay 1.5
```

## Audit maintenance

### API
```text
GET /audit/status
GET /audit/archives
GET /audit/archive-preview
GET /audit/archive-file
POST /audit/archive-delete
POST /audit/rotate
POST /audit/prune
```

### PowerShell
```powershell
.\scripts\rotate-audit.ps1 -Label maintenance
.\scripts\prune-audit.ps1 -KeepArchives 10
```

## Session cleanup

### API
```text
POST /sessions/cleanup
```

Example body:
```json
{
  "keep_recent": 25,
  "drop_empty_older_than_days": 7,
  "drop_inactive_older_than_days": 90,
  "dry_run": false
}
```

## Recovery packs

### API
```text
GET /maintenance/doctor
GET /maintenance/history
GET /maintenance/settings
GET /maintenance/packs
GET /maintenance/pack-preview
GET /maintenance/pack-file
POST /maintenance/settings
POST /maintenance/pack-delete
POST /maintenance/export-pack
POST /maintenance/import-pack
```

### PowerShell
```powershell
.\scripts\export-recovery-pack.ps1 -Label before-major-change
.\scripts\import-recovery-pack.ps1 -PackPath data/recovery/packs/<pack-file>.zip
```

## Session cleanup dry-run example
```json
{
  "keep_recent": 25,
  "drop_empty_older_than_days": 7,
  "drop_inactive_older_than_days": 90,
  "dry_run": true
}
```
