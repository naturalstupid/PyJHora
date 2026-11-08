param(
  [Parameter(Mandatory=$true)][string]$Version,   # e.g. 0.9.8.5
  [string]$Message = ""                           # optional description
)
Set-Location $PSScriptRoot
$f = "src/jhora/ui/nicegui/_web_version.txt"
Set-Content $f -Value $Version -NoNewline
git add -A
git commit -m "V$Version $Message"
git tag -a "V$Version" -m "V$Version $Message"
git log --oneline -1
git tag --list "V$Version"
Write-Host "Done locally. To publish later: git push; git push origin V$Version"