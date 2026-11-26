<#
.SYNOPSIS
  Dual-flagship adversarial debate runner (Windows / PowerShell 5.1+).

.DESCRIPTION
  Implements the debate protocol's Round 1 / Round 2 dispatch for hosts that cannot
  spawn isolated read-only flagship subagents natively (CLI-ephemeral pattern):

    Round 1: two isolated read-only debaters, dispatched in parallel, blind opening
    Round 2: two FRESH isolated sessions, each fed [Step 0 baseline + own R1 + opponent R1]

  Read-only is enforced where the CLI allows it (codex: -s read-only). Claude Code has no
  hard read-only, so the runner records `git status` before and after and warns on any change.

.NOTES
  Requires: codex CLI (with `exec -s/--ephemeral`) and/or claude CLI (`-p`), on PATH.
  Output: out-*/r1-*.md, r2-*.md, *.prompt.md, *.log.txt, RUN-META.txt
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory = $true)][string]$TopicFile,
  [string]$OutDir,
  [ValidateSet('cross-vendor', 'dual-codex', 'dual-claude')][string]$Mode = 'cross-vendor',
  [ValidateSet(1, 2)][int]$Rounds = 2,
  [string]$WorkDir = (Get-Location).Path,
  [int]$TimeoutSec = 900,
  # Optional extra system prompt for the debaters (team coding/review conventions, persona, etc.)
  [string]$AppendSystemPrompt,
  # Model overrides; leave empty to use each CLI's own configured default.
  [string]$CodexModel,
  [string]$ClaudeModel
)

$ErrorActionPreference = 'Stop'
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
[Console]::OutputEncoding = $utf8NoBom
chcp 65001 > $null

function Write-Utf8 {
  param([string]$Path, [string]$Text)
  [System.IO.File]::WriteAllText($Path, $Text, $utf8NoBom)
}

if (-not (Test-Path $TopicFile)) { throw "Topic file not found: $TopicFile" }
$topic = [System.IO.File]::ReadAllText((Resolve-Path $TopicFile).Path, [System.Text.Encoding]::UTF8)
if (-not $OutDir) { $OutDir = Join-Path (Get-Location) ('debate-' + (Get-Date -Format 'yyyyMMdd-HHmmss')) }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$OutDir = (Resolve-Path $OutDir).Path

$extra = ''
if ($AppendSystemPrompt) {
  if (-not (Test-Path $AppendSystemPrompt)) { throw "AppendSystemPrompt file not found: $AppendSystemPrompt" }
  $extra = [System.IO.File]::ReadAllText((Resolve-Path $AppendSystemPrompt).Path, [System.Text.Encoding]::UTF8)
}

$r1Rules = @"
[READ-ONLY] This round is read-only analysis: do not create, modify or delete any file, do not run
git writes, do not install anything.
[LANGUAGE] Answer in the language of the Step 0 baseline; keep the section structure as given.
[ANTI-SYCOPHANCY] No polite compromise, no "everyone is partly right" mush. Never abandon a stance
without citing new evidence, a counter-example, or a causal argument.
[OUTPUT] <= 1200 characters, exactly four sections:
1. Stance status: CONVERGED / SHIFTED / MAINTAINING_DISSENT (+ calibration of the Step 0 baseline)
2. Core position and reasoning (name your load-bearing premises)
3. Three lethal questions aimed at the opponent's weakest load-bearing assumption or hidden cost
4. Evidence you actually verified (files read / commands run); write "unverified" if none
"@

$r2Rules = @"
[READ-ONLY] Same as Round 1: read-only.
[ANTI-SYCOPHANCY] No mush consensus. If you shift, cite the specific new evidence that moved you.
[STEELMAN] Before rebutting, restate the opponent's strongest premise in 1-2 sentences. No strawmen.
[ATOMIC REBUTTALS] Format each: Claim -> Flaw type (fact/constraint violated | hidden assumption
failed | boundary or scale collapse | incentive or second-order backlash | logical leap) -> counter
or alternative path.
[OUTPUT] <= 1000 characters, exactly four sections:
1. New stance status and what you concede
2. Point-by-point answers to the opponent's three questions (concede blind spots explicitly)
3. Double Crux: 1-2 unproven assumptions that carry the decision, plus their falsifiers
4. Your converged recommendation
"@

