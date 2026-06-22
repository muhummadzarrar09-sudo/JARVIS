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
.\scripts\validate-runtime.ps1 -AttemptBrowserStarts -FocusTitle "Visual Studio Code"
```

## Expected output
- JSON report in `data/validation/`
- browser candidate availability
- browser doctor state
- desktop safety state
- desktop active window and window list
- optional browser launch attempt results
