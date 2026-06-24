param(
    [switch]$AttemptBrowserStarts,
    [switch]$AttemptBrowserOpens,
    [string[]]$Browser,
    [string]$BrowserUrl = "https://example.com",
    [string]$FocusTitle,
    [int]$FocusMatchIndex = 0,
    [string]$Output
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$argsList = @("scripts/runtime_validation.py")
if ($AttemptBrowserStarts) { $argsList += "--attempt-browser-starts" }
if ($AttemptBrowserOpens) { $argsList += "--attempt-browser-opens" }
if ($BrowserUrl) { $argsList += @("--browser-url", $BrowserUrl) }
if ($Browser) {
    foreach ($name in $Browser) {
        if ($name) { $argsList += @("--browser", $name) }
    }
}
if ($FocusTitle) { $argsList += @("--focus-title", $FocusTitle) }
if ($FocusMatchIndex -ne 0) { $argsList += @("--focus-match-index", $FocusMatchIndex) }
if ($Output) { $argsList += @("--output", $Output) }

python @argsList
