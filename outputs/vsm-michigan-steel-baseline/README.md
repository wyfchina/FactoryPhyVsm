# Michigan Steel VSM 仿真项目

本项目按 Factory Physics for Managers 第 9 章的 Michigan Steel VSM 案例，逐步建立 Simio 模型并验证每次复杂度增量。案例 PDF 是事实和作者方法的来源；Skill、项目路线和 Issue 文件规定本项目的建模、验证与协作记录方式。

## 当前交接状态

- 模型快照：`VSM_V0.12_FlowDemandLedgerCandidate`
- 当前迭代：`I1`；路线环节见 [`01.md`](01.md)，核心 Issue 记录见 [`iterations/I1/`](iterations/I1/)
- 阶段门：`HOLD`
- 已验证范围：20 件计算批次表达、初始 WIP 17,130 件的装载、W03-R 10 件尾批、W05 初始成品需求驱动分配、来源/需求台账、换型/故障续作、确定性需求边界和保存重载回归；V0.12 保存包 SHA 与回读证据一致
- 未通过范围：正式 B0/B1/B2 基线、物理托盘组批语义、随机复制与置信区间、20 件计算批次对批内制造时序的等价性、作者结果对照
- 当前模型包、输入哈希、运行证据和未关闭事项：[`iterations/I1/06-V012-implementation-evidence.md`](iterations/I1/06-V012-implementation-evidence.md)

保存包中的旧实验场景元数据和对象说明仍记录为 `DQ-005`，需在后续维护中统一。V0.12 关闭重开后的原生回归已完成：诊断 0 errors、运行警告 0，输出表逐行一致，件数和来源/需求账本均守恒。模型仍是受控候选快照，不能标为正式 B0/B1；20 件计算批次与逐件实体模型的制造时序等价性尚未验证。

## 文件导航

| 内容 | 路径 |
|---|---|
| 项目路线与迭代到 Issue 的映射 | [`01.md`](01.md) |
| 项目范围和当前状态 | [`00-delivery-scope.md`](00-delivery-scope.md) |
| 项目模型基线定义 | [`01-project-baseline.md`](01-project-baseline.md) |
| 来源提取与解析核算 | [`02-source-extraction.md`](02-source-extraction.md)、[`04-expected-analytic-checks.md`](04-expected-analytic-checks.md) |
| 模型契约和验证计划 | [`03-model-contract.md`](03-model-contract.md)、[`05-verification-plan.md`](05-verification-plan.md) |
| 合规审查和 Simio 运行证据 | [`07-baseline-compliance-review.md`](07-baseline-compliance-review.md)、[`09-simio-baseline-run-evidence.md`](09-simio-baseline-run-evidence.md) |
| 输入数据与假设 | [`data/`](data/)、[`assumptions-register.csv`](assumptions-register.csv) |
| V0.6 逐件参照、V0.7 历史批次、V0.12 活动候选和回滚快照 | [`models/`](models/)、[`snapshots/`](snapshots/) |
| 通用规划 Skill | [`../../skills/supply-chain-simulation-planning/SKILL.md`](../../skills/supply-chain-simulation-planning/SKILL.md) |

## GitHub 协作状态

项目规划和 I1 的 01–14 工作包 Markdown 已整理为仓库内容。Issue 01–06 已有线上工作项；Issue 06 的技术证据已齐，当前同步为技术通过、业务评审待确认。20 件聚合适用性与统计研究转交 Issue 08，I1/B0/B1仍为HOLD。目标远端为 [`wyfchina/FactoryPhyVsm`](https://github.com/wyfchina/FactoryPhyVsm)，本地分支为 `codex/vsm-v04-github-ready`。

每项后续模型变更应关联 Issue，记录目标、依赖、设计、验收条件、预期和实际结果以及证据路径。每次运行都须绑定模型文件哈希、输入快照和 Simio 版本；不能用提交、上传或文件名代替阶段验收。
