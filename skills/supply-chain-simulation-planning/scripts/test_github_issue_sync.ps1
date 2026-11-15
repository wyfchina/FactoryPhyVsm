[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$TestRoot,
    [string]$CheckerPath=(Join-Path $PSScriptRoot 'github_issue_sync_check.ps1'),
    [string]$ReportPath
)
$ErrorActionPreference='Stop'
$TestRoot=[IO.Path]::GetFullPath($TestRoot)
$CheckerPath=[IO.Path]::GetFullPath($CheckerPath)
if(Test-Path -LiteralPath $TestRoot) { throw 'Use a new isolated TestRoot; existing files are never deleted or overwritten' }
[IO.Directory]::CreateDirectory((Join-Path $TestRoot 'evidence'))|Out-Null
[IO.Directory]::CreateDirectory((Join-Path $TestRoot 'iterations/I3'))|Out-Null
$utf8=[Text.UTF8Encoding]::new($false)
function Save-Json([string]$Path,$Value) { [IO.File]::WriteAllText($Path,($Value|ConvertTo-Json -Depth 30),$utf8) }
[IO.File]::WriteAllText((Join-Path $TestRoot 'iterations/I3/06.md'),"状态: Passed`n",$utf8)
[IO.File]::WriteAllText((Join-Path $TestRoot 'evidence/acceptance.md'),'Synthetic evidence for isolated regression only.',$utf8)
[IO.File]::WriteAllText((Join-Path $TestRoot 'evidence/local-only.md'),'Intentionally not in the synthetic commit.',$utf8)
$sha='a'*40
$baseRequest=[ordered]@{schema_version=1;repository='example/simulation-test';issue_number=42;local_file='iterations/I3/06.md';evidence_commit=$sha;evidence_paths=@('evidence/acceptance.md');decision_owner='DecisionOwner';business_reviewer='Reviewer';business_review_confirmed=$true;approval_reference='Synthetic approval, no live authorization';acceptance_summary='Synthetic specification scope; native model work remains outside this test.'}
$baseSnapshot=[ordered]@{
    issue=@{number=42;state='closed';state_reason='completed';labels=@(@{name='verification'},@{name='status:passed'})}
    comments=@(@{id=1;html_url='https://example.invalid/acceptance';body="Acceptance evidence $sha`nDecision owner: DecisionOwner`nBusiness reviewer: Reviewer"})
    commit=@{sha=$sha}
    files=@(@{path='evidence/acceptance.md';commit=$sha;type='file';sha=('b'*40)})
}
$cases=@(
    @{name='valid';exit=0}, @{name='local-partial';exit=2}, @{name='missing-evidence';exit=2},
    @{name='remote-open';exit=2}, @{name='no-acceptance-comment';exit=2}, @{name='wrong-close-reason';exit=2},
    @{name='conflicting-status-labels';exit=2}, @{name='uncommitted-evidence';exit=2},
    @{name='missing-commit';exit=2}, @{name='empty-evidence-list';exit=2}, @{name='path-outside-root';exit=2},
    @{name='snapshot-apply-prohibited';exit=2}, @{name='preclose-open';exit=0},
    @{name='unconfirmed-review';exit=2}, @{name='wrong-issue';exit=2}
)
$results=[Collections.Generic.List[object]]::new()
foreach($case in $cases) {
    $req=($baseRequest|ConvertTo-Json -Depth 20)|ConvertFrom-Json
    $snap=($baseSnapshot|ConvertTo-Json -Depth 20)|ConvertFrom-Json
    $phase='PostClose';$apply=$false
    $local=Join-Path $TestRoot 'iterations/I3/06.md'
    [IO.File]::WriteAllText($local,"状态: Passed`n",$utf8)
    switch($case.name) {
        'local-partial' {[IO.File]::WriteAllText($local,"状态: Partial`n",$utf8)}
        'missing-evidence' {$req.evidence_paths=@('evidence/missing.md')}
        'remote-open' {$snap.issue.state='open'}
        'no-acceptance-comment' {$snap.comments=@()}
        'wrong-close-reason' {$snap.issue.state_reason='not_planned'}
        'conflicting-status-labels' {$snap.issue.labels+=@{name='status:partial'}}
        'uncommitted-evidence' {$req.evidence_paths=@('evidence/local-only.md')}
        'missing-commit' {$snap.commit=$null}
        'empty-evidence-list' {$req.evidence_paths=@()}
        'path-outside-root' {$req.evidence_paths=@('../outside.md')}
        'snapshot-apply-prohibited' {$apply=$true}
        'preclose-open' {$phase='PreClose';$snap.issue.state='open';$snap.issue.state_reason=$null;$snap.issue.labels=@(@{name='status:partial'});$snap.comments=@()}
        'unconfirmed-review' {$phase='PreClose';$req.business_review_confirmed=$false}
        'wrong-issue' {$snap.issue.number=99}
    }
    $requestFile=Join-Path $TestRoot ($case.name+'-request.json')
    $snapshotFile=Join-Path $TestRoot ($case.name+'-snapshot.json')
    $receipt=Join-Path $TestRoot ($case.name+'-receipt.json')
    Save-Json $requestFile $req; Save-Json $snapshotFile $snap
    $params=@('-NoLogo','-NoProfile','-File',$CheckerPath,'-ProjectRoot',$TestRoot,'-RequestFile',$requestFile,'-SnapshotFile',$snapshotFile,'-Phase',$phase,'-ReportPath',$receipt)
    if($apply){$params+='-Apply'}
    $output=(& pwsh @params 2>&1)|Out-String
    $code=$LASTEXITCODE
    $report=Get-Content -LiteralPath $receipt -Raw|ConvertFrom-Json
    $ok=$code -eq $case.exit -and @($report.actions).Count -eq 0
    $results.Add([pscustomobject]@{case=$case.name;expected_exit=$case.exit;actual_exit=$code;passed=$ok;actions=@($report.actions);output=$output})
}

