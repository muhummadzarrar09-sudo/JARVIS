param(
    [string]$PythonCmd = "python",
    [string]$PreferredPythonVersion = "3.11",
    [switch]$SkipModelDownload,
    [switch]$SkipOptionalInstalls,
    [switch]$NoAutoRepairVenv,
    [string]$FastModelRepo = "bartowski/Qwen2.5-3B-Instruct-GGUF",
    [string]$FastModelFile = "Qwen2.5-3B-Instruct-Q4_K_M.gguf",
    [string]$MainModelRepo = "bartowski/Qwen2.5-7B-Instruct-GGUF",
    [string]$MainModelFile = "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
)

$ErrorActionPreference = "Stop"
$AutoRepairVenv = -not $NoAutoRepairVenv

function Write-Step($msg) {
    Write-Host "`n=== $msg ===" -ForegroundColor Cyan
}

function Ensure-Command($cmdName) {
    if (-not (Get-Command $cmdName -ErrorAction SilentlyContinue)) {
        throw "Required command not found: $cmdName"
    }
}

function Invoke-NativeChecked([string]$Label, [string]$FilePath, [string[]]$Arguments) {
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

function Invoke-NativeBestEffort([string]$Label, [string]$FilePath, [string[]]$Arguments) {
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "$Label failed with exit code $LASTEXITCODE"
        return $false
    }
    return $true
}

function Get-PythonVersionInfo([string]$FilePath, [string[]]$Arguments = @(), [string]$Label = $FilePath) {
    try {
        $output = (& $FilePath @Arguments "--version" 2>&1 | Out-String).Trim()
        $exitCode = $LASTEXITCODE
        if ($exitCode -ne 0 -or [string]::IsNullOrWhiteSpace($output)) {
            return [pscustomobject]@{
                Success = $false
                Label = $Label
                FilePath = $FilePath
                Arguments = $Arguments
                Output = $output
                Major = $null
                Minor = $null
                Patch = $null
                VersionString = $null
            }
        }

        if ($output -match "Python\s+(\d+)\.(\d+)\.(\d+)") {
            return [pscustomobject]@{
                Success = $true
                Label = $Label
                FilePath = $FilePath
                Arguments = $Arguments
                Output = $output
                Major = [int]$Matches[1]
                Minor = [int]$Matches[2]
                Patch = [int]$Matches[3]
                VersionString = "$($Matches[1]).$($Matches[2]).$($Matches[3])"
            }
        }

        if ($output -match "Python\s+(\d+)\.(\d+)") {
            return [pscustomobject]@{
                Success = $true
                Label = $Label
                FilePath = $FilePath
                Arguments = $Arguments
                Output = $output
                Major = [int]$Matches[1]
                Minor = [int]$Matches[2]
                Patch = 0
                VersionString = "$($Matches[1]).$($Matches[2]).0"
            }
        }

        return [pscustomobject]@{
            Success = $false
            Label = $Label
            FilePath = $FilePath
            Arguments = $Arguments
            Output = $output
            Major = $null
            Minor = $null
            Patch = $null
            VersionString = $null
        }
    } catch {
        return [pscustomobject]@{
            Success = $false
            Label = $Label
            FilePath = $FilePath
            Arguments = $Arguments
            Output = $_.Exception.Message
            Major = $null
            Minor = $null
            Patch = $null
            VersionString = $null
        }
    }
}

function Test-SupportedPythonVersion([int]$Major, [int]$Minor) {
    return ($Major -eq 3 -and $Minor -ge 10 -and $Minor -le 12)
}

function Get-PythonPreferenceScore([int]$Major, [int]$Minor, [string]$PreferredVersion) {
    if (-not (Test-SupportedPythonVersion $Major $Minor)) {
        return 0
    }
    $shortVersion = "$Major.$Minor"
    if ($shortVersion -eq $PreferredVersion) { return 100 }
    if ($shortVersion -eq "3.11") { return 95 }
    if ($shortVersion -eq "3.12") { return 85 }
    if ($shortVersion -eq "3.10") { return 80 }
    return 10
}

