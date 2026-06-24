param(
    [Parameter(Mandatory=$true)]
    [string]$ArchivePath
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_delete_audit_archive.py"
$code = @'
import json
import os
from app.services.audit import audit_service
print(json.dumps(audit_service.delete_archive(os.environ["JARVIS_AUDIT_ARCHIVE_PATH"]), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    $env:JARVIS_AUDIT_ARCHIVE_PATH = $ArchivePath
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Audit archive delete failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_AUDIT_ARCHIVE_PATH -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
