param(
    [string]$OutputDir = "data"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function TryDownload($url, $outPath) {
    try {
        Write-Output "Attempting download: $url -> $outPath"
        Invoke-WebRequest -Uri $url -OutFile $outPath -UseBasicParsing -ErrorAction Stop
        Write-Output "Saved: $outPath"
        return $true
    } catch {
        Write-Warning "Download failed for $url : $($_.Exception.Message)"
        return $false
    }
}

# Candidate placeholders - replace with direct CSV links if you have them.
$demCandidates = @(
    "https://www.bfs.admin.ch/bfsstatic/dam/assets/32208093/master",
    "https://www.bfs.admin.ch/dam/jcr:32208093-0cda-4f8b-b7f2-0e8d2f3b1a6e/canton_demographics.csv"
)
$demOut = Join-Path $OutputDir "bfs_demographics_by_canton.csv"
$downloaded = $false
foreach ($u in $demCandidates) {
    if (TryDownload $u $demOut) { $downloaded = $true; break }
}
if (-not $downloaded) {
    $url = Read-Host "Demographics CSV URL (paste direct CSV link or press Enter to skip)"
    if ($url) { TryDownload $url $demOut | Out-Null } else { Write-Warning "Skipping demographics." }
}

$lnCandidates = @(
    "https://www.bfs.admin.ch/bfsstatic/dam/assets/36062356/master",
    "https://www.bfs.admin.ch/dam/jcr:36062356-.../lastnames_by_canton.csv"
)
$lnOut = Join-Path $OutputDir "bfs_lastnames_by_canton.csv"
$downloaded = $false
foreach ($u in $lnCandidates) {
    if (TryDownload $u $lnOut) { $downloaded = $true; break }
}
if (-not $downloaded) {
    $url = Read-Host "Lastnames CSV URL (paste direct CSV link or press Enter to skip)"
    if ($url) { TryDownload $url $lnOut | Out-Null } else { Write-Warning "Skipping lastnames." }
}

$fnCandidates = @(
    "https://www.bfs.admin.ch/bfsstatic/dam/assets/32208746/master",
    "https://www.bfs.admin.ch/dam/jcr:32208746-.../firstnames_by_year.csv"
)
$fnOut = Join-Path $OutputDir "bfs_firstnames.csv"
$downloaded = $false
foreach ($u in $fnCandidates) {
    if (TryDownload $u $fnOut) { $downloaded = $true; break }
}
if (-not $downloaded) {
    $url = Read-Host "Firstnames CSV URL (paste direct CSV link or press Enter to skip)"
    if ($url) { TryDownload $url $fnOut | Out-Null } else { Write-Warning "Skipping first names." }
}

Write-Output "Fetch helper finished. Check $OutputDir for downloaded files."
