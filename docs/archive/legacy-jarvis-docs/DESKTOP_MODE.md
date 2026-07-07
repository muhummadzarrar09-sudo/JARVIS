# Desktop Mode Starter

This phase begins real laptop-control features beyond browser automation.

## Current capabilities
- list desktop windows
- inspect current active window
- inspect screen size and mouse position
- focus a window by title with safer verification
- type text into the focused app
- press a key
- send a hotkey combo
- click screen coordinates with bounds checks
- take a desktop screenshot with active-window context

## Install path
```powershell
.\scripts\install-desktop.ps1
```

## CLI examples

### List windows
```text
desktop windows
```

### Inspect current active window and screen state
```text
desktop active
desktop screen
```

### Focus a window by title
```text
desktop focus: Notepad
```

### Type into the focused window
```text
desktop type: hello from jarvis
```

### Press a key
```text
desktop press: enter
```

### Use a hotkey
```text
desktop hotkey: ctrl+shift+t
```

### Click coordinates
```text
desktop click: 500,300
desktop click: 500,300 ::: right
```

### Take a screenshot
```text
desktop screenshot
desktop screenshot: data/desktop/desk.png
```

## API
- `GET /tools/desktop/windows`
- `POST /tools/desktop/action`

## Notes
- this phase is Windows-first
- desktop control uses optional Python packages and may need reinstall in your local `.venv`
- screenshots are stored locally in the workspace
- this is the starter layer before richer focus/vision-driven control