function New-PythonCandidate([string]$FilePath, [string[]]$Arguments, [string]$Label) {
    $info = Get-PythonVersionInfo -FilePath $FilePath -Arguments $Arguments -Label $Label
    if (-not $info.Success) {
        return $null
    }
    return [pscustomobject]@{
        Label = $Label
        FilePath = $FilePath
        Arguments = $Arguments
        Major = $info.Major
        Minor = $info.Minor
        Patch = $info.Patch
        VersionString = $info.VersionString
        Supported = (Test-SupportedPythonVersion $info.Major $info.Minor)
        Score = (Get-PythonPreferenceScore $info.Major $info.Minor $PreferredPythonVersion)
    }
}

function Get-SystemPythonCandidates([string]$PreferredVersion, [string]$FallbackPythonCmd) {
    $candidateList = New-Object System.Collections.ArrayList
    $labelsSeen = @{}
    $preferredOrder = @($PreferredVersion, "3.11", "3.12", "3.10") | Select-Object -Unique

    if (Get-Command "py" -ErrorAction SilentlyContinue) {
        foreach ($ver in $preferredOrder) {
            $candidate = New-PythonCandidate -FilePath "py" -Arguments @("-$ver") -Label "py -$ver"
            if ($null -ne $candidate -and -not $labelsSeen.ContainsKey($candidate.Label)) {
                $labelsSeen[$candidate.Label] = $true
                [void]$candidateList.Add($candidate)
            }
        }

        $candidate = New-PythonCandidate -FilePath "py" -Arguments @() -Label "py"
        if ($null -ne $candidate -and -not $labelsSeen.ContainsKey($candidate.Label)) {
            $labelsSeen[$candidate.Label] = $true
            [void]$candidateList.Add($candidate)
        }
    }

    foreach ($cmd in @("python3.11", "python3.12", "python3.10", $FallbackPythonCmd) | Select-Object -Unique) {
        if ($cmd -and (Get-Command $cmd -ErrorAction SilentlyContinue)) {
            $candidate = New-PythonCandidate -FilePath $cmd -Arguments @() -Label $cmd
            if ($null -ne $candidate -and -not $labelsSeen.ContainsKey($candidate.Label)) {
                $labelsSeen[$candidate.Label] = $true
                [void]$candidateList.Add($candidate)
            }
        }
    }

    return $candidateList | Sort-Object -Property @{Expression = "Score"; Descending = $true}, @{Expression = "Label"; Descending = $false}
}

function Backup-Venv([string]$VenvPath) {
    if (-not (Test-Path $VenvPath)) {
        return $null
    }
    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $backupName = ".venv.backup-$timestamp"
    Move-Item -Path $VenvPath -Destination $backupName
    return $backupName
}

function Ensure-ModelEnvDefaults([string]$EnvPath) {
    if (-not (Test-Path $EnvPath)) {
        return
    }
    $content = Get-Content $EnvPath -Raw
    if ($content -notmatch "DEFAULT_MODEL_PROVIDER") {
        Add-Content -Path $EnvPath -Value "`r`nDEFAULT_MODEL_PROVIDER=mock`r`n"
    }
}

Write-Step "JARVIS LOCAL BOOTSTRAP STARTING"
Write-Host "Project root: $PSScriptRoot" -ForegroundColor Yellow
Set-Location $PSScriptRoot

Ensure-Command $PythonCmd

Write-Step "Inspecting available Python interpreters"
$systemCandidates = Get-SystemPythonCandidates -PreferredVersion $PreferredPythonVersion -FallbackPythonCmd $PythonCmd
if (-not $systemCandidates -or $systemCandidates.Count -eq 0) {
    throw "No usable Python interpreter was found. Install Python 3.11 and rerun bootstrap."
}

foreach ($candidate in $systemCandidates) {
    $supportTag = if ($candidate.Supported) { "supported" } else { "unsupported for llama-cpp" }
    Write-Host ("- {0} -> Python {1} [{2}]" -f $candidate.Label, $candidate.VersionString, $supportTag)
}

$bestSystemPython = $systemCandidates | Select-Object -First 1
$preferredAvailable = $bestSystemPython.Supported
if ($preferredAvailable) {
    Write-Host ("Selected bootstrap interpreter: {0} (Python {1})" -f $bestSystemPython.Label, $bestSystemPython.VersionString) -ForegroundColor Green
} else {
    Write-Warning "No supported Python 3.10-3.12 interpreter was found. Browser mode may still work, but llama-cpp-python will likely fail. Install Python 3.11."
}

