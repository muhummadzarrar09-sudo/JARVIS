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
- `terminal.project`
- `terminal.command`
- `browser.search`
- `browser.research`
- `browser.snapshot`
- `project.starter`

## Smarter wrapper behavior
Wrappers now maintain lightweight remembered state such as:
- last target/path/url
- last recipe used
- last known successful action

That allows commands like `app ensure` to reuse prior targets where it makes sense.

## CLI commands

### List wrappers, recipes, and status
```text
app wrappers
app recipes
app status
app status: browser
app state: vscode
```

### Open / ensure wrappers
```text
app open: notepad
app open: calculator
app open: explorer ::: .
app open: vscode ::: .
app open: browser ::: https://example.com
app open: terminal
app ensure: terminal ::: .
app ensure: browser ::: https://example.com
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
app recipe: terminal.project ::: .
app recipe: terminal.command ::: python -m uvicorn app.main:app --reload
app recipe: browser.search ::: jarvis local assistant
app recipe: browser.research ::: local ai agents
app recipe: browser.snapshot ::: https://example.com
app recipe: project.starter ::: .
```

## API
- `GET /tools/apps/wrappers`
- `GET /tools/apps/recipes`
- `GET /tools/apps/status`
- `POST /tools/apps/action`

## Sequence position
This sits after the initial desktop starter because wrappers depend on:
- process launch
- focus logic
- browser integration
- desktop input primitives

It is the bridge between low-level control and the future product-grade desktop app shell.
