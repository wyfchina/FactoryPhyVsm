# I1 / Issue 06 闭环证据

记录日期：2026-11-15。线上工作项：[#6](https://github.com/wyfchina/FactoryPhyVsm/issues/6)。决策责任人和业务评审人：Wu。

## 验收结论

**Passed（V0.12 实施与确定性实现范围），可按 `completed` 关闭。**

本次关闭范围是 V0.12 初始 WIP、动态来源/需求/成品账本、9 张 Output Table、生产批次、ManufacturingCT/删失、方案 A 履约、换型、故障续作、保存重载和确定性实现回归。证据包括模型包 SHA-256 `73A98D963B756E485D6EB8B2A460954391047ED229290A823CEEB6CE9BFDD62F`、15 个来源在 6 个位置和 21 个时点的 1,890 条快照、来源/位置守恒差为 0、F01–F07 与机制小例、诊断 0 errors、运行警告 0，以及保存前后输出逐行一致。

## 明确延期

20 件计算实体和逐件参照的发运与按期需求结果一致，但制造完成量相差 15 件、已完成制造 CT 加权均值相差 14.7333 分钟，因此本次不声明批内制造时序等价。R1 独立随机复制、95% 置信区间、目标可用率观测、随机流/种子平台映射、20 件聚合适用性、作者结果对照和正式 B0/B1 阶段门转由 Issue 09/后续基线评审负责。

## 受控记录

- 详细实施记录：[iterations/I1/06.md](iterations/I1/06.md)
- V0.12 实施证据：[iterations/I1/06-V012-implementation-evidence.md](iterations/I1/06-V012-implementation-evidence.md)
- 确定性验证与守恒：[iterations/I1/08.md](iterations/I1/08.md)
- 验证计划：[05-verification-plan.md](05-verification-plan.md)
- 模型文件：[models/VSM_MichiganSteel_V0.12_FlowDemandLedgerCandidate.spfx](models/VSM_MichiganSteel_V0.12_FlowDemandLedgerCandidate.spfx)

关闭条件必须同时具备：证据提交、Wu 业务评审、线上验收评论、`status:passed` 标签、`closed/completed` 状态和闭环回读。线上 Issue 号仍是 `#6`；本地 `I1.4` 只表示路线位置。

## 线上回读

- 状态：`closed / completed`
- 标签：`建模`、`status:passed`；`status:partial` 已移除
- 验收评论：[issuecomment-6892979311](https://github.com/wyfchina/FactoryPhyVsm/issues/6#issuecomment-6892979311)
- 证据提交：`7191bba2a9ce64245b0210845ee584d3ccdabbfa`
- Action 提交：`0491239efdec8260b1526eb7a302593a97d83792`
- 机器可读回执：[issue06-closure-readback-20261115.json](evidence/issue06-closure-readback-20261115.json)
