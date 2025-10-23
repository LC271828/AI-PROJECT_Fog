param(
  [string]$ConfigPath = "scripts/issues.json",
  [switch]$SkipExisting
)

# Load config (PowerShell 5.1 friendly)
if (!(Test-Path $ConfigPath)) { throw "Config file not found: $ConfigPath" }
$config = Get-Content -Raw -Path $ConfigPath | ConvertFrom-Json

$Repo = $config.repo
if (-not $Repo) { throw "Missing 'repo' in config" }
$fallbackAssignee = $config.fallbackAssignee

# Create labels from config (ignore if exist)
if ($config.labels) {
  foreach ($l in $config.labels) {
    try { gh label create $l.name --color $l.color --description $l.description --repo $Repo | Out-Null } catch {}
  }
}

function Get-IssueNumberByTitle {
  param(
    [string]$Title
  )
  $search = gh issue list --repo $Repo -S $Title --state all --json number,title | ConvertFrom-Json
  if ($search) {
    # exact match first
    $exact = @($search | Where-Object { $_.title -eq $Title })
    if ($exact.Count -gt 0) { return $exact[0].number }
    return $search[0].number
  }
  return $null
}

function Add-AssigneesSafely {
  param(
    [int]$IssueNumber,
    [string[]]$Assignees
  )
  $assigned = $false
  if ($Assignees) {
    foreach ($a in $Assignees) {
      $name = $a.Trim()
      if (-not $name) { continue }
      try { gh issue edit $IssueNumber --repo $Repo --add-assignee $name | Out-Null; $assigned = $true } catch {}
    }
  }
  if (-not $assigned -and $fallbackAssignee) {
    try { gh issue edit $IssueNumber --repo $Repo --add-assignee $fallbackAssignee | Out-Null } catch {}
  }
}

function Add-LabelsSafely {
  param(
    [int]$IssueNumber,
    [string[]]$Labels
  )
  if ($Labels) {
    foreach ($lab in $Labels) {
      $lname = $lab.Trim()
      if (-not $lname) { continue }
      try { gh issue edit $IssueNumber --repo $Repo --add-label $lname | Out-Null } catch {}
    }
  }
}

function Add-CommentsSafely {
  param(
    [int]$IssueNumber,
    [string[]]$Comments
  )
  if ($Comments) {
    foreach ($c in $Comments) {
      if ([string]::IsNullOrWhiteSpace($c)) { continue }
      gh issue comment $IssueNumber --repo $Repo --body $c | Out-Null
    }
  }
}

foreach ($issue in $config.issues) {
  $title = $issue.title
  $labels = @($issue.labels)
  $assignees = @($issue.assignees)

  $existingNum = Get-IssueNumberByTitle -Title $title

  if ($existingNum -and $SkipExisting) {
    # Update labels/assignees/comments for existing issue and continue
  Add-LabelsSafely -IssueNumber $existingNum -Labels $labels
  Add-AssigneesSafely -IssueNumber $existingNum -Assignees $assignees
  Add-CommentsSafely -IssueNumber $existingNum -Comments $issue.comments
    Write-Host "Updated existing issue #$existingNum - $title" -ForegroundColor Yellow
    continue
  }

  # Prepare body text: prefer bodyFile, fallback to body string
  $bodyText = ""
  if ($issue.bodyFile) {
    $path = $issue.bodyFile
    if (!(Test-Path $path)) { throw "Body file not found: $path for issue '$title'" }
    $bodyText = Get-Content -Raw -Path $path
  } elseif ($issue.body) {
    $bodyText = [string]$issue.body
  }

  # Build create command (labels and project/milestone handled here if provided)
  $cmdArgs = @("issue", "create", "--repo", $Repo, "--title", $title, "--body-file", "-")
  if ($issue.milestone) { $cmdArgs += @("--milestone", $issue.milestone) }
  if ($issue.project)   { $cmdArgs += @("--project", $issue.project) }
  if ($labels) {
    foreach ($lab in $labels) { if ($lab) { $cmdArgs += @("--label", $lab) } }
  }

  $out = $bodyText | gh @cmdArgs 2>&1
  $num = $null
  if ($out -match "/issues/(\d+)") { $num = $Matches[1] }
  if (-not $num) { $num = Get-IssueNumberByTitle -Title $title }
  if (-not $num) { Write-Host "Warning: couldn't resolve number for '$title'" -ForegroundColor Yellow; continue }

  Add-AssigneesSafely -IssueNumber $num -Assignees $assignees
  Add-CommentsSafely -IssueNumber $num -Comments $issue.comments
  Write-Host "Created/updated #$num - $title" -ForegroundColor Green
}
