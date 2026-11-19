# Publish only known, generated research artifacts to the owner's private repositories.
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
hf upload $dataset README.md README.md --type dataset --commit-message "Update research card"
if ($LASTEXITCODE -ne 0) { throw "Card upload failed" }
hf upload $space site . --type space --commit-message "Update private results explorer"
if ($LASTEXITCODE -ne 0) { throw "Explorer upload failed" }