function New-DebaterPrompt {
  param([string]$Baseline, [string]$Rules, [string]$Side, [string]$OwnR1 = '', [string]$OppR1 = '')
  $sb = New-Object System.Text.StringBuilder
  if ($extra) {
    [void]$sb.AppendLine($extra)
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('--- end of baseline, task brief follows ---')
    [void]$sb.AppendLine()
  }
  [void]$sb.AppendLine("# Adversarial debate - task brief ($Side)")
  [void]$sb.AppendLine()
  [void]$sb.AppendLine('## Topic and Step 0 verified baseline')
  [void]$sb.AppendLine($Baseline)
  [void]$sb.AppendLine()
  if ($OwnR1 -or $OppR1) {
    [void]$sb.AppendLine('## Your own Round 1 output - verbatim')
    [void]$sb.AppendLine($OwnR1)
    [void]$sb.AppendLine()
    [void]$sb.AppendLine('## Opponent Round 1 output - verbatim, not summarized')
    [void]$sb.AppendLine($OppR1)
    [void]$sb.AppendLine()
  }
  [void]$sb.AppendLine('## Rules for this round')
  [void]$sb.AppendLine($Rules)
  $sb.ToString()
}

function Invoke-Debater {
  param([string]$Who, [string]$Engine, [string]$PromptText, [string]$Tag)
  $promptFile = Join-Path $OutDir ('{0}-{1}.prompt.md' -f $Tag, $Who)
  $outFile = Join-Path $OutDir ('{0}-{1}.out.md' -f $Tag, $Who)
  $logFile = Join-Path $OutDir ('{0}-{1}.log.txt' -f $Tag, $Who)
  Write-Utf8 -Path $promptFile -Text $PromptText

  if ($Engine -eq 'codex') {
    $modelArg = if ($CodexModel) { ' -m "{0}"' -f $CodexModel } else { '' }
    $cli = 'codex exec --skip-git-repo-check -s read-only --ephemeral{0} -C "{1}" -o "{2}" < "{3}" > "{4}" 2>&1' -f $modelArg, $WorkDir, $outFile, $promptFile, $logFile
  }
  else {
    $modelArg = if ($ClaudeModel) { ' --model "{0}"' -f $ClaudeModel } else { '' }
    $sysArg = if ($AppendSystemPrompt) { ' --append-system-prompt-file "{0}"' -f (Resolve-Path $AppendSystemPrompt).Path } else { '' }
    $cli = 'claude -p --output-format text{0}{1} < "{2}" > "{3}" 2>&1' -f $modelArg, $sysArg, $promptFile, $outFile
  }
  Write-Host ('  [{0}/{1}] dispatch: {2}' -f $Tag, $Who, $Engine) -ForegroundColor DarkGray
  $p = Start-Process -FilePath 'cmd.exe' -ArgumentList '/c', $cli -WindowStyle Hidden -PassThru
  New-Object psobject -Property @{ Who = $Who; Engine = $Engine; Proc = $p; Out = $outFile; Log = $logFile }
}

function Wait-Batch {
  param($Batch)
  foreach ($b in $Batch) {
    if (-not $b.Proc.WaitForExit($TimeoutSec * 1000)) {
      try { $b.Proc.Kill() } catch {}
      Write-Warning ('{0} timed out after {1}s, killed' -f $b.Who, $TimeoutSec)
    }
  }
  foreach ($b in $Batch) {
    $size = if (Test-Path $b.Out) { (Get-Item $b.Out).Length } else { 0 }
    Write-Host ('  [{0}] {1} done exit={2} output={3} bytes' -f $b.Who, $b.Engine, $b.Proc.ExitCode, $size) -ForegroundColor DarkGray
  }
}

function Read-Result {
  param([string]$Path)
  if (Test-Path $Path) { [System.IO.File]::ReadAllText($Path, [System.Text.Encoding]::UTF8) } else { '' }
}

