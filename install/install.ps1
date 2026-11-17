<#
.SYNOPSIS
  Install or update agentic-dev-kit in a project.
.EXAMPLE
  .\install.ps1 -Target D:\GitHub\my-project -Stacks python,typescript -Tools claude,copilot
.EXAMPLE
  .\install.ps1 -Target D:\GitHub\my-app -Stacks dotnet,typescript -Standards dotnet-microsoft,typescript-strict
.EXAMPLE
  .\install.ps1 -Target D:\GitHub\my-project -Update
#>
param(
    [string]$Target = (Get-Location).Path,
    [string[]]$Stacks,
    [string[]]$Domains,
    [string[]]$Standards,
    [string[]]$Tools,
    [string[]]$Owners,
    [switch]$Update,
    [switch]$NoHooks,
    [switch]$NoCi,
    [switch]$CiReview,
    [switch]$Devcontainer
)
$ErrorActionPreference = 'Stop'
$installer = Join-Path $PSScriptRoot 'install.py'

$py = $null; $pre = @()
foreach ($c in @(@('python'), @('py', '-3'), @('python3'))) {
    $exe = Get-Command $c[0] -ErrorAction SilentlyContinue
    if (-not $exe) { continue }
    $p = @(); if ($c.Count -gt 1) { $p = $c[1..($c.Count - 1)] }
    & $exe.Source @p -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { $py = $exe.Source; $pre = $p; break }
}
if (-not $py) { Write-Error 'Python 3.11+ is required (https://www.python.org/downloads/).'; exit 2 }

$argv = @('--target', $Target)
if ($Stacks)  { $argv += @('--stacks',  ($Stacks -join ',')) }
if ($Domains) { $argv += @('--domains', ($Domains -join ',')) }
if ($Standards) { $argv += @('--standards', ($Standards -join ',')) }
if ($Tools)   { $argv += @('--tools',   ($Tools -join ',')) }
if ($Owners)  { $argv += @('--owners',  ($Owners -join ',')) }
if ($Update)  { $argv += '--update' }
if ($NoHooks) { $argv += '--no-hooks' }
if ($NoCi)    { $argv += '--no-ci' }
if ($CiReview) { $argv += '--ci-review' }
if ($Devcontainer) { $argv += '--devcontainer' }

& $py @pre $installer @argv
exit $LASTEXITCODE
