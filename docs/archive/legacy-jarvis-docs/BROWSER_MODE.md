# Browser Mode

## Purpose
Browser mode gives JARVIS a real web action layer using Playwright.

## Install path
```powershell
.\scripts\install-browser.ps1
```

This installs:
- Python Playwright package
- Chromium browser binary used by Playwright

## CLI command patterns

### Start browser
```text
browser start
```

### Open a URL
```text
browser open: https://example.com
```

### Read page title
```text
browser title
```

### Read visible page text snapshot
```text
browser text
```

### Click an element
```text
browser click: text=More information
```

Shorthand also works now:
```text
browser click I'm Feeling Lucky
```

### Inspect why a selector is failing
```text
browser inspect: text=I'm Feeling Lucky
```

### Force-click a matched element
```text
browser forceclick: text=I'm Feeling Lucky
```

### Fill a field
```text
browser fill: input[name='q'] ::: jarvis local agent
```

### Press a key in a field
```text
browser press: input[name='q'] ::: Enter
```

### Take a screenshot
```text
browser screenshot: data/browser/home.png
```

### Go back / forward
```text
browser back
browser forward
```

### Close browser
```text
browser close
```

## API route
Use `POST /tools/browser/action`.

Example payload:
```json
{
  "action": "open",
  "url": "https://example.com"
}
```

## Notes
- browser mode starts lazily on first use
- tool output is logged to the audit trail
- screenshots are saved inside the workspace only
- current implementation is phase-1 browser control; multi-tab and richer workflows come later
