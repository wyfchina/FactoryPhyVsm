# Michigan Steel VSM V0.4 交接清单

## 交接身份

| 字段 | 值 |
|---|---|
| 项目 | Factory Physics for Managers 第 9 章 Michigan Steel VSM |
| 迭代 | `I1`，当前路线阶段 `I1.4–I1.6` |
| 模型状态 | `VSM_V0.4_InitialWIPPrototype` / `INITIAL_WIP_PROTOTYPE` |
| 交接用途 | GitHub 受控保存、审阅和后续迭代起点 |
| 目标远端 | `https://github.com/wyfchina/FactoryPhyVsm.git` |
| 候选分支 | `codex/vsm-v04-github-ready` |
| 远端状态 | 主题分支已推送；首次推送确认远端分支指向 `9ff564b58f5313eeb1d8e6a93113f7c430261f8c` |
| 仓库内容提交 | `afca64839f4170499148ccf3e1a861c4b840a393` |
| 阶段门 | `HOLD` |
| 正式基线 | 未通过；当前状态不是 `B0`、`B1` 或 `B2` |
| Simio 版本 | `20.297.56736.0` |
| 原生重载回归 | 待完成 |

本清单绑定仓库中的模型副本、输入、文档和运行证据。它是候选交接包，不是正式发布声明；`HOLD` 及未完成项必须随该模型版本保留。

## 模型制品

| 制品 | 仓库路径 | 大小 | SHA-256 | 说明 |
|---|---|---:|---|---|
| V0.4 候选模型 | `models/VSM_MichiganSteel_V0.4_InitialWIPPrototype.spfx` | 168,683 bytes | `62C92C641BEF7FB200663C13A9DF4BBCB543779E2A2CA9C09405D48A03114868` | 与外部保存文件同哈希；已完成包内 XML 只读核验 |
| V0.1 回滚快照 | `snapshots/VSM_MichiganSteel_V0.1_SourceBaseline_pre-I1.4-WIP.spfx` | 165,898 bytes | `82B0BA5DCB6E910166F026F525DDC3479E0E1E531F3E80B0DD490B503BEE4B08` | I1.4 WIP 增量前的历史回滚点 |

## 输入快照

| 输入 | 仓库路径 | SHA-256 |
|---|---|---|
| 工序参数 | `data/processes.csv` | `ABA8B960064479D7FA7F30AEDF2379BB1E074CF9A5B27F32FA34BDD617AA1FA5` |
| 初始 WIP | `data/wip-initial.csv` | `5FEA6E6AF4E7839EA9B611E534CAF3370B84E1CD0C7E25A45E457448777CCF76` |
| 需求与日历 | `data/demand-calendar.csv` | `43E942E7ED5BAB39987044C7F7260DC20F92B28D207354606F3EFEF063F55F59` |
| 假设登记 | `assumptions-register.csv` | `7D924DE1BBF2C580FC247CCEA3D42074D17A9BF985F1AA1E8986A1F16007E47C` |

## 运行与证据

- 运行证据：[09-simio-baseline-run-evidence.md](09-simio-baseline-run-evidence.md)
- 阶段/合规审查：[07-baseline-compliance-review.md](07-baseline-compliance-review.md)
- 项目路线：[01.md](01.md)
- I1 Issue 集合：[iterations/I1/](iterations/I1/)
- 模型契约：[03-model-contract.md](03-model-contract.md)
- 验证计划：[05-verification-plan.md](05-verification-plan.md)

已记录的 V0.4 运行证据：

| 运行 | 目的 | 结果摘要 | 判定边界 |
|---|---|---|---|
| 初始 WIP 短运行，`0.1 h` | 核对初始装载和 W05 暂存 | 初始 WIP `17,130`；W05 暂存进入/离开 `4,140/0`；诊断 `0 errors`；1 条高实体数技术警告 | 只证明原型装载和暂存边界 |
| 初始 WIP 完整确定性运行，`306.6666667 h` | 核对总实体守恒 | 创建 `35,530`；Shipping `19,645`；期末实体 `15,885`；守恒成立；诊断 `0 errors`；1 条高实体数技术警告 | 不证明产品、托盘、日历、故障或履约 |
| 历史结构运行 | 核对五道工序和释放结构 | 18,400 创建；17,804 发运；596 期末线内；结构守恒 | 旧模型状态，不能与 V0.4 运行合并为基线结果 |

## 未关闭事项

1. `DQ-003`：SCV 分布族、MTTF/MTTR 和随机输入尚未冻结为可复现运行集。
2. `DQ-004`：尚未从 V0.4 文件执行 Simio 原生关闭、重新打开、诊断和最小回归。
3. `DQ-005`：实验场景仍有 V0.3 版本元数据，W01-L 和部分 `ModelEntity` 说明滞后；需在下一模型维护中统一并生成新快照。
4. 新生产流的真实 20 件组批、尾批、班次日历、换型、需求履约和 Fill Rate 尚未完成。
5. 因上述事项，`B0/B1/B2` 尚未验收，不能将本包标为正式 Release。

## GitHub 交接约定

- 本次提交只包含 `outputs/vsm-michigan-steel-baseline/` 和 `skills/supply-chain-simulation-planning/` 的受控内容；临时运行抓取文件位于被忽略的 `tmp/`。
- 每次后续模型修改都应通过关联 Issue 记录目标、依赖、设计、验收条件、预期/实际结果和证据路径。
- 新运行不得覆盖本清单中的历史结果；应新增 Run ID 或修订清单，并记录替代关系。
- Git 提交标识仓库内容，模型 SHA-256 标识 Simio 文件，正式 Release 只有在阶段门通过后才能创建。