$venvDir = Join-Path $PSScriptRoot ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"
$venvNeedsCreate = $true

if (Test-Path $venvPython) {
    Write-Step "Inspecting existing virtual environment"
    $venvInfo = Get-PythonVersionInfo -FilePath $venvPython -Arguments @() -Label ".venv python"
    if ($venvInfo.Success) {
        Write-Host ("Existing .venv uses Python {0}" -f $venvInfo.VersionString)
        $venvSupported = Test-SupportedPythonVersion $venvInfo.Major $venvInfo.Minor
        if ($venvSupported) {
            Write-Host ".venv is already using a supported Python version. Reusing it." -ForegroundColor Green
            $venvNeedsCreate = $false
        } elseif ($AutoRepairVenv -and $preferredAvailable) {
            $backupName = Backup-Venv -VenvPath $venvDir
            Write-Warning ("Existing .venv was incompatible for llama-cpp-python and has been backed up to {0}" -f $backupName)
            $venvNeedsCreate = $true
        } else {
            Write-Warning "Existing .venv uses an unsupported Python version and auto-repair is unavailable/disabled. Proceeding, but llama-cpp-python will likely fail."
            $venvNeedsCreate = $false
        }
    } else {
        if ($AutoRepairVenv -and $preferredAvailable) {
            $backupName = Backup-Venv -VenvPath $venvDir
            Write-Warning ("Existing .venv could not be inspected and has been backed up to {0}" -f $backupName)
            $venvNeedsCreate = $true
        } else {
            Write-Warning "Could not inspect existing .venv. Proceeding with it as-is."
            $venvNeedsCreate = $false
        }
    }
} elseif (Test-Path $venvDir) {
    if ($AutoRepairVenv -and $preferredAvailable) {
        $backupName = Backup-Venv -VenvPath $venvDir
        Write-Warning ("Existing .venv folder looked invalid and has been backed up to {0}" -f $backupName)
    }
    $venvNeedsCreate = $true
}

