# BRAVO-1

Clean rebuild workspace for BRAVO-1.

## Quick start
### Arena / local shell
- PowerShell: `./scripts/start-cli.ps1`
- Bash: `./scripts/start-cli.sh`

### Direct Python
- `PYTHONPATH=app python -m bravo1.cli`

## Core dirs
- `app/` application code
- `runtime/` local model/runtime orchestration
- `shell/` shell UI/TUI/web surface
- `research/` working research notes and extracted patterns
- `evals/` evaluation sets and validation flows
- `scripts/` developer/build/bootstrap scripts
- `installer/` Windows setup and packaging assets
- `models/` model manifests, download notes, quantization/runtime config
- `data/` local app data layout notes
- `config/` config templates and defaults
- `tests/` automated tests
- `docs/` planning, imported research, archived legacy docs
