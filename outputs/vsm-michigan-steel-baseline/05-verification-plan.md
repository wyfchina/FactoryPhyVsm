# VSM 基线验证计划

## 验证原则

先验证资料转录和解析边界，再验证模型机制，最后才把作者模型输出作为条件性对照。每项测试都记录预期、容差、实际结果、证据路径和失败后的下游影响；解析值、模型响应和作者报告值不得混写。`Passed` 只表示该测试范围有直接证据，不等于 B0/B1 整体通过。

验证责任映射如下。责任 Issue 定义测试输入、实现或关闭条件；Issue 08 承担相关的确定性守恒回归。

| 测试 ID | 负责 Issue |
|---|---|
| VSM-01 | Issue 02、03 |
| VSM-02 | Issue 02、08 |
| VSM-03 | Issue 03、08 |
| VSM-04 | Issue 02 |
| VSM-05 | Issue 04、06、08 |
| VSM-06 | Issue 02、06、08 |
| VSM-07 | Issue 03、06、08 |
| VSM-08 | Issue 06、08 |
| VSM-09 | Issue 06、08 |
| VSM-10 | Issue 03、06、08 |
| VSM-11 | Issue 06、08 |
| VSM-12 | Issue 06、07、08 |
| VSM-13 | Issue 07、09 |
| VSM-14 | Issue 06、08 |
| VSM-15 | Issue 06、08 |
| VSM-16 | Issue 06、07、08 |
| VSM-17 | Issue 05、08 |
| VSM-18 | Issue 06、07、08 |

## Issue 07 统计契约继承

Issue 07 的[指标与统计框架](iterations/I1/07.md)和[方案 A 详细规则](iterations/I1/07-fill-rate-contract.md)是本计划中指标定义、统计总体、加权规则和期末处理的详细来源。方案 A 由 Wu 于 2026-11-15 确认；口径确认不等于模型运行通过。

Issue 07 现按指标与统计规范验收 Passed；06/08/09 具名承接实现、执行和作者对照。所有小时为有效工时：55,200 秒/工作日，20 日 1,104,000 秒，不插入非工作时间；加工、排队、换型和故障/维修依机制计时。需求同刻和终点行为仍须原生验证。见 [07 闭环证据](issue07-closure-evidence.md)。

| 统计范围 | 固定规则 | 允许的结论 |
|---|---|---|
| D0-Deterministic-Validation | 306.6666667 h、无预热、随机关闭、单次；初始 WIP 保留 | 输入核对、结构响应、总量/L/R/位置守恒；不能推出随机性能、CT 或 Fill Rate |
| R1-Finite-Horizon-Research | Wu 已确认有限期、无预热、保留初始 WIP；随机开启；初始 30 个独立复制并报告 95% CI | B0/B1 候选的 CT、吞吐、利用率、可用率、WIP、方案 A 按期件数满足率；模型挂钩待完成 |
| S1-Steady-State-Research | 只有在批准预热和稳态总体后启用，不能与 D0/R1 混合 | 稳态响应；需要单独模型/输入版本和证据 |

共同规则：工件指标按 VSM_QuantityState 加权，原生实体数另列；期末实体进入 EndWIP 和守恒，对有合法起点的未完成 CT 样本标为右删失；已到期但未满足的需求计失败/积压，保留在服务指标分母中。Shipping / Release 不得称为 Fill Rate。正式响应必须绑定模型、输入、运行和复制元数据；已冻结规则但模型未消费的指标为 Defined / Pending。

## Issue 01–09 反向映射

Issue 定义工作目标、依赖和验收责任；本表是验证 ID 的唯一索引。每个 Issue 只报告其负责的验证项，不得把其他 Issue 的局部通过状态提升为本 Issue 或整体基线通过。

