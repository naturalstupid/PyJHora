param(
    [Parameter(Mandatory = $true)][ValidateSet("core", "web")][string]$ReleaseType,
    [Parameter(Mandatory = $true)][string]$Version,
    [Parameter(Mandatory = $true)][string]$Message
)

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

# Files searched (in order) for the core version assignment, e.g.  __version__ = "5.0.2"
$CoreVersionCandidates = @(
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

# Accept "5.0.3", "V5.0.3" or "web-V0.9.9.4" - the prefix is added by the script
$Version = $Version.Trim()
if ($Version.StartsWith($WebTagPrefix, "OrdinalIgnoreCase")) { $Version = $Version.Substring($WebTagPrefix.Length) }
$Version = $Version -replace "^[vV]", ""
$Message = ($Message -replace '\s+', ' ').Trim()

if ($Version -notmatch '^\d+(\.\d+){1,3}$') {
    Stop-Release "Version '$Version' is not valid. Use numbers separated by dots, for example 5.0.3 or 0.9.9.4"
}
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

$CoreVersionFile = $null
$GeneratedFiles = @()

if ($ReleaseType -eq "core") {
    $Tag = "$TagPrefix$Version"

    $coreChanges = @($ChangedFiles | Where-Object { (Test-PathInside $_ $JHoraRoot) -and -not (Test-PathInside $_ $NiceGuiRoot) })
    if ($coreChanges.Count -eq 0) {
        $allWeb = @($ChangedFiles | Where-Object { -not (Test-PathInside $_ $NiceGuiRoot) }).Count -eq 0
        if ($allWeb) { Stop-Release "All changes are under '$NiceGuiRoot'. Use the 'Release NiceGUI Web' task instead." }
        Stop-Release "No changes found under '$JHoraRoot' (outside '$NiceGuiRoot'). A core release needs at least one."
    }

    $CoreVersionFile = Find-CoreVersionFile
    if (-not $CoreVersionFile) {
        Stop-Release "Could not find the core version assignment. Add the right file to `$CoreVersionCandidates at the top of release.ps1."
    }
    $GeneratedFiles = @($CoreVersionFile)
    if ($CoreHistoryFile) { $GeneratedFiles += $CoreHistoryFile }
}
else {
    $Tag = "$WebTagPrefix$TagPrefix$Version"

    $outside = @($ChangedFiles | Where-Object { -not (Test-PathInside $_ $NiceGuiRoot) })
    if ($outside.Count -gt 0) {
        Write-Host ""
        Write-Host "Files outside '$NiceGuiRoot':" -ForegroundColor Yellow
        $outside | ForEach-Object { Write-Host "  $_" -ForegroundColor Yellow }
        Stop-Release "A web release may only contain changes under '$NiceGuiRoot'. Use the 'Release PyJHora Core' task, or commit/stash the other files."
    }
    if (-not (Test-Path -LiteralPath (Get-FullPath $NiceGuiRoot) -PathType Container)) { Stop-Release "Folder '$NiceGuiRoot' does not exist." }
    $GeneratedFiles = @($WebVersionFile, $WebHistoryFile)
}

# Tag must be unused locally and on origin
$localTag = Invoke-GitCapture @("tag", "-l", $Tag)
if (($localTag.Output -join "").Trim()) { Stop-Release "Tag '$Tag' already exists locally. Use a new version number." }

$remoteTag = Invoke-GitCapture @("ls-remote", "--tags", "origin", "refs/tags/$Tag")
if ($remoteTag.Code -ne 0) { Stop-Release "Unable to check tags on 'origin'. Check network/credentials." }
if (($remoteTag.Output -join "").Trim()) { Stop-Release "Tag '$Tag' already exists on origin. Use a new version number." }

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
Write-Host "  Tag:     $Tag"
Write-Host "  Branch:  $Branch"
Write-Host "  Message: $Message"
if ($CoreVersionFile) { Write-Host "  Version file: $CoreVersionFile" }

# ======================================================================
# RELEASE
# ======================================================================
$CommitCreated = $false
$TagCreated = $false
$GeneratedFiles | ForEach-Object { Save-Backup $_ }

try {
    # ---- 1. Update version + release history ----
    if ($ReleaseType -eq "core") {
        Update-CoreVersion $CoreVersionFile $Version
        if ($CoreHistoryFile) { Add-ReleaseHistoryEntry $CoreHistoryFile $Version $Message }
    }
    else {
        Write-TextNoBom $WebVersionFile $Version
        Add-ReleaseHistoryEntry $WebHistoryFile $Version $Message
    }

    # ---- 2. Stage (web: only the NiceGUI folder) ----
    if ($ReleaseType -eq "core") { Invoke-Git @("add", "-A") "git add failed" }
    else                         { Invoke-Git @("add", "-A", "--", $NiceGuiRoot) "git add failed" }

    $staged = @((Invoke-GitCapture @("-c", "core.quotepath=false", "diff", "--cached", "--name-only")).Output)
    if ($staged.Count -eq 0) { throw "No files were staged for the release." }
    if ($ReleaseType -eq "web") {
        $bad = @($staged | Where-Object { -not (Test-PathInside $_ $NiceGuiRoot) })
        if ($bad.Count -gt 0) { throw "Files outside '$NiceGuiRoot' were staged: $($bad -join ', ')" }
    }
    Write-Host ""
    Write-Host "Staged for release:" -ForegroundColor Cyan
    $staged | ForEach-Object { Write-Host "  $_" }

    # ---- 3. Commit + annotated tag (message passed via file: quotes/special characters are safe) ----
    $msgFile = [System.IO.Path]::GetTempFileName()
    try {
        [System.IO.File]::WriteAllText($msgFile, "$Tag $Message`n", (New-Object System.Text.UTF8Encoding($false)))
        Invoke-Git @("commit", "-F", $msgFile) "git commit failed"
        $CommitCreated = $true
        Invoke-Git @("tag", "-a", $Tag, "-F", $msgFile) "git tag failed"
        $TagCreated = $true
    }
    finally { Remove-Item $msgFile -ErrorAction SilentlyContinue }

    # ---- 4. Push ----
    Write-Host ""
    Write-Host "Pushing branch '$Branch'..." -ForegroundColor Cyan
    Invoke-Git @("push", "origin", $Branch) "Commit created locally, but pushing branch '$Branch' failed."
    Write-Host "Pushing tag '$Tag'..." -ForegroundColor Cyan
    Invoke-Git @("push", "origin", $Tag) "Branch pushed, but pushing tag '$Tag' failed."

    Write-Host ""
    Write-Host "RELEASE COMPLETED: $Tag on $Branch" -ForegroundColor Green
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
        Write-Host "A local release commit exists" -NoNewline -ForegroundColor Yellow
        if ($TagCreated) { Write-Host " and local tag '$Tag'." -ForegroundColor Yellow } else { Write-Host " (tag NOT created)." -ForegroundColor Yellow }
        Write-Host "Check with:  git status ; git log --oneline -3"
        Write-Host "Publish with:"
        Write-Host "  git push origin $Branch"
        if ($TagCreated) { Write-Host "  git push origin $Tag" }
        else { Write-Host "  git tag -a $Tag -m `"$Tag $Message`" ; git push origin $Tag" }
    }
    exit 1
}