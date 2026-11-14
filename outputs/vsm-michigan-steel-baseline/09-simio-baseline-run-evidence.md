# Simio 基线运行证据

## V0.11 当前 MCP 候选：初始 WIP cohort

V0.11 继承 V0.10 公共模型骨架，在 `VSM_InitializeWIP` 中启用
`CopyOverTableRowReferences=True`，并把每个初始 WIP 计算实体的
`VSM_ProductionBatchState` 写为 `WIP:<WIPRecordId>`。活动模型 `/Project/Model`
的根属性为 `VSM_ModelVersion=VSM_V0.11_InitialWIPCohortCandidate`、
`VSM_BaselineStage=INITIAL_FLOW_CANDIDATE`。用户已另存独立保存包
`models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx`，SHA-256 为
`D023F7420FF2E1FF21046A0E9481E64E3268CD7B2C7EC7F8D0532C9A606D6F52`。

### 复位态检查

在 `/Project/Model/Runtime/Objects/ModelEntity/DefaultEntity` 上执行 `Reset` 后，
仿真时间为 `0 h`，`Population.NumberInSystem=857`。运行时表达式读取到：

| 表达式 | 结果 |
|---|---|
| `Population.FirstItem.ModelEntity.VSM_ProductionBatchState` | `WIP:InitialWIP_W01_L` |
| `Population.FirstItem.ModelEntity.VSM_QuantityState` | `20` |
| `Population.LastItem.ModelEntity.VSM_ProductionBatchState` | `WIP:InitialWIP_W05_R` |
| `Population.LastItem.ModelEntity.VSM_ProductTypeState` | `Right` |
| `Population.LastItem.ModelEntity.VSM_QuantityState` | `20` |

上述结果证明 cohort 标签写入实体状态并可读；MCP 不能从实体表达式直接返回
`VSM_InitialWIPTable.WIPRecordId` 的表行对象，因此不能据此声称逐行动态账本已完成。

### 保存后确定性回归

运行设置为确定性、无预热、随机性关闭，`RunLength=306.6666667 h`。保存后的活动候选执行
`Reset → FastForward`，`get_diagnostics` 返回 `0 errors`，`get_run_status` 返回
`0 warnings`、`lastError=null`。

| 指标 | 结果 |
|---|---:|
| Left 生产释放 | 12,000 件 |
| Right 生产释放 | 6,400 件 |
| 总生产释放 | 18,400 件 |
| 加权 Shipping | 19,630 件 |
| 期末加权 WIP | 15,900 件 |
| 实体创建/销毁 | 1,777 / 982 |
| 期末实体 | 795 |
| 件数守恒 | `17,130 + 18,400 = 19,630 + 15,900` |
| Left 守恒 | `11,200 + 12,000 = 14,500 + 8,700` |
| Right 守恒 | `5,930 + 6,400 = 5,130 + 7,200` |

本节证据是“保存后活动会话回归”，尚未包含关闭 Simio 后重新打开 V0.11 文件的独立原生回归；因此 VSM-14 仍为 `Partial`。逐行 `WIPRecordId` cohort ledger、真实生产批次动态守恒、班次、换型、故障/维修、物理托盘和服务指标仍未完成。详见 [V0.11 cohort 证据](vsm-v11-initial-wip-cohort-evidence.md)。

## V0.10 当前 MCP 候选：公共模型骨架

V0.10 继承 V0.9 的产品分组审计和位置级加权 WIP 逻辑，本次只完成公共骨架的命名、说明和版本标识增量。活动模型 `/Project/Model` 的根属性为 `VSM_ModelVersion=VSM_V0.10_CommonSkeletonCandidate`、`VSM_BaselineStage=COMMON_SKELETON`。变更前的 V0.9 保存包 SHA-256 为 `49197D44DA482F97B6B06E4A47D97931875AF6C4DA639C684D6FF8794B5363A8`，快照见 `snapshots/VSM_MichiganSteel_V0.9_ProductGroupAuditCandidate.before-I1.4-issue05-skeleton.spfx`。用户已另存独立 V0.10 保存包 `models/VSM_MichiganSteel_V0.10_CommonSkeletonCandidate.spfx`，SHA-256 为 `B719029E9A04AD2DD2F93E0594C5C06BE79087DC2D62BC66B58DAD186FCC1CAF`；关闭/重开回归仍待完成。

