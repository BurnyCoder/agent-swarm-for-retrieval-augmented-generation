# Publish only known, generated research artifacts to the owner's private repositories.
param([string]$TranscriptArchives)
$ErrorActionPreference = 'Stop'
$dataset = 'BurnyCoder/luna-folder-swarm-results'
$space = 'BurnyCoder/luna-folder-swarm-explorer'
foreach ($item in @(@($dataset,'datasets'),@($space,'spaces'))) {
    $info = hf $item[1] info $item[0] --format json | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0 -or $info.private -ne $true) { throw "Private repository verification failed for $($item[0])" }
}
foreach ($dir in @('reports','protocol','results')) {
    hf upload $dataset $dir $dir --type dataset --commit-message "Update private research $dir"
    if ($LASTEXITCODE -ne 0) { throw "Upload failed for $dir" }
}
$revision = git rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw "Cannot identify the source revision" }
New-Item -ItemType Directory -Force .runtime | Out-Null
git archive --format=zip --output=.runtime/source.zip HEAD
if ($LASTEXITCODE -ne 0) { throw "Source archive failed" }
hf upload $dataset .runtime/source.zip source.zip --type dataset --commit-message "Archive tracked source $revision"
if ($LASTEXITCODE -ne 0) { throw "Source publication failed" }
hf upload $dataset protocol/hub-card.md README.md --type dataset --commit-message "Update research card"
if ($LASTEXITCODE -ne 0) { throw "Card upload failed" }
hf upload $space site . --type space --commit-message "Update private results explorer"
if ($LASTEXITCODE -ne 0) { throw "Explorer upload failed" }
if ($TranscriptArchives) {
    foreach ($phase in @('dev','test','diagnostics','retry')) {
        $archive = Join-Path $TranscriptArchives ($phase + '.tar.gz')
        if (Test-Path -LiteralPath $archive -PathType Leaf) {
            hf upload $dataset $archive ("traces/" + $phase + '.tar.gz') --type dataset --commit-message "Archive private $phase transcripts"
            if ($LASTEXITCODE -ne 0) { throw "Transcript upload failed for $phase" }
        }
    }
}