# --- read-only guard: snapshot repo state ---
$isGit = Test-Path (Join-Path $WorkDir '.git')
$gitBefore = ''
if ($isGit) { $gitBefore = ((git -C $WorkDir status --porcelain) -join "`n") }

$pairs = @{
  'cross-vendor' = @(@{ Who = 'A'; Engine = 'codex' }, @{ Who = 'B'; Engine = 'claude' })
  'dual-codex'   = @(@{ Who = 'A'; Engine = 'codex' }, @{ Who = 'B'; Engine = 'codex' })
  'dual-claude'  = @(@{ Who = 'A'; Engine = 'claude' }, @{ Who = 'B'; Engine = 'claude' })
}
$pair = $pairs[$Mode]
$verdictNote = if ($Mode -eq 'cross-vendor') { '' } else { '模式：同旗舰双隔离 / mode: dual isolated sessions of a single flagship' }

Write-Host ('=== Round 1: parallel blind opening (mode={0}) ===' -f $Mode) -ForegroundColor Cyan
if ($verdictNote) { Write-Host ('    verdict line 1 must state: {0}' -f $verdictNote) -ForegroundColor Yellow }
$batch = @()
foreach ($d in $pair) {
  $batch += Invoke-Debater -Who $d.Who -Engine $d.Engine -Tag 'r1' -PromptText (New-DebaterPrompt -Baseline $topic -Rules $r1Rules -Side ('Debater ' + $d.Who))
}
Wait-Batch -Batch $batch

$r1A = Read-Result (Join-Path $OutDir 'r1-A.out.md')
$r1B = Read-Result (Join-Path $OutDir 'r1-B.out.md')

if ($Rounds -eq 2) {
  Write-Host '=== Round 2: stateless replay (own R1 + opponent R1 verbatim) ===' -ForegroundColor Cyan
  $batch = @()
  foreach ($d in $pair) {
    $own = if ($d.Who -eq 'A') { $r1A } else { $r1B }
    $opp = if ($d.Who -eq 'A') { $r1B } else { $r1A }
    $batch += Invoke-Debater -Who $d.Who -Engine $d.Engine -Tag 'r2' -PromptText (New-DebaterPrompt -Baseline $topic -Rules $r2Rules -Side ('Debater ' + $d.Who) -OwnR1 $own -OppR1 $opp)
  }
  Wait-Batch -Batch $batch
}

if ($isGit) {
  $gitAfter = ((git -C $WorkDir status --porcelain) -join "`n")
  if ($gitBefore -ne $gitAfter) {
    Write-Warning 'Workspace changed during the debate (Claude Code has no hard read-only). Review:'
    Write-Host $gitAfter
    Write-Utf8 -Path (Join-Path $OutDir 'WORKSPACE-DIFF-WARNING.txt') -Text $gitAfter
  }
  else { Write-Host '[read-only guard] git status unchanged before/after' -ForegroundColor Green }
}

$pairText = (($pair | ForEach-Object { $_.Who + ':' + $_.Engine }) -join ',')
$meta = @(
  'mode=' + $Mode,
  'rounds=' + $Rounds,
  'workdir=' + $WorkDir,
  'pair=' + $pairText,
  'codexModel=' + $CodexModel,
  'claudeModel=' + $ClaudeModel,
  'finished=' + (Get-Date -Format o)
)
Write-Utf8 -Path (Join-Path $OutDir 'RUN-META.txt') -Text ($meta -join "`r`n")

Write-Host ''
Write-Host ('=== Output: {0} ===' -f $OutDir) -ForegroundColor Cyan
Get-ChildItem $OutDir | Select-Object Name, Length | Format-Table -AutoSize
if ($r1A.Trim().Length -lt 80 -or $r1B.Trim().Length -lt 80) {
  Write-Warning 'A debater produced under 80 chars - check its *.log.txt for errors'
}
Write-Host 'Next: the host reads R1/R2 verbatim, fact-checks the new claims itself, then writes the five-part verdict.' -ForegroundColor Yellow
