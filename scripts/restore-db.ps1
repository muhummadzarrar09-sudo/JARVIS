param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath,
    [switch]$SkipSafetyBackup
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_restore_db.py"
$code = @'
import json
import os
from app.services.database_service import database_service
print(json.dumps(database_service.restore(
    backup_path=os.environ["JARVIS_DB_RESTORE_PATH"],
    create_backup_first=(os.environ.get("JARVIS_DB_SKIP_SAFETY_BACKUP") != "1"),
), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    $env:JARVIS_DB_RESTORE_PATH = $BackupPath
    if ($SkipSafetyBackup) { $env:JARVIS_DB_SKIP_SAFETY_BACKUP = "1" }
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Database restore failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_DB_RESTORE_PATH -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_DB_SKIP_SAFETY_BACKUP -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
