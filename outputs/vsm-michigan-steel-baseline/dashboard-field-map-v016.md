# V0.16 Dashboard 字段与绑定说明

当前数据层已在 Simio 原生运行中验证。数据源选择已在 Dashboard 编辑器界面确认；报表版式尚未保存或进行图形验收。

## 数据源与共同筛选

优先选择 `Table.VSM_Out_DashboardPeriods`，这是将原生库存统计与日末履约结算合并后的 Output Table。每次完整运行后筛选 `PeriodComplete = 1`；按 `PeriodType = Day` 或 `Month` 分开作图，并明确复制号。当前复制为 91030。

一行代表一个复制、一个日/月期间、一种产品（Left、Right、Total）。日/月行不能混加；Total不能再与Left、Right求和。横轴采用数值 `PeriodIndex`，而不是文本编号或日历日期。原生 `Periodic State Statistic Log` 也可作为库存图的数据源，库存平均读取 Average；需同时筛选 Category=VSMInventory、期间和产品。

## 推荐绑定

| 图 | 共同条件 | 横轴 | 系列及数值 | 聚合与格式 |
|---|---|---|---|---|
| 库存趋势 | Day或Month；Product=Total | PeriodIndex | AverageFGUnits、AverageManufacturingWIP | 每点每复制一行；单位件 |
| 到期数量欠交率 | Day或Month；保留L/R/Total为分开的系列 | PeriodIndex | Product；DueShortfallRate | 百分比，0–100%；不能跨产品相加 |
| 需求满足堆积柱 | Product=Total | PeriodIndex | OnTimeUnits、MissedAtDueUnits | 两者相加日920件/月18400件 |
| 期末欠交余额 | Product=Left或Right，分系列 | PeriodIndex | Product；ClosingBacklog | 件；时点存量，不能跨天求和 |
| 平均成品覆盖日数 | 单个产品、期间 | PeriodIndex | FGCoverageDays | 有效工作日；与制造CT区别 |

多个期间合并时：库存均值按PeriodHours加权；到期欠交率按MissedAtDueUnits合计 / DemandUnits合计；库存期末值取最后一个期间，不能累加。不同复制分别显示，不能将轨迹相加。

## 字段字典

