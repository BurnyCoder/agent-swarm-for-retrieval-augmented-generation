# Resume the registered study at a phase boundary and publish only private milestones.
param(
    [ValidateSet('dev','freeze','test','diagnostics')][string]$StartAt = 'dev',
    [int]$DevWorkers = 5,
    [int]$TestWorkers = 8,
    [int]$ControlWorkers = 5,
    [int]$WaitForDevPid = 0,
    [switch]$QuietConsole,
    [string]$ArcticVenv = '',
    [string]$DataRoot = 'D:\AI\luna-folderrag'
)
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $project
$linuxData = (wsl -d Ubuntu --cd $DataRoot --exec /bin/pwd).Trim()
if ($LASTEXITCODE -ne 0) { throw "Cannot open the experiment data directory" }
$environment = @("FOLDERRAG_HOME=$linuxData","OPENBLAS_NUM_THREADS=1","OMP_NUM_THREADS=2","PYTHONPATH=src")
if ($ArcticVenv) { $environment += "FOLDERRAG_ARCTIC_VENV=$ArcticVenv" }

function Invoke-StudyCommand([string[]]$Arguments) {
    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $log = Join-Path $DataRoot ("console-" + $Arguments[0] + "-$stamp.log")
    Write-Host (Get-Date -Format o) $Arguments 'Log' $log
    # Each model event is also written by the gateway to its unit-specific JSONL.
    if ($QuietConsole) {
        wsl -d Ubuntu --cd $project --exec env @environment sh scripts/linux-run folderrag @Arguments *> $log
    } else {
        wsl -d Ubuntu --cd $project --exec env @environment sh scripts/linux-run folderrag @Arguments 2>&1 | Tee-Object -FilePath $log
    }
    if ($LASTEXITCODE -ne 0) { throw "Research command failed. See $log" }
}

function Publish-Milestone([string]$Message) {
    Invoke-StudyCommand -Arguments @('report')
    git add -- README.md reports results site/data.json protocol
    if ($LASTEXITCODE -ne 0) { throw "Cannot stage the research artifacts" }
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 1) {
        git commit -m $Message
        if ($LASTEXITCODE -ne 0) { throw "Milestone commit failed" }
    }
    git push origin HEAD:main
    if ($LASTEXITCODE -ne 0) { throw "Private GitHub milestone failed" }
    Invoke-StudyCommand -Arguments @('archive')
    & (Join-Path $PSScriptRoot 'release.ps1') -TranscriptArchives (Join-Path $DataRoot 'archives')
}

$remote = (gh repo view --json visibility --jq '.visibility').Trim()
if ($LASTEXITCODE -ne 0 -or $remote -ne 'PRIVATE') { throw "The research remote must be private" }
if ($WaitForDevPid -gt 0) {
    do {
        $running = wsl -d Ubuntu --exec ps -p "$WaitForDevPid" -o args=
        if ("$running" -notmatch 'folderrag\.cli run dev') { break }
        Start-Sleep -Seconds 45
    } while ($true)
}
if ($StartAt -eq 'dev') {
    Invoke-StudyCommand -Arguments @('historical')
    Invoke-StudyCommand -Arguments @('run','dev','--workers',"$DevWorkers")
}
if ($StartAt -in @('dev','freeze')) {
    Invoke-StudyCommand -Arguments @('freeze')
    Publish-Milestone -Message 'Freeze swarm size and affordable paired test blocks'
}
# The exact freeze used by the test must be present on the published branch.
git fetch --quiet origin main
if ($LASTEXITCODE -ne 0) { throw "Cannot verify the private freeze" }
$localFreeze = (git hash-object protocol/freeze.json)
$remoteFreeze = (git rev-parse origin/main:protocol/freeze.json)
if ($LASTEXITCODE -ne 0 -or $localFreeze -ne $remoteFreeze) { throw "The published freeze differs from the local selection" }
if ($StartAt -ne 'diagnostics') {
    Invoke-StudyCommand -Arguments @('run','test','--workers',"$TestWorkers")
    Publish-Milestone -Message 'Archive paired held-out Luna results and primary comparisons'
}
Invoke-StudyCommand -Arguments @('run','diagnostics','--workers',"$ControlWorkers")
Invoke-StudyCommand -Arguments @('counterfactual')
Invoke-StudyCommand -Arguments @('diagnostics-audit')
Publish-Milestone -Message 'Publish fixed controls, repeat runs, evidence audits and dated paper'
