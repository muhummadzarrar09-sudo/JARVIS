param(
    [string]$Label,
    [switch]$SkipBackups,
    [switch]$SkipArchives
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_export_recovery_pack.py"
$code = @'
import json
import os
from app.services.recovery_service import recovery_service
print(json.dumps(recovery_service.export_pack(
    label=os.environ.get("JARVIS_RECOVERY_LABEL"),
    include_backups=(os.environ.get("JARVIS_RECOVERY_SKIP_BACKUPS") != "1"),
    include_archives=(os.environ.get("JARVIS_RECOVERY_SKIP_ARCHIVES") != "1"),
), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    if ($Label) { $env:JARVIS_RECOVERY_LABEL = $Label }
    if ($SkipBackups) { $env:JARVIS_RECOVERY_SKIP_BACKUPS = "1" }
    if ($SkipArchives) { $env:JARVIS_RECOVERY_SKIP_ARCHIVES = "1" }
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Recovery pack export failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_RECOVERY_LABEL -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_SKIP_BACKUPS -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_SKIP_ARCHIVES -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
