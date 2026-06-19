Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1
pip install -r requirements-browser.txt
python -m playwright install chromium
