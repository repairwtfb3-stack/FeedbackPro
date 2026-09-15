param(
    [Parameter(Mandatory=$true)][string]$ZipPath,
    [string]$OutPath = ""
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $ZipPath)) { throw "ZIP not found: $ZipPath" }
$Hash = (Get-FileHash -Path $ZipPath -Algorithm SHA256).Hash.ToLowerInvariant()
if (-not $OutPath) { $OutPath = [System.IO.Path]::ChangeExtension($ZipPath, ".sha256") }
"$Hash  $(Split-Path $ZipPath -Leaf)" | Set-Content -Path $OutPath -Encoding ascii
Write-Output $Hash
