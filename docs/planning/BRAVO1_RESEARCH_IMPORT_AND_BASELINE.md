# BRAVO-1 Research Import + Technical Baseline

## Imported research location
The attached external repo-research files were copied into:

- `docs/research/github-landscape-2026-07-07/`

Included files:
- `00-index.md`
- `01-executive-summary.md`
- `02-repos-deep-analysis.md`
- `03-pattern-map.md`
- `04-synthesis-plan.md`
- `05-recommended-stack.md`
- `06-speed-strategy.md`
- `07-commit-history-intelligence.md`
- `08-final-answer.md`

---

## Current Python baseline
Current Python version in the active environment used here:

- **Python 3.13.13**

Use this as the remembered baseline until we intentionally pin a different BRAVO-1 runtime version.

---

## Legacy script memory
The old implementation was intentionally nuked from the workspace, but these script names are worth remembering so they can be recovered from GitHub if needed:

### Main runtime / shell
- `scripts/start-api.ps1`
- `scripts/start-shell.ps1`
- `scripts/validate-runtime.ps1`
- `scripts/runtime_validation.py`
- `scripts/use-local-models.ps1`
- `scripts/use-mock-models.ps1`

### Database / recovery / audit
- `scripts/backup-db.ps1`
- `scripts/restore-db.ps1`
- `scripts/vacuum-db.ps1`
- `scripts/rotate-audit.ps1`
- `scripts/prune-audit.ps1`
- `scripts/export-recovery-pack.ps1`
- `scripts/import-recovery-pack.ps1`
- `scripts/delete-db-backup.ps1`
- `scripts/delete-audit-archive.ps1`
- `scripts/delete-recovery-pack.ps1`

### Acceptance
- `scripts/acceptance_sweep.py`
- `scripts/run-acceptance.ps1`
- `scripts/run-acceptance-loop.ps1`
- `scripts/export-acceptance.ps1`

These are not present in the current workspace anymore, but they are part of the remembered reconstruction baseline.

---

## Installer target we must not forget
After BRAVO-1 stabilizes, the product should have a real Windows installer:

### Target deliverable
- **`BRAVO-1-Setup.exe`**

### Installer expectations
- install BRAVO-1 into any user-selected folder
- set up Python/runtime dependencies needed by the chosen architecture
- install required browser/desktop automation dependencies
- create app folders, logs, memory, and model directories
- create Start Menu and Desktop shortcuts
- optional first-run setup wizard
- optional model download/setup flow
- optional autostart / launch-at-login checkbox
- clean uninstall path

### Important note
This is a **later hardening / packaging milestone**, not the immediate rebuild starting point.
The immediate priority is still:
1. lock architecture
2. rebuild the minimal core correctly
3. validate on real Windows hardware
4. then package

---

## Immediate caution on imported research
The imported research is valuable as a synthesis source, but before copying architecture blindly we should still verify:
- repo health
- license compatibility
- true local-first fit
- Windows fit
- hardware fit
- maintenance burden
- whether the repo's core magic is actually extractable

So the imported files are now part of the BRAVO-1 docs set, but they should be treated as:
- **high-value input**
- not unquestioned truth

---

## Recommended next doc step
Turn the imported research into a sharper execution board with:
- steal now
- study only
- avoid
- build ourselves
- week 1 rebuild targets
