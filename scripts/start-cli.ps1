Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1
python -m app.cli repl
