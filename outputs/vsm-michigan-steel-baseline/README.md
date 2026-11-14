# Michigan Steel VSM 仿真项目

本项目按 Factory Physics for Managers 第 9 章的 Michigan Steel VSM 案例，逐步建立 Simio 模型并验证每次复杂度增量。案例 PDF 是事实和作者方法的来源；Skill、项目路线和 Issue 文件规定本项目的建模、验证与协作记录方式。

## 当前交接状态

- 模型快照：`VSM_V0.7_InitialWIPTable`
- 当前迭代：`I1`；路线环节见 [`01.md`](01.md)，核心 Issue 记录见 [`iterations/I1/`](iterations/I1/)
- 阶段门：`HOLD`
- 已验证范围：20 件计算批次表达、初始 WIP 17,130 件的装载、W03-R 10 件尾批、W05 初始成品暂存、加权交付统计、确定性完整运行的件数与实体数守恒；V0.7 已保存并完成关闭重开回归
- 未通过范围：正式 B0/B1/B2 基线、物理托盘组批语义、班次日历、随机故障、换型、需求履约及 Fill Rate；20 件计算批次对批内时序指标的等价性仍未证明
- 当前模型包、输入哈希、运行证据和未关闭事项：[`vsm-v07-20piece-entity-evidence.md`](vsm-v07-20piece-entity-evidence.md)

保存包中的旧实验场景元数据和对象说明仍记录为 `DQ-005`，需在后续维护中统一。V0.7 关闭重开后的原生回归已完成：诊断 0 errors、运行警告 0，完整运行件数与实体数均守恒。模型仍是受控候选快照，不能标为正式基线；20 件计算批次与逐件实体模型的细节等价性尚未验证。

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
| V0.6 逐件参照、V0.7 20 件计算批次和回滚快照 | [`models/`](models/)、[`snapshots/`](snapshots/) |
| 通用规划 Skill | [`../../skills/supply-chain-simulation-planning/SKILL.md`](../../skills/supply-chain-simulation-planning/SKILL.md) |

## GitHub 协作状态

项目规划和 I1 的 01–14 工作包 Markdown 已整理为仓库内容。它们尚未绑定 GitHub 上的实际 Issue 编号、Pull Request 或 Milestone；绑定后应在路线文件和关联 Issue 中补记链接。目标远端为 [`wyfchina/FactoryPhyVsm`](https://github.com/wyfchina/FactoryPhyVsm)，分支 `codex/vsm-v04-github-ready` 已推送。线上 Issue、Pull Request 和 Milestone 尚未创建。

每项后续模型变更应关联 Issue，记录目标、依赖、设计、验收条件、预期和实际结果以及证据路径。每次运行都须绑定模型文件哈希、输入快照和 Simio 版本；不能用提交、上传或文件名代替阶段验收。