| Issue | 负责测试 | 当前验证状态摘要 | 主要证据/说明 |
|---|---|---|---|
| 01 | 文档治理检查，不分配 VSM 运行测试 | Issue 01 治理验收已通过；I1 整体阶段仍为 HOLD | `01.md` 的 I1.1–I1.7 路线表、Issue 映射、`iterations/I1/01.md` 及本表 |
| 02 | VSM-01、02、04、06 | Issue 02 口径与假设治理已通过；VSM-01 输入来源核对已通过，VSM-06 动态批次语义仍由 Issue 06/08 验证 | `iterations/I1/02.md`、`04-expected-analytic-checks.md`、`assumptions-register.csv` |
| 03 | VSM-01、03、07、10 | Issue 03 输入快照已通过；VSM-03/07 端到端模型核对和 VSM-10 观测可用率仍由 Issue 06/08 验证 | `iterations/I1/03.md`、`input-snapshot-manifest-v0.9.md`、`data/*.csv`、`assumptions-register.csv` |
| 04 | VSM-05（Issue 04 机制范围） | V0.9 当前候选原生回归通过总量释放、事件挂接、五工序路径、守恒和 Assembly #1 能力压力；旧历史运行版本未知；VSM-05 完整流程适用性仍由 Issue 06/08 检查 | `iterations/I1/04.md`、`09-simio-baseline-run-evidence.md`、`04-expected-analytic-checks.md` |
| 05 | VSM-17 | V0.10 公共骨架静态检查和保存包身份核对通过：对象、命名链接、Data Table、初始 WIP Process、事件挂钩、Output Statistic 和诊断均已核对；关闭/重载仍待完成 | `iterations/I1/05.md`、`03-model-contract.md`、`09-simio-baseline-run-evidence.md` |
| 06 | VSM-05–12、14–16、18 | V0.11 cohort 标签和 L/R 聚合子集通过；方案 A 的 FG/需求发运控制为待实现增量 | `iterations/I1/06.md`、`vsm-v11-initial-wip-cohort-evidence.md`、`iterations/I1/07-fill-rate-contract.md` |
| 07 | VSM-12、13、16、18（定义责任） | Passed（指标与统计规范）；CT、批次、R1、方案 A 和有效工时已冻结；06 实现、08 执行、09 作者对照仍待完成，测试状态保持原状 | `iterations/I1/07.md`、`iterations/I1/07-fill-rate-contract.md`、`data/demand-due-calendar.csv`、`issue07-closure-evidence.md` |
| 08 | VSM-02、03、05–12、14–18 | V0.11 聚合和标签子集通过；服务指标 F01–F07、关闭/重载、逐行 cohort ledger 和完整批次守恒未完成 | `iterations/I1/08.md`、`vsm-v11-initial-wip-cohort-evidence.md`、`iterations/I1/07-fill-rate-contract.md` |
| 09 | VSM-13 | 作者结果对照未运行；正式 B0/B1 为 Blocked / HOLD | `iterations/I1/09.md`、`02-source-extraction.md` |

反向映射也必须在 `iterations/I1/01.md`–`09.md` 的“验证计划映射”段落中出现。某项 Issue 没有 VSM 测试时，应明确标注为文档/治理验收，而不是留下未说明的空缺。

## 测试矩阵

2026-11-15 GitHub同步检查：02–05已按各自文档验收范围以completed关闭；01治理Passed已登记在仍Open的#1总览，06仍Open/HOLD。逐项回执见[同步结果](issue01-06-sync-result.md)。本次只检验治理同步，不新增原生运行结果，以下测试状态及未完成边界保持原判定。

