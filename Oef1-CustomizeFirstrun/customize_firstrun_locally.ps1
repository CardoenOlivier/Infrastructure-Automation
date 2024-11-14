# Set paths to the files in the current directory
$firstrunPath = Join-Path -Path (Get-Location) -ChildPath "firstrun.sh"
$apipaPath = Join-Path -Path (Get-Location) -ChildPath "apipa.txt"
$staticIPPath = Join-Path -Path (Get-Location) -ChildPath "Static_IP.nmconnection"

# Check if 'firstrun.sh' exists
if (-not (Test-Path $firstrunPath)) {
    Write-Output "firstrun.sh niet gevonden in de huidige map."
    exit
}

# Check if 'firstrun.sh' is a Linux (Unix) file
$firstRunContent = Get-Content -Raw -Path $firstrunPath
if ($firstRunContent -notmatch "`n") {
    Write-Output "firstrun.sh is geen Linux (Unix) bestand."
    exit
}

# Read the last two lines of 'apipa.txt' if it exists
if (Test-Path $apipaPath) {
    $lastTwoLines = Get-Content $apipaPath | Select-Object -Last 2
}
else {
    Write-Output "apipa.txt niet gevonden in de huidige map."
    exit
}

# Read contents of 'Static_IP.nmconnection' if it exists
if (Test-Path $staticIPPath) {
    $staticIPContent = Get-Content -Raw -Path $staticIPPath
}
else {
    Write-Output "Static_IP.nmconnection niet gevonden in de huidige map."
    exit
}

# Read 'firstrun.sh' into an array for line-by-line manipulation
$firstRunLines = Get-Content -Path $firstrunPath
$rmLineIndex = $firstRunLines.IndexOf("rm -rf /boot/firstrun.sh")

# Ensure no redundant modifications are made
if ($firstRunLines[$rmLineIndex - 1] -match $lastTwoLines[0]) {
    Write-Output "Script al bijgewerkt, geen aanpassingen nodig."
    exit
}

# Modify 'firstrun.sh' by inserting the content above the 'rm -rf' line
$modifiedContent = $firstRunLines[0..($rmLineIndex - 1)] + $staticIPContent + $lastTwoLines + $firstRunLines[$rmLineIndex..($firstRunLines.Length - 1)]
Set-Content -Path $firstrunPath -Value $modifiedContent

Write-Output "firstrun.sh is succesvol bijgewerkt."
