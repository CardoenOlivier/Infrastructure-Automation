# Check if a "bootfs" partition exists
$bootPartition = Get-Volume | Where-Object { $_.FileSystemLabel -eq "bootfs" }
if (-not $bootPartition) {
    Write-Output "Geen bootfs partitie gevonden."
    exit
}

# Path to 'firstrun.sh' on the boot partition
$bootPath = Join-Path $bootPartition.DriveLetter "firstrun.sh"

# Check if 'firstrun.sh' exists on boot partition
if (-not (Test-Path $bootPath)) {
    Write-Output "firstrun.sh niet gevonden op de boot partitie."
    exit
}

# Check if 'firstrun.sh' is a Linux (Unix) file
$firstRunContent = Get-Content -Raw -Path $bootPath
if ($firstRunContent -notmatch "`n") {
    Write-Output "firstrun.sh is geen Linux (Unix) bestand."
    exit
}

# Prevent polluting 'firstrun.sh' with redundant data on repeated runs
$apipaPath = Join-Path $bootPartition.DriveLetter "apipa.txt"
$staticIPPath = Join-Path $bootPartition.DriveLetter "Static_IP.nmconnection"

# Read the last two lines of 'apipa.txt' if it exists
if (Test-Path $apipaPath) {
    $lastTwoLines = Get-Content $apipaPath | Select-Object -Last 2
} else {
    Write-Output "apipa.txt niet gevonden."
    exit
}

# Read contents of 'Static_IP.nmconnection' if it exists
if (Test-Path $staticIPPath) {
    $staticIPContent = Get-Content -Raw -Path $staticIPPath
} else {
    Write-Output "Static_IP.nmconnection niet gevonden."
    exit
}

# Read 'firstrun.sh' into an array for line-by-line manipulation
$firstRunLines = Get-Content -Path $bootPath
$rmLineIndex = $firstRunLines.IndexOf("rm -rf /boot/firstrun.sh")

# Ensure no redundant modifications are made
if ($firstRunLines[$rmLineIndex - 1] -match $lastTwoLines[0]) {
    Write-Output "Script al bijgewerkt, geen aanpassingen nodig."
    exit
}

# Modify 'firstrun.sh' by inserting the content above the 'rm -rf' line
$modifiedContent = $firstRunLines[0..($rmLineIndex - 1)] + $staticIPContent + $lastTwoLines + $firstRunLines[$rmLineIndex..($firstRunLines.Length - 1)]
Set-Content -Path $bootPath -Value $modifiedContent

Write-Output "firstrun.sh is succesvol bijgewerkt."
