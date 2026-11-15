# I1 / Issue 06：V0.12 实施与验收记录

记录日期：2026-11-15。责任人与业务评审人：Wu。线上工作项：[#6](https://github.com/wyfchina/FactoryPhyVsm/issues/6)。

## 当前结论

已在Simio活动模型`/Project/Model`完成`VSM_V0.12_FlowDemandLedgerCandidate`的实现和原生自测。用户已将其保存为`VSM_MichiganSteel_V0.12_FlowDemandLedgerCandidate.spfx`并关闭重开；保存包哈希为`73a98d963b756e485d6eb8b2a460954391047ed229290a823ceeb6ce9bfdd62f`。保存后的结构核查、诊断和输出逐行回读通过，**06技术验收范围通过；Wu最终业务验收未单独登记，GitHub #6 保持Open。**

本次是06实现验收候选，不是B0/B1通过，也不是作者结果复现。08已完成确定性验证与守恒范围闭环；09仍负责独立随机复制、可用率与置信区间、统计精度、聚合适用性及作者对照。原来的V0.11、历史发运19,630件记录及输入快照不被新机制结果覆盖。

## 实际运行与证据

Simio版本`21.298.57236.0`。正式配置保留初始WIP、零预热、20有效工作日；一天55,200秒，总计1,104,000秒。通过原生`Math.Epsilon`晚优先级等待同刻事件，通过`EndRun`在当前时刻所有事件完成后结束；**没有延长一个epsilon秒**。每日按整数有效秒计算绝对时刻，避免小时小数反复相乘导致到期事件稍晚而被误记迟交。

| 检查 | 预期和实际结果 | 直接证据（项目根目录相对路径） |
|---|---|---|
| D0旧行为回归 | 不启用新发运控制、换型/故障：发运19,630、期末15,900；15来源×6位置×21时点=1,890快照，来源平衡差全部0；无警告 | `evidence/issue06-d0-ledger-regression.json` |
| F01–F07 | 不同产品缺货、旧积压优先、初始成品/未完WIP区分、20拆10+10、due±1秒、恰好第20日末、零需求全部通过 | `evidence/issue06-F01-F07-summary.json`及各`issue06-F*.json` |
| M01换型 | L,L,R,R,L,L序列：首件0，同类0，产品变更两次；Stamping各1h、两焊接各0.167h，完成时长不重复计 | `evidence/issue06-M01-changeover-LLRRLL.json`、`issue06-mechanisms-summary.json` |
| M02故障续作 | 1h冻结作业，t=0.5故障、1.5修复、2.0完工；不是重做1h或重抽样 | `evidence/issue06-M02-failure-resume.json` |
| M03待机故障 | 无生产实体时，仍在t=0.5发生故障；验证累计含待机、维修期间不累计下次uptime | `evidence/issue06-M03-idle-failure.json` |
| M04 CT/批次/空实体退出 | 首实体制造CT=188×20/3600h；40件分10/10/20在t=2/3/3交付，批次Makespan=3h；创建2、销毁2、剩余0，六处资源占用均0 | `evidence/issue06-CT-batch-summary.json`、`issue06-M04-CT-complete-batch-partial-shipment.json` |
| M05观测中性 | 关闭盘点、工序和设备事件日志后，同复制的来源/需求/库存/分配/CT/批次/运行摘要逐行相同 | `evidence/issue06-observation-neutrality.json` |
| 复位与重复 | 复位后分配输出0行；同原生复制号重复运行，全部输出表逐行一致，无旧运行行混入 | `evidence/issue06-acceptance-summary.json`及两份`issue06-V012-*-rep20261114.json` |
| 保存/重载 | 用户已另存V0.12并关闭重开；模型身份、结构、诊断和输出逐行与保存前一致 | `evidence/issue06-persistence-readback.json`、`evidence/issue06-persistence-structure-readback.json` |

最终随机自测是一条固定随机轨迹，不能当成30复制或置信区间：

| 指标 | 实际值 |
|---|---:|
| 初始WIP / 新释放 | 17,130 / 18,400件 |
| 实际发运 / 期末剩余 | 18,400 / 17,130件 |
| 制造中未完工 / 可用成品 | 11,720 / 5,410件 |
| 到期需求 / 准时 / 迟交补交 / 未交 | 18,400 / 18,250 / 150 / 0件 |
| 本次轨迹按期件数满足率 | 99.1847826% |
| 原生创建 / 销毁 / 期末实体 | 1,777 / 920 / 857 |
| 来源、位置、产品、需求和库存分配平衡差 | 全部0件 |
| 原生诊断 / 运行警告 | 0 / 0 |

全部35,530件的去向均可追溯。期末仍被制造Server占用的容量对应合法未完工作；FG中271个未全分配实体保留，代表5,410件。不能把期末所有资源占用强行归零；空系统小例才应全部为0。

## 模型结构与操作

用户另存文件为`VSM_MichiganSteel_V0.12_FlowDemandLedgerCandidate.spfx`，位置为项目`models/`。保存由用户操作，代理没有调用Computer Use或任何保存接口。旧V0.11文件仍由历史快照保护，修改前快照在`snapshots/VSM_V0.11.user-save.pre-Issue06-20261115-094928.spfx`。历史受验收包的不同哈希不能替代当前V0.12用户文件。

Facility保留五个制造Server、现有节点/布局/符号。仅把Assembly2出口改接FG，再接Shipping。Source只负责普通生产释放；初始WIP继续由Data Table和Process创建。FG不承担制造产能，足够大容量用于保留尚未交完的库存实体。

Data有17张表，其中新增来源/需求台账和9张Output Table。9张输出分别为`VSM_Out_WIPSnapshot`、`VSM_Out_BatchSummary`、`VSM_Out_FlowTimes`、`VSM_Out_DemandFulfillment`、`VSM_Out_ShipmentAllocation`、`VSM_Out_FGInventory`、`VSM_Out_OperationLog`、`VSM_Out_ResourceEvents`、`VSM_Out_RunSummary`。中文描述和时间Unit Type保存在模型内。输出行冻结模型版本、原生复制号和随机开关；保存包SHA记录在输入快照manifest和保存重载回读证据中。

`VSM_SourceLedger`有11个期初来源加4张生产工单，State维护Received/Manufactured/Shipped、各位置In/Out。实体携带固定来源行号，位置流转直接寻址，不频繁搜索全表。每日/期末盘点将State冻结进Output Table。`VSM_Out_FGInventory`明确是**可变当前库存账本**，RemainingUnits随分配扣减；其他历史记录不会跟着当前余额重算。

成品按产品用FIFO链表和需求游标直接寻址。部分交付逐次写实际数量、交付时刻、FG等待和端到端时间。成品实体绑定自己的库存行；处理后先检查余额，再等待分配事件，余额0时由Server原生流程释放容量进入Sink。Sink只回收实体，不再次累计原始20件。这修复了实现自测中发现的“数量已清零而实体未退出”问题。

生产Source于t=0和552,000有效秒下达四张工单P1-L/P1-R/P2-L/P2-R，每期6,000/3,200，先L后R。第二期不等待第一期清空。初始WIP独立编号，不并入P1/P2。

新生产ManufacturingCT为Stamping进入到Assembly2离开，不含FG等待；初始WIP历史起点未知，只记从t0开始的剩余完成/交付时间。未制造完成样本在期末以Censored=1、完成时刻/完整CT=-1单列。完整批次Makespan只在全部计划件数实际交付后输出，否则为-1并标未完成。

已有`Exp_VSM_Baseline`作为历史对象保留，未升级为本次验收实验。复现实验配置应按09后续研究单独完成；本次证据来自MCP原生交互运行，不把旧实验默认响应当作V0.12统计结果。GUI外观未目视验收。

## 实现选择、单位与适用边界

加工引用`VSM_OperationTable`的时间与随机流。q件按`Math.SumOfSamples(Random.Exponential(mean,stream),q)`独立累加，开始时冻结；非q乘一次抽样。秒/分钟字段设置Time及相应单位，实体时间State以小时存储。换型仅前后L/R改变时发生，首件不加；Stamping1h，两焊接0.167h。两焊接表中历史10分钟已受控修正为0.167h=10.02分钟，保留原始来源/旧模型记录。

原生Server使用冻结加工+换型作为本次占用时长，二者分别输出，故障使剩余占用暂停/续作。原生设备Setup状态没有单列，不能从原生Busy统计直接分离纯加工与换型；精确分解用冻结日志。故障参数来自`VSM_ReliabilityTable`，Stamping MTTF=5.6667h、Weld2=4h，MTTR均1h，指数分布；开机有效工时含待机、排除维修。该表中旧原型MTTF=8h参数已替换，防止模型与台账冲突。

随机流映射PROC_P01–P05→101–105，FAIL_P01间隔/维修→201/202，FAIL_P03→211/212。MCP没有直接任意主种子设置接口；本次原生复现身份是`SpecificReplicationNumber=20261114`+固定流+Simio版本，**不能声称已设置任意主种子20261114**。07中的“主种子20261114、复制1–30”尚需09作平台映射和独立性验证；本次不据此输出30复制统计。该偏差显式登记，不静默修改已验收07契约。

20件计算实体不是物理托盘。无换型/故障的确定性整月参照：q20/q1的发运18,400、准时18,250、迟交150一致；新生产制造完成6,640/6,655件，件数加权已完成CT为249.6000/249.3544444h，差0.2455556h=14.7333分钟。期末未完工11,760/11,745件。**这证明数量和这组交期结果一致，同时证明制造时序并非完全等价。**随机、批量优化和临近交期场景仍需08灵敏度；不预先设定可接受精度。逐件参照触发>20,000实体提示，该已知容量提示保留在证据中，正式20件候选无警告。证据：`evidence/issue06-aggregation-comparison.json`及Q1/Q20原生记录。

取消订单、报废、返工、真实托盘内部拆并、日历非工作时间不是此次新增业务功能。若后续研究需要，须设计相应生命周期和异常路径，不把未实现功能标为测试Passed。

## 保存重载与闭环清单

1. 用户保存、关闭重开和启动MCP已完成。
2. 已核对包哈希、模型身份、15来源、40需求、9输出表、过程/表/State引用、单位和描述；诊断0；同复制原生重跑与保存前输出逐行一致。
3. Wu仍需确认06限定验收范围，并知悉20件聚合与逐件参照的已知时序差异；08/09责任保留。
4. 本轮先提交并推送实现、输入和回归证据，线上同步技术进度但保持#6为Open/status:partial；取得Wu业务评审后，再按闭环检查要求补充线上验收评论、状态更新和回读。技术回归不自动代表业务批准。

构建及最小测试位于项目根`scripts/vsm/`；原生修改记录在`evidence/issue06-native-operations.jsonl`，设计快照为`evidence/issue06-V012-native-design-manifest.json`。这些脚本按阶段使用，测试脚本会临时改变活动模型并在finally恢复，不应并行运行；不要将整个构建脚本再次应用到已完成候选。用户保存包是首要交付物，脚本是可追溯实现/测试资源。
