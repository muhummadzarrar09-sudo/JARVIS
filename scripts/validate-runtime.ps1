param(
    [switch]$AttemptBrowserStarts,
    [string]$FocusTitle,
    [string]$Output
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$argsList = @("scripts/runtime_validation.py")
if ($AttemptBrowserStarts) { $argsList += "--attempt-browser-starts" }
if ($FocusTitle) { $argsList += @("--focus-title", $FocusTitle) }
if ($Output) { $argsList += @("--output", $Output) }

python @argsList
