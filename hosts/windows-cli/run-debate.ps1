<#
.SYNOPSIS
  Windows PowerShell 5.1+ entry point for the shared Python debate runner.

.DESCRIPTION
  Converts the Windows parameters to a temporary preset configuration and invokes
  skills/dual-flagship-debate/scripts/run_debate.py. The Python runner owns rounds,
  working directories, subprocesses, timeouts, logs, and result validation.

.NOTES
  Requires Python 3.10+ and the selected model CLIs on PATH. PythonExecutable may
  specify a Python executable or the Windows py launcher; otherwise python3,
  python, and py -3 are tried in that order. The engine exit code is preserved.
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$TopicFile,
  [string]$OutDir,
  [ValidateSet('cross-vendor', 'dual-codex', 'dual-claude')][string]$Mode = 'cross-vendor',
  [ValidateSet(1, 2)][int]$Rounds = 2,
  [string]$WorkDir = (Get-Location).Path,
  [ValidateRange(1, 2147483647)][int]$TimeoutSec = 900,
  [string]$AppendSystemPrompt,
  # Empty model/effort values leave the Python preset and CLI defaults intact.
  [string]$CodexModel,
  [string]$ClaudeModel,
  [string]$CodexEffort,
  [string]$ClaudeEffort,
  [ValidateRange(1, 2147483647)][Nullable[int]]$TotalTimeoutSec,
  [string]$PythonExecutable
)

$ErrorActionPreference = 'Stop'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom

function Resolve-Python {
  $candidates = if ($PythonExecutable) { @($PythonExecutable) } else { @('python3', 'python', 'py') }
  foreach ($candidate in $candidates) {
    $command = Get-Command -Name $candidate -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $command) { continue }
    $prefixArgs = @()
    if ([System.IO.Path]::GetFileNameWithoutExtension($command.Source) -eq 'py') {
      $prefixArgs = @('-3')
    }
    $savedPreference = $ErrorActionPreference
    try {
      $ErrorActionPreference = 'Continue'
      $global:LASTEXITCODE = $null
      $probe = @(& $command.Source @prefixArgs -c "import sys; print('.'.join(map(str, sys.version_info[:3])))" 2>$null)
      $version = $null
      if ($global:LASTEXITCODE -eq 0 -and [version]::TryParse(($probe -join '').Trim(), [ref]$version) -and $version -ge [version]'3.10') {
        return @{ Executable = $command.Source; PrefixArgs = $prefixArgs }
      }
    }
    catch {
      # A missing runtime or an unusable Windows application alias is skipped.
    }
    finally {
      $ErrorActionPreference = $savedPreference
    }
  }
  throw 'Python 3.10 or newer is required. Install Python or set -PythonExecutable to its executable.'
}

if (-not (Test-Path -LiteralPath $TopicFile -PathType Leaf)) { throw "Topic file not found: $TopicFile" }
if (-not (Test-Path -LiteralPath $WorkDir -PathType Container)) { throw "Working directory not found: $WorkDir" }
$topicPath = (Resolve-Path -LiteralPath $TopicFile).ProviderPath
$workdirPath = (Resolve-Path -LiteralPath $WorkDir).ProviderPath
$enginePath = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../skills/dual-flagship-debate/scripts/run_debate.py'))
if (-not (Test-Path -LiteralPath $enginePath -PathType Leaf)) { throw "Shared Python runner not found: $enginePath" }

$engineArgs = @($enginePath, '--topic', $topicPath, '--rounds', [string]$Rounds,
                '--workdir', $workdirPath, '--timeout', [string]$TimeoutSec)
if ($OutDir) {
  $outdirPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutDir)
  $engineArgs += @('--out-dir', $outdirPath)
}
if ($null -ne $TotalTimeoutSec) { $engineArgs += @('--total-timeout', [string]$TotalTimeoutSec) }
if ($AppendSystemPrompt) {
  if (-not (Test-Path -LiteralPath $AppendSystemPrompt -PathType Leaf)) { throw "AppendSystemPrompt file not found: $AppendSystemPrompt" }
  $engineArgs += @('--append-system-prompt', (Resolve-Path -LiteralPath $AppendSystemPrompt).ProviderPath)
}

$engines = switch ($Mode) {
  'dual-codex' { @('codex', 'codex') }
  'dual-claude' { @('claude', 'claude') }
  default { @('codex', 'claude') }
}
$debaters = [ordered]@{}
for ($i = 0; $i -lt 2; $i++) {
  $side = @('A', 'B')[$i]
  if ($engines[$i] -eq 'codex') {
    $spec = [ordered]@{ preset = 'codex-cli'; name = "Codex $side" }
    $model = $CodexModel
    $effort = $CodexEffort
  }
  else {
    $spec = [ordered]@{ preset = 'claude-code'; name = "Claude $side" }
    $model = $ClaudeModel
    $effort = $ClaudeEffort
  }
  if (-not [string]::IsNullOrWhiteSpace($model)) { $spec['model'] = $model }
  if (-not [string]::IsNullOrWhiteSpace($effort)) { $spec['effort'] = $effort }
  $debaters[$side] = $spec
}

$python = Resolve-Python
$configPath = Join-Path ([System.IO.Path]::GetTempPath()) ('dual-flagship-debate-' + [guid]::NewGuid().ToString('N') + '.json')
try {
  $config = [ordered]@{ debaters = $debaters } | ConvertTo-Json -Depth 5
  [System.IO.File]::WriteAllText($configPath, $config, $utf8NoBom)
  $pythonArgs = @($python.PrefixArgs) + $engineArgs + @('--config', $configPath)
  # Keep native stderr separate and allow the engine's nonzero code to propagate.
  $savedPreference = $ErrorActionPreference
  try {
    $ErrorActionPreference = 'Continue'
    $PSNativeCommandUseErrorActionPreference = $false
    $global:LASTEXITCODE = $null
    & $python.Executable @pythonArgs
    if ($null -eq $global:LASTEXITCODE) { throw 'Failed to start the shared Python runner.' }
    $engineExitCode = $global:LASTEXITCODE
  }
  finally {
    $ErrorActionPreference = $savedPreference
  }
}
finally {
  if (Test-Path -LiteralPath $configPath) { Remove-Item -LiteralPath $configPath -Force }
}
exit $engineExitCode
