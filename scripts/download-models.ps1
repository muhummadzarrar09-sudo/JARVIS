param(
    [string]$FastModelRepo = "bartowski/Qwen2.5-3B-Instruct-GGUF",
    [string]$FastModelFile = "Qwen2.5-3B-Instruct-Q4_K_M.gguf",
    [string]$MainModelRepo = "bartowski/Qwen2.5-7B-Instruct-GGUF",
    [string]$MainModelFile = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment python not found at $venvPython"
}

$downloadScript = @"
from huggingface_hub import hf_hub_download
from pathlib import Path

pairs = [
    ("$FastModelRepo", "$FastModelFile"),
    ("$MainModelRepo", "$MainModelFile"),
]

local_dir = Path("data/models")
local_dir.mkdir(parents=True, exist_ok=True)

for repo_id, filename in pairs:
    print(f"Downloading {repo_id} :: {filename}")
    path = hf_hub_download(
        repo_id=repo_id,
        filename=filename,
        local_dir=str(local_dir),
        local_dir_use_symlinks=False,
    )
    print(f"Saved to: {path}")
"@

$tempDownloadScript = Join-Path (Get-Location) ".tmp_hf_download.py"
Set-Content -Path $tempDownloadScript -Value $downloadScript -Encoding UTF8
try {
    & $venvPython $tempDownloadScript
    if ($LASTEXITCODE -ne 0) {
        throw "Model download failed with exit code $LASTEXITCODE"
    }
} finally {
    if (Test-Path $tempDownloadScript) {
        Remove-Item $tempDownloadScript -Force -ErrorAction SilentlyContinue
    }
}