# A local REST double exercises writes and retry behavior. Unknown endpoints fail;
# it never falls through to real HTTP and uses a dummy token in a child process.
$mockSource=@'
param([string]$Checker,[string]$Root,[string]$Request,[string]$Case,[string]$StateFile,[string]$Workflow)
$ErrorActionPreference='Stop'
$global:SyncTestState=@{issue=[pscustomobject]@{number=42;state='open';state_reason=$null;labels=@(@{name='verification'},@{name='status:partial'})};comments=@();writes=@();failOnce=($Case -eq 'partial-write-retry')}
$env:GITHUB_TOKEN='synthetic-token-used-only-by-local-test-double'
function Invoke-RestMethod {
    param($Uri,$Method,$Headers,$TimeoutSec,$Body,$ContentType)
    $path=[Uri]::UnescapeDataString(([Uri]$Uri).AbsolutePath)
    $data=if($null -ne $Body){[Text.Encoding]::UTF8.GetString($Body)|ConvertFrom-Json}else{$null}
    if($Method -eq 'GET') {
        if($path -match '/commits/') {return [pscustomobject]@{sha=('a'*40)}}
        if($path -match '/contents/') {return [pscustomobject]@{type='file';sha=('b'*40)}}
        if($path -match '/issues/42/comments$') {return @($global:SyncTestState.comments)}
        if($path -match '/issues/42$') {return $global:SyncTestState.issue}
        if($path -match '/labels/status:passed$') {return [pscustomobject]@{name='status:passed'}}
        throw "Unknown test read endpoint: $path"
    }
    if($Method -eq 'POST' -and $path -match '/issues/42/comments$') {
        $comment=[pscustomobject]@{id=1;html_url='https://example.invalid/acceptance';body=$data.body}
        $global:SyncTestState.comments+=@($comment);$global:SyncTestState.writes+=@('comment');return $comment
    }
    if($Method -eq 'PUT' -and $path -match '/issues/42/labels$') {
        if($global:SyncTestState.failOnce){$global:SyncTestState.failOnce=$false;throw 'Synthetic transport interruption after acceptance comment'}
        $global:SyncTestState.issue.labels=@($data.labels|ForEach-Object{[pscustomobject]@{name=$_}})
        $global:SyncTestState.writes+=@('labels');return $global:SyncTestState.issue.labels
    }
    if($Method -eq 'PATCH' -and $path -match '/issues/42$') {
        $global:SyncTestState.issue.state=$data.state;$global:SyncTestState.issue.state_reason=$data.state_reason
        $global:SyncTestState.writes+=@('close');return $global:SyncTestState.issue
    }
    throw "Unknown test mutation endpoint: $Method $path"
}
# Hide any real gh executable without changing machine configuration.
function Get-Command {
    param([string]$Name,$ErrorAction)
    if($Name -eq 'gh'){return $null}
    Microsoft.PowerShell.Core\Get-Command -Name $Name -ErrorAction $ErrorAction
}
if($Workflow) {
    Set-Location -LiteralPath $Root
    $env:GITHUB_REPOSITORY='example/simulation-test'
    $env:GITHUB_REF=if($Case -eq 'workflow-wrong-branch'){'refs/heads/other'}else{'refs/heads/main'}
    $env:GITHUB_EVENT_NAME='workflow_dispatch';$env:RUNNER_TEMP=$Root
    $eventPath=Join-Path $Root ($Case+'-event.json')
    $event=@{repository=@{default_branch='main'};inputs=@{request_file='.github/issue-closures/request.json';apply=$(if($Case -eq 'workflow-apply'){'true'}else{'false'})}}
    [IO.File]::WriteAllText($eventPath,($event|ConvertTo-Json -Depth 10),[Text.UTF8Encoding]::new($false))
    $env:GITHUB_EVENT_PATH=$eventPath
    $runnerExit=0;$message=''
    try {& $Workflow;$runnerExit=[int]$LASTEXITCODE}catch{$runnerExit=2;$message=$_.Exception.Message}
    $result=@{runner_exit=$runnerExit;message=$message;writes=$global:SyncTestState.writes;issue=$global:SyncTestState.issue}
    [IO.File]::WriteAllText($StateFile,($result|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
    exit 0
}
& $Checker -ProjectRoot $Root -RequestFile $Request -Apply -ReportPath (Join-Path $Root ($Case+'-first.json'))
$first=$LASTEXITCODE
& $Checker -ProjectRoot $Root -RequestFile $Request -Apply -ReportPath (Join-Path $Root ($Case+'-second.json'))
$second=$LASTEXITCODE
$result=@{first_exit=$first;second_exit=$second;issue=$global:SyncTestState.issue;writes=$global:SyncTestState.writes;comments=$global:SyncTestState.comments}
[IO.File]::WriteAllText($StateFile,($result|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
exit 0
'@
$mockFile=Join-Path $TestRoot 'mock-rest-apply.ps1'
[IO.File]::WriteAllText($mockFile,$mockSource,$utf8)
[IO.File]::WriteAllText((Join-Path $TestRoot 'iterations/I3/06.md'),"状态: Passed`n",$utf8)
$applyRequest=Join-Path $TestRoot 'apply-request.json';Save-Json $applyRequest $baseRequest
foreach($name in @('apply-idempotent','partial-write-retry')) {
    $stateFile=Join-Path $TestRoot ($name+'-state.json')
    $output=(& pwsh -NoLogo -NoProfile -File $mockFile -Checker $CheckerPath -Root $TestRoot -Request $applyRequest -Case $name -StateFile $stateFile 2>&1)|Out-String
    $code=$LASTEXITCODE
    $state=if(Test-Path -LiteralPath $stateFile){Get-Content -LiteralPath $stateFile -Raw|ConvertFrom-Json}else{$null}
    $expectedFirst=if($name -eq 'partial-write-retry'){3}else{0}
    $ok=$code -eq 0 -and $state.first_exit -eq $expectedFirst -and $state.second_exit -eq 0 -and $state.issue.state -eq 'closed' -and $state.issue.state_reason -eq 'completed' -and @($state.comments).Count -eq 1 -and @($state.writes).Count -eq 3
    $results.Add([pscustomobject]@{case=$name;passed=$ok;first_exit=$state.first_exit;second_exit=$state.second_exit;writes=$state.writes;output=$output})
}
$workflowPath=Join-Path ([IO.Path]::GetDirectoryName($CheckerPath)) 'github_issue_sync_workflow.ps1'
[IO.Directory]::CreateDirectory((Join-Path $TestRoot '.github/issue-closures'))|Out-Null
foreach($name in @('workflow-audit','workflow-apply','workflow-wrong-repository','workflow-wrong-branch')) {
    $req=($baseRequest|ConvertTo-Json -Depth 20)|ConvertFrom-Json
    $req|Add-Member mode $(if($name -eq 'workflow-apply'){'apply'}else{'audit'})
    $req|Add-Member target_branch 'main'
    if($name -eq 'workflow-wrong-repository'){$req.repository='other/repository'}
    Save-Json (Join-Path $TestRoot '.github/issue-closures/request.json') $req
    $stateFile=Join-Path $TestRoot ($name+'-state.json')
    $output=(& pwsh -NoLogo -NoProfile -File $mockFile -Checker $CheckerPath -Root $TestRoot -Request $applyRequest -Case $name -StateFile $stateFile -Workflow $workflowPath 2>&1)|Out-String
    $code=$LASTEXITCODE
    $state=if(Test-Path -LiteralPath $stateFile){Get-Content -LiteralPath $stateFile -Raw|ConvertFrom-Json}else{$null}
    $expected=if($name -match 'wrong-'){2}else{0}
    $expectedWrites=if($name -eq 'workflow-apply'){3}else{0}
    $ok=$code -eq 0 -and $state.runner_exit -eq $expected -and @($state.writes).Count -eq $expectedWrites
    $results.Add([pscustomobject]@{case=$name;passed=$ok;actual_exit=$state.runner_exit;writes=$state.writes;output=$output})
}
$final=[ordered]@{captured_at_utc=[DateTime]::UtcNow.ToString('o');network_writes=$false;fixture_kind='Synthetic isolated audit snapshots and local REST double';checker_sha256=(Get-FileHash -LiteralPath $CheckerPath).Hash;passed=@($results|Where-Object passed).Count;total=$results.Count;cases=@($results.ToArray())}
if($ReportPath){Save-Json ([IO.Path]::GetFullPath($ReportPath)) $final}
$results|Select-Object case,passed,expected_exit,actual_exit,first_exit,second_exit|Format-Table -AutoSize
if($final.passed -ne $final.total){exit 1}
exit 0
