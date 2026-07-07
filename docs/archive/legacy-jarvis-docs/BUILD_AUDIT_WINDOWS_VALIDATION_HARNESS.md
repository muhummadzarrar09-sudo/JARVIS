# Build Audit — Windows Validation Harness

## Added files
- `scripts/runtime_validation.py`
  - collects a runtime validation report
  - can optionally attempt launching browser candidates
  - can optionally test fuzzy desktop window finding for a given title
  - writes JSON output to `data/validation/`

- `scripts/validate-runtime.ps1`
  - PowerShell wrapper for the runtime validation script

- `docs/PHASE5_DESKTOP_SHELL_PLAN.md`
  - planning document for the packaged desktop shell after Phase 4

## Purpose
This sprint prepares the next real step after Phase 4 checklist completion:
- validating actual Windows/browser behavior on the target machine
- gathering concrete runtime evidence
- shaping the next desktop shell phase

## Usage
Example:
```powershell
.\scripts\validate-runtime.ps1
.\scripts\validate-runtime.ps1 -AttemptBrowserStarts
.\scripts\validate-runtime.ps1 -AttemptBrowserOpens -Browser chrome,msedge -BrowserUrl "https://example.com"
.\scripts\validate-runtime.ps1 -FocusTitle "Visual Studio Code" -FocusMatchIndex 0
```

## Expected output
- JSON report in `data/validation/`
- browser candidate availability + default candidate
- browser doctor + browser context state
- desktop safety state
- desktop active window and window list
- shell launcher readiness
- optional browser launch/open attempt results
- optional desktop focus attempt + undo result

## Model runtime checks
- `show model status` in chat or shell
- `POST /models/use-local` to prefer downloaded GGUF models
- `.\scripts\use-local-models.ps1` to switch `.env` quickly on Windows
