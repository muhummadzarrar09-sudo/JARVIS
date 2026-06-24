param(
    [switch]$BrowserOnly,
    [switch]$PrintDiagnostics,
    [switch]$OpenRecoveryOnFailure,
    [string]$Host = "127.0.0.1",
    [int]$Port = 8000,
    [int]$RetryCount = 8,
    [double]$RetryDelay = 1.0
)

Set-Location (Join-Path $PSScriptRoot "..")
. .\.venv\Scripts\Activate.ps1

$argsList = @("-m", "desktop_shell.app", "--host", $Host, "--port", "$Port", "--retry-count", "$RetryCount", "--retry-delay", "$RetryDelay")
if ($BrowserOnly) { $argsList += "--browser-only" }
if ($PrintDiagnostics) { $argsList += "--print-diagnostics" }
if ($OpenRecoveryOnFailure) { $argsList += "--open-recovery-on-failure" }

python @argsList
