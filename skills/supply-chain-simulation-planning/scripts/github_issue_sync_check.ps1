[CmdletBinding()]
param(
    [string]$RequestFile,
    [string]$Repository,
    [int]$IssueNumber,
    [string]$LocalFile,
    [string]$EvidenceCommit,
    [string[]]$EvidencePath = @(),
    [string]$DecisionOwner,
    [string]$BusinessReviewer,
    [switch]$BusinessReviewConfirmed,
    [string]$ApprovalReference,
    [string]$AcceptanceSummary,
    [string]$ExpectedStatusLabel = 'status:passed',
    [ValidateSet('PreClose','PostClose')][string]$Phase = 'PostClose',
    [string]$ProjectRoot = (Get-Location).Path,
    [string]$SnapshotFile,
    [string]$ReportPath,
    [switch]$Apply
)

$ErrorActionPreference = 'Stop'
$Checks = [Collections.Generic.List[object]]::new()
$Actions = [Collections.Generic.List[string]]::new()
$Transport = 'Not selected'
$Root = [IO.Path]::GetFullPath($ProjectRoot)
$ReviewConfirmed = [bool]$BusinessReviewConfirmed

function Add-Check([string]$Name,[bool]$Passed,[string]$Detail) {
    $Checks.Add([pscustomobject]@{ Name=$Name; Passed=$Passed; Detail=$Detail })
}
function Stop-Input([string]$Message) {
    $e = [ArgumentException]::new($Message)
    $e.Data['InputError'] = $true
    throw $e
}
function Finish([string]$Result,[int]$Code,[string]$Detail='') {
    $report = [ordered]@{
        schema_version=1; captured_at_utc=[DateTime]::UtcNow.ToString('o')
        repository=$Repository; issue_number=$IssueNumber; evidence_commit=$EvidenceCommit
        phase=$(if($Apply){'ApplyAndPostClose'}else{$Phase}); transport=$Transport
        snapshot_only=[bool]$SnapshotFile; result=$Result; detail=$Detail
        actions=@($Actions.ToArray()); checks=@($Checks.ToArray())
        observed_issue=$(if($ObservedIssue){@{number=$ObservedIssue.number;state=$ObservedIssue.state;state_reason=$ObservedIssue.state_reason;labels=@(Labels $ObservedIssue)}}else{$null})
        acceptance_comment_url=$ObservedAcceptanceUrl
    }
    Write-Output "GitHub Issue sync audit: $Repository#$IssueNumber [$Transport]"
    foreach($c in $Checks) { Write-Output "[$(if($c.Passed){'PASS'}else{'FAIL'})] $($c.Name): $($c.Detail)" }
    Write-Output "Result: $Result. $Detail"
    if($ReportPath) {
        $reportFull=[IO.Path]::GetFullPath($ReportPath,$Root)
        [IO.Directory]::CreateDirectory([IO.Path]::GetDirectoryName($reportFull)) | Out-Null
        try { [IO.File]::WriteAllText($reportFull,($report|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false)) }
        catch { Write-Output "Receipt could not be saved: $($_.Exception.Message)"; exit 3 }
    }
    exit $Code
}
function Repo-Path([string]$Path) {
    if([string]::IsNullOrWhiteSpace($Path)) { Stop-Input 'A repository-relative path is required' }
    $p=$Path.Replace('\','/')
    if([string]::IsNullOrWhiteSpace($p) -or $p -match '(^/|:|(^|/)\.\.(/|$))') { Stop-Input "Expected repository-relative path: $Path" }
    $p=$p -replace '^\./',''
    $full=[IO.Path]::GetFullPath($p,$Root)
    $rel=[IO.Path]::GetRelativePath($Root,$full)
    if($rel -eq '..' -or $rel.StartsWith('..'+[IO.Path]::DirectorySeparatorChar)) { Stop-Input 'Path leaves project root' }
    return $p
}
function Is-NotFound($ErrorRecord) {
    return $ErrorRecord.Exception.Data['Status'] -eq 404 -or $ErrorRecord.Exception.Message -match '\b404\b|Not Found'
}
function Invoke-GitHub([string]$Endpoint,[string]$Method='GET',$Body=$null) {
    if($SnapshotFile) { throw 'Snapshot replay prohibits network calls and mutations' }
    if($Transport -eq 'gh') {
        if($null -eq $Body) { $raw = & gh api $Endpoint --method $Method 2>&1 }
        else { $raw = ($Body|ConvertTo-Json -Depth 15 -Compress) | & gh api $Endpoint --method $Method --input - 2>&1 }
        if($LASTEXITCODE -ne 0) { throw (($raw|Out-String).Trim()) }
        if([string]::IsNullOrWhiteSpace(($raw|Out-String))) { return $null }
        return ($raw|ConvertFrom-Json)
    }
    $headers=@{ Accept='application/vnd.github+json'; 'X-GitHub-Api-Version'='2022-11-28'; 'User-Agent'='simulation-issue-sync' }
    if($env:GITHUB_TOKEN) { $headers.Authorization="Bearer $env:GITHUB_TOKEN" }
    elseif($Method -ne 'GET') { throw 'GitHub writes require an authenticated gh session or GITHUB_TOKEN' }
    $args=@{ Uri="https://api.github.com/$Endpoint"; Method=$Method; Headers=$headers; TimeoutSec=30 }
    if($null -ne $Body) {
        $args.ContentType='application/json; charset=utf-8'
        $args.Body=[Text.Encoding]::UTF8.GetBytes(($Body|ConvertTo-Json -Depth 15 -Compress))
    }
    return Invoke-RestMethod @args
}
function Read-Issue {
    if($SnapshotFile) { return $Snapshot.issue }
    return Invoke-GitHub "repos/$Repository/issues/$IssueNumber"
}
function Read-Comments {
    if($SnapshotFile) { return @($Snapshot.comments) }
    $all=[Collections.Generic.List[object]]::new()
    for($page=1;$page -le 100;$page++) {
        $batch=@(Invoke-GitHub "repos/$Repository/issues/$IssueNumber/comments?per_page=100&page=$page")
        foreach($c in $batch) { $all.Add($c) }
        if($batch.Count -lt 100) { return $all.ToArray() }
    }
    throw 'Comment retrieval reached its limit; audit is incomplete'
}
function Labels($Issue) {
    return @($Issue.labels | ForEach-Object { if($_ -is [string]){$_}else{$_.name} })
}
function Acceptance-Comment($Comments) {
    return ($Comments | Where-Object {
        $_.body -and $_.body.Contains($EvidenceCommit) -and
        $_.body -match '(?i)验收|acceptance|evidence|证据' -and
        $_.body.Contains("Decision owner: $DecisionOwner") -and
        $_.body.Contains("Business reviewer: $BusinessReviewer")
    } | Select-Object -First 1)
}
function Has-Acceptance($Comments) { return $null -ne (Acceptance-Comment $Comments) }
function Check-Closed($Issue,$Comments) {
    $script:ObservedIssue=$Issue
    $script:ObservedAcceptanceUrl=(Acceptance-Comment $Comments).html_url
    $names=@(Labels $Issue)
    Add-Check 'remote-state' ($Issue.state -eq 'closed') "State: $($Issue.state)"
    Add-Check 'closure-reason' ($Issue.state_reason -eq 'completed') "Reason: $($Issue.state_reason)"
    Add-Check 'status-label' ($names -contains $ExpectedStatusLabel) "Required: $ExpectedStatusLabel"
    $conflicts=@($names | Where-Object { $_ -match '^status:' -and $_ -ne $ExpectedStatusLabel })
    Add-Check 'exclusive-status-label' ($conflicts.Count -eq 0) "Conflicting labels: $($conflicts -join ', ')"
    Add-Check 'acceptance-comment' (Has-Acceptance $Comments) 'Acceptance comment binds evidence commit and named decision owner/business reviewer'
}

try {
    if($RequestFile) {
        $requestPath=[IO.Path]::GetFullPath($RequestFile,$Root)
        $request=Get-Content -LiteralPath $requestPath -Raw | ConvertFrom-Json
        if($request.schema_version -ne 1) { Stop-Input 'Unsupported closure request schema_version' }
        $Repository=[string]$request.repository; $IssueNumber=[int]$request.issue_number
        $LocalFile=[string]$request.local_file; $EvidenceCommit=[string]$request.evidence_commit
        $EvidencePath=@($request.evidence_paths); $DecisionOwner=[string]$request.decision_owner
        $BusinessReviewer=[string]$request.business_reviewer
        $ReviewConfirmed=$request.business_review_confirmed -eq $true
        $ApprovalReference=[string]$request.approval_reference
        $AcceptanceSummary=[string]$request.acceptance_summary
        if($request.expected_status_label) { $ExpectedStatusLabel=[string]$request.expected_status_label }
    }
    if($Repository -notmatch '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' -or $IssueNumber -le 0) { Stop-Input 'Repository and positive IssueNumber are required' }
    if($EvidenceCommit -notmatch '^[0-9a-fA-F]{40}([0-9a-fA-F]{24})?$') { Stop-Input 'EvidenceCommit must be a full immutable commit SHA' }
    if($ExpectedStatusLabel -ne 'status:passed') { Stop-Input 'A Passed closure requires status:passed' }
    $LocalFile=Repo-Path $LocalFile
    $EvidencePath=@($EvidencePath | ForEach-Object { Repo-Path $_ } | Select-Object -Unique)
    if($EvidencePath.Count -eq 0) { Stop-Input 'At least one evidence path is required' }
    if(-not(Test-Path -LiteralPath (Join-Path $Root $LocalFile) -PathType Leaf)) { Stop-Input 'Local Issue file was not found' }
    $localText=Get-Content -LiteralPath (Join-Path $Root $LocalFile) -Raw
    $status=[regex]::Match($localText,'(?im)^\s*(?:-\s*)?(?:状态|Status|Local status)\s*[:：]\s*`?(Passed|Partial|In Progress|Blocked|Rework|N/A)')
    Add-Check 'local-status' ($status.Success -and $status.Groups[1].Value -eq 'Passed') "Local status: $($status.Groups[1].Value)"
    Add-Check 'decision-owner' (-not[string]::IsNullOrWhiteSpace($DecisionOwner)) "Decision owner: $DecisionOwner"
    Add-Check 'business-reviewer' (-not[string]::IsNullOrWhiteSpace($BusinessReviewer)) "Business reviewer: $BusinessReviewer"
    foreach($p in $EvidencePath) { Add-Check "evidence-file:$p" (Test-Path -LiteralPath (Join-Path $Root $p) -PathType Leaf) 'Evidence file exists locally' }
    if($Apply -or $Phase -eq 'PreClose') {
        Add-Check 'business-review-confirmed' $ReviewConfirmed 'Business review confirmation supplied'
        Add-Check 'approval-reference' (-not[string]::IsNullOrWhiteSpace($ApprovalReference)) 'Approval record reference supplied; authorization must be established by the agent'
        Add-Check 'acceptance-summary' (-not[string]::IsNullOrWhiteSpace($AcceptanceSummary)) 'Acceptance scope and any approved deferred work are documented'
    }
    if(@($Checks | Where-Object {-not $_.Passed}).Count) { Finish 'Drift' 2 'Local prerequisites are incomplete; no GitHub mutations.' }
    if($SnapshotFile) {
        if($Apply) { Stop-Input 'Apply is prohibited for snapshot replay' }
        $Snapshot=Get-Content -LiteralPath $SnapshotFile -Raw | ConvertFrom-Json
        $Transport='Snapshot (offline, read-only)'
    } elseif(Get-Command gh -ErrorAction SilentlyContinue) { $Transport='gh' }
    elseif($env:GITHUB_TOKEN) { $Transport='REST token' }
    else { $Transport='REST anonymous (read-only)' }

    $remoteCommit=$null
    try {
        $remoteCommit=if($SnapshotFile){$Snapshot.commit}else{Invoke-GitHub "repos/$Repository/commits/$EvidenceCommit"}
    } catch { if(-not(Is-NotFound $_)){throw} }
    Add-Check 'remote-commit' ($remoteCommit.sha -eq $EvidenceCommit) 'Immutable evidence commit exists in the target repository'
    foreach($p in $EvidencePath) {
        $remoteFile=$null
        if($remoteCommit.sha -eq $EvidenceCommit) {
            try {
                if($SnapshotFile) { $remoteFile=@($Snapshot.files | Where-Object {$_.path -ceq $p -and $_.commit -eq $EvidenceCommit}) | Select-Object -First 1 }
                else {
                    $encoded=($p.Split('/') | ForEach-Object {[Uri]::EscapeDataString($_)}) -join '/'
                    $remoteFile=Invoke-GitHub "repos/$Repository/contents/${encoded}?ref=$EvidenceCommit"
                }
            } catch { if(-not(Is-NotFound $_)){throw} }
        }
        Add-Check "committed-evidence:$p" ($remoteFile.type -eq 'file' -and -not[string]::IsNullOrWhiteSpace($remoteFile.sha)) "Path is a file in evidence commit $EvidenceCommit"
    }
    $issue=Read-Issue; $comments=@(Read-Comments)
    Add-Check 'issue-identity' ($issue.number -eq $IssueNumber -and -not $issue.pull_request) 'Target is the requested Issue, not a PR'
    if($Apply -or $Phase -eq 'PreClose') {
        Add-Check 'closeable-state' ($issue.state -eq 'open' -or ($issue.state -eq 'closed' -and $issue.state_reason -eq 'completed')) 'No conflicting historical closure reason'
        $statuses=@((Labels $issue) | Where-Object {$_ -match '^status:'})
        Add-Check 'nonconflicting-status' ($statuses.Count -le 1) "Existing status labels: $($statuses -join ', ')"
    } else { Check-Closed $issue $comments }
    if(@($Checks | Where-Object {-not $_.Passed}).Count) { Finish 'Drift' 2 'Closure prerequisites or online state are inconsistent; no GitHub mutations.' }
    if(-not $Apply) { Finish $(if($Phase -eq 'PreClose'){'Ready'}else{'Passed'}) 0 'Read-only audit; no GitHub mutations. Snapshot success is not live verification.' }
    if($Transport -eq 'REST anonymous (read-only)') { Finish 'Unavailable' 3 'Write authentication is unavailable; no GitHub mutations.' }

    $marker="<!-- simulation-issue-closure:$Repository`:$IssueNumber`:$EvidenceCommit -->"
    if(-not(Has-Acceptance $comments)) {
        $links=($EvidencePath | ForEach-Object { "- [$_](https://github.com/$Repository/blob/$EvidenceCommit/$_)" }) -join "`n"
        $body=@"
$marker
## Issue closure acceptance

- Local status: Passed
- Decision owner: $DecisionOwner
- Business reviewer: $BusinessReviewer
- Approval reference: $ApprovalReference
- Evidence commit: $EvidenceCommit
- Local Issue file: $LocalFile
- Closure reason: completed

$AcceptanceSummary

$links
"@
        Invoke-GitHub "repos/$Repository/issues/$IssueNumber/comments" 'POST' @{body=$body} | Out-Null
        $Actions.Add('acceptance-comment')
    }
    $labelExists=$true
    try { Invoke-GitHub "repos/$Repository/labels/$([Uri]::EscapeDataString($ExpectedStatusLabel))" | Out-Null }
    catch { if(Is-NotFound $_){$labelExists=$false}else{throw} }
    if(-not $labelExists) {
        Invoke-GitHub "repos/$Repository/labels" 'POST' @{name=$ExpectedStatusLabel;color='0e8a16';description='Passed within the documented acceptance scope'} | Out-Null
        $Actions.Add('create-status-label')
    }
    $current=@(Labels $issue)
    if($current -notcontains $ExpectedStatusLabel) {
        $newLabels=@($current | Where-Object {$_ -notmatch '^status:'}) + @($ExpectedStatusLabel)
        Invoke-GitHub "repos/$Repository/issues/$IssueNumber/labels" 'PUT' @{labels=@($newLabels)} | Out-Null
        $Actions.Add('status-label')
    }
    if($issue.state -ne 'closed') {
        Invoke-GitHub "repos/$Repository/issues/$IssueNumber" 'PATCH' @{state='closed';state_reason='completed'} | Out-Null
        $Actions.Add('completed-close')
    }
    Check-Closed (Read-Issue) @(Read-Comments)
    if(@($Checks | Where-Object {-not $_.Passed}).Count) { Finish 'Drift' 2 'Post-write readback failed; retain partial actions and investigate before retrying.' }
    Finish 'Passed' 0 'Online closure read back successfully. Update local sync status and commit the receipt.'
} catch {
    if($_.Exception.Data['InputError']) { Finish 'InvalidInput' 2 $_.Exception.Message }
    Finish 'Unavailable' 3 $_.Exception.Message
}
