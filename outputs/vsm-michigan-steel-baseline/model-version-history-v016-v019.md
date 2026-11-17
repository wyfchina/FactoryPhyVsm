# VSM 模型版本清单：V0.16–V0.19

本清单把连续版本、文件身份、已验证内容和未验证边界放在同一处，便于审阅与恢复。每个 `.spfx` 都是候选快照；提交、上传或文件名本身不等同于 Simio 保存重载验收。

| 版本 | 模型文件 | 主要增量 | 验证/状态 |
|---|---|---|---|
| V0.16 | `models/VSM_MichiganSteel_V0.16_PeriodicInventoryDeliveryCandidate.spfx` | 期间库存、制造 WIP、欠交、准时交付及 Dashboard 数据层 | 原生 240 日运行与守恒/聚合检查记录在版本报告；Dashboard 报表导入、外观和保存重载仍有待验收 |
| V0.17 | `models/VSM_MichiganSteel_V0.17_ProductBatchAttributeCandidate.spfx` | 左右产品生产批量改为实验属性 | 属性化中间快照；单独重载回归证据未归档 |
| V0.18 | `models/VSM_MichiganSteel_V0.18_AdaptiveReleaseRateCandidate.spfx` | 批量变化时同步调整投产间隔，保持长期平均投产速率 | 机制在 V0.19 四场景候选中使用；单独重载回归证据未归档 |
| V0.19 | `models/VSM_MichiganSteel_V0.19_ParameterizedAssemblyWorkersCandidate.spfx` | 参数化装配组织方式与人数、连续完成两道装配的共享工人；保留批量属性 | 四种批量/装配情景各一次随机运行，机制检查通过；不能据此声称统计优势。Server 利用率 Dashboard 已有数据，指标与展示正确性尚待核验 |

## 文件身份

以下 SHA-256 用于确认归档对象未被静默替换：

| 版本 | 大小（字节） | SHA-256 |
|---|---:|---|
| V0.16 | 300007 | `8FFB57215F5D7C2D3F099AB15C2EB006C1390A0F1758A88DA04E96C3F306E98B` |
| V0.17 | 300015 | `C2CAAE3BF98F2430906E14B9D30BE0A815A69A846323E4774A17BDC50322D2F6` |
| V0.18 | 18667431 | `48F12E758E06FC060F29352A0596B58D2F8EE1BB79A913B444E659D6BE157DE6` |
| V0.19 | 20778111 | `040FFE89E67A08D8FEF7F0F8255C1CE34973F751880AD442B2B6F2CC6C49031A` |

## 证据与限制

- V0.16 240 日汇总验证：[validation JSON](evidence/v016-periodic-dashboard/continuous-240d-aligned-validation.json)；逐月表：[monthly results](evidence/v016-periodic-dashboard/monthly-results-table.md)。大体量逐事件和逐实体运行日志不纳入本次版本 PR。
- V0.19 四场景响应摘要：[experiment response statistics](evidence/assembly-parallel-v019/experiment-response-statistics.json)；装配机制及混合尾批检查：[two-worker mechanism](evidence/assembly-parallel-v019/final-mechanism-mode1-workers2.json)、[mixed-tail mechanism](evidence/assembly-parallel-v019/final-mechanism-mixed-tail.json)。
- Server 利用率 Dashboard 定义：[applied Dashboard XML](evidence/server-utilization-dashboard-20261117/资源利用率.applied.xml)。用户开启交互运行日志后确认图表显示数据；本地已有的 `log-ResourceUsage.json` 是开关开启前捕获（`totalCount=0`），不纳入当前运行证据。应重新捕获日志后再核实指标公式、维度/筛选语义和图表是否适合作为正式 KPI。
- 更早模型版本 V0.13–V0.15 未包含在本次归档范围；本 PR 只归档 V0.16–V0.19，不能作为 V0.12 到 V0.19 的完整逐版历史。
- Issue 09 仍为 `Open / Partial`，B0/B1 阶段门仍 `HOLD`。本次不修改任何线上 Issue 状态，也不将这些探索性版本解释为正式实验通过。
