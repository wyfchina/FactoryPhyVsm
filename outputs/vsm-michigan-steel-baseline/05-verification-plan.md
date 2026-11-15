# VSM 基线验证计划

## 2026-11-15：V0.12 当前增量状态（优先于下文历史矩阵）

`VSM_V0.12_FlowDemandLedgerCandidate`的实现、用户保存关闭重开和原生回读均通过；保存包SHA为`73A98D963B756E485D6EB8B2A460954391047ED229290A823CEEB6CE9BFDD62F`。06限定验收范围的Wu业务评审待确认；Issue 08 的确定性验证与守恒范围已通过，R1统计研究、20件聚合时序适用性和09作者对照仍未完成。验收明细见[06实施记录](iterations/I1/06-V012-implementation-evidence.md)和[Issue 08闭环证据](issue08-closure-evidence.md)。下文V0.7–V0.11数值和“待实现”描述保留为当时的历史状态；不能用于否定新证据，也不能据新证据认定所有研究门通过。

| 测试 | 最新直接证据与结论 | 剩余责任 |
|---|---|---|
| VSM-03、08 | 初始11来源含W03-R10件尾批；15来源全程件数平衡0；旧行为D0回归发运19,630，期末15,900；V0.12保存重载逐行一致 | 09后续复核统计适用性 |
| VSM-05、06 | 工序容量仍1；q20/q1确定性整月参照已完成，履约一致但完工差15件、已完成CT差14.7333分钟 | 20件不具备逐件时序完全等价；09定精度并做随机/近交期适用性测试 |
| VSM-07 | t0/第11日释放、每日及第20日末、due±1秒原生验证通过；整数有效秒绝对日界+晚优先级，不添加额外时间 | V0.12保存重载已回归；09继续统计复制 |
| VSM-09 | M01双向产品切换、首件不换型、同类不换型；1h/0.167h只计一次 | 仅当前会话机制Passed，完整统计由09处理 |
| VSM-10 | M02故障后续剩余工作；M03空闲故障；指数MTTF/MTTR已消费权威表 | 目标85%/80%的观测CI、30独立复制和种子平台映射仍归09；总体Partial |
| VSM-11 | M04空系统：创建2/销毁2、六处容量占用0；故障恢复无重抽；整月正常流程容量无重叠 | 未纳入取消/报废业务，不能将这些路径标Passed |
| VSM-12 | 最终同原生复制两次整月输出逐行相同、复位清表；诊断0/警告0；M05观测日志开关不改变业务输出 | 单轨迹自测不是随机研究结果；09统计责任保留 |
| VSM-14 | V0.12保存包SHA、模型身份、结构、诊断和输出逐行回读与保存前一致 | 业务评审仍单独登记 |
| VSM-15、16 | 15来源×6位置×21时点=1,890快照，全部来源平衡差0；P1/P2实际释放和批次完整/不完整响应可追溯；实体与件数分别守恒；保存重载一致 | 09继续检验20件时序适用性 |
| VSM-18 | F01–F07全部通过；M04部分发运有独立时间戳/CT/FGWait；月末不漏第20日；保存重载一致 | R1独立复制和统计适用性待09验收 |
| VSM-13 | 未执行作者比较 | 09仍Blocked / HOLD；不能用本次99.1848%单轨迹数值替代作者算法 |

机器可读证据：`evidence/issue06-acceptance-summary.json`、`issue06-F01-F07-summary.json`、`issue06-mechanisms-summary.json`、`issue06-CT-batch-summary.json`、`issue06-observation-neutrality.json`、`issue06-aggregation-comparison.json`及对应原生运行记录。06、08与B0/B1状态独立判断。

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

