# Michigan Steel VSM V0.7 交接清单

## 交接身份

| 字段 | 值 |
|---|---|
| 项目 | Factory Physics for Managers 第 9 章 Michigan Steel VSM |
| 迭代 | `I1`，20 件计算批次实现增量 |
| 模型状态 | `VSM_V0.7_InitialWIPTable` |
| 交接用途 | 以 V0.6 逐件模型为参照，降低实体数量并保留工件总量统计 |
| Simio 文件 | `VSM_V0.7_InitialWIPTable.spfx` |
| 文件大小 | 179,795 bytes |
| SHA-256 | `D49089368991FA7F14B435D5BE6A5EAC1E74259A1F52ED2DA4ACC7A00F50EA7F` |
| 阶段门 | `HOLD` |
| 正式基线 | 未通过；当前状态不是 `B0`、`B1` 或 `B2` |
| Simio 版本 | `20.297.56736.0` |
| 原生重载回归 | 已完成 |

## 表达规则

- 标准实体代表 20 件工件，数量保存在 `ModelEntity.VSM_QuantityState`。
- 初始 WIP 17,130 件对应 857 个实体；W03-R 的 850 件拆为 42 个 20 件实体和 1 个 10 件尾批实体。
- 生产释放每次创建 460 个实体，对应 9,200 件；完整运行共释放 920 个实体、18,400 件。
- Shipping 使用加权件数统计；Simio 原生 NumberCreated/NumberDestroyed 仍按实体计数。
- 该版本是计算批次近似，不能直接把实体级队列、流动时间或批内事件时序解释为逐件结果。

## 回归结果

确定性快进运行，`RunLength = 306.6666667 h`，随机性关闭，无预热：

| 指标 | 结果 | 口径 |
|---|---:|---|
| 初始 WIP | 17,130 件 / 857 实体 | `VSM_InitialWIPTable` 加权数量 |
| 生产释放 | 18,400 件 / 920 实体 | 两次 9,200 件释放 |
| 总创建 | 35,530 件 / 1,777 实体 | 初始 WIP + 生产释放 |
| Shipping 加权交付 | 19,630 件 | `VSM_ShippedUnitOutput` |
| Shipping 销毁实体 | 982 | 实体数，不是件数 |
| 期末实体 | 795 | 1,777 - 982 |
| 期末工件等价数 | 15,900 件 | 按实体 `VSM_QuantityState` 加权 |
| Left/Right 释放 | 12,000 / 6,400 件 | 加权释放统计 |
| 模型诊断 | 0 errors | 重载后 MCP 诊断 |
| 运行警告 | 0 | 重载后运行状态 |

件数守恒：`17,130 + 18,400 = 19,630 + 15,900 = 35,530`。

## 参照关系和限制

V0.6 继续保留为逐件实体参照版本。V0.7 适合验证总量、工作内容、释放和交付统计，并降低实体数量；它尚未证明与 V0.6 在详细队列动态、批内完成时间、Fill Rate 或作者报告 KPI 上等价。

详细过程证据见 [`vsm-v07-20piece-entity-evidence.md`](vsm-v07-20piece-entity-evidence.md)。
