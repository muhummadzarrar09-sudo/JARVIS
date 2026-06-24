param(
    [Parameter(Mandatory=$true)]
    [string]$PackPath,
    [switch]$ExtractOnly,
    [switch]$SkipSafetyBackup,
    [switch]$SkipDatabase,
    [switch]$SkipAudit,
    [switch]$SkipWrapperState
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_import_recovery_pack.py"
$code = @'
import json
import os
from app.services.recovery_service import recovery_service
print(json.dumps(recovery_service.import_pack(
    pack_path=os.environ["JARVIS_RECOVERY_PACK_PATH"],
    restore_database=(os.environ.get("JARVIS_RECOVERY_SKIP_DATABASE") != "1"),
    restore_audit=(os.environ.get("JARVIS_RECOVERY_SKIP_AUDIT") != "1"),
    restore_wrapper_state=(os.environ.get("JARVIS_RECOVERY_SKIP_WRAPPER") != "1"),
    extract_only=(os.environ.get("JARVIS_RECOVERY_EXTRACT_ONLY") == "1"),
    create_safety_backup=(os.environ.get("JARVIS_RECOVERY_SKIP_SAFETY") != "1"),
), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    $env:JARVIS_RECOVERY_PACK_PATH = $PackPath
    if ($ExtractOnly) { $env:JARVIS_RECOVERY_EXTRACT_ONLY = "1" }
    if ($SkipSafetyBackup) { $env:JARVIS_RECOVERY_SKIP_SAFETY = "1" }
    if ($SkipDatabase) { $env:JARVIS_RECOVERY_SKIP_DATABASE = "1" }
    if ($SkipAudit) { $env:JARVIS_RECOVERY_SKIP_AUDIT = "1" }
    if ($SkipWrapperState) { $env:JARVIS_RECOVERY_SKIP_WRAPPER = "1" }
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Recovery pack import failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_RECOVERY_PACK_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_EXTRACT_ONLY -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_SKIP_SAFETY -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_SKIP_DATABASE -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_SKIP_AUDIT -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_RECOVERY_SKIP_WRAPPER -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
