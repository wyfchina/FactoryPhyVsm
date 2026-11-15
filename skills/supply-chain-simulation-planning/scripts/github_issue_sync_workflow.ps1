[CmdletBinding()]
param()
$ErrorActionPreference='Stop'
if(-not $env:GITHUB_EVENT_PATH -or -not $env:GITHUB_REPOSITORY) { throw 'This runner requires a GitHub Actions event context' }
$event=Get-Content -LiteralPath $env:GITHUB_EVENT_PATH -Raw | ConvertFrom-Json
if($env:GITHUB_REF -ne "refs/heads/$($event.repository.default_branch)") { throw 'This template runs only on the repository default branch; explicitly adapt the project workflow for another approved integration branch' }
if($env:GITHUB_EVENT_NAME -eq 'workflow_dispatch') {
    $requests=@([string]$event.inputs.request_file)
} elseif($env:GITHUB_EVENT_NAME -eq 'push') {
    if($event.before -match '^0+$') {
        $requests=@(& git ls-tree -r --name-only $env:GITHUB_SHA -- .github/issue-closures)
    } else {
        $requests=@(& git diff --name-only --diff-filter=AM $event.before $env:GITHUB_SHA -- .github/issue-closures)
    }
    if($LASTEXITCODE -ne 0) { throw 'Unable to determine changed closure requests; no Issue mutations' }
} else { throw 'Unsupported workflow event' }
$reports=Join-Path $env:RUNNER_TEMP 'issue-sync-receipts'
[IO.Directory]::CreateDirectory($reports)|Out-Null
$checker=Join-Path $PSScriptRoot 'github_issue_sync_check.ps1'
foreach($file in $requests) {
    if($file -notmatch '^\.github/issue-closures/[A-Za-z0-9_.-]+\.json$') { throw "Invalid closure request path: $file" }
    $request=Get-Content -LiteralPath $file -Raw | ConvertFrom-Json
    if($request.repository -cne $env:GITHUB_REPOSITORY -or "refs/heads/$($request.target_branch)" -cne $env:GITHUB_REF) { throw 'Closure request repository or target branch does not match this run' }
    if($request.mode -notin @('audit','apply')) { throw 'Closure request mode must be audit or apply' }
    $doApply=$request.mode -eq 'apply'
    if($env:GITHUB_EVENT_NAME -eq 'workflow_dispatch') {
        $manualApply=[string]$event.inputs.apply -eq 'true'
        if($manualApply -and -not $doApply) { throw 'Manual apply requires a request explicitly marked mode=apply' }
        $doApply=$doApply -and $manualApply
    }
    $arguments=@{RequestFile=$file;Phase='PreClose';ReportPath=(Join-Path $reports ([IO.Path]::GetFileNameWithoutExtension($file)+'.json'))}
    if($doApply) { $arguments.Apply=$true }
    & $checker @arguments
    if($LASTEXITCODE -ne 0) { throw "Issue sync did not complete for $file (exit $LASTEXITCODE); inspect the receipt before retrying" }
}
