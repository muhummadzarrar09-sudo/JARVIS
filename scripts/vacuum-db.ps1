Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_vacuum_db.py"
$code = @'
import json
from app.services.database_service import database_service
print(json.dumps(database_service.vacuum(), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Database vacuum failed with exit code $LASTEXITCODE"
    }
} finally {
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