if ($venvNeedsCreate) {
    if (-not $preferredAvailable) {
        Write-Warning "Creating .venv with the best available interpreter, but it is not ideal for local llama runtime."
    }
    Write-Step "Creating virtual environment"
    $createArgs = @()
    if ($bestSystemPython.Arguments) {
        $createArgs += $bestSystemPython.Arguments
    }
    $createArgs += @("-m", "venv", ".venv")
    Invoke-NativeChecked "Creating virtual environment" $bestSystemPython.FilePath $createArgs
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"

if (-not (Test-Path $venvPython)) {
    throw "Virtual environment python not found at $venvPython"
}
if (-not (Test-Path $venvPip)) {
    throw "Virtual environment pip not found at $venvPip"
}

Write-Step "Checking final virtual environment Python"
$finalVenvInfo = Get-PythonVersionInfo -FilePath $venvPython -Arguments @() -Label ".venv python"
if (-not $finalVenvInfo.Success) {
    throw "Unable to inspect virtual environment Python."
}
Write-Host ("Final .venv interpreter: Python {0}" -f $finalVenvInfo.VersionString)
$finalVenvSupported = Test-SupportedPythonVersion $finalVenvInfo.Major $finalVenvInfo.Minor
if (-not $finalVenvSupported) {
    Write-Warning "This .venv is not on a recommended Python version for llama-cpp-python. Install Python 3.11 and rerun bootstrap if you want local GGUF inference."
}

Write-Step "Upgrading pip"
Invoke-NativeChecked "Upgrading pip" $venvPython @("-m", "pip", "install", "--upgrade", "pip", "wheel", "setuptools")

Write-Step "Installing base requirements"
Invoke-NativeChecked "Installing base requirements" $venvPip @("install", "-r", "requirements.txt")

if (-not $SkipOptionalInstalls) {
    Write-Step "Installing llama-cpp-python (best effort)"
    if ($finalVenvSupported) {
        $llamaInstalled = Invoke-NativeBestEffort "llama-cpp-python install" $venvPip @("install", "--prefer-binary", "-r", "requirements-llm.txt")
        if ($llamaInstalled) {
            $llamaImportOk = Invoke-NativeBestEffort "llama_cpp import check" $venvPython @("-c", "import llama_cpp; print(getattr(llama_cpp, '__version__', 'ok'))")
            if ($llamaImportOk) {
                Write-Host "llama-cpp-python installed and import-checked successfully" -ForegroundColor Green
            } else {
                Write-Warning "llama-cpp-python installed but import check failed. Recreate the venv with Python 3.11 or inspect build/runtime details."
            }
        } else {
            Write-Warning "llama-cpp-python install failed. If Python is already 3.11, you may need Visual Studio C++ Build Tools or a compatible wheel."
        }
    } else {
        Write-Warning "Skipping llama-cpp-python install because the current .venv Python version is not recommended. Install Python 3.11 and rerun bootstrap."
    }

    Write-Step "Installing Playwright browser tooling (best effort)"
    $playwrightInstalled = Invoke-NativeBestEffort "Playwright package install" $venvPip @("install", "-r", "requirements-browser.txt")
    if ($playwrightInstalled) {
        $playwrightImportOk = Invoke-NativeBestEffort "Playwright import check" $venvPython @("-c", "import playwright; print('playwright-ok')")
        if ($playwrightImportOk) {
            Write-Host "Playwright Python package installed successfully" -ForegroundColor Green
        }
        $chromiumInstalled = Invoke-NativeBestEffort "Playwright Chromium install" $venvPython @("-m", "playwright", "install", "chromium")
        if ($chromiumInstalled) {
            Write-Host "Playwright Chromium installed successfully" -ForegroundColor Green
        } else {
            Write-Warning "Playwright Chromium install failed. You can rerun: python -m playwright install chromium"
        }
    } else {
        Write-Warning "Playwright package install failed. Browser mode will be unavailable until fixed."
    }
} else {
    Write-Warning "Skipping optional installs by request. llama-cpp-python and Playwright were not installed."
}

Write-Step "Creating local folders"
$folders = @(
    "data",
    "data\models",
    "data\memory",
    "data\logs",
    "data\uploads",
    "data\browser"
)

foreach ($folder in $folders) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder | Out-Null
        Write-Host "Created: $folder" -ForegroundColor Green
    }
}

Write-Step "Creating .env if missing"
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example" -ForegroundColor Green
} else {
    Write-Host ".env already exists, leaving it untouched" -ForegroundColor DarkYellow
}
Ensure-ModelEnvDefaults -EnvPath ".env"

if (-not $SkipModelDownload) {
    Write-Step "Attempting GGUF model downloads via huggingface_hub"

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
    try:
        path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(local_dir),
            local_dir_use_symlinks=False,
        )
        print(f"Saved to: {path}")
    except Exception as e:
        print(f"WARNING: download failed for {repo_id}/{filename}: {e}")
"@

    $tempDownloadScript = Join-Path $PSScriptRoot ".tmp_hf_download.py"
    Set-Content -Path $tempDownloadScript -Value $downloadScript -Encoding UTF8
    try {
        $downloadOk = Invoke-NativeBestEffort "GGUF model download" $venvPython @($tempDownloadScript)
        if (-not $downloadOk) {
            Write-Warning "Model download script failed. You can rerun bootstrap later or run .\scripts\download-models.ps1"
        }
    } finally {
        if (Test-Path $tempDownloadScript) {
            Remove-Item $tempDownloadScript -Force -ErrorAction SilentlyContinue
        }
    }
} else {
    Write-Host "Skipping model download by request" -ForegroundColor DarkYellow
}

Write-Step "Bootstrap complete"
Write-Host "Next steps:" -ForegroundColor Green
Write-Host "1. .\.venv\Scripts\Activate.ps1"
Write-Host "2. .\scripts\start-cli.ps1"
Write-Host "3. .\scripts\start-api.ps1"
Write-Host "4. Keep DEFAULT_MODEL_PROVIDER=mock until CLI/API tests pass"
Write-Host "5. Switch to DEFAULT_MODEL_PROVIDER=llama_cpp only after GGUF files exist and llama_cpp import succeeded"
