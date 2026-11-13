# Michigan Steel VSM 仿真项目

本项目按 Factory Physics for Managers 第 9 章的 Michigan Steel VSM 案例，逐步建立 Simio 模型并验证每次复杂度增量。案例 PDF 是事实和作者方法的来源；Skill、项目路线和 Issue 文件规定本项目的建模、验证与协作记录方式。

## 当前交接状态

- 模型快照：`VSM_V0.4_InitialWIPPrototype`
- 当前迭代：`I1`；路线环节见 [`01.md`](01.md)，核心 Issue 记录见 [`iterations/I1/`](iterations/I1/)
- 阶段门：`HOLD`
- 已验证范围：初始 WIP 17,130 件的装载、W05 初始成品暂存、确定性完整运行的全系统实体守恒
- 未通过范围：正式 B0/B1/B2 基线、保存后原生重载回归、实际托盘组批/尾批、班次日历、随机故障、换型、需求履约及 Fill Rate
- 当前模型包、输入哈希、运行证据和未关闭事项：[`release-manifest-v0.4.md`](release-manifest-v0.4.md)

保存包内部仍有 V0.3 实验场景元数据和过时对象说明，记录为 `DQ-005`。完整运行出现 1 条高实体数量技术警告，原生重载回归后需复核。这些状态不妨碍把模型作为受控候选快照提交审阅，但不允许将其标为正式基线或发布版本。

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
| V0.4 模型与 V0.1 回滚快照 | [`models/`](models/)、[`snapshots/`](snapshots/) |
| 通用规划 Skill | [`../../skills/supply-chain-simulation-planning/SKILL.md`](../../skills/supply-chain-simulation-planning/SKILL.md) |

## GitHub 协作状态

项目规划和 I1 的 01–14 工作包 Markdown 已整理为仓库内容。它们尚未绑定 GitHub 上的实际 Issue 编号、Pull Request 或 Milestone；绑定后应在路线文件和关联 Issue 中补记链接。当前工作区未配置 Git 远端，因此本次可以形成候选分支和本地提交，推送与创建 GitHub Issue 需要先确定目标仓库。

每项后续模型变更应关联 Issue，记录目标、依赖、设计、验收条件、预期和实际结果以及证据路径。每次运行都须绑定模型文件哈希、输入快照和 Simio 版本；不能用提交、上传或文件名代替阶段验收。