| 字段 | 原生类型 | 含义 |
|---|---|---|
| PeriodType | String | Day或Month；独立完整期间。 |
| PeriodIndex | Integer | 累计期间编号；日1至240，月1至12。 |
| Product | String | Left、Right、Total；Total与产品行不能重复加总。 |
| Scenario | String | 本次场景标识。 |
| StartEffectiveHours | Discrete | 期间开始有效小时。 |
| EndEffectiveHours | Discrete | 期间结束有效小时。 |
| PeriodHours | Discrete | 期间有效小时数；非日历小时。 |
| Month | Integer | 业务月编号，每月20日；日行也提供所属月。 |
| PeriodComplete | Integer | 日末先写0；整次运行末统一核定原生期间统计后写1；Dashboard仅筛选1。 |
| OpeningFG | Integer | 期初可用成品工件件数。 |
| ClosingFG | Integer | 日/月末到期需求分配后的可用成品工件件数。 |
| AverageFGUnits | Discrete | 原生Periodic State Statistic本期间时间加权平均成品件数。 |
| MinFGUnits | Discrete | 本期间原生成品最小件数；含同刻边界状态。 |
| MaxFGUnits | Discrete | 本期间原生成品最大件数。 |
| FGCoverageDays | Discrete | 平均成品件数/该产品每日需求；单位有效工作日。 |
| AverageManufacturingWIP | Discrete | 原生期间时间加权平均制造工件数；含排队/加工，不含成品。 |
| ClosingManufacturingWIP | Integer | 期间结算制造件数，剔除归属下期的同刻边界投产。 |
| PhysicalManufacturingWIP | Integer | 结算后同刻的实际制造件数，可能含下期边界投产。 |
| BoundaryReleaseUnits | Integer | 物理制造件数与结算制造件数之差；归属下期，不删除实体。 |
| ManufacturingCoverageDays | Discrete | 平均制造件数/每日需求；覆盖日数，不直接代表CT。 |
| AverageBacklogUnits | Discrete | 原生期间时间加权平均已到期未交件数。 |
| MaxBacklogUnits | Discrete | 原生期间最大欠交与本期期末欠交取较大值，包含末端需求结算。 |
| OpeningBacklog | Integer | 期初已到期仍未交件数。 |
| ClosingBacklog | Integer | 期末已到期仍未交件数。 |
| BacklogCoverageDays | Discrete | 期末欠交件数/每日需求，单位日。 |
| DemandUnits | Integer | 原到期日在本期间的需求件数。 |
| OnTimeUnits | Integer | 本期间原到期需求中按时分配发运件数。 |
| MissedAtDueUnits | Integer | 本期间需求-准时件数，后续补交不回改。 |
| DueShortfallRate | Discrete | 到期未交件数/本期间到期需求；0至1，零需求不适用。 |
| OnTimeRate | Discrete | 准时件数/本期间到期需求；0至1。 |
| ReleasedUnits | Integer | 本期间新生产工单释放件数。 |
| ReceiptUnits | Integer | 本期间制造完工成品入库件数，不重复含t0成品。 |
| ShipmentUnits | Integer | 本期间实际发运件数，含旧欠单补交。 |
| LateShipmentUnits | Integer | 本期间发运中补交以前到期需求的件数。 |
| AvailableForDueUnits | Integer | 仅Day：先抵旧欠交后可用于本日新增需求的成品数量；Month不适用为-1。 |
| StockoutTimeShare | Discrete | 仅Left/Right：期间成品为零的时间占比0至1；Total不适用为-1。 |
| InitialSourceRemaining | Integer | 初始来源尚未发运件数，含制造及成品。 |
| StockBalance | Integer | 期初成品+入库-发运-期末成品，必须0。 |
| DemandBalance | Integer | 期初欠交+需求-发运-期末欠交，必须0。 |
| Version | String | 本行冻结时的模型版本。 |
| Replication | Integer | 本次原生复制编号。 |
| RandomnessDisabled | Integer | 1为确定性检查，0为随机运行。 |
| NativeMaxBacklogUnits | Discrete | 原生期间最大欠交；周期在日末分配前闭合时，末端新欠交归下一原生窗口；业务最大值另含期末欠交。 |

## 边界规则

- Average字段来自原生StateStatistic → PeriodicStatistic的时间加权平均；每个库存变化都参与，而非日末点的算术平均。
- 日末业务快照在到期需求分配完毕后冻结；原生窗口的EndValue可能位于同刻需求分配之前，不能将其冒充ClosingFG。
- 原生Minimum/Maximum可能包含t0初始化或同刻边界的零时长状态。MinFGUnits=0不能单独证明发生了有持续时间的缺货；持续零库存用StockoutTimeShare，交期用DueShortfallRate。
- NativeMaxBacklogUnits保留原生最大值；MaxBacklogUnits另包含本期末新增需求结算产生的欠交。
- AvailableForDueUnits仅适用于Day；StockoutTimeShare仅适用于Left、Right。其他行的-1表示不适用，Dashboard应隐藏，不能画成负数。
- ClosingManufacturingWIP是结算口径；PhysicalManufacturingWIP可能多出同刻归下期的投产，差额为BoundaryReleaseUnits。
- 报表不是实时动画。日末先记录业务行，整次运行结束统一核定原生统计后PeriodComplete才为1。

## 交付的数据文件

`dashboard-data/v016-r91030/` 包含全表、日表、月表、原生日志CSV及哈希manifest。CSV是本次完成运行的静态快照；原生Output Table才是重新运行后自动更新的来源。

`VSM_Day_Dashboard_IMPORT_CANDIDATE.xml` 和 `VSM_Month_Dashboard_IMPORT_CANDIDATE.xml` 为依据随附官方Dashboard示例结构生成的导入候选，已检查XML结构和字段存在性；尚未原生导入、保存或目视验收，不能视为可直接验收的最终报表。用户可在“结果 → 仪表板报告 → 导入”中试用，完成报表登记后继续验收。报表和模型文件的保存均由用户操作。

候选版式默认库存/需求显示Total，欠交余额按L/R；可按业务需要进一步增加产品筛选、指标卡及月度下钻。当前已验证的是统计与数据接口。
