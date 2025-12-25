# Copyright (C) 2025 originalFactor
# 
# This file is part of autouploader.
# 
# autouploader is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# autouploader is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with autouploader.  If not, see <https://www.gnu.org/licenses/>.

param(
    [Parameter(Mandatory = $true)]
    [string]$File,

    [Parameter(Mandatory = $true)]
    [string]$ChunkSize,

    [Parameter(Mandatory = $true)]
    [string]$Output
)

function Parse-Size($sizeStr) {
    if ($sizeStr -match '^\d+[Kk]$') {
        return [int]($sizeStr.TrimEnd('K','k')) * 1KB
    }
    elseif ($sizeStr -match '^\d+[Mm]$') {
        return [int]($sizeStr.TrimEnd('M','m')) * 1MB
    }
    elseif ($sizeStr -match '^\d+[Gg]$') {
        return [int]($sizeStr.TrimEnd('G','g')) * 1GB
    }
    else {
        return [int]$sizeStr
    }
}

$chunkBytes = Parse-Size $ChunkSize
$buffer = New-Object byte[] $chunkBytes

# 确保输出目录存在
[System.IO.Directory]::CreateDirectory($Output) | Out-Null

$fs = [System.IO.File]::OpenRead($File)
$index = 1

while ($true) {
    $read = $fs.Read($buffer, 0, $chunkBytes)
    if ($read -le 0) { break }

    $chunkName = "{0:D2}.bin" -f $index
    $outFile = [System.IO.Path]::Combine($Output, $chunkName)

    $outStream = [System.IO.File]::OpenWrite($outFile)
    $outStream.Write($buffer, 0, $read)
    $outStream.Close()

    Write-Host "Created $outFile ($read bytes)"
    $index++
}

$fs.Close()
