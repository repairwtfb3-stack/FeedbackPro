param(
    [string]$ReleaseDir = "release",
    [string]$ExpectedSourceCommit = $env:FEEDBACKPRO_SOURCE_COMMIT
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$ReleaseRoot = Join-Path $Root $ReleaseDir
$ManifestPath = Join-Path $ReleaseRoot "release-manifest.json"
if (-not (Test-Path $ManifestPath)) { throw "release-manifest.json not found" }
$Manifest = Get-Content $ManifestPath -Raw | ConvertFrom-Json
$Folder = Join-Path $ReleaseRoot $Manifest.artifact_folder
$Zip = Join-Path $ReleaseRoot $Manifest.artifact_zip
$Sha = Join-Path $ReleaseRoot $Manifest.sha256_file
foreach ($Path in @($Folder, $Zip, $Sha)) {
    if (-not (Test-Path $Path)) { throw "Release artifact missing: $Path" }
}
if (-not (Test-Path (Join-Path $Folder "FeedbackPro.exe"))) { throw "FeedbackPro.exe missing" }
if (-not [string]::IsNullOrWhiteSpace($ExpectedSourceCommit)) {
    if ($Manifest.source_commit -ne $ExpectedSourceCommit) {
        throw "Manifest source_commit mismatch: expected $ExpectedSourceCommit, got $($Manifest.source_commit)"
    }
}
$Actual = (Get-FileHash -Path $Zip -Algorithm SHA256).Hash.ToLowerInvariant()
if ($Actual -ne $Manifest.sha256) { throw "SHA-256 mismatch" }
$ShaText = (Get-Content $Sha -Raw).Trim()
if (-not $ShaText.StartsWith($Actual)) { throw "Checksum file mismatch" }
foreach ($Screen in 1..10) {
    $Pattern = "S{0:D2}*.qml" -f $Screen
    if (-not (Get-ChildItem -Path $Folder -Recurse -File -Filter $Pattern | Select-Object -First 1)) {
        throw "Packaged screen is missing: S$('{0:D2}' -f $Screen)"
    }
}
Write-Host "A4-R2 PACKAGE_SMOKE=PASS"
Write-Host "A4-R2 SOURCE_COMMIT=$($Manifest.source_commit)"
Write-Host "A4-R2 ARTIFACT=$($Manifest.artifact_zip)"
Write-Host "A4-R2 SHA256=$Actual"