### 骨架静态检查

- Facility 对象 20 个、节点 15 个、链接 11 条；普通生产链路使用 6 条业务命名 Connector，初始 WIP 使用 5 条业务命名 Connector。
- `Source_ProductionRelease`、5 个制造 Server、`Server_FG_Staging`、`Sink_Shipping`、`DefaultEntity` 和 `Transfer_InitialWIP` 均存在。
- 6 张 Data Table 可读取；`VSM_InitialWIPTable` 为 11 行，包含 `CurrentResource`、`BatchEntityCount` 和 `BatchUnitQuantity`；其余表行数分别为 Operation 6、Product 2、Inventory 6、Scenario 2、Reliability 5。
- `VSM_InitializeWIP`、`VSM_OnProductionRelease`、`VSM_OnShipment` 以及六个位置的 Entered/Exited 过程均可读取；初始 WIP、生产释放、位置审计和 Shipping 事件引用与模型契约一致。
- 公共 Output Statistic 覆盖生产释放、Shipping、位置 WIP、位置流入/流出和 Left/Right 分组；关键链接、实体和输出已补充中文职责说明。
- `get_diagnostics` 返回 `0 errors`。

### V0.10 当前候选回归

运行设置：确定性、无预热、随机性关闭，`RunLength=306.6666667 h`。MCP 重启后在完成 Issue 05 结构增量的活动候选上于 `2026-11-14 21:15:10 +08:00` 执行 `Reset → FastForward`，`get_run_status` 返回 `0 warnings`、`lastError=null`。

| 指标 | 结果 | 口径 |
|---|---:|---|
| Left 生产释放 | 12,000 件 | `LeftReleasedWorkpieces` |
| Right 生产释放 | 6,400 件 | `RightReleasedWorkpieces` |
| 总生产释放 | 18,400 件 | `ReleasedWorkpieces` |
| 加权 Shipping | 19,630 件 | `ShippedWorkpieces` |
| 期末加权 WIP | 15,900 件 | 六位置 Output Statistic 合计 |
| 实体创建/销毁 | 1,777 / 982 | `DefaultEntity.Population` |
| 实体守恒 | `1,777 - 982 = 795` | 期末实体 |
| Assembly #1 利用率 | 100% | ScheduledUtilization |
| Assembly #1 处理时间 | 306.6667 h | Total TimeProcessing |
| Assembly #1 输入缓冲峰值 | 432 个实体 | Maximum NumberInStation |
| 件数守恒 | `17,130 + 18,400 = 19,630 + 15,900` | 初始 WIP + 生产释放 = Shipping + 期末 WIP |

该回归与 V0.9 关键结果一致，说明 Issue 05 的命名、说明和版本标识增量没有改变流程、加工、批量或会计逻辑。V0.10 已另存并完成保存包身份核对；由于尚未关闭/重开，VSM-14 的持久化子项仍为 `Partial`。

## V0.9 当前 MCP 候选：L/R 产品分组审计

V0.9 在活动模型 `/Project/Model` 上继承 V0.8 的位置级加权 WIP 审计，并增加独立的 Left/Right 初始量、发运量和六个位置的当前 WIP 状态。模型根属性已更新为 `VSM_ModelVersion = VSM_V0.9_ProductGroupAuditCandidate`、`VSM_BaselineStage = PRODUCT_GROUP_AUDIT`。当前已形成独立保存包 `models/VSM_MichiganSteel_V0.9_ProductGroupAuditCandidate.spfx`，SHA-256 为 `49197D44DA482F97B6B06E4A47D97931875AF6C4DA639C684D6FF8794B5363A8`；V0.8 原文件已恢复为 `5B6EC5355F082755F45F3D308534E63C01F27EBB73779C09C138A88B88C1F0E4`。V0.9 尚未完成关闭、重新打开后的原生回归，因此 VSM-14 仍未关闭。

