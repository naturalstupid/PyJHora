param(
    [string]$Version = "",   # e.g. 0.9.8.5  (required)
    [string]$Message = ""    # release comment (REQUIRED - the release is rejected without it)
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

# ---- Release rules. Everything is checked BEFORE any file is edited, committed or tagged. ----
$MinMessageLength = 10
# Comments that say nothing. Add more words here if people find new ways round the rule.
$BannedMessages = @('new version', 'new release', 'bug fixes', 'minor changes', 'misc changes', 'work in progress',
                    'no comment', 'none', 'n/a', 'test', 'testing', 'update', 'updated', 'fix', 'fixes', 'wip')

function Stop-Release([string]$Reason) {
    Write-Host ""
    Write-Host "RELEASE REJECTED: $Reason" -ForegroundColor Red
    Write-Host "Nothing was changed: no file edited, no commit, no tag." -ForegroundColor Red
    exit 1
}

$Version = $Version.Trim()
$Message = ($Message -replace '\s+', ' ').Trim()      # tabs and line breaks become single spaces: one line per release

if ($Version -notmatch '^\d+(\.\d+){1,3}$') {
    Stop-Release "Version '$Version' is not valid. Use numbers separated by dots, for example 0.9.9.2"
}
if ($Message.Length -eq 0) {
    Stop-Release "A release comment is required. Say what changed in this version, for example: get places from IP address"
}
if ($Message.Length -lt $MinMessageLength) {
    Stop-Release "The release comment is too short ($($Message.Length) characters; at least $MinMessageLength are needed). Say what changed in this version."
}
if (($Message -replace '[^\p{L}]', '').Length -lt 5) {
    Stop-Release "The release comment must contain words, not just numbers or symbols."
}
if ($BannedMessages -contains $Message.TrimEnd('.', '!').ToLower()) {
    Stop-Release "'$Message' does not say what changed. Describe the change."
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Stop-Release "git was not found. Install it or add it to PATH."
}
if (git tag -l "web-V$Version") {
    Stop-Release "Version $Version already exists (tag web-V$Version). Use a new version number."
}

# ---- Checks passed: do the release ----
$f = "src/jhora/ui/nicegui/_web_version.txt"
Set-Content $f -Value $Version -NoNewline

# Release history shown on the About page: this release becomes the first line
$h = "src/jhora/ui/nicegui/_release_history.txt"
$entry = "V$Version - $Message"
$old = @()
if (Test-Path $h) { $old = @(Get-Content $h -Encoding UTF8 | Where-Object { $_ -ne "V$Version" -and $_ -notlike "V$Version - *" }) }
Set-Content $h -Value (@($entry) + $old) -Encoding UTF8

# The comment goes to git through a file (-F), so quotes and special characters in it cannot break the command line
$msgFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($msgFile, "web-V$Version $Message`n", (New-Object System.Text.UTF8Encoding($false)))
try {
    git add -A
    if ($LASTEXITCODE -ne 0) { throw "git add failed" }
    git commit -F $msgFile
    if ($LASTEXITCODE -ne 0) { throw "git commit failed" }
    git tag -a "web-V$Version" -F $msgFile
    if ($LASTEXITCODE -ne 0) { throw "git tag failed" }
}
finally {
    Remove-Item $msgFile -ErrorAction SilentlyContinue
}
git log --oneline -1
git tag --list "web-V$Version"
Write-Host "Done locally. To publish later: git push; git push origin web-V$Version"
