param(
    [switch]$Deep
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$argsList = @("scripts/acceptance_sweep.py")
if ($Deep) { $argsList += "--deep" }
python @argsList
