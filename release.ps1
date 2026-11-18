param(
    [Parameter(Mandatory = $true)][ValidateSet("core", "web", "both")][string]$ReleaseType,
    [string]$Version = "",          # core/web release version. Empty = ask (shows the current version)
    [string]$WebVersion = "",       # 'both' only: web version. Empty = ask (shows the current version)
    [Parameter(Mandatory = $true)][string]$Message
)
# Release types:
#   core : PyJHora core only (changes outside the NiceGUI folder)      -> tag V5.0.3
#   web  : NiceGUI web only (changes inside the NiceGUI folder only)   -> tag web-V1.0.2
#   both : one change in core AND web (e.g. vedic_calendar.py + calendar_tab.py)
#          -> ONE commit, TWO tags (V5.0.3 and web-V1.0.2); both versions and both release histories
#             are updated; the web history entry says "(with PyJHora V5.0.3)".
# When a version is not given, the script shows the current one and suggests the next (Enter accepts it).
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
# ======================================================================
# CONFIGURATION - change these if folders or naming ever change
# ======================================================================
$JHoraRoot     = "src/jhora"                  # PyJHora core package folder
$NiceGuiRoot   = "src/jhora/ui/nicegui"       # web service folder (rename here if it moves)
$TagPrefix     = "V"                          # core tag:  V5.0.3
$WebTagPrefix  = "web-"                       # web tag:   web-V0.9.9.4  (prefix + $TagPrefix + version)
# Web release files (inside $NiceGuiRoot)
$WebVersionFile = "$NiceGuiRoot/_web_version.txt"
$WebHistoryFile = "$NiceGuiRoot/_release_history.txt"
# Core release files. History file: set to "" to disable.
$CoreHistoryFile = "$JHoraRoot/_release_history.txt"
# Files searched (in order) for the core version assignment, e.g.  version = "5.0.2"
$CoreVersionCandidates = @(
    "src/jhora/_package_info.py",
    "pyproject.toml",
    "src/jhora/_version.py",
    "src/jhora/version.py",
    "src/jhora/__init__.py",
    "src/jhora/const.py",
    "setup.py"
)
$MinMessageLength = 10
$BannedMessages = @('new version', 'new release', 'bug fixes', 'minor changes', 'misc changes', 'work in progress',
                    'no comment', 'none', 'n/a', 'test', 'testing', 'update', 'updated', 'fix', 'fixes', 'wip')
