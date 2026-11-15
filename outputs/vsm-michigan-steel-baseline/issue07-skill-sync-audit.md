# Issue 07 闭环同步与 Skill 实测

日期：2026-11-15。关联：[GitHub #7](https://github.com/wyfchina/FactoryPhyVsm/issues/7)。本记录检验同步结果及现有通用检查规则，不修改 Skill、模型或已关闭 Issue。

## 结论与适用范围

本次 #7 的线上同步与验收链通过。通用同步能力为部分通过：已安装 Skill 能要求代理启动检查，但本地脚本在当前环境不能直接读取 GitHub；Connector 缺少写入权限；最终通过新增的项目专用 Action 完成闭环。该 Action 是针对 #7 的一次实现，不等于 Skill 已提供所有 Issue 都可复用的自动化。

另以真实线上快照对已安装通用脚本做8项只读重放，5项符合预期、3项漏检。该结果评价脚本检查能力；本次真实 #7 没有这3种异常，不影响其已完成的验收。

## 1. 本次同步是否实际触发

| 检查 | 实际证据 | 结论 |
|---|---|---|
| GitHub 管理已启用 | 01-project-baseline.md 的 github_management: enabled、仓库和#7映射 | 满足触发前提 |
| 本地规范验收及Wu评审 | I1/07：Passed，Decision owner / Business reviewer均为Wu，用户明确授权闭环 | 满足验收与写入前提 |
| 证据先提交 | f821e0044453146a4eff350307bcc4240f5552c7，重新在线读取确认存在 | 通过 |
| 关闭前运行同步脚本 | 原始诊断记录退出1，缺少gh/GITHUB_TOKEN | 已启动，但原生通道未完成 |
| Connector备用通道 | 读取成功，写评论返回403 | 写入通道不可用 |
| Action真正执行 | [运行43656517136](https://github.com/wyfchina/FactoryPhyVsm/actions/runs/43656517136)：event=push、completed/success | 通过 |
| 线上验收评论 | [评论6886336335](https://github.com/wyfchina/FactoryPhyVsm/issues/7#issuecomment-6886336335)包含证据SHA、范围和Wu评审 | 通过 |
| 关闭状态与标签 | 本轮重新读取：closed/completed、status:passed，已无status:partial | 通过 |
| 本地回填与推送 | I1/07为GitHub sync: Closed；远端提交dd535d66d57598d73c74fee338761d598f3d65ed与本地一致（本次审计前） | 通过 |
| 下游责任未被错误关闭 | #6/#8/#9仍open/status:partial，具备承接评论；I1与B0/B1仍HOLD | 通过 |

原始闭环证据见 [issue07-closure-evidence.md](issue07-closure-evidence.md)和[线上回读](evidence/issue07-closure-readback-20261115.json)。

时间顺序是：本地Passed与业务评审 → 提交证据 → 启动同步检查 → 写验收评论及标签 → GitHub completed关闭 → 回读与本地回填。它不是“在GitHub已经关闭后才启动验收”。

## 2. 实际触发方式的边界

- Skill中的“触发”是代理执行工作时必须遵守的规则，不是常驻后台监听器。单独把Markdown改成Passed不会自行运行程序。
- 当前仓库Action由向codex/vsm-v04-github-ready推送指定的工作流、脚本或#7闭环请求文件触发；没有监听所有Issue的closed事件。
- 当前Action与脚本固定了仓库、分支、#7、证据SHA和#6/#8/#9承接目标。因此后续Issue不能直接套用本次请求，也不能据此宣称已具备通用自动闭环能力。

## 3. 通用同步脚本只读重放

对象：已安装的supply-chain-simulation-planning/scripts/github_issue_sync_check.ps1。

SHA-256：A9956CD528D690EB010A24A232EF9F0E4B01163DEE1CAFAAD444BD179D91B311。

方法：本轮重新通过Connector读取真实#7、评论和证据提交，保留真实内容；把标签转换为脚本期望的REST对象格式。在临时测试进程中提供仅允许已登记读取端点的本地响应适配器，调用原脚本的只读模式，不传Apply，不修改线上数据。每项异常测试只改变一项输入。退出0表示通过，退出2表示状态漂移或前提不完整。此重放不证明本机gh登录或Connector写入权限已恢复。

| 用例 | 预期行为 | 实际行为 | 检验结果 |
|---|---|---|---|
| 真实有效快照 | 通过，退出0 | 退出0 | 符合 |
| 本地状态改为Partial | 拒绝，退出2 | 退出2 | 符合 |
| 本地证据路径不存在 | 拒绝，退出2 | 退出2 | 符合 |
| 线上状态改为open | 拒绝，退出2 | 退出2 | 符合 |
| 删除验收评论 | 拒绝，退出2 | 退出2 | 符合 |
| closed但原因为not_planned | 拒绝，退出2 | 退出0 | 漏检 |
| status:passed与status:partial并存 | 拒绝，退出2 | 退出0 | 漏检 |
| 指定仅本地存在、未提交的证据文件 | 拒绝，退出2 | 退出0 | 漏检 |

原因由源码复核：目前只检查state=closed，没有检查state_reason=completed；只检查包含status:passed，没有排除冲突状态标签；证据路径只做本地存在性检查，远程只确认提交本身存在，没有核对路径确实位于该提交。

原始逐项输出见 [issue07-skill-sync-replay-results-20261115.json](evidence/issue07-skill-sync-replay-results-20261115.json)。这些是审计测试结果，不是仿真运行结果。

## 4. Skill副本一致性

| 文件 | 已安装版本 | 工作区skills目录副本 |
|---|---|---|
| SKILL.md | 包含闭环前必须启动同步检查的规则 | 内容不同，尚无该检查入口 |
| references/github-project-governance.md | 包含GitHub同步状态机、检查清单及Connector备选要求 | 内容不同，缺少该新增同步章节 |
| scripts/github_issue_sync_check.ps1 | 存在，已执行并参与本次测试 | 不存在 |

本次实际使用的是已安装版本；不能把工作区旧副本当作相同版本分发。以上比较区分了真实内容差异，不仅依据换行符或哈希差异判断。

## 5. 后续升级建议

1. 补齐通用脚本的completed原因、互斥状态标签及证据提交内路径核对，并保留上述异常回归用例。
2. 把当前#7专用Action提炼为参数化请求与通用校验；保留明确批准、权限最小化、幂等和事后回读要求。不能用“关闭事件发生”替代验收批准。
3. 在Skill中规定可用通道的检查和切换顺序、失败记录及最终状态回填，避免每次临时编写专用动作。
4. 明确Skill维护源、安装位置和版本核验方式，同步工作区副本与已安装版本。

本轮仅记录实测与建议，没有执行上述规范升级，也未重新开关#7或改动Simio。
