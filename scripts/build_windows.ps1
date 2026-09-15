param(
    [string]$OutputDir = "release"
)

$ErrorActionPreference = "Stop"
$Root = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
& (Join-Path $Root "packaging\windows\build.ps1") -OutputDir $OutputDir
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
