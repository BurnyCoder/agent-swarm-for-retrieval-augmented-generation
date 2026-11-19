# Run the actual Windows entry point on fixed public fixtures and save only study evidence.
param([string]$DataRoot = 'D:\AI\luna-folderrag', [switch]$UseSavedOutputs)
$ErrorActionPreference = 'Stop'
$project = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location -LiteralPath $project
$cases = @(
    @{Name='windows-dense-smoke'; Agents=4; Extra=@(); Expected='41'; Question='How many stops are on the schedule followed by the Brook service? Give the integer.'},
    @{Name='windows-missing'; Agents=2; Extra=@('--lexical-only'); Expected='Insufficient information'; Question='In which four-digit year did the Brook service open? If the files give no date, answer Insufficient information.'}
)
$dest = Join-Path $DataRoot 'smoke'
New-Item -ItemType Directory -Path $dest -Force | Out-Null
foreach ($case in $cases) {
    $name = $case.Name
    $output = Join-Path $DataRoot ($name + '.json')
    $log = Join-Path $DataRoot ($name + '.log')
    if (-not $UseSavedOutputs) {
        $extra = $case.Extra
        uv run folderrag ask --folder tests/fixtures/cross_file --agents $case.Agents --json @extra $case.Question > $output 2> $log
        if ($LASTEXITCODE -ne 0) { throw "Smoke run failed. See $log" }
    }
    $response = Get-Content -Raw -LiteralPath $output | ConvertFrom-Json
    $verified = @($response.citations | Where-Object valid)
    if ($response.answer -ne $case.Expected -or $response.workers_completed -ne ($case.Agents-1)) { throw "Unexpected answer or investigator count in $output" }
    if ($case.Expected -eq '41' -and @($verified.path | Select-Object -Unique).Count -ne 2) { throw "Missing cross-file proof" }
    $summary = [ordered]@{
        unit=$name; utc=(Get-Item -LiteralPath $output).LastWriteTimeUtc.ToString('o')
        question=$case.Question; expected=$case.Expected; answer=$response.answer; agents=$case.Agents
        investigators_completed=$response.workers_completed; investigators_contributing=$response.workers_contributing
        citations=@($verified | Select-Object path,line,offset,quote,valid)
        seconds=$response.seconds; requests=$response.requests; cost_upper_usd=$response.cost_upper_usd
    }
    $summary | ConvertTo-Json -Depth 6 | Set-Content -Encoding utf8NoBOM -LiteralPath (Join-Path $dest ($name+'.json'))
}
