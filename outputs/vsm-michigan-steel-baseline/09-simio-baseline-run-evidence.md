# Simio 基线运行证据

## 模型身份

- 活动模型：`/Project/Model`
- Simio 版本：`20.297.56736.0`
- MCP 活动模型描述：Michigan Steel 初始 WIP 原型；模型根属性 `VSM_ModelVersion = VSM_V0.4_InitialWIPPrototype`、`VSM_BaselineStage = INITIAL_WIP_PROTOTYPE`。Simio 窗口标题和属性面板也显示 V0.4；但已保存实验场景仍覆盖为 V0.3，需在原生重载和场景回归中统一确认。
- 场景：`Exp_VSM_Baseline / VSM_Original_Structural`
- 运行边界：`RunLength = 306.6666667` 小时，`FreezePeriodHours = 0`
- 随机性：关闭（确定性结构检查）
- 历史结构运行输入源：18,400 件，单件到达间隔 60 秒，实体/到达=1；V0.4 当前采用周期生产批次 Source 并额外创建初始 WIP，见下方对应运行记录
- 故障：Stamping 和 S. Weld #2 在本次 SOURCE_BASELINE 结构运行中设为 `No Failures`
- 释放事件过程：`/Project/Model/Processes/VSM_OnProductionRelease`
- I1 增量：`ModelEntity` 增加 `VSM_ProductTypeState`、`VSM_TrayIDState`、`VSM_ProductionBatchState`、`VSM_ReleaseTimeHoursState`；释放过程按每个 9,200 件周期先释放 L=6,000、再释放 R=3,200，写入产品类型和批次标签，并按每 20 件生成候选托盘号。候选号不代表实际托盘组批。
- I1 增量：新增全局累计状态 `VSM_LeftReleasedCount`、`VSM_RightReleasedCount`，并接入释放过程。状态描述已补充单位、初始化和更新时点；实验响应已登记，但当前 Simio 实验返回空观测，尚不能把它作为直接运行计数证据。
- I1 增量：增加 9 个初始 WIP Source，将 `data/wip-initial.csv` 中有件数的五个位置装入 17,130 件实体；W03 保留 1,600 L + 850 R，不生成历史托盘身份。增加 `Server_FG_Staging` 暂存 W05 的 4,140 件初始成品，并设置 `Transfer-Out Condition = 0`，避免缺少发运规则时自动进入 Shipping。
- 释放事件验证响应：`ReleaseSequence_Final = VSM_ReleaseSequence`
- 阶段映射：`INITIAL_WIP_PROTOTYPE`；不是正式 `B0`、`B1` 或 `B2`

### 版本身份与持久化差异

现有 `.spfx` 快照路径为 `snapshots/VSM_MichiganSteel_V0.1_SourceBaseline_pre-I1.4-WIP.spfx`，是保留的回滚点。V0.4 候选保存包已存在并完成包内 XML 只读核验；以下运行证据仍需在原生关闭重开后回归。实验场景的旧 V0.3 元数据尚未统一，故不能把当前包称为版本身份完全一致的正式交接版本。

### V0.4 保存包只读核验

用户保存的候选文件已定位并读取：

- 原始文件：用户保存的 V0.4 模型文件
- 仓库交接副本：`models/VSM_MichiganSteel_V0.4_InitialWIPPrototype.spfx`
- 文件大小：`168,683` bytes；最后修改时间：`2026-11-13 16:34:34`
- SHA-256：`62C92C641BEF7FB200663C13A9DF4BBCB543779E2A2CA9C09405D48A03114868`
- `Project.xml` 中存在 `VSM_ModelVersion=VSM_V0.4_InitialWIPPrototype`、`VSM_BaselineStage=INITIAL_WIP_PROTOTYPE` 和已接受的 `VSM_InitialWIPRule`。
- `Models/Model/*.xml` 中存在 `Source_Initial_W01_L/R`、`W02_L/R`、`W03_L/R`、`W04_L/R`、`W05_L/R`，以及 `Server_FG_Staging`；保存包内的 `InitialNumberEntities` 与输入快照一致，W03-R 为 850。
- `Server_FG_Staging` 保存为 `ProcessingTime=0`、`TransferOutConstraintsType=Custom Condition`、`TransferOutCondition=0`。
- 保存包的 `Exp_VSM_Baseline / VSM_Original_Structural` 场景属性仍是 `VSM_V0.3_ReleaseBatchPrototype` / `SOURCE_BASELINE_RELEASE_BATCH_PROTOTYPE`，与项目根属性 V0.4 不一致；该场景身份应在下一次模型维护中统一后再作为正式运行身份。
- `Source_Initial_W01_L` 的对象描述仍写“当前仅 1 件 L”，但保存参数为 `InitialNumberEntities=4600`；`ModelEntity` 的部分状态描述仍保留早期 Pending/候选托盘措辞。它们是维护元数据滞后，不改变当前读取到的运行参数，但必须在交接前修正。

