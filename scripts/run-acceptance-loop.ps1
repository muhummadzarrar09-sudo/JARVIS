param(
    [int]$Iterations = 3,
    [int]$DelaySeconds = 3,
    [switch]$Deep
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

for ($i = 1; $i -le $Iterations; $i++) {
    Write-Host "=== Acceptance iteration $i / $Iterations ===" -ForegroundColor Cyan
    $argsList = @("scripts/acceptance_sweep.py")
    if ($Deep) { $argsList += "--deep" }
    python @argsList
    if ($i -lt $Iterations) {
        Start-Sleep -Seconds $DelaySeconds
    }
}
