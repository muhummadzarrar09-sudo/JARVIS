param(
    [string]$OutputPath
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_export_acceptance.py"
$code = @'
import json
import os
from app.services.acceptance_service import acceptance_service
print(json.dumps(acceptance_service.export_latest(output_path=os.environ.get("JARVIS_ACCEPTANCE_OUTPUT")), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    if ($OutputPath) { $env:JARVIS_ACCEPTANCE_OUTPUT = $OutputPath }
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Acceptance export failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_ACCEPTANCE_OUTPUT -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
