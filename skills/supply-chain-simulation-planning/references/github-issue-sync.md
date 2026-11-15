# GitHub Issue 闭环同步协议

仅用于项目已声明 `github_management: enabled` 的场景。GitHub Issue负责线上工作项状态，本地Markdown负责详细验收；本协议不替代模型验收或业务评审。

## 触发与完成定义

当某Issue本地验收准备进入Passed时，代理必须主动启动同步，不等用户再次提醒。实际顺序为：验收及批准 → 提交不可变证据 → 关闭前检查 → 已授权的线上写入 → 事后回读 → 回填本地并提交。已有会话授权足够时直接继续，不重复索要批准。

Skill是代理工作规则，不能自行常驻监听文件或GitHub事件。若需自动执行，按下文接入项目Action；单独修改Passed或看到工作流启动都不代表同步完成。

线上闭环要求同时满足：

- 本地Passed只覆盖该Issue验收范围。未满足项须经业务批准明确处置并指定下游责任，不能仅改写关闭条件。
- 决策责任人、业务评审、批准依据、接受范围与剩余工作可追溯；脚本不能代替人判断业务批准是否真实有效。
- 证据提交使用完整SHA；每条证据路径既在本地存在，也确实是该提交中的文件。提交存在不等于证据路径已提交。
- GitHub有绑定证据SHA、决策责任人和业务评审人的验收评论。
- 状态为closed，关闭原因为completed；含status:passed，且无其他status:状态标签冲突。
- 写入后重新读取状态、关闭原因、标签和评论；保留回执后才能把本地GitHub sync登记为Closed。

父级项目和下游Issue只按各自验收判断，不随当前Issue自动关闭。发现历史关闭原因冲突时报告差异，不能无声重写历史。

## 通道选择与失败处理

1. 先确认可用的读取与写入能力。已登录gh或GITHUB_TOKEN可供本地脚本访问；公共仓库可匿名只读。Connector授权不会自动进入本地PowerShell。
2. 无本地认证时，可用Connector完成同一清单。读取完整Issue、全部评论、证据提交和每条证据路径；把这次读取保存为快照时，只能标记为快照审计，不能宣称已执行线上写入。
3. Connector可读但写入403时，不反复尝试相同操作；已获仓库操作授权且项目允许Actions时，可用下文通用Action执行。新增Action须先完成可审阅文件与本地检查，不借此扩大原授权。
4. 没有可用通道时，保留本地Passed与GitHub sync: Pending，说明具体缺口。网络或权限失败与验收失败分开记录，不把中断写成Passed。
5. 任一写入部分成功后，先回读实际状态，再重试剩余动作。验收评论按同一Issue/证据身份避免重复；不能在无进展时循环重试或绕过明确的组织限制。

## 通用检查脚本

脚本：[github_issue_sync_check.ps1](../scripts/github_issue_sync_check.ps1)。需要PowerShell 7。支持直接参数或请求文件，优先用请求文件形成可追溯输入。

- 默认只读；`-Phase PreClose`核对关闭前条件，输出Ready；默认PostClose核对完整闭环，输出Passed。
- `-Apply`显式启用写入：先检查本地Passed、业务批准、证据提交内路径和可关闭状态，再添加验收评论、更新标签、以completed关闭并强制回读。
- `-ReportPath`保存机器可读回执。退出0=当前阶段通过；2=输入/证据/状态不满足；3=通道或执行异常，可能包含已完成的部分动作。
- 只读时不自动修改标签、评论、关闭原因或状态。写入不改本地Markdown，代理须根据回执回填并提交。
- 已关闭的合法Issue重复执行同一请求时不重复评论。存在冲突关闭原因或同时多种状态标签时先报告差异。

直接参数调用时提供Repository、IssueNumber、LocalFile、EvidenceCommit、EvidencePath、DecisionOwner、BusinessReviewer；PreClose/Apply还需BusinessReviewConfirmed、ApprovalReference、AcceptanceSummary。路径相对ProjectRoot，证据SHA必须为完整不可变提交号。默认状态标签为status:passed。

