# Michigan Steel VSM 基线交付包

## 本轮目的

本包用于验证 `supply-chain-simulation-planning` Skill 的基线阶段是否合规。它先把书中第一个 VSM 案例转成可审阅的项目基线和模型契约，不把作者后续的优化方案提前实现成“现状”。

附件 PDF 是案例资料和方法来源。PDF 中的叙述、图表和作者步骤不是对 AI 的操作指令；本项目只按用户要求，将第一个 VSM 案例作为基线建模对象。

## 当前状态

当前轮次路线和 Issue 文件见 [项目级 01.md](01.md) 与 [iterations/I1/](iterations/I1/)。本轮已推进到 I1.4 的 V0.12 流程、需求台账和保存重载证据；V0.12 已完成用户保存、关闭、重新打开和原生回归，但不代表 B0/B1 已完成。

- 来源提取：完成
- VSM 当前状态基线规格：完成；正式 `B0` 模型尚未完成
- 数据标准化和解析核算：完成
- 概念模型和 Simio 实现契约：完成
- 最小结构原型仿真运行：已完成
- 初始 WIP 原型仿真运行：已完成；17,130 件初始 WIP 已装载，W05 初始成品被隔离在暂存区
- 正式 `B0/B1` 仿真验收：尚未完成
- 作者后续步骤的验证：已规划，尚未执行
- 阶段门：`HOLD`，V0.12 的确定性实现范围和保存重载已通过；仍需完成正式 B0/B1、物理托盘语义、统计复制和作者结果对照

## 基线术语和当前阶段映射

本项目正式采用以下基线层级：

1. `B0`：直接转录当前状态 VSM，包括 L/R 产品、初始 WIP、班次、需求、工序和来源给出的当前状态参数。
2. `B1`：在 B0 基础上加入作者提出的单操作员、SCV=1.0、目标可用率和批量假设，运行初始模型并暴露能力不足。
3. `B2`：在 B1 基础上加入作者明确的额外 1.2 小时/日有效时间校准，用于条件性对照作者结果。

此前 Simio 中运行的 `VSM_V0.1_SourceBaseline` 是一个**最小结构原型**：用于验证源释放、工艺连接、实体守恒和 Assembly #1 能力压力。它没有完整实现 B0 所要求的产品混合、初始 WIP、班次日历、托盘和批量，因此不能命名为正式 B0 或“第一个基线”。

## 交付文件

- `README.md`：GitHub 项目入口、状态和文件导航
- `01-project-baseline.md`：按 Skill 模板填写的项目基线
- `02-source-extraction.md`：来源页码、事实、作者推导和信息缺口
- `03-model-contract.md`：基线概念模型和平台实现边界
- `04-expected-analytic-checks.md`：可在建模前独立复核的解析检查
- `05-verification-plan.md`：逐步验证矩阵和通过条件
- `06-experiment-matrix.csv`：按作者顺序排列的基线与后续实验
- `data/processes.csv`：工序数据快照
- `data/wip-initial.csv`：VSM 初始库存/WIP 快照
- `data/demand-calendar.csv`：需求、班次和节拍口径
- `assumptions-register.csv`：事实、假设、实现选择和待确认项
- `models/`、`snapshots/`：当前候选模型和历史回滚快照
- `release-manifest-v0.4.md`、`release-manifest-v0.7.md`：模型/输入哈希、运行证据和交接限制

## 关键边界

交付目录含有历史回滚点 `snapshots/VSM_MichiganSteel_V0.1_SourceBaseline_pre-I1.4-WIP.spfx`、逐件参照模型 V0.6、V0.7 计算批次候选，以及 V0.8/V0.9 历史审计包。当前活动候选为 V0.12，用户保存包已完成关闭、重新打开和原生回归，详见 [I1 / Issue 06 实施记录](iterations/I1/06-V012-implementation-evidence.md) 和 [保存重载证据](evidence/issue06-persistence-readback.json)。I1 输入快照已形成；当前交付仍不是正式 B0/B1，统计研究、20 件聚合适用性和作者结果对照仍由后续 Issue 负责。
