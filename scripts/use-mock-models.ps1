Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$tempScript = Join-Path (Get-Location) ".tmp_use_mock_models.py"
$code = @'
import json
from app.services.model_service import model_service
print(json.dumps(model_service.configure_mock_mode(), indent=2))
'@
Set-Content -Path $tempScript -Value $code -Encoding UTF8
try {
    python $tempScript
    if ($LASTEXITCODE -ne 0) {
        throw "Mock model configuration failed with exit code $LASTEXITCODE"
    }
} finally {
    if (Test-Path $tempScript) {
        Remove-Item $tempScript -Force -ErrorAction SilentlyContinue
    }
}