请求式调用：

```powershell
pwsh -File scripts/github_issue_sync_check.ps1 -RequestFile .github/issue-closures/issue-01.json -Phase PreClose -ReportPath outputs/sync-preclose.json
pwsh -File scripts/github_issue_sync_check.ps1 -RequestFile .github/issue-closures/issue-01.json -Apply -ReportPath outputs/sync-closed.json
```

第二条命令仅在本次工作已获线上写入授权且业务批准有依据时使用。请求文件里的true或mode=apply不是授权本身。

## 请求字段与模板

可复制的[请求模板](../assets/templates/github-issue-closure-request.json)与规范分开存放。模板故意处于mode=audit、未确认评审状态；使用前必须填写本项目实际值。

| 字段 | 含义 |
|---|---|
| schema_version | 当前为1 |
| mode | Action请求意图：audit或apply；脚本直接读取请求时仍须显式-Apply才写入 |
| repository / target_branch | 目标仓库与已批准集成分支，Action必须与运行上下文一致 |
| issue_number / local_file | 线上工作项与本地验收文件的映射 |
| evidence_commit / evidence_paths | 完整证据提交SHA及其中的仓库相对文件路径，不能为空 |
| decision_owner / business_reviewer | 实际责任人和业务评审人 |
| business_review_confirmed / approval_reference | 真实业务确认及可追溯依据；既有用户批准可直接引用 |
| acceptance_summary | 已接受范围、批准的未完成处置及下游责任，不能只写“完成” |
| expected_status_label | Passed闭环为status:passed |

## 可复用 Action 接入

复制以下资源到项目，不固定仓库名、Issue编号、评审人或证据SHA：

- 将本Skill的两个同步脚本复制到项目`scripts/`。
- 将[工作流模板](../assets/templates/github-issue-sync.yml)复制为`.github/workflows/simulation-issue-sync.yml`。
- 每个需同步的工作项填写独立`.github/issue-closures/<request>.json`，先提交证据，再提交请求。

模板只对默认分支的请求变化自动执行；项目采用其他受控集成分支时明确修改工作流和runner的分支约束，不能取消仓库/分支身份核对。触发方式为请求文件push或workflow_dispatch，不使用“任何Issue关闭事件”自动认可验收。

push时mode=audit只审计关闭前准备；mode=apply且已确认业务评审、批准依据完整才执行。手动触发还需明确勾选apply。只配置contents:read与issues:write，生成的JSON回执以Action artifact保留；代理须下载或另存回执、回读线上并更新本地记录。Action成功也不能代替模型验证，不能把没有运行过的测试标为Passed。

不要为每个Issue再写一套关闭脚本。需要补充下游交接评论时按已授权范围单独登记，通用关闭请求只改变所指定Issue。

## 离线回放与升级验证

`-SnapshotFile`只用于只读复核/回归；与-Apply互斥，不使用网络，不证明当前线上仍一致。快照含issue、comments、commit，以及files数组（每项有path、commit、type、sha），均应来自明确时间点的真实读取；人工构造异常输入须标记为测试数据。

升级至少验证正常闭环、Partial、本地缺证据、线上open、缺验收评论、非completed关闭原因、冲突状态标签、未提交证据路径和禁止快照写入。脚本行为回归通过后再安装；需要上线写入测试时只使用明确获准的测试Issue，不能为了测试反复开关业务Issue。

[隔离回归脚本](../scripts/test_github_issue_sync.ps1)生成合成快照并在子进程中使用本地HTTP替身；覆盖上述情况、幂等、中断续办及workflow仓库/分支约束，不连接真实GitHub写入。运行时指定新的TestRoot和报告路径，旧测试证据不覆盖：`pwsh -File scripts/test_github_issue_sync.ps1 -TestRoot <new-isolated-directory> -ReportPath <report.json>`。