| ID | 负责 Issue | 类别 | 配置/方法 | 通过判据与容差 | 实际结果 | 状态 | 证据 | 下一步/失败处理 |
|---|---|---|---|---|---|---|---|
| VSM-01 | Issue 02、03 | 来源转录与输入快照 | 对照 Figure 9-1、Table 9-1、Figure 9-2 | 五道工序、产品、需求、WIP、过程参数与来源逐项有来源；数值字段按输入单位精确对账 | 来源字段、单位、派生值和实现选择已分开登记并通过输入级复核；运行实现由 VSM-07/10/17 验证 | Passed（来源/输入快照范围） | `02-source-extraction.md`、`data/*.csv`、`input-snapshot-manifest-v0.9.md` | 保留输入哈希；运行级验证由对应测试负责 |
| VSM-02 | Issue 02、08 | 需求节拍 | 18,400 件/月、20 日/月 | 日需求=920 件/日；节拍=60 秒/件；件数误差 0 | V0.7 加权生产释放=18,400 件；解析值一致 | Passed（范围限定） | `04-expected-analytic-checks.md`、`vsm-v07-20piece-entity-evidence.md` | 保留为回归测试，不外推到日历可用性 |
| VSM-03 | Issue 03、08 | WIP 对账 | 汇总 `wip-initial.csv`，核对 V0.7/V0.9/V0.11 初始化表和末期加权 WIP | 工序 WIP=12,990、FG=4,140、初始有件数=17,130；W03-R=850；L/R=11,200/5,930；误差 0 | V0.11 复位态实体数=857，首尾标签为 W01-L/W05-R，聚合输入仍对账；表行级动态账本未完成 | Partial | `data/wip-initial.csv`、`vsm-v11-initial-wip-cohort-evidence.md`、`09-simio-baseline-run-evidence.md` | 建立逐行 cohort ledger 并核对全部 WIPRecordId |
| VSM-04 | Issue 02 | 价值时间 | 累加五道工序过程时间 | 188 秒=3.1333 分钟；不含换型、等待；算术误差 < 1e-9 秒 | 解析值已独立复算 | Passed（解析范围） | `04-expected-analytic-checks.md` | 运行模型中另行核对加权处理时间 |
| VSM-05 | Issue 04、06、08 | 能力边界 | 单操作员、无额外有效时间 | Assembly #1 名义负荷=62/60=103.33%；模型不得用统计上限掩盖超载 | V0.9 确定性回归中 Assembly #1 资源忙碌率=100%、处理时间=306.6667 h 且输入积压；解析负荷仍独立报告为 103.33%；完整日历适用性未验证 | Partial（Issue 04 子集 Passed） | `04-expected-analytic-checks.md`、`iterations/I1/04.md`、`iterations/I1/08.md`、`09-simio-baseline-run-evidence.md` | Issue 06/08 接入并验证日历和完整流程后回归 |
| VSM-06 | Issue 02、06、08 | 批量语义 | 20 件计算实体；L/R 生产批量 6,000/3,200，每 10 个工作日于 Stamping 前释放 | 来源件数守恒；标准实体权重 20；尾批保留；计算实体不冒充物理托盘 | V0.7 已验证 20 件表示、W03-R 10 件尾批、18,400 件加权释放；物理托盘和批内时序未验证 | Partial | `vsm-v07-20piece-entity-evidence.md`、`release-manifest-v0.7.md` | 先做 V0.6/V0.7 等价性和尾批动态测试 |
| VSM-07 | Issue 03、06、08 | 有效工时与事件边界 | A-022：仅计有效工时，两班×27,600秒/日 | 20日=1,104,000秒；不插入非工作间隔；工时换算一致，释放/到期/终点顺序正确 | Wu 确认；V0.11 只读核对 RunLength=306.6666667h、预热0、五制造工位 Fixed/1，无班次启停；动态边界待验证 | Partial（时间规范与静态配置 Passed；动态边界 Pending） | `data/demand-calendar.csv`、A-022、`issue07-closure-evidence.md`、原始 MCP JSON | 06/08 验证10日释放和每日/第20天需求事件；不要求补造真实班次日历 |
| VSM-08 | Issue 06、08 | 初始状态 | `VSM_InitialWIPTable` + `VSM_InitializeWIP` Process；W05 独立暂存 | 初始件数、位置、产品和 cohort 标签一致；总量/实体守恒；W05 不自动发运；误差 0 | V0.11 复位态首实体=`WIP:InitialWIP_W01_L`、尾实体=`WIP:InitialWIP_W05_R`，初始实体=857；W05 4,140 件保持暂存；逐行动态账本未完成 | Partial | `vsm-v11-initial-wip-cohort-evidence.md`、`09-simio-baseline-run-evidence.md` | 建立每个 WIPRecordId 的独立累计响应，并完成 V0.11 关闭/重开回归 |
| VSM-09 | Issue 06、08 | 换型 | L→R、R→L 各做一次确定性小例 | 只在定义资源发生；换型时间只计一次；顺序和总时长可解释 | 未实现/未运行 | Planned | 无 | 冻结切换规则后建立小例 |
| VSM-10 | Issue 03、06、08 | 故障可用率 | 选定 MTTF/MTTR 或等效可用率机制，多复制 | 目标为 85%/80%；数值容差、运行长度和复制数须在运行前登记；报告观测值及置信区间，随机流可复现 | 输入快照已冻结 MTTF/MTTR、分布和随机流；尚未执行故障运行，观测误差、复制数和置信区间待 Issue 07/08 | Partial（输入范围通过） | `input-snapshot-manifest-v0.9.md`、`assumptions-register.csv` | 冻结统计契约后由 Issue 06/08 运行并检验目标可用率 |
| VSM-11 | Issue 06、08 | 资源释放与异常 | 完工、取消、异常退出各一例 | 无资源/队列泄漏；件数和实体数均守恒 | 未执行 | Planned | 无 | 在完整流程模型上执行 |
| VSM-12 | Issue 06、07、08 | 候选状态响应 | D0：V0.11 确定性 306.6666667 h，无预热 | 运行错误=0、警告=0；件数和实体守恒误差 0；指标口径与版本一致 | 17,130+18,400=19,630+15,900；1,777-982=795；L/R 分组守恒成立；诊断 0、警告 0 | Partial（聚合、位置、L/R 和 cohort 标签审计子集） | `iterations/I1/07.md`、`vsm-v11-initial-wip-cohort-evidence.md`、`09-simio-baseline-run-evidence.md` | 完成 V0.11 关闭/重开，再完成逐行 cohort、逐实体时间响应和随机统计 |
| VSM-13 | Issue 07、09 | 作者结果对照 | R1/B2 仅在 CT、服务指标和运行总体可比后比较 14.8/12.8 日等结果 | 明确已复现、条件性支持或未复现；附差异、删失、复制和输入版本 | 项目 CT/方案 A/R1 已确认；作者软件的 Fill Rate 算法和统计总体尚未映射，B2 未运行 | Blocked / Planned | `iterations/I1/07.md`、`iterations/I1/07-fill-rate-contract.md`、`02-source-extraction.md` | 区分项目按期件数满足率与作者算法，不能直接等同 |
| VSM-14 | Issue 06、08 | 持久化与重载 | 保存 V0.7，关闭、重新打开、诊断并重跑确定性回归；随后对 V0.9/V0.10/V0.11 重复 | 模型身份、输入和统计保持一致；诊断 0 errors、运行警告 0 | V0.7 已完成；V0.11 已保存并完成保存后的活动会话回归，身份、诊断、警告和关键统计一致；关闭/重开尚未执行 | Partial（V0.7 Passed；V0.11 保存后当前会话 Passed；独立关闭/重载待完成） | `models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx`、`vsm-v11-initial-wip-cohort-evidence.md`、`09-simio-baseline-run-evidence.md` | 关闭 Simio 后重新打开 V0.11 包，复核身份、诊断、警告、cohort 标签和关键统计 |
| VSM-15 | Issue 06、08 | 位置级动态守恒 | 在确定性运行中按 Stamping、Weld 1、Weld 2、Assembly 1、Assembly 2、FG staging 和 Shipping 边界盘点加权件数 | 每个边界满足期初件数 + 流入 - 流出 = 期末件数；误差 0 件；盘点时刻和统计边界固定 | V0.11 位置状态与 L/R 状态仍满足两终点差分和聚合一致性；保存后当前会话回归通过 | Passed（两时点及 L/R 聚合范围，非持久化范围） | `vsm-v11-initial-wip-cohort-evidence.md`、`09-simio-baseline-run-evidence.md` | 完成关闭/重载后再扩展中间时点和逐件等价性 |
| VSM-16 | Issue 06、07、08 | 产品/批次分组守恒 | 按 `VSM_ProductTypeState` 和生产/初始批次标签分别核对 L/R 及初始 WIP 行 | 每个产品组、每个输入批次满足到达/释放 = Shipping + 期末剩余；误差 0 件；标签口径与真实生产批次分开说明 | L/R 聚合子集通过；V0.11 复位态首尾初始 WIP 标签可读取；按每个 `WIPRecordId` 的动态 Shipping/期末账本和真实生产批次仍未执行 | Partial（L/R 与 cohort 标签子集通过） | `iterations/I1/07.md`、`vsm-v11-initial-wip-cohort-evidence.md`、`09-simio-baseline-run-evidence.md`、`iterations/I1/08.md` | 建立按 WIPRecordId/ProductionBatch 的独立 cohort 审计，并完成关闭/重载回归 |
| VSM-17 | Issue 05、08 | 结构架构 | 静态检查 Facility 路线、Data Table、初始 WIP Process、普通生产 Source、状态/表引用及命名；执行原生诊断 | 初始 WIP 由 Data Table + 专用 Process 初始化；普通生产释放与初始装载职责分开；目标位置有效；诊断 0 errors；静态检查结果与运行证据对应同一模型身份 | V0.10 当前候选已核对 20 个对象、15 个节点、11 条业务命名链接、6 张表、初始 WIP/生产/位置/Shipping 过程和公共 Output Statistic；诊断 0 errors，回归 0 warnings；另存/重载仍未完成 | Passed（当前会话静态结构范围） | `iterations/I1/05.md`、`03-model-contract.md`、`09-simio-baseline-run-evidence.md` | 用户另存并重载 V0.10 后复核对象/引用/描述及诊断，与 VSM-14 一起关闭持久化范围 |
| VSM-18 | Issue 06、07、08 | 需求分配和按期件数满足率 | 方案 A：每日 L600/R320，55,200s/工作日，分产品 FIFO、部分交付；F01–F07 | 需求=准时+迟交+未交；供应守恒；件数误差0；正确处理同刻和第20天；比率0–100%，0分母N/A | 用户确认规则，需求表解析核对通过；无原生小例或服务运行结果 | Planned | `iterations/I1/07-fill-rate-contract.md`、`data/demand-due-calendar.csv`、A-021 | 实现 FG/需求/发运分配，先小例、再完整确定性回归、再独立复制 |