# Matches: version = "x" / __version__ = "x" / VERSION = "x"  (optional ": str", optional leading V in value)
$VersionAssignmentPattern = @'
(?m)^(\s*(?:__version__|VERSION|version)\s*(?::\s*str\s*)?=\s*["'])(V?)[^"']+(["'])
'@
# Same, but captures the version value (used to show the current version)
$VersionValuePattern = @'
(?m)^\s*(?:__version__|VERSION|version)\s*(?::\s*str\s*)?=\s*["']V?([^"']+)["']
'@
# ======================================================================
# HELPERS
# ======================================================================
function Stop-Release([string]$Reason) {
    Write-Host ""
    Write-Host "RELEASE REJECTED: $Reason" -ForegroundColor Red
    Write-Host "Nothing was changed: no file edited, no commit, no tag." -ForegroundColor Red
    exit 1
}
# Runs git quietly; returns Code + Output (stdout lines)
function Invoke-GitCapture([string[]]$GitArgs) {
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { $out = & git @GitArgs 2>$null; $code = $LASTEXITCODE }
    finally { $ErrorActionPreference = $old }
    return [pscustomobject]@{ Code = $code; Output = @($out) }
}
# Runs git with visible output; throws on failure
function Invoke-Git([string[]]$GitArgs, [string]$FailureMessage) {
    $old = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try { & git @GitArgs; $code = $LASTEXITCODE }
    finally { $ErrorActionPreference = $old }
    if ($code -ne 0) { throw $FailureMessage }
}
function ConvertTo-RepoPath([string]$Path) {
    $p = $Path.Trim().Replace("\", "/")
    while ($p.StartsWith("./")) { $p = $p.Substring(2) }
    return $p.TrimEnd("/")
}
function Test-PathInside([string]$Path, [string]$Parent) {
    $p = ConvertTo-RepoPath $Path
    $r = ConvertTo-RepoPath $Parent
    return ($p -eq $r -or $p.StartsWith("$r/"))
}
function Get-FullPath([string]$RelativePath) {
    return (Join-Path $PSScriptRoot ($RelativePath.Replace("/", "\")))
}
function Get-ChangedFiles {
    $r = Invoke-GitCapture @("-c", "core.quotepath=false", "status", "--porcelain=v1", "--untracked-files=all")
    if ($r.Code -ne 0) { Stop-Release "Unable to read the Git working-tree status." }
    $files = @()
    foreach ($line in $r.Output) {
        $text = [string]$line
        if ($text.Trim().Length -eq 0 -or $text.Length -lt 4) { continue }
        $path = $text.Substring(3).Trim()
        if ($path -match " -> ") { $path = ($path -split " -> ")[-1] }
        $path = ConvertTo-RepoPath ($path.Trim('"'))
        if ($path) { $files += $path }
    }
    return @($files | Sort-Object -Unique)
}
function Find-CoreVersionFile {
    foreach ($candidate in $CoreVersionCandidates) {
        $full = Get-FullPath $candidate
        if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { continue }
        $text = [System.IO.File]::ReadAllText($full)
        if ($text -match $VersionAssignmentPattern) { return $candidate }
    }
    return $null
}
# Current version text, or "" if unknown
function Get-CoreVersion([string]$RelativePath) {
    if (-not $RelativePath) { return "" }
    $text = [System.IO.File]::ReadAllText((Get-FullPath $RelativePath))
    $m = [System.Text.RegularExpressions.Regex]::Match($text, $VersionValuePattern)
    if ($m.Success) { return $m.Groups[1].Value.Trim() }
    return ""
}
function Get-WebVersion {
    $full = Get-FullPath $WebVersionFile
    if (-not (Test-Path -LiteralPath $full -PathType Leaf)) { return "" }
    return (([System.IO.File]::ReadAllText($full)).Trim() -replace "^[vV]", "")
}
# 5.0.3 -> 5.0.4 ; 1.0.9.3 -> 1.0.9.4 ; "" if the version is not all numbers
function Get-NextVersion([string]$Current) {
    if ($Current -notmatch '^\d+(\.\d+)*$') { return "" }
    $parts = $Current.Split('.')
    $parts[-1] = [string]([int64]$parts[-1] + 1)
    return ($parts -join '.')
}
# "5.0.3" / "V5.0.3" / "web-V1.0.2" -> "5.0.3"
function ConvertTo-PlainVersion([string]$Value) {
    $v = $Value.Trim()
    if ($v.StartsWith($WebTagPrefix, "OrdinalIgnoreCase")) { $v = $v.Substring($WebTagPrefix.Length) }
    return ($v -replace "^[vV]", "")
}
# Shows the current version and asks for the new one; Enter accepts the suggested next version
function Read-NewVersion([string]$What, [string]$Current, [string]$Where) {
    $suggested = Get-NextVersion $Current
    $cur = if ($Current) { $Current } else { "(unknown)" }
    Write-Host ""
    Write-Host ("Current {0} version: {1}   ({2})" -f $What, $cur, $Where) -ForegroundColor Cyan
    $prompt = if ($suggested) { "New $What version [Enter = $suggested]" } else { "New $What version" }
    $answer = Read-Host $prompt
    if ([string]::IsNullOrWhiteSpace($answer)) { $answer = $suggested }
    return (ConvertTo-PlainVersion $answer)
}
function Test-VersionText([string]$What, [string]$Value) {
    if ($Value -notmatch '^\d+(\.\d+){1,3}$') {
        Stop-Release "$What version '$Value' is not valid. Use numbers separated by dots, for example 5.0.3 or 1.0.2"
    }
}
# Tag must be unused locally and on origin
function Test-TagUnused([string]$Tag) {
    $localTag = Invoke-GitCapture @("tag", "-l", $Tag)
    if (($localTag.Output -join "").Trim()) { Stop-Release "Tag '$Tag' already exists locally. Use a new version number." }
    $remoteTag = Invoke-GitCapture @("ls-remote", "--tags", "origin", "refs/tags/$Tag")
    if ($remoteTag.Code -ne 0) { Stop-Release "Unable to check tags on 'origin'. Check network/credentials." }
    if (($remoteTag.Output -join "").Trim()) { Stop-Release "Tag '$Tag' already exists on origin. Use a new version number." }
}
# ---- Backups so a failure before the commit leaves your files exactly as they were ----
$Backups = @{}
function Save-Backup([string]$RelativePath) {
    if (-not $RelativePath) { return }
    $full = Get-FullPath $RelativePath
    if (Test-Path -LiteralPath $full -PathType Leaf) { $Backups[$RelativePath] = [System.IO.File]::ReadAllBytes($full) }
    else { $Backups[$RelativePath] = $null }
}
function Restore-Backups {
    foreach ($rel in $Backups.Keys) {
        $full = Get-FullPath $rel
        if ($null -eq $Backups[$rel]) {
            if (Test-Path -LiteralPath $full) { Remove-Item -LiteralPath $full -Force -ErrorAction SilentlyContinue }
        }
        else { [System.IO.File]::WriteAllBytes($full, $Backups[$rel]) }
    }
}
function Write-TextNoBom([string]$RelativePath, [string]$Text) {
    [System.IO.File]::WriteAllText((Get-FullPath $RelativePath), $Text, (New-Object System.Text.UTF8Encoding($false)))
}
function Update-CoreVersion([string]$RelativePath, [string]$NewVersion) {
    $full = Get-FullPath $RelativePath
    $text = [System.IO.File]::ReadAllText($full)
    $regex = New-Object System.Text.RegularExpressions.Regex($VersionAssignmentPattern)
    if (-not $regex.IsMatch($text)) { throw "No version assignment found in '$RelativePath'." }
    $updated = $regex.Replace($text, ('${1}${2}' + $NewVersion + '${3}'), 1)
    Write-TextNoBom $RelativePath $updated
}
# Newest release first; an existing entry for the same version is replaced
function Add-ReleaseHistoryEntry([string]$RelativePath, [string]$Ver, [string]$Msg) {
    $full = Get-FullPath $RelativePath
    $entry = "V$Ver - $Msg"
    $old = @()
    if (Test-Path -LiteralPath $full) {
        $old = @(Get-Content -LiteralPath $full -Encoding UTF8 |
                 Where-Object { $_ -ne "V$Ver" -and $_ -notlike "V$Ver - *" })
    }
    Write-TextNoBom $RelativePath ((@($entry) + $old) -join "`r`n")
}
# ======================================================================
# VALIDATION (nothing is edited until all of this passes)
# ======================================================================
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Stop-Release "git was not found. Install it or add it to PATH." }
if ((Invoke-GitCapture @("rev-parse", "--is-inside-work-tree")).Code -ne 0) { Stop-Release "'$PSScriptRoot' is not inside a Git working tree." }
if ((Invoke-GitCapture @("remote", "get-url", "origin")).Code -ne 0) { Stop-Release "Git remote 'origin' is not configured." }

$Message = ($Message -replace '\s+', ' ').Trim()
if ($Message.Length -eq 0)                 { Stop-Release "A release comment is required. Say what changed in this version." }
if ($Message.Length -lt $MinMessageLength) { Stop-Release "The release comment is too short ($($Message.Length) characters; at least $MinMessageLength needed)." }
if (($Message -replace '[^\p{L}]', '').Length -lt 5) { Stop-Release "The release comment must contain words, not just numbers or symbols." }
if ($BannedMessages -contains $Message.TrimEnd('.', '!').ToLowerInvariant()) { Stop-Release "'$Message' does not say what changed. Describe the change." }

$branchResult = Invoke-GitCapture @("branch", "--show-current")
$Branch = (($branchResult.Output -join "").Trim())
if ($branchResult.Code -ne 0 -or $Branch.Trim().Length -eq 0) { Stop-Release "Detached HEAD or unknown branch. Check out a branch first." }
$ChangedFiles = @(Get-ChangedFiles)
if ($ChangedFiles.Count -eq 0) { Stop-Release "There are no changed files to release." }
Write-Host ""
Write-Host "Changed files:" -ForegroundColor Cyan
$ChangedFiles | ForEach-Object { Write-Host "  $_" }

$coreChanges = @($ChangedFiles | Where-Object { (Test-PathInside $_ $JHoraRoot) -and -not (Test-PathInside $_ $NiceGuiRoot) })
$webChanges  = @($ChangedFiles | Where-Object { Test-PathInside $_ $NiceGuiRoot })
$IsCore = ($ReleaseType -eq "core" -or $ReleaseType -eq "both")
$IsWeb  = ($ReleaseType -eq "web"  -or $ReleaseType -eq "both")

# ---- which files changed: must suit the release type ----
if ($ReleaseType -eq "core" -and $coreChanges.Count -eq 0) {
    if (@($ChangedFiles | Where-Object { -not (Test-PathInside $_ $NiceGuiRoot) }).Count -eq 0) {
        Stop-Release "All changes are under '$NiceGuiRoot'. Use the 'Release NiceGUI Web' task instead."
    }
    Stop-Release "No changes found under '$JHoraRoot' (outside '$NiceGuiRoot'). A core release needs at least one."
}
if ($ReleaseType -eq "core" -and $webChanges.Count -gt 0) {
    Write-Host ""
    Write-Host "Files under '$NiceGuiRoot' are changed too:" -ForegroundColor Yellow
    $webChanges | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
    Stop-Release "Core and web files are both changed. Use the 'Release PyJHora Core + Web' task, so the web version and web release history are updated too."
}
if ($ReleaseType -eq "web") {
    $outside = @($ChangedFiles | Where-Object { -not (Test-PathInside $_ $NiceGuiRoot) })
    if ($outside.Count -gt 0) {
        Write-Host ""
        Write-Host "Files outside '$NiceGuiRoot':" -ForegroundColor Yellow
        $outside | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        if ($coreChanges.Count -gt 0) {
            Stop-Release "Core files are changed too. Use the 'Release PyJHora Core + Web' task, or commit/stash the other files."
        }
        Stop-Release "A web release may only contain changes under '$NiceGuiRoot'. Use the 'Release PyJHora Core' task, or commit/stash the other files."
    }
}
if ($ReleaseType -eq "both") {
    if ($coreChanges.Count -eq 0) { Stop-Release "No core changes (under '$JHoraRoot', outside '$NiceGuiRoot'). Use the 'Release NiceGUI Web' task instead." }
    if ($webChanges.Count -eq 0)  { Stop-Release "No web changes (under '$NiceGuiRoot'). Use the 'Release PyJHora Core' task instead." }
}
if ($IsWeb -and -not (Test-Path -LiteralPath (Get-FullPath $NiceGuiRoot) -PathType Container)) { Stop-Release "Folder '$NiceGuiRoot' does not exist." }

# ---- versions (asked for here when not given; current version shown) ----
$CoreVersionFile = $null
$CoreVersion = ""
$WebVer = ""
if ($IsCore) {
    $CoreVersionFile = Find-CoreVersionFile
    if (-not $CoreVersionFile) {
        Stop-Release "Could not find the core version assignment. Add the right file to `$CoreVersionCandidates at the top of release.ps1."
    }
    $CoreVersion = ConvertTo-PlainVersion $Version
    if (-not $CoreVersion) { $CoreVersion = Read-NewVersion "PyJHora core" (Get-CoreVersion $CoreVersionFile) $CoreVersionFile }
    Test-VersionText "Core" $CoreVersion
}
if ($IsWeb) {
    $WebVer = if ($ReleaseType -eq "both") { ConvertTo-PlainVersion $WebVersion } else { ConvertTo-PlainVersion $Version }
    if (-not $WebVer) { $WebVer = Read-NewVersion "NiceGUI web" (Get-WebVersion) $WebVersionFile }
    Test-VersionText "Web" $WebVer
}

$Tags = @()
if ($IsCore) { $Tags += "$TagPrefix$CoreVersion" }
if ($IsWeb)  { $Tags += "$WebTagPrefix$TagPrefix$WebVer" }
$Tags | ForEach-Object { Test-TagUnused $_ }

$GeneratedFiles = @()
if ($IsCore) { $GeneratedFiles += $CoreVersionFile; if ($CoreHistoryFile) { $GeneratedFiles += $CoreHistoryFile } }
if ($IsWeb)  { $GeneratedFiles += @($WebVersionFile, $WebHistoryFile) }

# Web history entry says which core version it goes with (shown in the About page's Release History)
$WebMessage = if ($ReleaseType -eq "both") { "$Message (with PyJHora $TagPrefix$CoreVersion)" } else { $Message }

# Local branch must not be behind origin
$remoteBranch = Invoke-GitCapture @("ls-remote", "--exit-code", "--heads", "origin", $Branch)
if ($remoteBranch.Code -eq 0) {
    $fetch = Invoke-GitCapture @("fetch", "--quiet", "origin", $Branch)
    if ($fetch.Code -ne 0) { Stop-Release "Could not fetch origin/$Branch." }
    $behind = Invoke-GitCapture @("rev-list", "--count", "HEAD..origin/$Branch")
    if ($behind.Code -ne 0) { Stop-Release "Could not compare with origin/$Branch." }
    if (($behind.Output -join "").Trim() -ne "0") { Stop-Release "Local branch is behind origin/$Branch. Pull or rebase first." }
}
Write-Host ""
Write-Host "Release plan" -ForegroundColor Cyan
Write-Host "  Type:    $ReleaseType"
Write-Host "  Tag(s):  $($Tags -join ', ')"
Write-Host "  Branch:  $Branch"
Write-Host "  Message: $Message"
if ($IsCore) { Write-Host "  Core version file: $CoreVersionFile  ->  $CoreVersion" }
if ($IsWeb)  { Write-Host "  Web version file:  $WebVersionFile  ->  $WebVer"; Write-Host "  Web history entry: V$WebVer - $WebMessage" }
# ======================================================================
# RELEASE
# ======================================================================
$CommitCreated = $false
$TagsCreated = @()
$GeneratedFiles | ForEach-Object { Save-Backup $_ }
try {
    # ---- 1. Update version(s) + release history(ies) ----
    if ($IsCore) {
        Update-CoreVersion $CoreVersionFile $CoreVersion
        if ($CoreHistoryFile) { Add-ReleaseHistoryEntry $CoreHistoryFile $CoreVersion $Message }
    }
    if ($IsWeb) {
        Write-TextNoBom $WebVersionFile $WebVer
        Add-ReleaseHistoryEntry $WebHistoryFile $WebVer $WebMessage
    }
    # ---- 2. Stage (web only: only the NiceGUI folder) ----
    if ($ReleaseType -eq "web") { Invoke-Git @("add", "-A", "--", $NiceGuiRoot) "git add failed" }
    else                        { Invoke-Git @("add", "-A") "git add failed" }
    $staged = @((Invoke-GitCapture @("-c", "core.quotepath=false", "diff", "--cached", "--name-only")).Output)
    if ($staged.Count -eq 0) { throw "No files were staged for the release." }
    if ($ReleaseType -eq "web") {
        $bad = @($staged | Where-Object { -not (Test-PathInside $_ $NiceGuiRoot) })
        if ($bad.Count -gt 0) { throw "Files outside '$NiceGuiRoot' were staged: $($bad -join ', ')" }
    }
    Write-Host ""
    Write-Host "Staged for release:" -ForegroundColor Cyan
    $staged | ForEach-Object { Write-Host "  $_" }
    # ---- 3. ONE commit + an annotated tag per version (message via file: quotes/special characters are safe) ----
    $msgFile = [System.IO.Path]::GetTempFileName()
    try {
        [System.IO.File]::WriteAllText($msgFile, "$($Tags -join ' + ') $Message`n", (New-Object System.Text.UTF8Encoding($false)))
        Invoke-Git @("commit", "-F", $msgFile) "git commit failed"
        $CommitCreated = $true
        foreach ($t in $Tags) {
            $tagMsg = if ($t.StartsWith($WebTagPrefix)) { "$t $WebMessage" } else { "$t $Message" }
            [System.IO.File]::WriteAllText($msgFile, "$tagMsg`n", (New-Object System.Text.UTF8Encoding($false)))
            Invoke-Git @("tag", "-a", $t, "-F", $msgFile) "git tag '$t' failed"
            $TagsCreated += $t
        }
    }
    finally { Remove-Item $msgFile -ErrorAction SilentlyContinue }
    # ---- 4. Push ----
    Write-Host ""
    Write-Host "Pushing branch '$Branch'..." -ForegroundColor Cyan
    Invoke-Git @("push", "origin", $Branch) "Commit created locally, but pushing branch '$Branch' failed."
    Write-Host "Pushing tag(s) $($Tags -join ', ')..." -ForegroundColor Cyan
    Invoke-Git (@("push", "origin") + $Tags) "Branch pushed, but pushing tag(s) $($Tags -join ', ') failed."
    Write-Host ""
    Write-Host "RELEASE COMPLETED: $($Tags -join ' + ') on $Branch" -ForegroundColor Green
    & git log --oneline -1
}
catch {
    Write-Host ""
    Write-Host "RELEASE FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if (-not $CommitCreated) {
        Write-Host "Undoing version/history edits and unstaging..." -ForegroundColor Yellow
        Invoke-GitCapture @("reset", "-q") | Out-Null
        Restore-Backups
        Write-Host "Your files are back to how they were before the release." -ForegroundColor Yellow
    }
    else {
        Write-Host ""
        Write-Host "A local release commit exists." -ForegroundColor Yellow
        if ($TagsCreated.Count -gt 0) { Write-Host "Local tag(s) created: $($TagsCreated -join ', ')" -ForegroundColor Yellow }
        Write-Host "Check with:  git status ; git log --oneline -3"
        Write-Host "Publish with:"
        Write-Host "  git push origin $Branch"
        foreach ($t in $Tags) {
            if ($TagsCreated -contains $t) { Write-Host "  git push origin $t" }
            else { Write-Host "  git tag -a $t -m `"$t $Message`" ; git push origin $t" }
        }
    }
    exit 1
}
