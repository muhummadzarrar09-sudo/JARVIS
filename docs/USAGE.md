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

### List wrappers and recipes
```text
app wrappers
app recipes
app status
app status: vscode
app state: browser
```

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

## Switching from mock mode to real GGUF inference

Open `.env` and set:
```env
DEFAULT_MODEL_PROVIDER=llama_cpp
```

Make sure your GGUF file names match:
```env
DEFAULT_FAST_MODEL=Qwen2.5-3B-Instruct-Q4_K_M.gguf
DEFAULT_MAIN_MODEL=Qwen2.5-7B-Instruct-Q4_K_M.gguf
```

## Notes
- current tool use is explicit/prefix-based for reliability
- later phases can let the planner decide tools automatically
- workspace_root is restricted so file operations stay inside the project scope
- browser mode is currently single-session and Chromium-based
- if browser start fails, run `python -m playwright install chromium` inside the venv