新增审计逻辑保持业务行为不变：

- `VSM_InitializeWIP` 在每个由 `VSM_InitialWIPTable` 行创建的计算实体上，按 `BatchUnitQuantity` 将该行件数累加到 `VSM_InitialLeftUnitCount` 或 `VSM_InitialRightUnitCount`；尾批仍按实际件数计量。
- `VSM_OnShipment` 按 `VSM_ProductTypeState` 将 `VSM_QuantityState` 独立累加到 `VSM_ShippedLeftUnitCount` 或 `VSM_ShippedRightUnitCount`。
- 六个 Server 的 Entered/Exited 过程分别维护 Left/Right 当前加权 WIP；16 个 Output Statistic 仅报告这些状态，不重新抽样，也不改变路由或处理时间。

运行设置：确定性、无预热、随机性关闭，`RunLength = 306.6666667 h`；Simio MCP `get_diagnostics` 返回 `0 errors`，`get_run_status` 返回 0 warnings。结果来自 MCP `get_statistics` 的 Interactive Run #0：

| 产品组 | 初始 WIP | 生产释放 | Shipping | 期末六位置 WIP | 守恒 |
|---|---:|---:|---:|---:|---|
| Left | 11,200 | 12,000 | 14,500 | 8,700 | `11,200 + 12,000 = 14,500 + 8,700` |
| Right | 5,930 | 6,400 | 5,130 | 7,200 | `5,930 + 6,400 = 5,130 + 7,200` |
| 合计 | 17,130 | 18,400 | 19,630 | 15,900 | `17,130 + 18,400 = 19,630 + 15,900` |

完整运行期末的 L/R 位置状态如下：

| 位置 | Left | Right | 合计 |
|---|---:|---:|---:|
| Stamping | 0 | 0 | 0 |
| Weld 1 | 0 | 0 | 0 |
| Weld 2 | 0 | 3,100 | 3,100 |
| Assembly 1 | 6,000 | 2,660 | 8,660 |
| Assembly 2 | 0 | 0 | 0 |
| FG staging | 2,700 | 1,440 | 4,140 |
| **合计** | **8,700** | **7,200** | **15,900** |

该结果关闭 VSM-16 的 **L/R 聚合守恒子集**，也验证 L/R 位置状态相加等于 V0.8 的位置总量。它没有关闭按 `WIPRecordId` 的初始记录 cohort 守恒，也没有把 `ProductionBatch` 追溯标签解释成真实生产批次；这两项仍保持 `Partial / HOLD`。

### V0.9 保存包与当前会话回归

V0.9 保存包已从用户保存后的活动候选中独立留存，V0.8 原文件通过匹配的 `.backup` 恢复。随后在当前 Simio 会话对 V0.9 候选执行了 `Reset → FastForward`，运行设置仍为确定性、无预热、`306.6666667 h`。本次回归结果为：诊断 `0 errors`、运行警告 `0`；加权 Shipping `19,630` 件；期末加权 WIP `15,900` 件；实体创建 `1,777`、销毁 `982`、期末 `795`；Left `11,200 + 12,000 = 14,500 + 8,700`，Right `5,930 + 6,400 = 5,130 + 7,200`。这确认保存包内容与当前活动候选的运行口径一致，但尚未证明关闭 Simio、重新打开该独立 V0.9 文件后仍能复现，因此不能把 VSM-14 标为 Passed。

## V0.8 当前 MCP 候选：位置级加权 WIP 审计

本节记录 V0.9 之前的 V0.8 活动候选证据。V0.8 的位置级审计结果已被 V0.9 继承；本节保留原运行边界和两终点差分证据，不能把它与 V0.9 的产品分组结果混写。