Issue 07 现按指标与统计规范验收 Passed；06承接实现、08承接的确定性执行已通过、09承接随机研究和作者对照。所有小时为有效工时：55,200 秒/工作日，20 日 1,104,000 秒，不插入非工作时间；加工、排队、换型和故障/维修依机制计时。需求同刻和终点行为已有 V0.12 原生验证证据。见 [07 闭环证据](issue07-closure-evidence.md)。

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
| 05 | VSM-17 | V0.10 公共骨架验收范围已通过；V0.12在同一骨架上另行核对完整结构、表/过程/State引用和原生诊断 | `iterations/I1/05.md`、`03-model-contract.md`、`evidence/issue06-persistence-structure-readback.json` |
| 06 | VSM-05–12、14–16、18 | V0.12已实现初始WIP动态台账、输出表、生产批次、CT、方案A履约、换型/故障和保存重载；技术范围Passed，业务评审待确认；20件时序近似交09研究 | `iterations/I1/06.md`、`iterations/I1/06-V012-implementation-evidence.md`、`evidence/issue06-acceptance-summary.json` |
| 07 | VSM-12、13、16、18（定义责任） | Passed（指标与统计规范）；CT、批次、R1、方案 A 和有效工时已冻结；06实现、08确定性执行已完成，09随机研究和作者对照仍待完成，测试状态按范围分别报告 | `iterations/I1/07.md`、`iterations/I1/07-fill-rate-contract.md`、`data/demand-due-calendar.csv`、`issue07-closure-evidence.md` |
| 08 | VSM-02、03、05–12、14–18 | **Passed（确定性验证与守恒范围）**：V0.12机制小例、F01–F07、分层守恒、保存重载和固定复制回归已通过；R1独立随机复制、95%CI、目标可用率观测、种子映射和20件适用性转交后续研究 | `iterations/I1/08.md`、`issue08-closure-evidence.md`、`evidence/issue06-acceptance-summary.json`、`evidence/issue06-aggregation-comparison.json` |
| 09 | VSM-13 | 作者结果对照未运行；正式 B0/B1 为 Blocked / HOLD | `iterations/I1/09.md`、`02-source-extraction.md` |

反向映射也必须在 `iterations/I1/01.md`–`09.md` 的“验证计划映射”段落中出现。某项 Issue 没有 VSM 测试时，应明确标注为文档/治理验收，而不是留下未说明的空缺。

## 测试矩阵

2026-11-15同步检查：02–05按各自文档验收范围以completed关闭；01治理Passed已登记在仍Open的#1总览。06 V0.12技术证据和线上进度在本轮同步；业务评审待Wu确认。08已按本文件限定的确定性验证与守恒范围形成闭环，R1统计、20件时序适用性和作者对照仍由后续研究/09承接。02–05历史回执见[同步结果](issue01-06-sync-result.md)。

