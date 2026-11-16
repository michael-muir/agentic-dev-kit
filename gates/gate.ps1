# Windows wrapper: finds Python 3.11+ and runs gate.py with the same arguments.
$ErrorActionPreference = 'Stop'
$gate = Join-Path $PSScriptRoot 'gate.py'
$candidates = @(@('python'), @('py', '-3'), @('python3'))
foreach ($c in $candidates) {
    $exe = Get-Command $c[0] -ErrorAction SilentlyContinue
    if (-not $exe) { continue }
    $pre = @(); if ($c.Count -gt 1) { $pre = $c[1..($c.Count - 1)] }
    & $exe.Source @pre -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) {
        & $exe.Source @pre $gate @args
        exit $LASTEXITCODE
    }
}
Write-Error 'agentic-dev-kit: Python 3.11+ not found on PATH.'
exit 2
