# App Wrappers Phase

This phase adds higher-level application wrappers on top of raw desktop/process/browser tools.

## Why wrappers exist
Raw desktop actions are powerful but low-level.
Wrappers give JARVIS reusable app-specific entry points with cleaner commands and safer defaults.

## Current wrappers
- notepad
- calculator
- explorer
- vscode
- browser
- terminal

## Current wrapper recipes
- `note.quick`
- `explorer.workspace`
- `vscode.project`
- `vscode.file`
- `vscode.readme`
- `terminal.project`
- `terminal.command`
- `browser.search`
- `browser.research`
- `browser.snapshot`
- `browser.resume`
- `project.inspect`
- `project.starter`
- `project.resume`
- `vscode.resume`

## Smarter wrapper behavior
Wrappers now maintain lightweight remembered state such as:
- last target/path/url
- last recipe used
- last known successful action
- last query / last command where relevant

That allows commands like `app ensure` to reuse prior targets where it makes sense.

## CLI commands

### List wrappers, recipes, status, diagnostics, and project context
```text
app wrappers
app recipes
app status
app status: browser
app state: vscode
app doctor
app doctor: browser
app project
app project: .
app context: .
```

### Console-level visibility helpers
```text
/starter
/next
/status
/projects
/doctor
/timeline
/replay
/palette
/tasks
/sessions
/resume
```

Quick beginner shortcut:
```text
/do open readme
/do show my tasks
/do work on next task
```

### Easy natural commands
```text
help me start
show my project
open browser
search for local ai agents
open code here
open files here
open terminal here
open readme
resume project
take screenshot
write note remember this idea
```

### Open / ensure / reset wrappers
```text
app open: notepad
app open: calculator
app open: explorer ::: .
app open: vscode ::: .
app open: browser ::: https://example.com
app open: terminal
app ensure: terminal ::: .
app ensure: browser ::: https://example.com
app reset: browser
app reset
```

### Focus wrappers
```text
app focus: notepad
app focusexact: calculator
```

### Wrapper shortcuts
```text
app note: hello from jarvis
app explore: .
app code: .
app browse: https://example.com
```

### Run recipes
```text
app recipe: note.quick ::: hello from jarvis
app recipe: explorer.workspace ::: .
app recipe: vscode.project ::: .
app recipe: vscode.file ::: README.md
app recipe: vscode.readme ::: .
app recipe: vscode.resume
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

## API
- `GET /tools/apps/wrappers`
- `GET /tools/apps/recipes`
- `GET /tools/apps/status`
- `GET /tools/apps/doctor`
- `GET /tools/apps/project-context`
- `GET /audit/timeline`
- `GET /audit/operator-summary`
- `GET /audit/replay`
- `POST /tools/apps/action`

## Sequence position
This sits after the initial desktop starter because wrappers depend on:
- process launch
- focus logic
- browser integration
- desktop input primitives

It is the bridge between low-level control and the future product-grade desktop app shell.