## V0.7–V0.11 当前运行证据

当前候选为 `VSM_V0.7_InitialWIPTable`，运行长度 `306.6666667 h`，无预热、随机性关闭。初始 WIP 为 17,130 件/857 实体，生产释放为 18,400 件/920 实体，加权 Shipping 为 19,630 件，期末加权 WIP 为 15,900 件；模型诊断为 0 errors，运行警告为 0。该证据覆盖计算批次的聚合工作内容和持久化回归，不覆盖物理托盘、批内时序、位置级动态、日历、换型、故障、Fill Rate 或 V0.6 详细指标等价性。

V0.9 独立保存包的当前会话回归复现相同的总量、实体和 L/R 分组结果；它已进入持久化回归队列，但尚未完成关闭/重新打开后的原生检查。因此 V0.9 的结果可用于继续模型增量和审计，不可作为已完成重载的正式交接版本。

V0.10 公共模型骨架候选在 V0.9 上只增加业务命名、中文说明和模型阶段标识。当前会话和独立保存包身份核对通过，确定性回归复现 18,400 件生产释放、19,630 件加权 Shipping、15,900 件期末加权 WIP、实体 `1,777 - 982 = 795`、0 errors 和 0 warnings；文件哈希为 `B719029E9A04AD2DD2F93E0594C5C06BE79087DC2D62BC66B58DAD186FCC1CAF`。关闭/重开仍待完成，不能把当前会话证据当作已完成的重载交接证据。