新增内容仅用于验证，不改变生产释放、加工时间、路由或实体权重：

- 六个位置状态：`VSM_StampingWIP`、`VSM_Weld1WIP`、`VSM_Weld2WIP`、`VSM_Assembly1WIP`、`VSM_Assembly2WIP`、`VSM_FGStagingWIP`，单位均为工件件数；每个 Server 的 `Entered` 过程加上 `ModelEntity.VSM_QuantityState`，`Exited` 过程减去同一数量。
- 六个 Output Statistic 记录上述状态的最终值；`Sink_Shipping.Entered` 仍由 `VSM_OnShipment` 记录加权发运。
- 过程 XML 已重读确认包含 `BeginStepID=2` 和 Assign 步骤；模型诊断为 0 errors。

### 位置审计运行结果

运行设置：确定性、无预热、随机性关闭；完整运行 `306.6666667 h`，另有初始化检查 `0.01 h`；两次运行均无运行错误或警告。

| 位置状态 | 0.01 h | 306.6666667 h | 独立解释 |
|---|---:|---:|---|
| Stamping | 9,180 | 0 | 生产释放实体已基本离开；完整运行无期末残留 |
| Weld 1 | 7,020 | 0 | 初始 7,000 + 已进入流量 - 已离开流量 |
| Weld 2 | 1,700 | 3,100 | 初始 1,700；完整运行期末保留 3,100 |
| Assembly 1 | 2,450 | 8,660 | 初始 2,450；完整运行期末保留 8,660 |
| Assembly 2 | 1,840 | 0 | 初始 1,840；完整运行期末已离开 |
| FG staging | 4,140 | 4,140 | W05 初始成品暂存，未自动发运 |
| **位置状态合计** | **26,330** | **15,900** | 与总创建/期末加权 WIP 对账 |

完整运行累计流量分别在 `0.01 h` 和 `306.6666667 h` 两个相同输入、随机关闭的确定性运行中读取。第二列流入/流出是完整运行累计值减去 `0.01 h` 运行累计值，因此代表这两个检查点间的流量增量：

| 位置 | `0.01 h` 期初状态 | 区间流入增量 | 区间流出增量 | 完整运行期末状态 | 平衡 |
|---|---:|---:|---:|---:|---:|
| Stamping | 9,180 | 9,200 | 18,380 | 0 | 9,180 + 9,200 - 18,380 = 0 |
| Weld 1 | 7,020 | 18,380 | 25,400 | 0 | 7,020 + 18,380 - 25,400 = 0 |
| Weld 2 | 1,700 | 25,400 | 24,000 | 3,100 | 1,700 + 25,400 - 24,000 = 3,100 |
| Assembly 1 | 2,450 | 24,000 | 17,790 | 8,660 | 2,450 + 24,000 - 17,790 = 8,660 |
| Assembly 2 | 1,840 | 17,790 | 19,630 | 0 | 1,840 + 17,790 - 19,630 = 0 |
| FG staging | 4,140 | 0 | 0 | 4,140 | 4,140 + 0 - 0 = 4,140 |

六个位置的区间平衡误差均为 0 件；末期位置和为 15,900 件，与全系统加权守恒相符。由于两个检查点分别通过重置运行获得，VSM-15 的证据范围限定为同一确定性输入下的两个运行终点差分，后续可再用同一次运行的中间快照扩展。

完整运行的独立总量结果仍为：初始 WIP `17,130` 件、生产释放 `18,400` 件、Shipping `19,630` 件、期末位置状态合计 `15,900` 件；`17,130 + 18,400 = 19,630 + 15,900 = 35,530`。实体数为 `1,777 - 982 = 795`，诊断 0 errors、运行警告 0。

按完整运行末期的审计状态，位置结果为 Stamping `0`、Weld 1 `0`、Weld 2 `3,100`、Assembly 1 `8,660`、Assembly 2 `0`、FG staging `4,140`；合计 `15,900`。这些结果关闭 VSM-15 的“两终点差分平衡”子集，不等同于产品分组、批内时序或逐件等价性确认。

