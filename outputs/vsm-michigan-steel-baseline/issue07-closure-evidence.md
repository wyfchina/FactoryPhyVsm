# I1 / Issue 07 闭环证据：指标、统计与有效工时

- 验收日期：2026-11-15（项目记录日期；原始 MCP 文件保留实际 UTC 采集时间）。
- 工作项：[本地 I1/07](iterations/I1/07.md) / [GitHub #7](https://github.com/wyfchina/FactoryPhyVsm/issues/7)。
- 决策责任人、业务评审人：Wu。
- 本地验收：`Passed（指标与统计规范）`。GitHub 同步：`Closed`，已按“证据提交 → 评论与标签 → completed关闭 → 回读”完成。
- 本次没有修改内存模型、执行新仿真、保存或重载 `.spfx`；保存和重开仍由用户操作。

## 1. 批准记录与范围

Wu 已确认 ManufacturingCT 为 Stamping 进入至 Assembly #2 离开，不含成品等待；真实批次为 P1-L/P1-R/P2-L/P2-R；R1 为20工作日、无预热、保留初始WIP、随机开启、初始30个独立复制与95%置信区间；服务指标采用方案 A。

本轮用户进一步明确：“仿真是直接利用工作时间，非工作时间一律不计入仿真了，也就是不计入日历时间”，并授权“如果你确认是这样，现在你可以闭环07”。已登记为 A-022。用户确认与本次只读配置相符。

07 原始线上目标是固定指标和统计框架。此前本地又把模型挂钩与随机运行列作关闭要求；本次按用户授权对范围作明确处置：07 验收规范，原有未完成实现和执行要求由06/08/09具名承接，不删除要求，不补造运行通过。Git/线上原正文保留原范围记录。

## 2. 时间与需求算术检查（已执行）

| 检查 | 结果 | 判定 |
|---|---|---|
| 每日有效时间 | 2×27,600=55,200秒=15小时20分钟 | Passed |
| 20日研究期 | 1,104,000秒=18,400分钟=306小时40分钟 | Passed |
| 工作日换算 | 有效小时/(55,200/3,600)，不用 Simio 默认24小时/日 | 规范已冻结 |
| 需求行数和编号 | 20行、唯一工作日1–20 | Passed |
| 每日需求 | L600/R320，共920件 | Passed |
| 月需求汇总 | L12,000/R6,400，共18,400件 | Passed，整数误差0 |
| 精确到期秒 | 每行=55,200×工作日；末行1,104,000秒 | Passed，整数误差0 |
| 小时列与秒列 | 逐行换算误差小于1e-6秒；所有到期点不超过当前306.6666667h运行长度 | Passed |

需求输入见 [demand-due-calendar.csv](data/demand-due-calendar.csv)。整数秒是权威时点；运行长度的小数表示不替代同刻事件与终止优先级验证。非工作时间不插入时钟；工作时段内排队、换型、故障和维修依其机制消耗有效工时。

本轮还已执行变更文件的 `git diff --check`（通过）和 Markdown 相对链接检查（80个链接，缺失0）。这些检查验证文档完整性，不是原生仿真运行测试。

## 3. 当前模型只读核对（已执行）

原始证据：[issue07-timebase-readonly-20261115.json](evidence/issue07-timebase-readonly-20261115.json)。

| 项目 | 实际回读 | 解释 |
|---|---|---|
| Simio版本 | 21.298.57236.0 | 不以其他会话结果代替当前身份 |
| 活动模型 | /Project/Model；VSM_ModelVersion=VSM_V0.11_InitialWIPCohortCandidate | 描述仍含V0.10旧文字，以根属性识别 |
| 阶段 | INITIAL_FLOW_CANDIDATE | 不是B0/B1 |
| RunEndType / EndTimeValue | RunLength / 306.6666667小时 | 对应20有效工作日 |
| FreezePeriodHours | 0 | 无预热 |
| DisableRandomness | true | 当前为确定性候选配置；R1未执行 |
| 五制造工位 | Capacity Type=Fixed；Initial Capacity=1；Failure Type=No Failures | 未按真实班次日历启停，故障机制仍待实施 |
| 生产释放Source间隔 | 153.3333333小时 | 10有效工作日的静态参数；事件与批次账本仍待回归 |

显示 StartTime=2026-11-16T00:00:00、EndTime=2026-11-28T18:40:00 是界面日期锚点，不能解读为真实20工作日历。静态核对支持当前有效工时时间轴，不代替释放、需求和期末行为测试。

保存包：[VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx](models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx)。本轮重新计算 SHA-256 为 `D023F7420FF2E1FF21046A0E9481E64E3268CD7B2C7EC7F8D0532C9A606D6F52`，与原保存包一致；本轮不增加模型运行结论。

## 4. 规范验收与未完成责任

指标完整定义、件数权重/原生实体区分、初始WIP剩余时间、删失、需求分母、有限期、独立复制和Student-t置信区间见 [07规范](iterations/I1/07.md)及[方案A附件](iterations/I1/07-fill-rate-contract.md)。方案A正式响应名为 DueDateUnitFillRate，不预设与作者软件同名Fill Rate等价。

| 承接工作项 | 待完成内容 | 当前状态 |
|---|---|---|
| [06](iterations/I1/06.md) / [#6](https://github.com/wyfchina/FactoryPhyVsm/issues/6) | CT时间戳、初始WIP剩余CT、FG/需求/发运账本、真实生产批次、复制配置；保留既有换型/故障等待办 | In Progress / HOLD |
| [08](iterations/I1/08.md) / [#8](https://github.com/wyfchina/FactoryPhyVsm/issues/8) | F01–F07、同刻/终点边界、分层守恒、独立随机复制和CI、保存重载回归 | Partial / HOLD |
| [09](iterations/I1/09.md) / [#9](https://github.com/wyfchina/FactoryPhyVsm/issues/9) | 作者CT/服务算法/工作日与统计总体映射，以及正式B0/B1/B2状态评审 | Blocked / HOLD |

M09–M13 实现状态仍为 Not available 或 Defined/Pending；VSM-12/13/16/18 不因07验收自动通过。I1整体及正式B0/B1仍为HOLD。旧版Shipping=19,630和期末WIP=15,900只属于旧确定性边界，不能要求需求控制新版本强行复现。

## 5. GitHub 闭环同步

验收证据提交：`f821e0044453146a4eff350307bcc4240f5552c7`，已推送并通过 GitHub 回读确认。

执行过程：本地只读同步脚本已实际执行，因无gh/GITHUB_TOKEN退出1，见[原始诊断](evidence/issue07-sync-script-20261115.txt)。随后Connector读取成功，但对#7/#6/#8/#9添加评论均返回403 `Resource not accessible by integration`，该通道没有写入。这是Connector写入权限不足，不是验收失败。

改用仓库自有 GitHub Action 执行同一授权闭环清单：[限定工作流](../../.github/workflows/issue07-closure.yml)、[脚本](../../scripts/github/close-issue07.cjs)、[闭环请求](evidence/issue07-closure-request.json)。脚本只允许仓库所有者向指定分支推送触发；校验本地Passed、不可变证据祖先提交、Wu评审、V0.11哈希和需求表，然后添加幂等验收/交接评论，只关闭#7并回读closed/completed/status:passed；#6/#8/#9保持原状态。该Action只在这三个指定文件变化时触发，不随一般模型/文档提交自动验收其他Issue。

脚本语法与本地请求校验通过；提交 `fb7ea4627c96c1912132b2ff6ed65dc5a9f2e578` 推送后触发 [Action 43656517136](https://github.com/wyfchina/FactoryPhyVsm/actions/runs/43656517136)，状态 completed / success。Action自身完成关闭后回读，随后又通过Connector独立回读确认；[回读证据](evidence/issue07-closure-readback-20261115.json)保留完整验收/转交评论及核对清单。

| 同步项 | 最终核对 |
|---|---|
| #7 工作项状态 | closed / completed；关闭时间2026-11-15T00:06:36Z |
| #7 标签 | 建模、status:passed；status:partial已移除 |
| 验收评论 | [6886336335](https://github.com/wyfchina/FactoryPhyVsm/issues/7#issuecomment-6886336335)，含Wu评审、批准范围及不可变证据提交 |
| #6 实现转交 | [6886336518](https://github.com/wyfchina/FactoryPhyVsm/issues/6#issuecomment-6886336518)，工作项仍open/status:partial |
| #8 执行转交 | [6886336705](https://github.com/wyfchina/FactoryPhyVsm/issues/8#issuecomment-6886336705)，后续确定性验证范围已形成闭环；R1统计和聚合时序适用性继续由后续研究承接 |
| #9 作者对照转交 | [6886336909](https://github.com/wyfchina/FactoryPhyVsm/issues/9#issuecomment-6886336909)，工作项仍open/status:partial |
| 本地记录 | 07为Passed / GitHub sync: Closed，01路线与验证计划一致；I1与B0/B1仍HOLD |

以上只证明07自身已按批准范围闭环；不代表模型挂钩、小例、随机性能、保存重载或作者结果复现通过。本轮未修改Simio，无需用户另存模型。
