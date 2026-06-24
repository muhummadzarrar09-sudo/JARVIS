param(
    [Parameter(Mandatory=$true)]
    [string]$BackupPath
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_delete_db_backup.py"
$code = @'
import json
import os
from app.services.database_service import database_service
print(json.dumps(database_service.delete_backup(os.environ["JARVIS_DB_BACKUP_PATH"]), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    $env:JARVIS_DB_BACKUP_PATH = $BackupPath
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Database backup delete failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_DB_BACKUP_PATH -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