### V0.8 运行边界

本次验证只证明位置状态的进入/离开审计在初始化检查点和完整运行终点可闭合。尚未完成用户保存后的关闭/重开回归、L/R 产品分组守恒、真实生产批次语义、班次、换型、故障/维修、Fill Rate、V0.6 逐件等价性和作者结果对照。

## V0.7 当前候选：关闭/重开后的原生回归

用户已确认 `VSM_V0.7_InitialWIPTable.spfx` 已保存、关闭、重新打开并完成原生回归。重载后的当前 MCP 状态为：模型版本 `VSM_V0.7_InitialWIPTable`，诊断 `0 errors`，运行警告 `0`，确定性运行长度 `306.6666667 h`，无预热。当前证据详见 [V0.7 20 件实体证据](vsm-v07-20piece-entity-evidence.md) 和 [V0.7 交接清单](release-manifest-v0.7.md)。

V0.7 回归结果为：17,130 件初始 WIP / 857 个实体，18,400 件生产释放 / 920 个实体，加权 Shipping 19,630 件，期末加权 WIP 15,900 件，期末实体 795 个；件数守恒为 `17,130 + 18,400 = 19,630 + 15,900 = 35,530`，实体数守恒为 `1,777 - 982 = 795`。该结果确认 V0.7 的计算批次表达、加权统计和持久化回归，不等同于正式 B0/B1，也不证明与 V0.6 逐件模型的详细动态等价。

以下 V0.4 运行内容保留为历史逐件原型证据；其中“原生关闭、重开和回归待完成”只适用于 V0.4，不适用于已完成重载回归的 V0.7。

## V0.4 历史模型身份

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

### V0.4 历史版本身份与持久化差异

现有 `.spfx` 快照路径为 `snapshots/VSM_MichiganSteel_V0.1_SourceBaseline_pre-I1.4-WIP.spfx`，是保留的回滚点。V0.4 候选保存包已完成包内 XML 只读核验，但未完成其自身的原生关闭重开回归；V0.4 已由 V0.6/V0.7 演进链保留为历史参照。实验场景的旧 V0.3 元数据尚未统一，不能把 V0.4 称为正式交接版本。

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

上述是保存包内容的只读核验，证明 V0.4 的关键结构已写入磁盘。V0.4 的原生关闭、重新打开和最小回归未完成，因此本历史项状态为“保存包已核验，重载回归待完成”；该状态不应外推到已完成 V0.7 重载回归的当前候选。实验场景和对象说明的旧版本元数据仍记录为 DQ-005。

## V0.4 历史原生诊断和运行状态

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

### 早期 18,400 件结构运行（历史，模型版本无法追溯）

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

### V0.9 Issue 04 结构机制确定性回归

| 项目 | 结果 | 口径/证据 |
|---|---:|---|
| 活动模型 | `VSM_V0.9_ProductGroupAuditCandidate` | `/Project/Model` 根属性；候选文件 SHA-256 `49197D44DA482F97B6B06E4A47D97931875AF6C4DA639C684D6FF8794B5363A8` |
| MCP/Simio | Simio `20.297.56736.0` | Desktop Interactive MCP |
| 运行设置 | 306.6666667 h；无预热；随机关闭 | `RunLength`; `FreezePeriodHours=0`; `DisableRandomness=true` |
| 生产源输出 | 920 个计算实体 / 18,400 件 | 每实体 20 件；两个周期到达，每批 460 个实体 |
| 产品释放 | L=12,000；R=6,400 件 | VSM weighted release statistics |
| Shipping | 19,630 件 | VSM weighted shipment statistic；含初始 WIP 与本期生产 |
| 期末加权 WIP | 15,900 件 | Weld #2=3,100；Assembly #1=8,660；FG staging=4,140，其余位置=0 |
| 件数守恒 | `17,130+18,400=19,630+15,900=35,530` | 初始 WIP + 生产释放 = Shipping + 期末 WIP |
| 实体守恒 | `1,777-982=795` | 创建实体 - 销毁实体 = 期末实体 |
| Assembly #1 | 100% 窗口忙碌；处理 306.6667 h；输入缓冲累计进入 1,323 个实体，峰值在站 432 个实体 | 原生 Resource/Queue statistics：`Total NumberEntered=1323`；`Maximum NumberInStation=432`；解析名义负荷 `62/60=103.33%` 单独保留 |
| 诊断/警告 | 0 errors / 0 warnings | `get_diagnostics`; `get_run_status` |
| 运行时间 | `2026-11-14 20:57:54–20:57:55 +08:00` | MCP 重启后新一轮 `Reset → FastForward`；`lastStartedUtc` / `lastCompletedUtc` |