| ID | 负责 Issue | 类别 | 配置/方法 | 通过判据与容差 | 实际结果 | 状态 | 证据 | 下一步/失败处理 |
|---|---|---|---|---|---|---|---|
| VSM-01 | Issue 02、03 | 来源转录与输入快照 | 对照 Figure 9-1、Table 9-1、Figure 9-2 | 五道工序、产品、需求、WIP、过程参数与来源逐项有来源；数值字段按输入单位精确对账 | 来源字段、单位、派生值和实现选择已分开登记并通过输入级复核；运行实现由 VSM-07/10/17 验证 | Passed（来源/输入快照范围） | `02-source-extraction.md`、`data/*.csv`、`input-snapshot-manifest-v0.9.md` | 保留输入哈希；运行级验证由对应测试负责 |
| VSM-02 | Issue 02、08 | 需求节拍 | 18,400 件/月、20 日/月 | 日需求=920 件/日；节拍=60 秒/件；件数误差 0 | V0.7 加权生产释放=18,400 件；解析值一致 | Passed（范围限定） | `04-expected-analytic-checks.md`、`vsm-v07-20piece-entity-evidence.md` | 保留为回归测试，不外推到日历可用性 |
| VSM-03 | Issue 03、08 | WIP 对账 | 汇总 `wip-initial.csv`，核对 V0.7/V0.9/V0.12 初始化和期末加权 WIP | 工序 WIP=12,990、FG=4,140、初始有件数=17,130；W03-R=850；L/R=11,200/5,930；误差 0 | V0.12保存回读含15来源和逐来源动态State，1,890位置快照的来源平衡差均为0 | Passed（来源/位置确定性范围） | `evidence/issue06-persistence-readback.json`、`evidence/issue06-persistence-structure-readback.json` | 随机统计及20件时序适用性由09扩展 |
| VSM-04 | Issue 02 | 价值时间 | 累加五道工序过程时间 | 188 秒=3.1333 分钟；不含换型、等待；算术误差 < 1e-9 秒 | 解析值已独立复算 | Passed（解析范围） | `04-expected-analytic-checks.md` | 运行模型中另行核对加权处理时间 |
| VSM-05 | Issue 04、06、08 | 能力边界 | 单操作员、无额外有效时间 | Assembly #1 名义负荷=62/60=103.33%；模型不得用统计上限掩盖超载 | V0.9能力解析范围与V0.12单资源约束保持；Assembly #1持续满负荷并形成积压，现场日历含义不属于本项目时间轴 | Partial（能力边界范围已通过） | `04-expected-analytic-checks.md`、`iterations/I1/04.md`、`iterations/I1/06-V012-implementation-evidence.md` | 业务适用性由09结合有限期统计判断 |
| VSM-06 | Issue 02、06、08 | 批量语义 | 20 件计算实体；L/R 生产批量 6,000/3,200，每 10 个工作日于 Stamping 前释放 | 来源件数守恒；标准实体权重 20；尾批保留；计算实体不冒充物理托盘 | V0.12来源、生产和尾批数量守恒通过；q20/q1整月履约量相同，但制造完成相差15件、完成CT加权均值相差14.7333分钟 | Passed（加权数量/机制范围）；时序适用性归09 | `evidence/issue06-aggregation-comparison.json`、`evidence/issue06-persistence-readback.json` | 09判断精度是否满足后续比较用途 |
| VSM-07 | Issue 03、06、08 | 有效工时与事件边界 | A-022：仅计有效工时，两班×27,600秒/日 | 20日=1,104,000秒；不插入非工作间隔；释放/到期/终点顺序正确 | V0.12验证10日释放、日需求、due±1秒、同刻完工及第20日末，时间不加epsilon；保存重载一致 | Passed（确定性事件边界）；随机事件统计归09 | `evidence/issue06-F01-F07-summary.json`、`evidence/issue06-persistence-readback.json` | 统计复制与研究映射由09承接 |
| VSM-08 | Issue 06、08 | 初始状态 | `VSM_InitialWIPTable` + `VSM_InitializeWIP` Process；W05独立暂存并按需求供货 | 初始件数、位置、产品和来源ID一致；总量/实体守恒；误差0 | V0.12保存回读含11个初始来源子批、10件尾批，W05按批准方案A进入成品供货；逐来源账本全程平衡0 | Passed（实现/确定性范围） | `evidence/issue06-persistence-readback.json`、`evidence/issue06-d0-ledger-regression.json` | 20件时序适用性由09继续评估 |
| VSM-09 | Issue 06、08 | 换型 | L→R、R→L 各做一次确定性小例 | 只在定义资源发生；换型时间只计一次；顺序和总时长可解释 | M01序列验证首件0、同产品0、L↔R各一次；时间分列且不重复计 | Passed（机制小例） | `evidence/issue06-M01-changeover-LLRRLL.json` | 统计复制中换型响应归09 |
| VSM-10 | Issue 03、06、08 | 故障可用率 | 机制小例；多复制观测目标85%/80% | 目标可用率、容差、运行长度、复制数及95% CI须报告 | M02/M03验证指数故障、含待机uptime、维修后续作；30复制和置信区间尚未执行 | Partial（机制通过，目标统计待09） | `evidence/issue06-M02-failure-resume.json`、`evidence/issue06-M03-idle-failure.json`、`assumptions-register.csv` | 09映射随机流并执行独立复制 |
| VSM-11 | Issue 06、08 | 资源释放与异常 | 正常完工、故障续作、空系统退出 | 范围内无资源/队列泄漏；件数和实体数守恒 | M04空系统创建2/销毁2/剩余0、六处容量归零；正常完工和维修续作通过；取消/报废未纳入 | Passed（本Issue承诺的正常路径）；异常业务仍待定义 | `evidence/issue06-M04-CT-complete-batch-partial-shipment.json` | 若纳入取消/报废，另建生命周期测试 |
| VSM-12 | Issue 06、07、08 | 候选状态响应 | D0：V0.12，306.6666667有效小时，无预热 | 运行错误=0、警告=0；件数和实体守恒误差0；指标口径与版本一致 | 来源、需求、位置、发运、库存、批次平衡差均为0；固定复制两次输出逐行一致；诊断0、警告0 | Passed（确定性回归）；随机统计归09 | `evidence/issue06-acceptance-summary.json`、`evidence/issue06-observation-neutrality.json` | 09独立复制和统计检验 |
| VSM-13 | Issue 07、09 | 作者结果对照 | R1/B2 仅在 CT、服务指标和运行总体可比后比较 14.8/12.8 日等结果 | 明确已复现、条件性支持或未复现；附差异、删失、复制和输入版本 | 项目 CT/方案 A/R1 已确认；作者软件的 Fill Rate 算法和统计总体尚未映射，B2 未运行 | Blocked / Planned | `iterations/I1/07.md`、`iterations/I1/07-fill-rate-contract.md`、`02-source-extraction.md` | 区分项目按期件数满足率与作者算法，不能直接等同 |
| VSM-14 | Issue 06、08 | 持久化与重载 | 保存V0.12，关闭重开、诊断并重跑同复制回归 | 模型身份、输入和输出保持一致；诊断0 errors、运行警告0 | V0.12 SHA、身份、结构核查通过；11张表完整读回，运行摘要与保存前逐行相同，诊断0、警告0 | Passed（V0.12持久化范围） | `evidence/issue06-persistence-readback.json`、`evidence/issue06-persistence-structure-readback.json` | 09继续随机复制和输出精度审核 |
| VSM-15 | Issue 06、08 | 位置级动态守恒 | 确定性运行按6个位置、21个时点盘点加权件数 | 每个来源/位置期初+流入-流出=期末；误差0件 | V0.12共1,890条来源×位置快照，来源平衡差全0；保存重载一致 | Passed（来源/位置确定性范围） | `evidence/issue06-persistence-readback.json` | 统计精度由09评估 |
| VSM-16 | Issue 06、07、08 | 产品/批次分组守恒 | 按来源ID、产品L/R、P1/P2真实工单核对动态账本 | 各来源及产品满足计划/实际流入=发运+在制/期末剩余；误差0件 | 15来源State逐行更新；四张生产工单逐行响应；来源/产品/批次差全0 | Passed（数量/来源范围）；20件时序近似另由09评审 | `evidence/issue06-persistence-readback.json`、`evidence/issue06-d0-ledger-regression.json` | 09决定20件离散粒度的决策精度 |
| VSM-17 | Issue 05、08 | 结构架构 | 静态检查 Facility 路线、Data Table、初始 WIP Process、普通生产 Source、状态/表引用及命名；执行原生诊断 | 初始 WIP由Data Table+专用Process初始化；生产释放与初始装载职责分开；表/过程/状态引用有效；诊断0 errors | V0.12保存重载结构检查163项全部通过，覆盖35个VSM业务过程、输入/输出表、时间单位、模型/实体State及参数；诊断0 errors；结构回读证据和运行证据绑定同一SHA | Passed（V0.12结构范围） | `evidence/issue06-persistence-structure-readback.json`、`evidence/issue06-persistence-readback.json` | 09按同一身份继续随机复制和统计检验 |
| VSM-18 | Issue 06、07、08 | 需求分配和按期件数满足率 | 方案A：每日L600/R320，55,200s/工作日，分产品FIFO、部分交付；F01–F07 | 需求=准时+迟交+未交；供应守恒；误差0；同刻和第20日正确；分母0时N/A | F01–F07、部分交付、同刻与第20日末通过；全程需求/供给平衡差0；保存重载输出一致 | Passed（确定性实现范围）；R1统计归09 | `evidence/issue06-F01-F07-summary.json`、`evidence/issue06-CT-batch-summary.json`、`evidence/issue06-persistence-readback.json` | 完成30复制和Fill Rate CI，再与作者口径比较 |

