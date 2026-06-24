param(
    [Parameter(Mandatory=$true)]
    [string]$PackPath
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_delete_recovery_pack.py"
$code = @'
import json
import os
from app.services.recovery_service import recovery_service
print(json.dumps(recovery_service.delete_pack(os.environ["JARVIS_RECOVERY_PACK_PATH"]), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    $env:JARVIS_RECOVERY_PACK_PATH = $PackPath
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Recovery pack delete failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_RECOVERY_PACK_PATH -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
