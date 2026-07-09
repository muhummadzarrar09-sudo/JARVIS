# BRAVO-1

Clean rebuild workspace for BRAVO-1.

## Quick start
### Arena / local shell
- PowerShell CLI: `./scripts/start-cli.ps1`
- Bash CLI: `./scripts/start-cli.sh`
- PowerShell web shell: `./scripts/start-web-shell.ps1`
- Bash web shell: `./scripts/start-web-shell.sh`
- PowerShell API: `./scripts/start-api.ps1`
- Bash API: `./scripts/start-api.sh`
- PowerShell validation: `./scripts/validate-runtime.ps1`
- Bash validation: `./scripts/validate-runtime.sh`
- PowerShell installer prereq check: `./scripts/check-installer-prereqs.ps1`
- Bash installer prereq check: `./scripts/check-installer-prereqs.sh`

### Direct Python
- CLI: `PYTHONPATH=app python -m bravo1.cli`
- Web shell: `PYTHONPATH=app python -m bravo1.web_main`
- API: `PYTHONPATH=app python -m bravo1.api_main`
- Validation: `PYTHONPATH=app python scripts/runtime_validation.py`

## Core dirs
- `app/` application code
- `runtime/` local model/runtime orchestration
- `app/bravo1/prompts/` operator prompt pack files
- `app/bravo1/adapters/` browser/windows capability adapters
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
- `requirements-runtime.txt` runtime dependency pin file (evolves later)
- `requirements-dev.txt` dev/test dependency pin file
