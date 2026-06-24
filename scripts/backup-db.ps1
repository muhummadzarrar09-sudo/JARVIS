param(
    [string]$Label
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_backup_db.py"
$code = @'
import json
import os
from app.services.database_service import database_service
print(json.dumps(database_service.backup(label=os.environ.get("JARVIS_DB_BACKUP_LABEL")), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    if ($Label) { $env:JARVIS_DB_BACKUP_LABEL = $Label }
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Database backup failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_DB_BACKUP_LABEL -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
