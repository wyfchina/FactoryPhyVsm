# V0.11 初始 WIP cohort 证据

## 版本身份

- 活动模型：`/Project/Model`
- 模型文件：`models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx`
- 文件状态：用户已另存；Simio 标题显示 `VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate`
- SHA-256：`D023F7420FF2E1FF21046A0E9481E64E3268CD7B2C7EC7F8D0532C9A606D6F52`
- 根属性：`VSM_ModelVersion=VSM_V0.11_InitialWIPCohortCandidate`
- 根属性：`VSM_BaselineStage=INITIAL_FLOW_CANDIDATE`
- 回滚副本：`models/VSM_MichiganSteel_V0.10_CommonSkeletonCandidate.pre-Issue06-cohort.spfx`

## 本次增量

`VSM_InitializeWIP` 保持 Data Table + Process 的初始化结构，只增加两项可追溯性增量：

1. `Search` 步骤的 `CopyOverTableRowReferences` 设置为 `True`。
2. 每个初始 WIP 计算实体的 `ModelEntity.VSM_ProductionBatchState` 写入
   `WIP:<WIPRecordId>`，例如 `WIP:InitialWIP_W01_L`。

当前实体仍以 20 件为标准权重，尾批保留实际件数；正常生产释放的
`L_6000_Batch` / `R_3200_Batch` 标签没有改变。

## 复位态 cohort 检查

在 `/Project/Model/Runtime/Objects/ModelEntity/DefaultEntity` 上执行 `Reset` 后，
仿真时间为 `0 h`，初始实体数为 `857`。运行时表达式读取结果为：

| 检查项 | 结果 |
|---|---|
| `Population.FirstItem.ModelEntity.VSM_ProductionBatchState` | `WIP:InitialWIP_W01_L` |
| `Population.FirstItem.ModelEntity.VSM_QuantityState` | `20` |
| `Population.LastItem.ModelEntity.VSM_ProductionBatchState` | `WIP:InitialWIP_W05_R` |
| `Population.LastItem.ModelEntity.VSM_ProductTypeState` | `Right` |
| `Population.LastItem.ModelEntity.VSM_QuantityState` | `20` |
| `Population.NumberInSystem` | `857` |

这证明初始 WIP 的 cohort 标签已写入实体状态并可在运行时读取。Simio MCP 当前不能从实体表达式直接返回 `VSM_InitialWIPTable.WIPRecordId` 的表行对象，因此不能把本证据解释为逐行动态账本已经完成。

## 保存后确定性回归

运行设置为 `RunLength=306.6666667 h`、无预热、关闭随机性。保存后的活动 V0.11 候选执行 `Reset → FastForward`，结果如下：

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
| 模型诊断 | `0 errors` |
| 运行警告 | `0` |

## 验收边界

- 已通过：cohort 标签写入和复位态首尾实体可读取；聚合件数、L/R 件数、实体守恒和确定性回归。
- 未通过/未完成：按每个 `WIPRecordId` 独立累计 Shipping 与期末剩余的动态 cohort ledger。
- 未完成：真实生产批次的独立动态守恒、班次日历、换型、故障/维修、物理托盘、批内时序、需求履约和 Fill Rate。
- 持久化状态：V0.11 文件已保存并完成保存后活动会话回归；本次证据尚未包含关闭 Simio 后重新打开 V0.11 文件的独立原生回归。