上述是保存包内容的只读核验，证明 V0.4 的关键结构已写入磁盘。当前 Simio 窗口标题和属性也显示 V0.4。原生关闭、重新打开该文件并运行最小回归尚未完成，因此本项状态为“保存包已核验，重载回归待完成”；由于实验场景和对象说明仍有旧版本元数据，尚不能判为版本身份完全一致。

## 原生诊断和运行状态

- 运行前诊断：0 errors。
- 旧 V0.3 运行完成：无运行错误、无警告。初始 WIP V0.4 完整运行出现 1 条 `Model_HighNumberOfAgentsInSystem` 高实体数量警告（仿真时间 0）；诊断 0 errors、运行错误 0。该警告与一次性装入初始 WIP 后实体数超过 Simio 建议阈值有关，是技术规模提示，不是已发现的业务逻辑错误；需在保存/重载后的候选模型中复核。
- 运行结束后：Simio 不在运行模式，状态为空闲。

## 运行结果

### V0.4 初始 WIP 装载短运行

运行长度：`0.1 h`。各初始 Source 的统计创建数与输入快照一致：W01-L/R=4,600/2,400，W02-L/R=1,100/600，W03-L/R=1,600/850，W04-L/R=1,200/640，W05-L/R=2,700/1,440；合计 17,130。该运行另有 9,200 件生产释放，因此总创建为 26,330。`Server_FG_Staging` OutputBuffer 进入 4,140、离开 0；Shipping 收到 9 件。诊断 0 errors，运行错误 0，出现 1 条高实体数量技术警告。

### V0.4 初始 WIP 完整长度确定性运行

运行长度：`306.6666667 h`，无预热、关闭随机性。该运行按实体总量核对：

| 统计项 | 结果 | 口径 |
|---|---:|---|
| 初始 WIP 创建 | 17,130 | 九个位置/产品 Source 的 NumberCreated 总和 |
| 生产释放创建 | 18,400 | 两个 9,200 件周期 |
| 总创建 | 35,530 | 初始 WIP + 生产释放 |
| Shipping 接收/销毁 | 19,645 | `Sink_Shipping` 接收数 |
| 期末系统实体 | 15,885 | 35,530 - 19,645 |
| W05 暂存区 OutputBuffer 进入/离开 | 4,140 / 0 | 初始成品仍被暂存，未自动发运 |
| 运行错误 | 0 | Simio run status |
| 模型诊断 | 0 errors | Simio diagnostics |
| 运行警告 | 1 | 仿真时间 0 的高实体数量技术提示 |

数量守恒成立：`17,130 + 18,400 = 19,645 + 15,885`。该守恒是全系统实体总量守恒；它不表示位置级 WIP 动态、产品分组或托盘分组已经验证。

### V0.3 释放状态烟雾运行（历史）

在临时设置 `RunLength = 0.5` 小时、保持确定性随机设置后，快进运行结果如下：

| 统计项 | 结果 | 口径 |
|---|---:|---|
| 实体创建 | 31 | `DefaultEntity.Population.NumberCreated` |
| 实体销毁/发运 | 26 | `DefaultEntity.Population.NumberDestroyed` |
| 期末线内实体 | 5 | `31 - 26` |
| 运行错误/警告 | 0 / 0 | `get_run_status` |
| 模型诊断 | 0 errors | `get_diagnostics` |

该运行只验证释放过程可执行及实体守恒，不能证明产品比例已由运行统计确认，也不是 B0/B1 性能结果。运行长度设置已恢复为 306.6666667 小时。

### 早期 18,400 件结构运行（历史，版本归属待核实）

