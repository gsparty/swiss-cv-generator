param(
    [string]$PdfDir = ".",
    [string]$GsExe  # optional explicit path to Ghostscript executable
)

# Try to auto-discover GS if not provided
if (-not $GsExe) {
    $g = Get-Command gswin64c -ErrorAction SilentlyContinue
    if (-not $g) { $g = Get-Command gswin32c -ErrorAction SilentlyContinue }
    if ($g) { $GsExe = $g.Path } else {
        # look under common install dirs
        $candidates = @("C:\Program Files\gs","C:\Program Files (x86)\gs","C:\Program Files\Ghostscript","C:\Program Files (x86)\Ghostscript")
        foreach ($base in $candidates) {
            if (Test-Path $base) {
                $exe = Get-ChildItem -Path $base -Recurse -Filter "gswin*.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
                if ($exe) { $GsExe = $exe.FullName; break }
            }
        }
    }
}

if (-not $GsExe -or -not (Test-Path $GsExe)) {
    Write-Warning "Ghostscript not found. To compress PDFs, install Ghostscript or pass its path as -GsExe."
    Write-Output "Official Ghostscript downloads: https://www.ghostscript.com/download/gsdnld.html"
    exit 0
}

$dir = Resolve-Path $PdfDir
Get-ChildItem -Path $dir -Filter *.pdf | ForEach-Object {
    $in = $_.FullName
    $out = Join-Path $_.DirectoryName ($_.BaseName + "_compressed.pdf")
    Write-Output "Compressing $($_.Name) -> $([IO.Path]::GetFileName($out))"
    & $GsExe -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dNOPAUSE -dQUIET -dBATCH -sOutputFile="$out" "$in"
    if (Test-Path $out) {
        $orig = Get-Item $in
        $cmp  = Get-Item $out
        Write-Output ("OK: {0} -> {1} (orig {2:N0} bytes, new {3:N0} bytes)" -f $_.Name, $cmp.Name, $orig.Length, $cmp.Length)
    } else {
        Write-Error "Failed to compress $in"
    }
}
