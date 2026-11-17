# Michigan Steel VSM 仿真项目

本项目按 Factory Physics for Managers 第 9 章的 Michigan Steel VSM 案例，逐步建立 Simio 模型并验证每次复杂度增量。案例 PDF 是事实和作者方法的来源；Skill、项目路线和 Issue 文件规定本项目的建模、验证与协作记录方式。

## 当前交接状态

- 最新本地候选快照：[`V0.19 参数化装配候选`](models/VSM_MichiganSteel_V0.19_ParameterizedAssemblyWorkersCandidate.spfx)；V0.16–V0.19 版本清单见 [`model-version-history-v016-v019.md`](model-version-history-v016-v019.md)
- 当前迭代：`I1`；路线环节见 [`01.md`](01.md)，核心 Issue 记录见 [`iterations/I1/`](iterations/I1/)
- 阶段门：`HOLD`
- 正式项目阶段门仍为 `HOLD`；Issue 09 仍开放。V0.16–V0.19 是用户要求的候选版本与探索性验证记录，不构成 B0/B1 验收，也不改变既有 Issue 状态
- 未通过范围：正式 B0/B1/B2 基线、物理托盘组批语义、后续随机复制与置信区间、20 件计算批次对批内制造时序的等价性、作者结果对照；这些不属于已闭环的 Issue 06/08 范围
- 当前模型包、输入哈希、运行证据和未关闭事项：[`iterations/I1/06-V012-implementation-evidence.md`](iterations/I1/06-V012-implementation-evidence.md)

V0.12 是此前完成保存重载回归的候选快照。后续 V0.16–V0.19 逐步增加期间库存/交付统计、可调生产批量、随批量调整的投产间隔，以及连续装配人员情景。V0.19 的服务器利用率 Dashboard 已显示数据，但指标正确性和图表业务解释尚未独立核验。模型仍是受控候选快照，不能标为正式 B0/B1；20 件计算批次与逐件实体模型的制造时序等价性尚未验证。

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
| V0.6 逐件参照、V0.7 历史批次、V0.12 实施候选及 V0.16–V0.19 演进候选 | [`models/`](models/)、[`snapshots/`](snapshots/)、[版本清单](model-version-history-v016-v019.md) |
| 通用规划 Skill | [`../../skills/supply-chain-simulation-planning/SKILL.md`](../../skills/supply-chain-simulation-planning/SKILL.md) |

## GitHub 协作状态

项目规划和 I1 的 01–14 工作包 Markdown 已整理为仓库内容。Issue 06 的 V0.12 实施与确定性实现范围已完成线上闭环，Issue 08 的确定性验证与守恒范围已闭环。随机复制、置信区间、20 件聚合适用性与作者结果对照转交 Issue 09，I1/B0/B1仍为HOLD。目标远端为 [`wyfchina/FactoryPhyVsm`](https://github.com/wyfchina/FactoryPhyVsm)，本地分支为 `codex/vsm-v04-github-ready`。

每项后续模型变更应关联 Issue，记录目标、依赖、设计、验收条件、预期和实际结果以及证据路径。每次运行都须绑定模型文件哈希、输入快照和 Simio 版本；不能用提交、上传或文件名代替阶段验收。