## V0.7–V0.11 历史运行证据

当前候选为 `VSM_V0.7_InitialWIPTable`，运行长度 `306.6666667 h`，无预热、随机性关闭。初始 WIP 为 17,130 件/857 实体，生产释放为 18,400 件/920 实体，加权 Shipping 为 19,630 件，期末加权 WIP 为 15,900 件；模型诊断为 0 errors，运行警告为 0。该证据覆盖计算批次的聚合工作内容和持久化回归，不覆盖物理托盘、批内时序、位置级动态、日历、换型、故障、Fill Rate 或 V0.6 详细指标等价性。

V0.9 独立保存包的当前会话回归复现相同的总量、实体和 L/R 分组结果；它已进入持久化回归队列，但尚未完成关闭/重新打开后的原生检查。因此 V0.9 的结果可用于继续模型增量和审计，不可作为已完成重载的正式交接版本。

V0.10 公共模型骨架候选在 V0.9 上只增加业务命名、中文说明和模型阶段标识。当前会话和独立保存包身份核对通过，确定性回归复现 18,400 件生产释放、19,630 件加权 Shipping、15,900 件期末加权 WIP、实体 `1,777 - 982 = 795`、0 errors 和 0 warnings；文件哈希为 `B719029E9A04AD2DD2F93E0594C5C06BE79087DC2D62BC66B58DAD186FCC1CAF`。关闭/重开仍待完成，不能把当前会话证据当作已完成的重载交接证据。

