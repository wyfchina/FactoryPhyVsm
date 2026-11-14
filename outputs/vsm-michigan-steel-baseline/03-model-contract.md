# VSM 基线模型契约

## 模型身份

- 模型名：`VSM_MichiganSteel`
- 阶段：`VSM_V0.10_CommonSkeletonCandidate`（继承 V0.9 产品分组审计并完成公共骨架命名/说明增量）
- 目的：表达 Figure 9-1 当前状态，并为后续作者步骤提供可验证的输入和响应。
- 运行类型：先做有限月度原型；是否建立稳态 warm-up 版本，留到 B1 运行设计确认。

## 实体和批次

### Bracket

| 状态/属性 | 含义 | 单位/编码 |
|---|---|---|
| EntityID | Simio 实体标识；V0.7 一个实体代表 20 件或尾批实际件数 | Simio entity |
| `VSM_QuantityState` | 当前计算实体代表的工件数 | 件；标准值 20，尾批为剩余件数 |
| `VSM_ProductTypeState` | 所代表工件的产品类型 | `L` / `R` |
| `VSM_TrayIDState` | 候选托盘/追溯状态；当前不证明实体已物理组托 | String/state |
| `VSM_ProductionBatchState` | 两周生产批次标识 | String/state |
| `VSM_ReleaseTimeHoursState` | 相对仿真开始的释放小时 | 小时 |
| CompletionTime | 实体完成 Shipping 的时刻；V0.7 不解析批内逐件完成时刻 | 仿真时间 |

### 初始 WIP

仿真开始时由 `VSM_InitialWIPTable` 保存 `data/wip-initial.csv` 的工件件数，由 `VSM_InitializeWIP` Process 在初始化阶段 Search/Create/Assign/Transfer 到对应位置。V0.7 的标准实体代表 20 件工件，尾批保存实际数量；若改为从零开始或通过预热生成稳定 WIP，必须改模型版本并重新执行基线验证。

## 生产逻辑

1. 按产品类型和生产批次生成/释放支架。
2. 按托盘 20 件组织跨工序转移；不要把转移批量误当成生产批量。
3. 每道工序使用其过程时间、换型时间、资源和可用率参数。
4. 同一工序在换型时遵循明确的产品切换规则；当前来源没有给出 L/R 顺序，第一版必须标为实现选择。
5. Assembly #2 后进入成品待发运区，再按发运规则进入 Shipping。若第一版采用零时间、无限容量 Shipping，应在响应中说明它不代表真实运输过程。

### V0.3 继承并在 V0.7 保留的释放批次挂接

当前 V0.7 模型包含生产释放过程 `VSM_OnProductionRelease`，触发事件为
`Output@Source_ProductionRelease.Entered`。该过程依次递增 `VSM_ReleaseSequence`，按每个
9,200 件周期先 L=6,000、再 R=3,200 设置实体产品状态和批次标签，并记录相对仿真小时
和候选托盘号；Experiment 响应 `ReleaseSequence_Final` 在 18,400 件输入下得到 18,400。
L 先于 R 是本项目的可复现实现选择，不是来源给出的详细排产顺序。计数器是验证钩子，
不是生产批量或托盘逻辑的替代品；其直接实验响应目前返回空观测。

实体定义保留产品、托盘、生产批次和释放时间等契约字段。V0.7 另以 `VSM_QuantityState`
表示每个计算实体承载的工件数；产品状态、释放小时、批次标签和候选托盘号已挂接到生产
释放过程。候选托盘号不表示实际物理组托。V0.7 回归记录的加权释放为 L=12,000、R=6,400
件；历史实验响应曾返回空观测的结果不用于覆盖当前版本证据。

### I1.4 已实施与待补齐的释放和初始状态增量

- 生产批量的入口控制点固定为 Stamping 前的生产线入口；每 10 个工作日释放 L=6,000、R=3,200。来源未指定 L/R 批次在周期内的先后顺序，模型必须将采用顺序单独登记。
- V0.7 的 `Source_ProductionRelease` 仍以每次 9,200 件的两次释放表达两周期总量，每次创建 460 个 20 件计算实体；它尚未实现按班次日历驱动的真实释放时点。I1.3 的逐件 60 秒 Source 结果须与本版本分开保存。
- 初始工序 WIP 由 `VSM_InitializeWIP` 从表读取并按产品类型赋值；不根据库存数量虚构历史托盘号。W03 的 R=850 件保留为 42 个标准实体和 1 个 10 件尾批实体。W05 初始成品进入独立 `Server_FG_Staging`，其外传条件为 0，直到发运规则明确前不自动进入 Shipping。仿真开始后的新生产转移和尾批语义仍需单独验证。
- 每班 27,600 秒、每日两班只固定有效工作时间总量。当前没有来源支持班次开始时刻和休息分布；若实现只表达每日 15.3333 小时总有效时间，必须标注其无法表达班间停顿的限制。