`VSM_OnProductionRelease` 的 `TriggeringEventName` 为 `Output@Source_ProductionRelease.Entered`，其过程每次将 `VSM_ReleaseSequence` 加 20 并更新 L/R 件数状态。本次 Source 配置是每 153.3333 h 到达 460 个 20 件计算实体、共两次到达；它不是旧结构运行中每 60 秒创建一个单件实体的配置。该回归用于 Issue 04 的机制合同检查，不追认旧运行的版本身份，也不作为逐件动态等价性或正式 B0/B1 证据。

MCP 重启后再次执行同一确定性回归，活动模型、运行设置、诊断和关键统计均复现：`0 errors`、`0 warnings`，18,400 件生产释放，19,630 件 Shipping，15,900 件期末加权 WIP，实体 `1,777 - 982 = 795`，Assembly #1 资源处理时间 `306.6667 h`、输入缓冲峰值在站 `432` 个实体。该结果确认 Simio MCP 的原生运行接口可用；它仍不替代 V0.9 独立文件的关闭/重新打开回归。

## 早期结构运行结果解释（历史，模型版本无法追溯）

以下结果只描述上文“早期 18,400 件结构运行”，其模型版本无法追溯，不归属于 V0.3、V0.4 或 V0.9。Issue 04 的关闭依据是 V0.9 表中版本身份明确的当前候选原生回归；以下旧运行数字不与 V0.9 指标拼接。

1. 生产源按 60 秒节拍创建 18,400 个实体。
2. 五道工序按现有连接顺序传递实体。
3. 在 306.6667 小时边界内，系统无法发运全部 18,400 件；596 件仍在线内。
4. Assembly #1 形成主要积压，输入缓冲峰值为 594 件，说明 62 秒加工时间相对 60 秒节拍的能力压力在模型中出现。
5. 运行统计把资源利用率上限表现为约 100%；因此不能用该统计值直接表达 103.33%。103.33% 必须继续保留为解析能力边界。
6. 释放事件过程对每个源输出实体执行一次，最终序号为 18,400；这验证了创建/释放事件挂接。L/R 总数 12,000/6,400 由释放公式和 18,400 个事件独立核算得到；尚未由实验响应直接读取累计状态。

V0.4 新增证据仅支持初始 WIP Source 数量、总实体守恒和 W05 初始成品暂存边界。V0.7 已在重载后复核为 0 warnings；V0.4 的高实体数量警告仍作为历史技术提示保留，不能替代 V0.7 的当前运行证据。

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

本节仅描述 V0.4 历史状态。V0.4 当时通过 Simio Desktop Interactive MCP 修改活动模型并完成运行，但 MCP 会话没有提供保存/另存为 `.spfx` 的接口；因此当时要求用户另存并重新加载。当前 V0.7 已由用户保存、关闭、重新打开并完成原生回归，当前交接文件为：

`VSM_V0.7_InitialWIPTable.spfx`

V0.4 的历史运行证据不能替代 V0.7 的当前回归证据；V0.7 的回归结果以本文件顶部、`vsm-v07-20piece-entity-evidence.md` 和 `release-manifest-v0.7.md` 为准。
