# Publish committed research artifacts and the named benchmark archives.
param([string]$TranscriptArchives)
$ErrorActionPreference = 'Stop'
$dataset = 'BurnyCoder/luna-folder-swarm-results'
$space = 'BurnyCoder/luna-folder-swarm-explorer'
foreach ($item in @(@($dataset,'datasets'),@($space,'spaces'))) {
    $info = hf $item[1] info $item[0] --format json | ConvertFrom-Json
    if ($LASTEXITCODE -ne 0 -or $info.id -ne $item[0] -or $info.private -ne $false) {
        throw "Public repository verification failed for $($item[0])"
    }
}
$project = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$revision = git -C $project rev-parse HEAD
if ($LASTEXITCODE -ne 0) { throw "Cannot identify the source revision" }
$runtime = (New-Item -ItemType Directory -Force (Join-Path $project '.runtime')).FullName
$source = Join-Path $runtime 'source.zip'
git -C $project archive --format=zip "--output=$source" $revision
if ($LASTEXITCODE -ne 0) { throw "Source archive failed" }
# Extract a fresh snapshot so local files placed beside the reports or site cannot be uploaded.
$stage = Join-Path $runtime ('hub-release-' + [guid]::NewGuid().ToString('N'))
try {
    [System.IO.Compression.ZipFile]::ExtractToDirectory($source, $stage)
    foreach ($dir in @('reports','protocol','results')) {
        hf upload $dataset (Join-Path $stage $dir) $dir --type dataset --commit-message "Update research $dir"
        if ($LASTEXITCODE -ne 0) { throw "Upload failed for $dir" }
    }
    hf upload $dataset $source source.zip --type dataset --commit-message "Archive tracked source $revision"
    if ($LASTEXITCODE -ne 0) { throw "Source publication failed" }
    $card = Join-Path $stage 'results/hub-card.md'
    if (-not (Test-Path -LiteralPath $card)) { $card = Join-Path $stage 'protocol/hub-card.md' }
    hf upload $dataset $card README.md --type dataset --commit-message "Update research card"
    if ($LASTEXITCODE -ne 0) { throw "Card upload failed" }
    hf upload $space (Join-Path $stage 'site') . --type space --commit-message "Update results explorer"
    if ($LASTEXITCODE -ne 0) { throw "Explorer upload failed" }
} finally {
    if (Test-Path -LiteralPath $stage) {
        $resolved = (Resolve-Path -LiteralPath $stage).Path
        if ([IO.Path]::GetDirectoryName($resolved) -ne $runtime) { throw "Unexpected release staging path" }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
}
if ($TranscriptArchives) {
    foreach ($phase in @('dev','test','diagnostics','retry')) {
        $archive = Join-Path $TranscriptArchives ($phase + '.tar.gz')
        if (Test-Path -LiteralPath $archive -PathType Leaf) {
            hf upload $dataset $archive ("traces/" + $phase + '.tar.gz') --type dataset --commit-message "Archive $phase benchmark transcripts"
            if ($LASTEXITCODE -ne 0) { throw "Transcript upload failed for $phase" }
        }
    }
}
