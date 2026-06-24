param(
    [string]$Label,
    [int]$KeepArchives = 10
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_rotate_audit.py"
$code = @'
import json
import os
from app.services.audit import audit_service
label = os.environ.get("JARVIS_AUDIT_ROTATE_LABEL")
keep = int(os.environ.get("JARVIS_AUDIT_KEEP", "10"))
print(json.dumps(audit_service.rotate(label=label, keep_archives=keep), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    if ($Label) { $env:JARVIS_AUDIT_ROTATE_LABEL = $Label }
    $env:JARVIS_AUDIT_KEEP = "$KeepArchives"
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Audit rotation failed with exit code $LASTEXITCODE"
    }
} finally {
    Remove-Item Env:JARVIS_AUDIT_ROTATE_LABEL -ErrorAction SilentlyContinue
    Remove-Item Env:JARVIS_AUDIT_KEEP -ErrorAction SilentlyContinue
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
