param(
    [string]$OutputDir = "release",
    [string]$SourceCommit = $env:FEEDBACKPRO_SOURCE_COMMIT
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $Root

$Version = (python -c "from feedbackpro.version import VERSION; print(VERSION)").Trim()
$ActualCommit = (git rev-parse HEAD).Trim()
if ([string]::IsNullOrWhiteSpace($SourceCommit)) { $SourceCommit = $ActualCommit }
if ($ActualCommit -ne $SourceCommit) {
    throw "Source provenance mismatch before build: expected $SourceCommit, got $ActualCommit"
}
$Commit = $SourceCommit
$BuildUtc = [DateTime]::UtcNow.ToString("o")

$BuildMeta = [ordered]@{
    version = $Version
    channel = "pilot-rc"
    commit = $Commit
    built_at = $BuildUtc
}
$BuildMeta | ConvertTo-Json -Compress | Set-Content -Path "src\feedbackpro\build_meta.json" -Encoding utf8NoBOM

foreach ($Path in @("build", "dist", $OutputDir)) {
    if (Test-Path $Path) { Remove-Item $Path -Recurse -Force }
}

python -m PyInstaller --noconfirm --clean "packaging\feedbackpro.spec"
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed with exit code $LASTEXITCODE" }

$DistFolder = Join-Path $Root "dist\FeedbackPro"
if (-not (Test-Path $DistFolder)) { throw "Expected PyInstaller folder not found: $DistFolder" }

$ReleaseRoot = Join-Path $Root $OutputDir
New-Item -ItemType Directory -Path $ReleaseRoot -Force | Out-Null
$FolderName = "FeedbackPro_${Version}_win64"
$ReleaseFolder = Join-Path $ReleaseRoot $FolderName
Move-Item -Path $DistFolder -Destination $ReleaseFolder

$Exe = Join-Path $ReleaseFolder "FeedbackPro.exe"
if (-not (Test-Path $Exe)) { throw "FeedbackPro.exe is missing from release folder" }

$RequiredQml = @(
    "Main.qml",
    "S01Dashboard.qml",
    "S02Reviews.qml",
    "S03ReviewCard.qml",
    "S04Import.qml",
    "S05Decisions.qml",
    "S06DecisionCard.qml",
    "S07Control.qml",
    "S08Analytics.qml",
    "S09Dictionaries.qml",
    "S10Settings.qml",
    "ErrorBanner.qml",
    "EmptyState.qml",
    "BusyState.qml"
)
foreach ($Name in $RequiredQml) {
    $Found = Get-ChildItem -Path $ReleaseFolder -Recurse -File -Filter $Name -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $Found) { throw "Packaged QML asset is missing: $Name" }
}

$ZipPath = Join-Path $ReleaseRoot "${FolderName}.zip"
Compress-Archive -Path $ReleaseFolder -DestinationPath $ZipPath -CompressionLevel Optimal
$ShaPath = Join-Path $ReleaseRoot "${FolderName}.sha256"
$Hash = (& (Join-Path $Root "scripts\hash_release.ps1") -ZipPath $ZipPath -OutPath $ShaPath).Trim()

$Manifest = [ordered]@{
    product = "FeedbackPro"
    version = $Version
    channel = "pilot-rc"
    platform = "windows-x64"
    source_commit = $Commit
    built_at_utc = $BuildUtc
    artifact_folder = $FolderName
    artifact_zip = (Split-Path $ZipPath -Leaf)
    sha256_file = (Split-Path $ShaPath -Leaf)
    sha256 = $Hash
    python = (python --version 2>&1).ToString().Trim()
    pyinstaller = (python -c "import PyInstaller; print(PyInstaller.__version__)").Trim()
    pyside6 = (python -c "import PySide6; print(PySide6.__version__)").Trim()
    schema_version = 3
    analysis_version = "a2-rules-1.0"
    custom_icon = $false
    icon_note = "RC uses the default PyInstaller icon until the FeedbackPro visual icon is explicitly approved."
}
$ManifestPath = Join-Path $ReleaseRoot "release-manifest.json"
$Manifest | ConvertTo-Json -Depth 4 | Set-Content -Path $ManifestPath -Encoding utf8NoBOM

Write-Host "RC_VERSION=$Version"
Write-Host "RC_COMMIT=$Commit"
Write-Host "RC_FOLDER=$FolderName"
Write-Host "RC_ZIP=$(Split-Path $ZipPath -Leaf)"
Write-Host "RC_SHA256=$Hash"
Write-Host "RC_MANIFEST=$(Split-Path $ManifestPath -Leaf)"