V0.11 初始流程候选在 V0.10 上增加初始 WIP 的表行引用复制和 `WIP:<WIPRecordId>` 实体标签。保存包文件为 `models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx`，SHA-256 为 `D023F7420FF2E1FF21046A0E9481E64E3268CD7B2C7EC7F8D0532C9A606D6F52`。复位态首尾实体分别为 `WIP:InitialWIP_W01_L` 和 `WIP:InitialWIP_W05_R`，初始实体数为 857；保存后的活动会话回归复现 18,400 件释放、19,630 件发运、15,900 件期末加权 WIP、实体 `1,777 - 982 = 795`、0 errors 和 0 warnings。该证据证明 cohort 标签写入实体状态，不证明逐行动态账本已经完成；V0.11 关闭/重开仍待执行。

V0.4 的高实体数量警告和未重载记录只属于历史逐件原型；不得用于否定 V0.7 的当前回归，也不得与 V0.7 的指标混合成一个基线结果。

## 进入正式 B0/B1 的条件

必须关闭或明确接受 VSM-03、VSM-06、VSM-07、VSM-08、VSM-09、VSM-10、VSM-11、VSM-12、VSM-15、VSM-16、VSM-18 的适用边界。Issue 07 统计契约已验收，不代替这些测试和 R1 复制运行。B0/B1 的模型、输入快照、运行设置和证据必须能通过同一版本身份复现；否则 Issue 09 保持 `Blocked / HOLD`。

## 运营确认边界

本案例是书中示例，没有真实工厂逐日交易数据。即使 VSM-13 通过，也只能说明模型与作者公开案例输出在指定口径下相符，不等于完成真实工厂运营确认。