| 统计项 | 结果 | 口径 |
|---|---:|---|
| 实体创建 | 18,400 | `DefaultEntity.Population.NumberCreated` |
| 实体销毁/发运 | 17,804 | `DefaultEntity.Population.NumberDestroyed`；与 Shipping InputBuffer 进入数一致 |
| 期末线内实体 | 596 | 18,400 - 17,804，守恒检查通过 |
| Assembly #1 处理资源忙时 | 306.6428 h | `Server_Assembly1` Resource 的 Total TimeProcessing |
| Assembly #1 排班利用率 | 99.9922% | Simio 原生 `Capacity.ScheduledUtilization`；这是仿真统计值 |
| Assembly #1 名义需求负荷 | 103.33% | 独立解析值 `62 / 60`，不是本次仿真输出 |
| 创建事件释放序号 | 18,400 | Experiment 响应 `ReleaseSequence_Final`；由 `VSM_OnProductionRelease` 在 `Output@Source_ProductionRelease.Entered` 事件上递增 |
| 运行警告 | 0 | 提高 `DefaultEntity.Maximum Number In System Limit` 至 50,000 后的 `get_run_status` |
| 释放规则解析总数 | L=12,000；R=6,400 | 两次 9,200 件 Source 到达；每周期公式为序号余数 1–6,000=L、6,001–9,200=R；这是独立公式核算，不是运行响应 |
| L/R 实验响应 | 无有效观测 | `LeftReleased_Final`、`RightReleased_Final` 已登记但全局状态在实验响应中返回空观测，不能作为通过证据 |

## 结果解释

早期 18,400 件结构运行和 V0.3/V0.4 是不同模型状态；旧记录对其版本归属存在不一致，以下结论仅视为结构运行证据，不作 V0.4 版本追溯。该运行显示以下机制可执行：

1. 生产源按 60 秒节拍创建 18,400 个实体。
2. 五道工序按现有连接顺序传递实体。
3. 在 306.6667 小时边界内，系统无法发运全部 18,400 件；596 件仍在线内。
4. Assembly #1 形成主要积压，输入缓冲峰值为 594 件，说明 62 秒加工时间相对 60 秒节拍的能力压力在模型中出现。
5. 运行统计把资源利用率上限表现为约 100%；因此不能用该统计值直接表达 103.33%。103.33% 必须继续保留为解析能力边界。
6. 释放事件过程对每个源输出实体执行一次，最终序号为 18,400；这验证了创建/释放事件挂接。L/R 总数 12,000/6,400 由释放公式和 18,400 个事件独立核算得到；尚未由实验响应直接读取累计状态。

V0.4 新增证据仅支持初始 WIP Source 数量、总实体守恒和 W05 初始成品暂存边界。高实体数量警告应在后续保存/重载回归时复核；当前证据没有把技术警告当作零警告通过。

## 尚未覆盖的机制

旧版 306.6667 小时结构运行和 0.5 小时释放状态烟雾运行属于早期结构/释放状态；旧记录的模型版本标签尚有冲突。上文单独记录的 V0.4 完整长度运行含初始 WIP。不同版本结果不可合并为一个基线结果。当前 V0.4 仍是初始 WIP 原型，不应解释为已完成正式 B0 或 B1。

本次证据不支持以下结论：

- L/R 产品身份在释放过程中的赋值已编译并接入；本次尚无按产品类型的直接运行聚合结果；
- 两周过程批量的标签和释放顺序原型已接入，但真实生产批次释放点、产品切换和实体组批仍未实现；
- 20 件托盘转移尚未形成批量实体行为；
- 初始 WIP 在仿真开始后的全部位置动态迁移均与来源/产品分类守恒；
- 2 班工作日历和每班 27,600 秒尚未在 Server 日历中实现；
- 换型停机已经按 L/R 切换发生；
- 85%/80% 随机可用率已经在本次运行中验证；
- FillRate、L/R 周期时间和作者 14.8/12.8 日结果已经复现。

## 持久化限制

本次通过 Simio Desktop Interactive MCP 修改了活动模型并完成运行，但 MCP 会话没有提供保存/另存为 `.spfx` 的接口。本文件和模型属性记录了本次配置与证据；要形成可重新加载的模型版本，需要在 Simio Desktop 中将当前活动模型另存为：

`VSM_MichiganSteel_V0.4_InitialWIPPrototype.spfx`

另存后必须重新加载并重复诊断、运行和结果核对。当前运行证据不能替代保存/重载证据。