## 资源、日历和故障

- 每个制造工序默认一个操作员，来源为作者假设。
- 工具数量未定义，不能无证据创建多个工具资源。
- Stamping 和 S. Weld #2 使用目标可用率；其余工序暂按 100% 目标，但要区分“没有故障数据”和“真实永不故障”。
- 项目实现选择为两状态指数故障/维修过程，时间按有效运行小时计；Stamping 的 MTTF/MTTR 为 5.6667/1 h，S. Weld #2 为 4/1 h。输入快照必须保留目标可用率、实现参数和来源区分；不得把目标值写成观测结果。
- 班次、休息和每班有效秒数必须统一到一个日历对象；不要在不同工序硬编码不同工作时间。

## 初始输入和控制

- 月需求：L=12,000、R=6,400。
- 工作日：20 日/月。
- 两周生产批量：L=6,000、R=3,200；项目约定在 Stamping 前释放，每 10 个工作日一轮。
- 转移批量：20 件/托盘。
- 释放规则：生产批次按上述入口和周期释放；不声称已重建 MRP。L/R 批次顺序仍是实现选择。
- 原料、工序 WIP 和成品库存：按 `data/wip-initial.csv`。

当前 V0.9 运行证据：表驱动 Process 代表 17,130 件/857 实体；306.6667 小时运行的总量为 35,530 件、加权 Shipping 19,630 件、期末加权 WIP 15,900 件，件数和实体数守恒，诊断 0 errors、运行警告 0。V0.9 另对 Left/Right 独立记账：Left `11,200+12,000=14,500+8,700`，Right `5,930+6,400=5,130+7,200`。该证据只关闭 L/R 聚合产品分组子集，不替代初始 WIP 行 cohort、真实生产批次、物理托盘分组或保存/重载验证。

V0.9 产品分组审计状态包括 `VSM_InitialLeftUnitCount`、`VSM_InitialRightUnitCount`、`VSM_ShippedLeftUnitCount`、`VSM_ShippedRightUnitCount`，以及六个位置各自的 Left/Right 当前加权 WIP 状态。初始累计按 `VSM_InitialWIPTable.BatchUnitQuantity` 在每个计算实体赋值时增加；发运累计按 `VSM_ProductTypeState` 和 `VSM_QuantityState` 在 `VSM_OnShipment` 中增加；位置状态由各 Server 的 Entered/Exited 过程维护。`ProductionBatch` 对初始 WIP 仍是追溯标签，不宣称真实生产批次。

V0.10 公共骨架增量只改变模型身份、链接业务命名和关键对象/Output Statistic 的说明，不改变上述状态更新、处理时间、路由、批量或守恒逻辑。活动模型和独立保存包已通过当前会话静态检查与确定性回归；保存包 SHA-256 为 `B719029E9A04AD2DD2F93E0594C5C06BE79087DC2D62BC66B58DAD186FCC1CAF`。关闭/重开回归仍由 VSM-14 承担。

## 输出和守恒

至少输出：DemandRate、TaktTime、ManufacturingCT、TotalInventoryDays、ProcessWIPDays、FGDays、Throughput、ResourceUtilization、FillRate（如规则已定义）和 BatchMakespan。

守恒检查：

- 各产品到达/释放 = 完工 + 报废 + 期末剩余。
- 每个托盘的件数符合 20 件规则，除非显式处理最后不足一托盘的尾批。
- WIP 按位置分类的初始总量与来源快照一致。
- W05 初始成品在发运规则明确前不得自动进入 Shipping；暂存进入/离开数必须可核对。
- 产品分组审计：对每个产品组，初始 WIP + 生产释放 = Shipping + 六个位置期末 WIP；按 `WIPRecordId` 或真实生产批次的独立 cohort 守恒需另行建立输入/响应，不能由 L/R 聚合结果代替。
- 资源忙时不超过排班可用时间；故障和换型时间不与加工时间重复累计。
- ManufacturingCT 不自动包含原料等待或成品待发运；TotalInventoryDays 分项显示。

## 不在 V0.1 中做的事情

不实现批量优化、工序合并、维修策略改进、加班、库存优化或作者最终方案。完成 B0/B1 的基线证据后，才按 `06-experiment-matrix.csv` 进入后续阶段。