V0.11 初始流程候选在 V0.10 上增加初始 WIP 的表行引用复制和 `WIP:<WIPRecordId>` 实体标签。保存包文件为 `models/VSM_MichiganSteel_V0.11_InitialWIPCohortCandidate.spfx`，SHA-256 为 `D023F7420FF2E1FF21046A0E9481E64E3268CD7B2C7EC7F8D0532C9A606D6F52`。复位态首尾实体分别为 `WIP:InitialWIP_W01_L` 和 `WIP:InitialWIP_W05_R`，初始实体数为 857；保存后的活动会话回归复现 18,400 件释放、19,630 件发运、15,900 件期末加权 WIP、实体 `1,777 - 982 = 795`、0 errors 和 0 warnings。该证据证明 cohort 标签写入实体状态，不证明逐行动态账本已经完成；V0.11 关闭/重开仍待执行。

V0.4 的高实体数量警告和未重载记录只属于历史逐件原型；不得用于否定 V0.7 的当前回归，也不得与 V0.7 的指标混合成一个基线结果。

## 进入正式 B0/B1 的条件

必须关闭或明确接受 VSM-03、VSM-06、VSM-07、VSM-08、VSM-09、VSM-10、VSM-11、VSM-12、VSM-15、VSM-16、VSM-18 的适用边界。Issue 07 统计契约已验收，不代替这些测试和 R1 复制运行。B0/B1 的模型、输入快照、运行设置和证据必须能通过同一版本身份复现；否则 Issue 09 保持 `Blocked / HOLD`。

## 运营确认边界

本案例是书中示例，没有真实工厂逐日交易数据。即使 VSM-13 通过，也只能说明模型与作者公开案例输出在指定口径下相符，不等于完成真实工厂运营确认。
