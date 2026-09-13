# Regulatory and Industry Data Contracts

> **Status**: Draft · **Date**: 2026-09-09
>
> **Decision state**: **FIX 版本已定为 4.4**（§3.1）。第一批五种报文的候选字段矩阵已按
> FIX 4.4 with 20030618 Errata 核对（§3.2 至 §3.3.1）；第一条最小订单生命周期 L-1
> 已填实（§3.4 至 §3.6）。本批次未扩展到撤单、改单和拒绝场景的完整状态机。
>
> **2026-09-12 追加**：三份 MDR 的 Part 1 至 Part 3 已读完（§4C）。Part 2 的具名约束把
> 两条此前记为 CMOP 决定的校验改判为规范要求，并为 S-2 的时点判定补上第二处独立出处。
>
> **Related**: [业务目标](business-objectives.md)、[原始数据源清单](raw-data-source-inventory.md)

## 1. 本文的作用与边界

Bronze 用真实的行业与监管报文标准装合成事实。本文记录这些标准里**被本项目实际使用的
最小子集**：字段、代码表、校验规则及其出处。

不追求覆盖完整性。FIX 与 ISO 20022 的完整规范合计上千页，而当前阶段的总预算有限。
判断标准只有一条：**够不够定义 Bronze 的 schema**。够了就停。

每个字段必须留下出处：规范名称、版本、章节或标签号。没有出处的条目保持 `待核对`。

## 2. 阅读顺序与当前范围

| 批次 | 范围 | 状态 |
|---|---|---|
| 第一批 | FIX 订单生命周期：新建、撤改、成交回报、状态机 | 五种报文的字段矩阵已核对；L-1 已填实 |
| 第二批 | FIX 分配指令与确认 | 七种报文的字段矩阵与规范自带流程已核对；A-1 与 C-1 已冻结 |
| 第三批 | ISO 20022 结算报文族 | 三种核心报文已从规范 XSD 与 MDR 核对；S-1 已冻结；状态转移已取得 |
| 第四批 | ISO 20022 资金报文族 | 十二种报文已核对；External Code Sets 已取得；**P-1 已冻结，六段链条闭合** |
| 第五批 | FINTRAC，仅取规则版本化所需语义 | 未开始，已降级 |
| 不做 | CIRO 深入报送规格、SEC EDGAR XBRL | 排除 |

## 3. FIX

### 3.1 版本决定：FIX 4.4

**已定案：全项目统一使用 FIX 4.4 with 20030618 Errata，不混用版本。**
**该决定已于 2026-09-12 提升为 [ADR 0006](../adr/0006-fix-single-version-baseline.md)**，
本节保留选择理由，ADR 补的是被否决的选项、回滚代价与"不自定义字段"这条约束的位置。 勘误版是取证时实际
使用的文件，见 §7；本文以下所有标签号、枚举取值与语义一律以它为准，引用其他版本的资料必须
显式注明版本，不得默认等价。

选择理由，按权重排列：

1. **后台覆盖面是决定性的，已由规范原文证实。** Volume 5 的 Allocation Instruction 一节
   明确称 Confirmation 与 Allocation Report 是 **4.4 新增**的报文，费用与开支的传达职责
   由分配指令移交给它们。只要项目要讲"从订单一路对到确认"，4.2 即出局。

   **但原先的措辞有一半不准，已更正。** 分配语义并非 4.4 才有：同一页写明 4.4 之前该报文
   名为 Allocation、其应答名为 Allocation ACK。**4.4 新增的是确认，不是分配。**
   核对于 2026-09-10，出处 Volume 5 p. 12。
2. **5.0 SP2 与 FIX Latest 多出的能力对本项目无用。** 5.0 的主要改动是把会话层拆为独立的
   FIXT，而本项目不运行 FIX 引擎，是把应用层报文批量生成落盘，会话层价值为零。其余扩展
   字段只增加需核对的表面积，不增加工程难点。4.4 的真实存量也远大于 5.0。
3. **标准的现代性由 ISO 20022 承担。** 结算与资金侧走 `sese`、`camt`、`pacs`，本就是当前
   标准。FIX 只需覆盖前台到中台这一段，而这一段是 4.4 最稳的地盘。
4. **标签等号值裸格式与嵌套重复组是真实的工程难点。** 分配类报文含分配明细、杂项费用、
   参与方等多层重复组，摊平进 Silver 是外生问题，不是为演示制造的问题。这一点优于 FIXML。

**使用约定：只用标准标签，不自定义字段。** 遇到标准未覆盖的语义，在本文显式登记一条缺口
并说明如何绕开，不得私自加用户自定义标签。私有标签会让整套报文失去"由公开规范推导"的
可信度，而那正是合成事实数据可信的唯一支点。

**已知的可选加分项，本阶段不做。** 真实机构同时承接不同 FIX 版本的对手方流量，版本差异
本身制造对账差异，例如某字段一边有一边无、枚举集合不一致。这与[原始数据源清单](raw-data-source-inventory.md) §5.1 里两个官方汇率口径
属于同一类**外生的口径性差异**素材。但引入第二个版本需要多读一份规范，会拖住字段表。
决定先按 4.4 单版本冻结，等第一个纵切跑通后再评估。

### 3.2 报文类型

`MsgType` 为标签 35。以下为第一批范围内的类型，取值以 FIX 4.4 为准。

| MsgType | 名称 | 用途 | 状态 |
|---|---|---|---|
| `D` | NewOrderSingle | 新建订单 | 已核对，V4 “New Order - Single” |
| `F` | OrderCancelRequest | 撤单请求 | 已核对，V4 “Order Cancel Request” |
| `G` | OrderCancelReplaceRequest | 改单请求 | 已核对，V4 “Order Cancel/Replace Request” |
| `9` | OrderCancelReject | 撤改被拒 | 已核对，V4 “Order Cancel Reject” |
| `8` | ExecutionReport | 成交与状态回报 | 已核对，V4 “Execution Reports” |

### 3.3 字段与报文的契约矩阵

原来的平铺清单只说"这些字段可能用得上"，无法回答"哪个报文上必须有它"。改为矩阵后，每一行
同时承载三件事：字段身份、逐报文的义务级别、以及出处。

**义务级别取值**：`必` 必填、`条` 条件必填、`选` 可选、`—` 不适用。条件必填必须在
§3.3.1 写明条件，只写 `条` 不写条件等于没写。

下表的义务级别是 **FIX 4.4 标准报文义务**，不是说每个字段在每条 Bronze 记录中都
非空。`进 Bronze` 标为“是（出现时）”表示 CMOP 不丢弃该标准字段；报文不适用或条件
不成立时，字段不出现，不伪造空值。

出处缩写（页码为各卷 PDF 页码）：`V4-NOS` 为 Volume 4 “New Order - Single” pp. 5–9，
`V4-ER` 为 “Execution Reports” pp. 10–20，`V4-OCRR` 为 “Order Cancel/Replace Request”
pp. 25–29，`V4-OCR` 为 “Order Cancel Request” pp. 30–31，`V4-OCJ` 为 “Order Cancel
Reject” pp. 32–33；`V1-Inst` 为 Volume 1 “Instrument component block”，`V1-Qty` 为
“OrderQtyData component block”，`V6` 为字段定义。

| 标签 | 名称 | D | F | G | 9 | 8 | 进 Bronze | 出处 | 核对日期 |
|---|---|---|---|---|---|---|---|---|---|
| 11 | ClOrdID | 必 | 必 | 必 | 必 | 条 | 是（出现时） | V4-NOS/OCR/OCRR/OCJ/ER | 2026-09-09 |
| 41 | OrigClOrdID | — | 必 | 必 | 必 | 条 | 是（出现时） | V4-OCR/OCRR/OCJ/ER | 2026-09-09 |
| 37 | OrderID | — | 选 | 选 | 必 | 必 | 是（出现时） | V4-OCR/OCRR/OCJ/ER | 2026-09-09 |
| 17 | ExecID | — | — | — | — | 必 | 是（出现时） | V4-ER | 2026-09-09 |
| 150 | ExecType | — | — | — | — | 必 | 是（出现时） | V4-ER；V6 tag 150 | 2026-09-09 |
| 39 | OrdStatus | — | — | — | 必 | 必 | 是（出现时） | V4-OCJ/ER；V6 tag 39 | 2026-09-09 |
| 1 | Account | 选 | 选 | 选 | 选 | 条 | 是（出现时） | V4-NOS/OCR/OCRR/OCJ/ER | 2026-09-09 |
| 55 | Symbol | 必 | 必 | 必 | — | 必 | 是（出现时） | V1-Inst；各报文的 Instrument 为必填 | 2026-09-09 |
| 48 | SecurityID | 选 | 选 | 选 | — | 选 | 是（出现时） | V1-Inst | 2026-09-09 |
| 22 | SecurityIDSource | 条 | 条 | 条 | — | 条 | 是（出现时） | V1-Inst | 2026-09-09 |
| 54 | Side | 必 | 必 | 必 | — | 必 | 是（出现时） | V4-NOS/OCR/OCRR/ER | 2026-09-09 |
| 38 | OrderQty | 条 | 条 | 条 | — | 条 | 是（出现时） | V1-Qty；V4-NOS/OCR/OCRR/ER | 2026-09-09 |
| 40 | OrdType | 必 | — | 必 | — | 选 | 是（出现时） | V4-NOS/OCRR/ER | 2026-09-09 |
| 44 | Price | 条 | — | 条 | — | 条 | 是（出现时） | V4-NOS/OCRR/ER | 2026-09-09 |
| 59 | TimeInForce | 选 | — | 选 | — | 选 | 是（出现时） | V4-NOS/OCRR/ER | 2026-09-09 |
| 32 | LastQty | — | — | — | — | 条 | 是（出现时） | V4-ER；V6 tag 32 | 2026-09-09 |
| 31 | LastPx | — | — | — | — | 条 | 是（出现时） | V4-ER；V6 tag 31 | 2026-09-09 |
| 14 | CumQty | — | — | — | — | 必 | 是（出现时） | V4-ER；V6 tag 14 | 2026-09-09 |
| 151 | LeavesQty | — | — | — | — | 必 | 是（出现时） | V4-ER；V6 tag 151 | 2026-09-09 |
| 6 | AvgPx | — | — | — | — | 必 | 是（出现时） | V4-ER；V6 tag 6 | 2026-09-09 |
| 60 | TransactTime | 必 | 必 | 必 | 选 | 选 | 是（出现时） | V4-NOS/OCR/OCRR/OCJ/ER | 2026-09-09 |
| 15 | Currency | 选 | — | 选 | — | 选 | 是（出现时） | V4-NOS/OCRR/ER | 2026-09-09 |
| 75 | TradeDate | 选 | — | 选 | 选 | 选 | 是（出现时） | V4-NOS/OCRR/OCJ/ER | 2026-09-09 |

出处至少写到卷与具名章节；页码稳定时一并登记。**没有出处的行不算已核对**，即使格子
填满了。

#### 3.3.1 条件必填的条件

每一个标为 `条` 的格子在此展开：字段、报文、触发条件、以及条件不成立时该字段的处理方式。
留空的条件必填字段在生成器里会变成静默的空值，而空值在下游读起来和"业务上确实没有"无法
区分。

| 标签 | 报文 | 条件 | 条件不成立时 | 出处 |
|---|---|---|---|---|
| 11 ClOrdID | ExecutionReport (`8`) | 电子提交的订单由机构或中介分配了 ClOrdID；CMOP 合成订单全部满足 | 仅手工录入且未分配 ClOrdID 的订单可不出现 | V4-ER |
| 41 OrigClOrdID | ExecutionReport (`8`) | 回应电子撤单或改单，且 `ExecType` 为 Pending Cancel、Replace 或 Canceled | 其他执行回报不出现 | V4-ER |
| 1 Account | ExecutionReport (`8`) | 电子提交的订单在原始订单上由机构或中介分配了 Account | 原始订单未分配账户时不出现 | V4-ER |
| 22 SecurityIDSource | `D`/`F`/`G`/`8` 的 Instrument | 出现 `SecurityID(48)` | 不出现；不得单独发送 tag 22 | V1-Inst |
| 38 OrderQty | `D`/`F`/`G` | `OrderQtyData` 为必填组件，且选用可交易单位数量；标准允许以 `CashOrderQty(152)` 或 CIV 的 `OrderPercent(516)` 代替 | 使用 tag 152 或 516；CMOP L-1 限定股数数量，因此实际不走代替分支 | V1-Qty；V4-NOS/OCR/OCRR |
| 38 OrderQty | ExecutionReport (`8`) | 单标的订单，除非是拒绝或确认使用 CashOrderQty/OrderPercent 的订单；CMOP L-1 全部满足 | 只在规范允许的 CashOrderQty/OrderPercent 拒绝或确认场景下不出现 | V4-ER |
| 44 Price | NewOrderSingle (`D`)、OrderCancelReplaceRequest (`G`) | `OrdType` 为限价类型 | 市价等不需要限价的类型不出现 | V4-NOS/OCRR |
| 44 Price | ExecutionReport (`8`) | 原始订单指定了 Price | 原始订单没有 Price 时不出现 | V4-ER |
| 32 LastQty | ExecutionReport (`8`) | `ExecType=F` (Trade) 或 `ExecType=G` (Trade Correct) | 非成交/成交更正回报不出现 | V4-ER |
| 31 LastPx | ExecutionReport (`8`) | `ExecType=F` (Trade) 或 `ExecType=G` (Trade Correct) | 非成交/成交更正回报不出现 | V4-ER |

### 3.4 订单状态机

从 Volume 4 “Order State Change Matrices” 抄录。FIX 4.4 原文明确提醒：**矩阵没有展示某个
转移，不必然表示该转移被 FIX 禁止**。因此不得把合法矩阵的简单补集写成“FIX 非法
转移”。

本批次只填 L-1 使用的 A.1.a 路径。表中“不合法（L-1）”是 **CMOP 场景契约违规**，
不宣称在其他 FIX 工作流中也非法。

| 起始状态 | 事件 | 目标状态 | 合法 | 出处 |
|---|---|---|---|---|
| 未确认（尚无 OrdStatus） | ExecutionReport: `ExecType=0` (New) | `OrdStatus=0` (New) | 是 | V4 A.1.a，步骤 1→2 |
| New (`0`) | ExecutionReport: `ExecType=F` (Trade) | Partially Filled (`1`) | 是 | V4 A.1.a，首次部分成交 |
| Partially Filled (`1`) | ExecutionReport: `ExecType=F` (Trade) | Partially Filled (`1`) | 是 | V4 A.1.a，后续部分成交 |
| Partially Filled (`1`) | ExecutionReport: `ExecType=F` (Trade) | Filled (`2`) | 是 | V4 A.1.a，末次成交 |
| 未确认（尚无 OrdStatus） | 直接产生 L-1 的 Trade 回报，跳过 New 接受回报 | Partially Filled 或 Filled | 不合法（仅 L-1） | 项目推导：违反冻结的 L-1 顺序；非 FIX 全局禁止 |
| New (`0`) | L-1 的首笔 Trade 就结束整单 | Filled (`2`) | 不合法（仅 L-1） | 项目推导：L-1 要求至少两笔部分成交后再全部成交；FIX 本身允许单笔全成 |
| Filled (`2`) | 继续发送未配套更正/取消语义的 L-1 Trade | Partially Filled 或 Filled | 不合法（仅 L-1） | 项目推导：Filled 是 L-1 终点；后续 Trade Correct/Trade Cancel 属于未展开场景 |

### 3.5 已冻结的最小订单生命周期 L-1

**路径：新建 → 接受 → 部分成交 → 全部成交。**

选它作为第一条冻结路径的理由：它是**最短的、同时产生多事件链与数量类不变量的路径**。单笔
全成太退化，链上只有两个事件，验不了 `CumQty`、`LeavesQty` 与 `AvgPx` 中的任何一条，而
BQ-2 的解释链恰恰要求多事件。

| 步骤 | 报文 | MsgType | ExecType | OrdStatus | CumQty | LeavesQty | AvgPx | 出处 |
|---|---|---|---|---|---|---|---|---|
| 1 | 新建订单 | `D` | — | — | — | — | — | V4-NOS |
| 2 | 接受回报 | `8` | `0` (New) | `0` (New) | `0` | `Q` | `0` | V4 A.1.a；V6 tags 150/39 |
| 3 | 首次部分成交 | `8` | `F` (Trade) | `1` (Partially Filled) | `q₁` | `Q - q₁` | `p₁` | V4 A.1.a；V6 tags 150/39 |
| 4 | 后续部分成交（至少一次） | `8` | `F` (Trade) | `1` (Partially Filled) | `Σqᵢ` | `Q - Σqᵢ` | `Σ(qᵢ×pᵢ) / Σqᵢ` | V4 A.1.a；V6 tags 6/14/31/32 |
| 5 | 末次成交，全部成交 | `8` | `F` (Trade) | `2` (Filled) | `Q` | `0` | `Σ(qᵢ×pᵢ) / Q` | V4 A.1.a；V6 tags 6/14/31/32/151 |

`Q` 是 `OrderQty(38)`，`qᵢ`/`pᵢ` 分别是第 i 笔成交的 `LastQty(32)`/`LastPx(31)`。
L-1 要求至少两笔部分成交，再以一笔末次成交结束（即至少三笔 Trade），且每笔 `qᵢ > 0`；
末笔之前 `Σqᵢ < Q`，末笔之后 `Σqᵢ = Q`。

**冻结的含义**：这条路径的报文序列与各步终态一经填定即为基准。生成器按它产出，验证规范按它
写断言，两侧不得各自解释。改动它需要在本节留下明确的变更记录，不能就地改表。

**L-1 不含**：撤单、改单、拒绝、跨日、部分成交后撤单。它们是后续路径，编号 L-2 起，在 L-1
填完并跑通之前不展开。

### 3.6 不变量与适用范围

三条规则已按 L-1 的适用范围填实。第一条是 FIX 明示带例外的通则；后两条由 FIX 字段语义
推导为 CMOP 验收规则，不冒充 FIX 原文。

| 不变量 | 依赖字段 | 适用条件 | 出处 | 结论 |
|---|---|---|---|---|
| `CumQty + LeavesQty = OrderQty` | `38 OrderQty`、`14 CumQty`、`151 LeavesQty`、`150 ExecType`、`39 OrdStatus` | L-1 的 New、Partially Filled 和 Filled 回报。不得无条件推广到 Canceled、DoneForTheDay、Expired、Calculated 或 Rejected，这些终止状态下 LeavesQty 可为 0 | V4 “Execution Reports” 通则；V6 tag 151 | **已核对：条件式** |
| 持仓等于历史成交累加 | `17 ExecID`、`150 ExecType`、`54 Side`、`48/22 SecurityID`、`32 LastQty`、`60 TransactTime` | 对 L-1 中去重后的 `ExecType=F` Trade，按买卖方向对 LastQty 求和。Trade Correct/Trade Cancel 尚未进入 L-1，扩展时必须改为净效应累加 | V6 tags 17/32/54/150；**CMOP 业务推导，非 FIX 显式不变量** | **L-1 已定** |
| `AvgPx` 与逐笔成交自洽 | `6 AvgPx`、`14 CumQty`、`31 LastPx`、`32 LastQty`、`150 ExecType` | L-1 的 Trade 回报：`CumQty=ΣLastQty`，`AvgPx=Σ(LastQty×LastPx)/CumQty`；New 接受回报中 `CumQty=0`、`AvgPx=0`。数值比较按后续 schema 冻结的价格精度进行 | V6 tag 6（所有 fills 的计算平均价）与 tags 14/31/32；公式为项目推导 | **L-1 已定** |

## 3A. 第二批：分配与确认

**第二批的七种报文已于 2026-09-10 全部核对完毕**，见 §3A.3 至 §3A.7。出处为 Volume 5
pp. 12–38 与 pp. 45–56，枚举值出处为 Volume 6 字段定义。规范自带的示例流程与拒绝场景
（V5 pp. 33–38 与 pp. 54–56）也已读完，结论写在 §3A.5 与 §3A.6。

**本节自身不作为出处，出处只能来自 FIX 4.4 卷本。**

### 3A.1 已定案：A-1 接在 L-1 之后

**决定于 2026-09-09。** 第二批不另起一段，A-1 以 L-1 的终态为输入。

理由：第一批冻结的 L-1 是一条走完的订单生命周期。若独立挑几条分配报文核对，得到的是互不
相连的片段，**而 BO-1 要证明的是一条链能从下单走到结算**。接续能让第二批结束时链条连续，
而不是多出一段孤立证据。

**本节的绑定契约现在生效，不依赖卷本；只有报文级取值待核对后填入 §3A.6。**

#### A-1 从 L-1 继承什么

| 项 | 来源 | 规则 |
|---|---|---|
| `OrderID` | L-1 接受步分配 | 直接引用，**不新编** |
| `ClOrdID` | L-1 新建步 | 直接引用 |
| 被分配数量 | L-1 终态的 `CumQty` | 直接引用；L-1 是全部成交，故等于 `OrderQty` |
| 均价 | L-1 各笔成交派生的 `AvgPx` | 直接引用，**不重算也不重采样** |
| 标的、买卖方向 | L-1 | 直接引用 |
| 交易日 | L-1 末笔 `TransactTime` 所属营业日 | 派生 |

**"不新编"是这张表的全部要点。** 任何一项在 A-1 里被重新生成，链条就断了：Bronze 里会出现
两个互不关联的订单标识，而逐笔追溯正是本项目的主张。

#### A-1 新引入什么，以及采样与派生的划分

沿用[合成数据生成规范](data-generation-specification.md) §6.1 的划分，**派生字段必须计算，
绝不允许采样**：

| 类别 | 内容 |
|---|---|
| 采样 | 分配账户数 N、各账户的分配比例 |
| 派生 | 各账户 `AllocQty`、分配层的均价与金额、分配总量 |

**数量拆分的坑与 §6.2 完全相同,解法也相同。** 把 `CumQty` 按比例切分再取整,会产生零数量
分配或合计对不上被分配数量。**必须按剩余量逐账户切分,每个账户至少一手,末个账户取精确余量**,
理由与 §6.2 一致:合计一旦错位,§3A.7 的第一条候选断言当场失效,生成器就产出了违反自身契约
的数据。

#### 由此暴露的一个缺口

**账户维度原本不存在,现已补上。** [合成数据生成规范](data-generation-specification.md) §3
只有标的维度,而 A-1 需要一组可分配的账户,账户本身也需要版本化。**这是 A-1 带出来的新工作,
不在原计划内**,已于 2026-09-10 定案,见该文档 §3A。

**补的过程里发现它与标的维度并不同类。** 开立、关闭、改名三类事件同构,**并户不是**:它是
跨键的多对一转移,单键上的 SCD Type 2 表达不了。契约定为并户绝不改写历史事实,细节见该文档
§3A.5。另外账户维度是自由参数,没有真实来源可继承,这一点与标的维度相反。

### 3A.2 报文类型与定位

**卷次已确认：Volume 5 “FIX Application Messages: Post-Trade”。** 该卷开篇将后台报文定义为
"typically communicated after the placement and successful execution of an order and prior to
settlement"，并分为七类，其中 ALLOCATION 与 CONFIRMATION 是第一、第二类。

以下页码取自 Volume 5 目录（`V5` 即该卷 PDF 页码），**报文名称已由目录证实，`MsgType`
标签值仍待从各报文定义页核对**：

| 报文 | 页码 | 在 A-1 中的角色 | MsgType |
|---|---|---|---|
| Allocation Instruction | V5 p. 12 | 发起分配 | **J**，已核对 |
| Allocation Instruction Ack | V5 p. 21 | 受理或拒绝 | **P**，已核对 |
| Allocation Report（aka Allocation Claim） | V5 p. 23 | 分配结果回报 | **AS**，已核对 |
| Allocation Report Ack（aka Allocation Claim Ack） | V5 p. 31 | 回报确认 | **AT**，已核对 |
| Confirmation | V5 p. 47 | 逐账户确认 | **AK**，已核对 |
| Confirmation Ack（aka Affirmation） | V5 p. 52 | 确认的应答 | **AU**，已核对 |
| Confirmation Request | V5 p. 53 | 索取确认 | **BH**，已核对 |

**另有两处现成的流程与拒绝场景可直接对照**：分配的示例流程与拒绝场景在 V5 pp. 33–38，
确认的示例用法与被拒确认在 V5 pp. 54–56。**填 §3A.5 状态机与 §3A.8 场景时应先读这两处**，
它们是规范自己给出的流程，比从字段表反推可靠。确认侧的三个示例流程已按此读法填入 §3A.6。

**七种报文分成三组，方向不是一致的。** 这一点必须先记住，Bronze 的交易对手字段依赖它。

| 组 | 报文 | 方向 | 出处 |
|---|---|---|---|
| 分配指令 | J、P | 买方发起，卖方应答 | V5 p.37 流程 1 与 2 |
| 分配回报 | AS、AT | **卖方发起，买方应答** | V5 p.23、p.37 流程 3 |
| 确认 | AK、AU | **卖方发起，买方应答** | V5-CF p.45 |

V5-CF p. 45 原文写道，永远是 Respondent 生成 FIX Confirmation 报文。AS 的开篇同样写明它
从卖方发往买方、卖方发往第三方或第三方发往买方。**生成器若照搬 J 的方向，AS 与 AK 两段都会
写反。**

**版本断言已结清，且原措辞有一半不准确。** V5-AI p. 12 原文在说明分配报文历史时写道，
费用与开支的传达职责已从 Allocation Instruction 移出，改由 "the new (to version 4.4)
Allocation Report and Confirmation messages" 承担。**规范自己声明 Confirmation 与
Allocation Report 是 4.4 新增的**，无需再与 4.2 对照。

但同一页也写明：4.4 之前该报文名为 Allocation，其 Ack 名为 Allocation ACK。
**因此"分配语义 4.4 才有"是错的，分配一直都在。** 4.4 真正新增的是确认报文，以及把费用与
开支从分配指令里剥离出来。§3.1 的理由已按此改写。

### 3A.3 字段矩阵：七种报文已核对

出处缩写：`V5-AI` 为 Volume 5 “Allocation Instruction” pp. 12–20，`V5-AIA` 为
“Allocation Instruction Ack” pp. 21–22。义务级别照抄规范的 Req'd 列。

**规范自带两个条件标记，必须原样保留，不得压平成"必"**（V5-AI p. 20 尾注）：

- `Y*`：`AllocTransType=Cancel` 时不必填。
- `Y**`：`AllocTransType=Cancel` 时不必填，`AllocType` 为 Ready-To-Book 或 Warehouse
  instruction 时亦不必填。

| 标签 | 名称 | J | P | 进 Bronze | 出处 | 核对日期 |
|---|---|---|---|---|---|---|
| — | Standard Header | 必（`MsgType=J`） | 必（`MsgType=P`） | 是 | V5-AI p.14；V5-AIA p.21 | 2026-09-10 |
| 70 | AllocID | 必 | 必 | 是 | V5-AI p.14；V5-AIA p.21 | 2026-09-10 |
| 71 | AllocTransType | 必 | — | 是 | V5-AI p.14 | 2026-09-10 |
| 626 | AllocType | 必 | 选 | 是（出现时） | V5-AI p.14；V5-AIA p.21 | 2026-09-10 |
| 72 | RefAllocID | 条 | — | 是（出现时） | V5-AI p.14 | 2026-09-10 |
| 796 | AllocCancReplaceReason | 条 | — | 是（出现时） | V5-AI p.14 | 2026-09-10 |
| 857 | AllocNoOrdersType | 必 | — | 是 | V5-AI p.14 | 2026-09-10 |
| 73 | NoOrders | 条 | — | 是（出现时） | V5-AI p.14 | 2026-09-10 |
| 11 | ClOrdID | 条 | — | 是（出现时） | V5-AI p.14 | 2026-09-10 |
| 37 | OrderID | 选 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 38 | OrderQty | 选 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 799 | OrderAvgPx | 选 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 800 | OrderBookingQty | 选 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 124 | NoExecs | 选 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 32 | LastQty | 条 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 31 | LastPx | 条 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 17 | ExecID | 选 | — | 是（出现时） | V5-AI p.15 | 2026-09-10 |
| 54 | Side | 必 | — | 是 | V5-AI p.15 | 2026-09-10 |
| — | component `<Instrument>` | 必 | — | 是 | V5-AI p.15 | 2026-09-10 |
| 53 | Quantity | 必 | — | 是 | V5-AI p.16 | 2026-09-10 |
| 6 | AvgPx | 必 | — | 是 | V5-AI p.16 | 2026-09-10 |
| 15 | Currency | 选 | — | 是（出现时） | V5-AI p.16 | 2026-09-10 |
| 75 | TradeDate | 必 | 选 | 是 | V5-AI p.16；V5-AIA p.21 | 2026-09-10 |
| 60 | TransactTime | 选 | **必** | 是 | V5-AI p.16；V5-AIA p.21 | 2026-09-10 |
| 63 | SettlType | 选 | — | 是（出现时） | V5-AI p.16 | 2026-09-10 |
| 64 | SettlDate | 条 | — | 是（出现时） | V5-AI p.16 | 2026-09-10 |
| 381 | GrossTradeAmt | 选 | — | 是（出现时） | V5-AI p.16 | 2026-09-10 |
| 118 | NetMoney | 选 | — | 是（出现时） | V5-AI p.17 | 2026-09-10 |
| 87 | AllocStatus | — | **必** | 是 | V5-AIA p.21 | 2026-09-10 |
| 88 | AllocRejCode | — | 条 | 是（出现时） | V5-AIA p.21 | 2026-09-10 |
| 573 | MatchStatus | 选 | 选 | 是（出现时） | V5-AI p.18；V5-AIA p.22 | 2026-09-10 |
| 78 | NoAllocs | `Y**` | 选 | 是（出现时） | V5-AI p.17；V5-AIA p.22 | 2026-09-10 |
| 79 | AllocAccount | `Y**`（组内） | 条（组内） | 是（出现时） | V5-AI p.18；V5-AIA p.22 | 2026-09-10 |
| 80 | AllocQty | `Y**`（组内） | — | 是（出现时） | V5-AI p.18 | 2026-09-10 |
| 366 | AllocPrice | 选（组内） | 选（组内） | 是（出现时） | V5-AI p.18；V5-AIA p.22 | 2026-09-10 |
| 153 | AllocAvgPx | 选（组内） | — | 是（出现时） | V5-AI p.18 | 2026-09-10 |
| 154 | AllocNetMoney | 选（组内） | — | 是（出现时） | V5-AI p.19 | 2026-09-10 |
| 467 | IndividualAllocID | 选（组内） | 选（组内） | 是（出现时） | V5-AI p.18；V5-AIA p.22 | 2026-09-10 |
| 776 | IndividualAllocRejCode | — | 条（组内） | 是（出现时） | V5-AIA p.22 | 2026-09-10 |
| — | Standard Trailer | 必 | 必 | 否 | V5-AI p.20；V5-AIA p.22 | 2026-09-10 |

#### 确认侧：AK、AU、BH 已核对

出处缩写：`V5-CF` 为 Volume 5 “Confirmation” pp. 47–51，`V5-CFA` 为 “Confirmation Ack
(aka Affirmation)” p. 52，`V5-CFR` 为 “Confirmation Request” pp. 53–54。义务级别照抄规范的
Req'd 列，`—` 表示该字段不属于这张报文。

| 标签 | 名称 | AK | AU | BH | 进 Bronze | 出处 | 核对日期 |
|---|---|---|---|---|---|---|---|
| — | Standard Header | 必（`MsgType=AK`） | 必（`MsgType=AU`） | 必（`MsgType=BH`） | 是 | V5-CF p.47；V5-CFA p.52；V5-CFR p.53 | 2026-09-10 |
| 664 | ConfirmID | 必 | 必 | — | 是 | V5-CF p.47；V5-CFA p.52 | 2026-09-10 |
| 772 | ConfirmRefID | 条 | — | — | 是（出现时） | V5-CF p.47 | 2026-09-10 |
| 859 | ConfirmReqID | 条 | — | 必 | 是（出现时） | V5-CF p.47；V5-CFR p.53 | 2026-09-10 |
| 666 | ConfirmTransType | 必 | — | — | 是 | V5-CF p.47 | 2026-09-10 |
| 773 | ConfirmType | 必 | — | 必 | 是 | V5-CF p.47；V5-CFR p.53 | 2026-09-10 |
| 665 | ConfirmStatus | 必 | — | — | 是 | V5-CF p.47 | 2026-09-10 |
| 940 | AffirmStatus | — | 必 | — | 是 | V5-CFA p.52 | 2026-09-10 |
| 774 | ConfirmRejReason | — | 条 | — | 是（出现时） | V5-CFA p.52 | 2026-09-10 |
| 797 | CopyMsgIndicator | 选 | — | — | 是（出现时） | V5-CF p.47 | 2026-09-10 |
| 650 | LegalConfirm | 选 | — | — | 是（出现时） | V5-CF p.47 | 2026-09-10 |
| — | component `<Parties>` | 选 | — | — | 是（出现时） | V5-CF p.48 | 2026-09-10 |
| 73 | NoOrders | 选 | — | 选 | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 11 | ClOrdID | 条（组内） | — | 条（组内） | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 37 | OrderID | 选（组内） | — | 选（组内） | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 38 | OrderQty | 选（组内） | — | 选（组内） | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 799 | OrderAvgPx | 选（组内） | — | 选（组内） | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 800 | OrderBookingQty | 选（组内） | — | 选（组内） | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 70 | AllocID | 选 | — | 选 | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 467 | IndividualAllocID | 选 | — | 选 | 是（出现时） | V5-CF p.48；V5-CFR p.53 | 2026-09-10 |
| 60 | TransactTime | 必 | 必 | 必 | 是 | V5-CF p.48；V5-CFA p.52；V5-CFR p.53 | 2026-09-10 |
| 75 | TradeDate | 必 | 必 | — | 是 | V5-CF p.48；V5-CFA p.52 | 2026-09-10 |
| — | component `<Instrument>` | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 711 | NoUnderlyings | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 555 | NoLegs | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 80 | AllocQty | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 54 | Side | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 15 | Currency | 选 | — | — | 是（出现时） | V5-CF p.49 | 2026-09-10 |
| 862 | NoCapacities | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 528 | OrderCapacity | 必（组内） | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 863 | OrderCapacityQty | 必（组内） | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 79 | AllocAccount | 必 | — | 选 | 是 | V5-CF p.49；V5-CFR p.54 | 2026-09-10 |
| 6 | AvgPx | 必 | — | — | 是 | V5-CF p.49 | 2026-09-10 |
| 381 | GrossTradeAmt | 必 | — | — | 是 | V5-CF p.50 | 2026-09-10 |
| 118 | NetMoney | 必 | — | — | 是 | V5-CF p.50 | 2026-09-10 |
| 63 | SettlType | 选 | — | — | 是（出现时） | V5-CF p.50 | 2026-09-10 |
| 64 | SettlDate | 选 | — | — | 是（出现时） | V5-CF p.50 | 2026-09-10 |
| — | component `<SettlInstructionsData>` | 选 | — | — | 是（出现时） | V5-CF p.50 | 2026-09-10 |
| — | component `<CommissionData>` | 选 | — | — | 是（出现时） | V5-CF p.50 | 2026-09-10 |
| 136 | NoMiscFees | 选 | — | — | 是（出现时） | V5-CF p.51 | 2026-09-10 |
| 573 | MatchStatus | — | 选 | — | 是（出现时） | V5-CFA p.52 | 2026-09-10 |
| 58 | Text | — | 选 | 选 | 是（出现时） | V5-CFA p.52；V5-CFR p.54 | 2026-09-10 |
| — | Standard Trailer | 必 | 必 | 必 | 否 | V5-CF p.51；V5-CFA p.52；V5-CFR p.54 | 2026-09-10 |

**规范在这三张表里留下了三处自相矛盾，必须记下来，不能照抄。** 它们都是从分配侧复制字段行
时没有改干净的痕迹：

1. AK 的 `NoOrders`(73) 注释写"`AllocNoOrdersType = 1` 时必填"，但 `AllocNoOrdersType`(857)
   **不是 AK 的字段**（V5-CF pp. 47–51 全表无此标签）。该条件在 AK 上无法求值。
2. AU 的 `ConfirmRejReason`(774) 注释写"Required for `ConfirmStatus = 1` (rejected)"，但
   AU **没有 `ConfirmStatus`(665)**，而且 `ConfirmStatus = 1` 的含义是 Received 而非
   rejected（V6 p. 232）。按语义，正确的条件是 `AffirmStatus = 2`（Confirm rejected）。
3. AU 的 `Text`(58) 注释写"can include explanation for `AllocRejCode = 7` (other)"，但 AU 里
   没有 `AllocRejCode`，且 other 在 `ConfirmRejReason` 上的取值是 99 而非 7（V6 p. 266）。

**处理方式是登记而非改写。** 矩阵照抄规范的义务级别，§3A.4 记 CMOP 的取用口径并标明它是
推断。**不要把推断混进出处列**，否则下一个人无法分辨哪一条是规范说的。

**还有一处不是矛盾但同样容易踩。** `NoUnderlyings`(711) 与 `NoLegs`(555) 在 AK 里标为必填，
而 CMOP 的标的是普通股票，既无 underlying 也无 leg。**A-1 与 C-1 的取值定为 0**，这与"必填"
不冲突：必填的是计数字段本身，不是它下面的重复组。

#### 回报侧：AS、AT 已核对

出处缩写：`V5-AR` 为 Volume 5 “Allocation Report (aka Allocation Claim)” pp. 23–30，
`V5-ARA` 为 “Allocation Report Ack” pp. 31–32。AS 沿用与 J 相同的 `Y*` / `Y**` 标记，
**但 `Y**` 的第二个豁免条件不同**：AS 上是 `AllocReportType = "Warehouse recap"` 时不必填，
而 J 上是 `AllocType` 为 Ready-To-Book 或 Warehouse instruction 时不必填（V5-AR p.30 尾注）。

| 标签 | 名称 | AS | AT | 进 Bronze | 出处 | 核对日期 |
|---|---|---|---|---|---|---|
| — | Standard Header | 必（`MsgType=AS`） | 必（`MsgType=AT`） | 是 | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 755 | AllocReportID | 必 | 必 | 是 | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 70 | AllocID | 选 | **必** | 是 | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 71 | AllocTransType | 必 | — | 是 | V5-AR p.24 | 2026-09-10 |
| 795 | AllocReportRefID | 条 | — | 是（出现时） | V5-AR p.24 | 2026-09-10 |
| 796 | AllocCancReplaceReason | 条 | — | 是（出现时） | V5-AR p.24 | 2026-09-10 |
| 72 | RefAllocID | 条 | — | 是（出现时） | V5-AR p.24 | 2026-09-10 |
| 793 | SecondaryAllocID | 选 | 选 | 是（出现时） | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 794 | AllocReportType | 必 | 选 | 是 | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 87 | AllocStatus | **必** | **必** | 是 | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 88 | AllocRejCode | 条 | 条 | 是（出现时） | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 808 | AllocIntermedReqType | 条 | 条 | 是（出现时） | V5-AR p.24；V5-ARA p.31 | 2026-09-10 |
| 857 | AllocNoOrdersType | 必 | — | 是 | V5-AR p.24 | 2026-09-10 |
| 73 | NoOrders | 条 | — | 是（出现时） | V5-AR p.25 | 2026-09-10 |
| 11 | ClOrdID | 条（组内） | — | 是（出现时） | V5-AR p.25 | 2026-09-10 |
| 37 | OrderID | 选（组内） | — | 是（出现时） | V5-AR p.25 | 2026-09-10 |
| 800 | OrderBookingQty | 选（组内） | — | 是（出现时） | V5-AR p.25 | 2026-09-10 |
| 124 | NoExecs | 选 | — | 是（出现时） | V5-AR p.25 | 2026-09-10 |
| 32 | LastQty、31 LastPx | 条（组内） | — | 是（出现时） | V5-AR p.25 | 2026-09-10 |
| 54 | Side | 必 | — | 是 | V5-AR p.26 | 2026-09-10 |
| — | component `<Instrument>` | 必 | — | 是 | V5-AR p.26 | 2026-09-10 |
| 711 | NoUnderlyings | **选** | — | 是（出现时） | V5-AR p.26 | 2026-09-10 |
| 555 | NoLegs | **选** | — | 是（出现时） | V5-AR p.26 | 2026-09-10 |
| 53 | Quantity | 必 | — | 是 | V5-AR p.26 | 2026-09-10 |
| 6 | AvgPx | 必 | — | 是 | V5-AR p.26 | 2026-09-10 |
| 75 | TradeDate | 必 | 选 | 是 | V5-AR p.26；V5-ARA p.31 | 2026-09-10 |
| 60 | TransactTime | **选** | **必** | 是 | V5-AR p.26；V5-ARA p.31 | 2026-09-10 |
| 63 | SettlType、64 SettlDate | 选 | — | 是（出现时） | V5-AR p.26 | 2026-09-10 |
| 381 | GrossTradeAmt | 选 | — | 是（出现时） | V5-AR p.27 | 2026-09-10 |
| 118 | NetMoney | 选 | — | 是（出现时） | V5-AR p.27 | 2026-09-10 |
| 573 | MatchStatus | 选（组内） | 选 | 是（出现时） | V5-AR p.28；V5-ARA p.31 | 2026-09-10 |
| 892 | TotNoAllocs | 条 | — | 是（出现时） | V5-AR p.27 | 2026-09-10 |
| 893 | LastFragment | 条 | — | 是（出现时） | V5-AR p.27 | 2026-09-10 |
| 78 | NoAllocs | `Y**` | 选 | 是（出现时） | V5-AR p.28；V5-ARA p.32 | 2026-09-10 |
| 79 | AllocAccount | `Y**`（组内） | 条（组内） | 是（出现时） | V5-AR p.28；V5-ARA p.32 | 2026-09-10 |
| 80 | AllocQty | `Y**`（组内） | — | 是（出现时） | V5-AR p.28 | 2026-09-10 |
| 366 | AllocPrice | 选（组内） | 选（组内） | 是（出现时） | V5-AR p.28；V5-ARA p.32 | 2026-09-10 |
| 153 | AllocAvgPx | 选（组内） | — | 是（出现时） | V5-AR p.28 | 2026-09-10 |
| 154 | AllocNetMoney | 选（组内） | — | 是（出现时） | V5-AR p.29 | 2026-09-10 |
| 467 | IndividualAllocID | 选（组内） | 选（组内） | 是（出现时） | V5-AR p.28；V5-ARA p.32 | 2026-09-10 |
| 776 | IndividualAllocRejCode | — | 条（组内） | 是（出现时） | V5-ARA p.32 | 2026-09-10 |
| 780 | AllocSettlInstType | 选（组内） | — | 是（出现时） | V5-AR p.29 | 2026-09-10 |
| — | component `<SettlInstructionsData>` | 条（组内） | — | 是（出现时） | V5-AR p.30 | 2026-09-10 |
| — | Standard Trailer | 必 | 必 | 否 | V5-AR p.30；V5-ARA p.32 | 2026-09-10 |

**AS 与 J 长得像，但有四处必须分开对待，照抄会出错：**

1. **AS 带 `AllocStatus`(87)，J 不带。** 分配回报自己就声明状态，它不是一条待受理的指令。
2. **AS 的标识是 `AllocReportID`(755)，`AllocID`(70) 只是可选引用；而 AT 里 `AllocID` 是必填。**
   **应答强制要求一个回报本身可以不带的标识**，这是个真实的坑：生成器若在 AS 上省掉
   `AllocID`，就造不出合法的 AT。CMOP 口径是 AS 一律填 `AllocID`，回引对应的分配指令。
3. **`NoUnderlyings`(711) 与 `NoLegs`(555) 在 AS 里是可选，在 AK 里是必填。** 同一对字段在
   两张报文上义务级别不同，不能共用一套生成逻辑。
4. **`TransactTime`(60) 在 AS 里可选，在 AT 里必填**，与 J、P 那一对的方向相同。

**`Y**` 的豁免条件在 J 与 AS 上不同名也不同义**，这一条前面已单列。**把两者压平成一个"分配
类报文"的通用规则，是本节最容易犯的错。**

#### 骨架核对小结

**骨架里三个猜测被证伪，一处证实。** 骨架臆测的
`ConfirmID` 等四个确认字段不属于 J 与 P，已从本表移除，现已在上面的确认侧矩阵中各就各位。
骨架漏掉了
`AllocNoOrdersType`(857) 与 `AllocPrice`(366)，二者均已补入。`Commission`(12) 不是
J 的顶层字段，而在组内 `<CommissionData>` 组件块中，骨架写错了位置。

### 3A.4 条件必填的条件，已填

| 字段 | 报文 | 条件 | 出处 |
|---|---|---|---|
| RefAllocID(72) | J | `AllocTransType` 为 Replace 或 Cancel 时必填 | V5-AI p.14 |
| AllocCancReplaceReason(796) | J | 同上 | V5-AI p.14 |
| NoOrders(73) | J | `AllocNoOrdersType = 1`（Explicit list provided）时必填 | V5-AI p.14 |
| ClOrdID(11) | J | `NoOrders > 0` 时必填，且**必须是组内第一个字段** | V5-AI p.14 |
| AllocAccount(79) | J | `NoAllocs > 0` 时必填，且**必须是组内第一个字段** | V5-AI p.18 |
| LastQty(32)、LastPx(31) | J | `NoExecs > 0` 时必填 | V5-AI p.15 |
| SettlDate(64) | J | 对特定 `SettlType` 取值条件必填或必须省略，且优先于 `SettlType` | V5-AI p.16 |
| AllocRejCode(88) | P | `AllocStatus = 1` 时必填；`AllocStatus = 2` 且本报文未逐账户给出拒绝原因时必填 | V5-AIA p.21 |
| IndividualAllocRejCode(776) | P | `NoAllocs > 0` 时必填 | V5-AIA p.22 |
| NoAllocs(78) | P | 仅在 `AllocStatus = 2` 时可用；**其他取值下不得填充该组** | V5-AIA p.22 |
| ConfirmRefID(772) | AK | `ConfirmTransType` 为 Replace 或 Cancel 时必填 | V5-CF p.47 |
| ConfirmReqID(859) | AK | 仅在本报文用于应答一条 Confirmation Request 时使用 | V5-CF p.47 |
| ClOrdID(11) | AK、BH | `NoOrders > 0` 时必填，且**必须是组内第一个字段** | V5-CF p.48；V5-CFR p.53 |
| NoOrders(73) | AK、BH | 规范写 `AllocNoOrdersType = 1` 时必填，**但 857 不是这两张报文的字段**；CMOP 口径：该组整体可选，A-1 与 C-1 不填 | V5-CF p.48（矛盾见 §3A.3） |
| ConfirmRejReason(774) | AU | 规范写 `ConfirmStatus = 1` 时必填，**但 AU 无 665**；CMOP 口径：`AffirmStatus = 2` 时必填 | V5-CFA p.52（矛盾见 §3A.3） |
| EncodedTextLen(354) | AU | 出现 `EncodedText`(355) 时必填，且**必须紧邻其前** | V5-CFA p.52 |
| AllocReportRefID(795) | AS | `AllocTransType` 为 Replace 或 Cancel 时必填 | V5-AR p.24 |
| AllocCancReplaceReason(796)、RefAllocID(72) | AS | 同上 | V5-AR p.24 |
| AllocIntermedReqType(808) | AS、AT | `AllocReportType = 8`（Request to Intermediary）时必填 | V5-AR p.24；V5-ARA p.31 |
| AllocLinkType(197) | AS | 指定了 `AllocLinkID`(196) 时必填 | V5-AR p.24 |
| TotNoAllocs(892)、LastFragment(893) | AS | 仅在报文被分片时必填；`TotNoAllocs` 必须等于各分片 `NoAllocs` 之和 | V5-AR p.27 |
| AllocRejCode(88) | AS、AT | `AllocStatus = 1` 时必填；`AllocStatus = 2` 且未逐账户给出原因时必填 | V5-AR p.24；V5-ARA p.31 |
| NoAllocs(78) | AT | 仅在 `AllocStatus = 2` 时可用；**其他取值下不得填充该组** | V5-ARA p.32 |
| SettlInstructionsData | AS | 组内 `AllocSettlInstType = 2 或 3` 时必填 | V5-AR p.30 |

**注意 `NoAllocs`(78) 那条的方向。** 它不是"某条件下必填"，而是"其他条件下禁止出现"。
生成器若在 `AllocStatus = 0` 的 Ack 上带出 NoAllocs 组，就违反了规范，**而这类错误不会被
"必填"式校验发现**。

**表里有两行的出处列写着"矛盾见 §3A.3"，那是有意的。** 这两条不是规范原文，是 CMOP 在规范
自相矛盾处选的口径。**任何以它们为前提的下游断言都要标成推断，不能标成 FIX 明确。**

### 3A.5 状态机：AllocStatus、ConfirmStatus 与 AffirmStatus 已核对

#### 分配侧：AllocStatus

`AllocStatus`(87) 在 V5-AIA p.21 的报文页上列了四个取值，逐条抄录如下。
**但报文页不全，字段字典给的是六个**，缺的两个见 §3A.10。

| 取值 | 含义 | 规范原文要点 |
|---|---|---|
| 3 | received, not yet processed | 仅确认收到；**应当后接第二条状态为 0、1 或 2 的 Ack，或一条 Allocation Report** |
| 0 | accepted | 已校验并成功处理 |
| 1 | block level reject | 整条 Allocation Instruction 被拒；必须填 `AllocRejCode` |
| 2 | account level reject | 块层匹配成功，但一个或多个账户明细校验失败 |

**规范明确给出的恢复路径**（V5-AI p.12），这是流程而非推断：

- 对 `block level reject` 的正确响应是一条**新的** Allocation Instruction，`AllocTransType=New`，
  因为前一条已被整体拒绝。
- 对 `account level reject`，两条路径二选一：先 `Cancel`（在 `RefAllocID` 中引用原件）再发一条
  `New`；或直接 `Replace`（同样引用 `RefAllocID`）。
- **`Replace` 必须携带替换后的全部数据**，规范原文强调 `all`，并把"识别哪些项发生了变化"的
  责任交给接收方。

**A-1 只走 3（可选）到 0 这一条路径。** 取值 1 与 2 属 A-2，取值 3 是否生成留作决策，见 §3A.6。

#### 确认侧：三个状态字段管三件不同的事

**这一点最容易搞混，所以先说结论：AK 上有两个"状态"，AU 上还有第三个，三者互不替代。**
取值抄自 Volume 6 字段定义（下称 `V6`）。

| 字段 | 在哪张报文 | 管什么 | 取值 | 出处 |
|---|---|---|---|---|
| `ConfirmTransType`(666) | AK | 这条确认是新发、替换还是撤销 | 0=New、1=Replace、2=Cancel | V6 p.232 |
| `ConfirmType`(773) | AK、BH | 这条确认是真确认还是状态播报 | 1=Status、2=Confirmation、3=Confirmation Request Rejected | V6 p.265 |
| `ConfirmStatus`(665) | AK | 卖方对这一笔的处理结果 | 1=Received、2=Mismatched account、3=Missing settlement instructions、4=Confirmed、5=Request rejected | V6 p.232 |
| `AffirmStatus`(940) | AU | 买方对这条确认的回应 | 1=Received、2=Confirm rejected（即未 affirm）、3=Affirmed | V6 p.315 |
| `ConfirmRejReason`(774) | AU | 买方拒绝的原因 | 1=Mismatched account、2=Missing settlement instructions、99=Other | V6 p.266 |

**规范自己给出的三种用法**（V5-CF p.54），照抄而非推断：

1. **电子交易确认**，需要对方 affirm 或 reject。
2. **抄送确认**，`CopyMsgIndicator = Y`，发给第三方，**收件方无权 affirm 或 reject**，
   且规范要求它排在主确认被 affirm 之后再发。
3. **状态播报**，`ConfirmType = 1`，用 `ConfirmStatus` 报 Mismatched account、
   Missing SSI 之类的卡点。

~~**三种用法的成功终态都是 `AffirmStatus = 3`（Affirmed）**~~
**这句话是错的，已于冻结 C-2 时推翻，见 §3A.11。** 规范的总述句确实这么写，
**但同一页的 Model 2 与 Model 3 流程图都只画到 `AffirmStatus = 1`（Received）**。
**只有 Model 1 到得了 Affirmed**，而"该笔已可进入结算"这个判据挂在 Affirmed 上，
**所以 C-1 与结算段之间的那个接口只对 Model 1 成立**，第三批的 ISO 20022 结算报文接在这里。

**被拒之后的恢复路径也是规范给的**（V5-CF pp. 55–56），与分配侧同构但不同名：

- 先发一条 `ConfirmTransType = Cancel` 的确认，再发一条 `New`；
- 或直接发一条 `ConfirmTransType = Replace`。

**C-1 只走用法 1，且一次通过：`ConfirmStatus = 4` → `AffirmStatus = 1` → `AffirmStatus = 3`。**
用法 2 与用法 3、以及 Cancel/Replace 恢复路径属 C-2，见 §3A.8。

#### 回报侧：AllocStatus 复用，但多了一个 AllocReportType

**`AllocStatus`(87) 在 AS 与 AT 上取值与语义完全相同**，就是上面分配侧那四个，不另立一套
（V5-ARA p.31）。**新增的是 `AllocReportType`(794)，它说明这条回报为什么被发出来**：

| 取值 | 含义 | 出处 |
|---|---|---|
| 3 | Sellside Calculated Using Preliminary（含 MiscFees、AccruedInterest、NetMoney） | V6 p.272 |
| 4 | Sellside Calculated Without Preliminary（卖方主动发起，同样含费用与净额） | V6 p.272 |
| 5 | Warehouse recap（卖方主动发出，回报某标的仓位的当前状态） | V6 p.272 |
| 8 | Request to Intermediary | V6 p.272 |

**只有这四个取值，没有 1 与 2。** 枚举从 3 起跳，生成器若按"从 1 开始"的惯例取值会直接越界。

#### 规范自带的六条示例流程：每一条都含 Received 那一步

V5 pp. 33–38 给出六条分配流程与两条拒绝场景，**它们不是可选附录，是规范对每种用法的规定
写法**。逐条读完的结论有三条，都改变了本节此前的判断：

1. **六条流程无一例外，`AllocStatus = 3`（Received Not Yet Processed）都是独立列出的一行。**
   没有任何一条把它写成可选。§3A.6 原先"不生成中间 Ack"的决定据此推翻，理由见该节。
2. **A-1 选的 `AllocType = Calculated` 得到规范确认。** V5 p.37 把"买方自算 MiscFees 与
   NetMoney"列为流程 1，并注明这是美国境内交易的典型流，正是 CMOP 的设定。
3. **费用与净额不走分配应答。** 规范原文说卖方不在 Allocation Instruction Ack 上回送费用与
   开支信息，**这类信息经由 Confirmation 报文传送**，并特别指出这与更早版本的 FIX 不同。
   **这就是金额链条必须落在 C-1 而不是 A-1 的规范依据**，此前只是推断。

**拒绝场景与 §3A.5 已登记的恢复路径一致**（V5 p.38），两条路径都以 `AllocStatus=3` 起手，
再给 Accepted：block level reject 后接一条新的 `New`；account level reject 后接 `Replace`，
或先 `Cancel` 再 `New`。

**AS 与 AT 在 CMOP 里暂时没有场景。** A-1 走的是流程 1，买方发起、卖方应答，全程不出现
Allocation Report。**卖方主动发起的分配回报是另一条流程**（V5 p.37 流程 3），已登记为 A-5，
见 §3A.8。**核对了不等于要用**，这一条写清楚，免得后来把 AS 硬塞进 A-1。

**照旧不写"FIX 不合法"。** 本节只登记规范明确给出的转移。A-1 与 C-1 不允许而规范未禁止的，
标注为"不合法（仅 A-1）"或"不合法（仅 C-1）"，解除条件写在 §3A.8 的对应场景上。

### 3A.6 A-1 与 C-1 的逐步取值

#### A-1

输入固定为 L-1 的终态，见 §3A.1。`AllocType` 取 Calculated，因为它是四种取值中唯一包含
MiscFees 与 NetMoney 的（V5-AI p.12），金额链条完整才谈得上对账。

| 步 | 报文 | 关键取值 | 之后状态 |
|---|---|---|---|
| 1 | J | `AllocTransType=New`、`AllocType=Calculated`、`AllocNoOrdersType=1`、`NoOrders=1`、`ClOrdID` 与 `OrderID` 取自 L-1、`Quantity` 取 L-1 的 `CumQty`、`AvgPx` 取 L-1 派生值、`NoAllocs=N` | 待受理 |
| 2 | P | `AllocID` 回引第 1 步、`AllocStatus=3`（Received Not Yet Processed）、`TransactTime` 必填 | 已收到 |
| 3 | P | `AllocID` 回引第 1 步、`AllocStatus=0`（Accepted）、`TransactTime` 必填 | 已接受，A-1 结束 |

**这里有一条决定被推翻了，原因是读了规范自己的流程。**

原先的写法是"不生成 `AllocStatus=3` 的中间 Ack"，理由是它多一条报文而不增加语义。**那个判断
只依据字段表，没有依据流程页。** V5 pp. 33–38 的六条示例流程与两条拒绝场景**全部把
`AllocStatus=3` 写成独立的一行**，没有一条标它可选。见 §3A.5。

**A-1 因此从两步改为三步。** 附带的好处是它与 C-1 的三步同构，两段链条的形状一致；但形状
一致不是理由，规范这么写才是。

**这是同一个方法教训的第二次出现：先读流程页，再定生成什么。** 第一次是纸面内存筛（见
[技术选型评估](technology-selection-evaluation.md) §7.1），从公开数字推结论而没有实测。
两次的错法相同：**拿一份不为这个问题写的材料当结论用。**

#### C-1

**输入固定为 A-1 的终态**：一条 `AllocStatus = 0` 的 Ack，以及 A-1 派生出的 N 个账户明细。
**C-1 对每个账户各跑一遍下面三步**，因此 C-1 产出 3N 条报文，而 A-1 是固定的 3 条。

`ConfirmType` 取 2（Confirmation）而非 1（Status），因为 C-1 要的是需 affirm 的真确认；
状态播报留给 C-2。`OrderCapacity` 取 `A`（Agency，V6 p.185），与 CMOP 的经纪业务设定一致。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | AK | 卖方 → 买方 | `ConfirmID` 新编、`ConfirmTransType=0`（New）、`ConfirmType=2`、`ConfirmStatus=4`（Confirmed）、`CopyMsgIndicator` 不填、`AllocID` 回引 A-1、`IndividualAllocID` 回引该账户、`AllocAccount` 为该账户、`AllocQty` 取 A-1 派生的该账户数量、`AvgPx` 取该账户 `AllocAvgPx`、`NoCapacities=1` 且 `OrderCapacity=A`、`OrderCapacityQty=AllocQty`、`NoUnderlyings=0`、`NoLegs=0`、`Side` 与 `<Instrument>` 与 `TradeDate` 承自 L-1 | 待应答 |
| 2 | AU | 买方 → 卖方 | `ConfirmID` 回引第 1 步、`AffirmStatus=1`（Received）、`TradeDate` 与 `TransactTime` 必填 | 已收到 |
| 3 | AU | 买方 → 卖方 | `ConfirmID` 回引第 1 步、`AffirmStatus=3`（Affirmed） | 已确认，C-1 结束，该笔可进结算 |

**第 2 步的依据与 A-1 第 2 步相同**：Received → Affirmed 两条 Ack 是规范 Model 1 示例流程里
并排列出的两行（V5-CF p.54），不是可选装饰。**另一个理由是 C-3 需要它**：确认迟到场景要测的
正是 Received 与 Affirmed 之间的时间差跨越了结算日，若第 2 步不生成，C-3 就没有可测的量。

**`AvgPx` 在 AK 里是 gross price，不是净价。** V5-CF p.49 原文写 "Gross price for the trade
being confirmed"。费用与佣金走 `<CommissionData>` 与 `NoMiscFees`，净额走 `NetMoney`。
生成器若把扣费后的价格填进 `AvgPx`，金额三件套会自洽地全错，**而每一条单独看都对**。

### 3A.7 不变量：已核对，且骨架里有两条写法是错的

#### 先说错的两条

**第一条。** 骨架写的是"各账户 `AllocQty` 之和等于**被分配订单的成交总量**"。**规范不支持
这个写法。**

V5-AI p.13 的原文是总分配数量必须等于 `Quantity`(53)，并**专门加了一个脚注**说明
`Quantity` 不必然等于被分配订单的总数量，举的例子是 GT 订单与跨日均价场景。

**这与第一批 `CumQty + LeavesQty = OrderQty` 是同一类错误**：把一个在窄场景下成立的等式，
写成了普遍不变量。区别是这次在填表时就被规范自己的脚注挡住了，没有流进生成器。

**第二条，同一类错误的第三次出现。** 骨架写的是"每个分配账户**恰好**对应一条 Confirmation"。
规范说的是账户层级、每个账户一条报文（V5-CF p.45），**但"恰好一条"不成立**：`ConfirmTransType`
的 Replace 与 Cancel 会让同一账户出现多条确认，`CopyMsgIndicator = Y` 的抄送确认又会再加一条。
正确写法是**每个分配账户至少一条**；"恰好一条"只在 C-1 的窄条件下成立，即全部为 New、无抄送、
无 Cancel/Replace。

**三次都是同一个动作：把窄场景等式当成普遍不变量。** 前两次靠规范原文挡下，这次靠规范的
Cancel/Replace 流程挡下。**这已经不是偶发失误，是骨架阶段的系统性倾向**，第三批写 ISO 20022
骨架时应默认每条候选断言都带适用条件列，而不是事后补。

#### 核对结果

| 断言 | 性质 | 适用条件 | 出处 |
|---|---|---|---|
| 总分配数量 = `Quantity`(53) | **FIX 明确** | 无条件 | V5-AI p.13 |
| `Quantity`(53) = 被分配各订单的成交总量 | **不成立** | 仅在无 GT、无跨日均价时成立，A-1 满足 | V5-AI p.13 脚注 |
| 组内各 `OrderBookingQty`(800) 之和 = `Quantity`(53) | **FIX 明确** | 出现该字段时 | V5-AI p.15 |
| `GrossTradeAmt`(381) = Σ(`AllocQty` × `AllocAvgPx` 或 `AllocPrice`) | **FIX 明确** | 出现该字段时 | V5-AI p.16 |
| `NetMoney`(118) = Σ`AllocNetMoney`(154) | **FIX 明确** | 出现该字段时 | V5-AI p.17 |
| 卖出：`AllocNetMoney` = (`AllocQty`×`AllocAvgPx`) − Commission − Σ(MiscFeeAmt + AccruedInterestAmt)；买入为加 | **FIX 明确** | 出现该字段时 | V5-AI p.19 |
| `SettlDate` = `TradeDate` + 1 营业日 | **CMOP 决定，非 FIX** | T+1 生效期之后；且 `SettlDate` 在 J 中并非必填 | 见 §6 |
| 每个分配账户**至少**对应一条 Confirmation | **FIX 明确** | 无条件 | V5-CF p.45 |
| 每个分配账户**恰好**对应一条 Confirmation | **仅窄条件成立** | 全为 New、无抄送、无 Cancel/Replace；C-1 满足 | V5-CF p.45、pp. 55–56 |
| 一条 AK 内 Σ`OrderCapacityQty`(863) = 该报文的 `AllocQty`(80) | **FIX 明确** | 无条件 | V5-CF p.47、p.49 |
| 各账户 AK 的 `AllocQty`(80) 之和 = 分配指令的 `Quantity`(53) | **CMOP 推论，非 FIX 明确** | 由"总分配数量 = Quantity"与"每账户恰好一条确认"合成，故只在 C-1 窄条件下成立 | 推自 V5-AI p.13 与 V5-CF p.45 |
| 抄送确认排在主确认被 affirm 之后 | **FIX 明确** | `CopyMsgIndicator = Y` 且买方走 Model 1 时 | V5-CF p.54 |
| AS 上 Σ`OrderBookingQty`(800) = `Quantity`(53) | **FIX 明确** | 出现该字段时 | V5-AR p.25 |
| AS 上 `GrossTradeAmt` 与 `NetMoney` 的两条求和式与 J 完全相同 | **FIX 明确** | 出现该字段时 | V5-AR pp.27、29 |
| `TotNoAllocs`(892) = 各分片 `NoAllocs`(78) 之和 | **FIX 明确** | 仅报文分片时 | V5-AR p.27 |
| `AccruedInterestAmt`(159) = 组内 Σ`AllocAccruedInterestAmt`(742) | **FIX 明确** | 出现该字段时 | V5-AR p.27 |
| 每条 AS 都带 `AllocID`(70) | **CMOP 决定，非 FIX** | AS 上该字段可选，但 AT 上必填，不填就造不出合法应答 | 推自 V5-AR p.24 与 V5-ARA p.31 |

**买卖方向进入了金额公式，这一条容易被漏。** `AllocNetMoney` 的符号取决于 `Side`，生成器若
两边同号，差异会以"金额对不上"的形式出现在 R1，而根因在生成器，不在管道。

### 3A.8 场景清单：CMOP 决定，不需核对规范

以下场景是本项目要覆盖的分配与确认路径，属业务范围决定。**A-1 现在冻结，其余按顺序解锁**，
与 L-1、L-2 的做法一致。

| 编号 | 场景 | 为什么要它 | 状态 |
|---|---|---|---|
| A-1 | L-1 的已成交订单分配到 N 个账户，一次通过 | 打通链条第三段，最小可证 | **已冻结**，见 §3A.6 |
| A-2 | 账户层拒绝后以 Replace 更正 | 制造一条 `RefAllocID` 版本链，检验维度与事实的版本对齐 | **已冻结**，见 §3A.10 |
| A-2a | 块层拒绝后重发新 New | 覆盖另一条恢复路径，**两条 J 之间无字段级引用** | 待解锁，优先级低 |
| A-2b | Cancel 再 New 的更正 | ~~把版本链从一跳拉到两跳~~ **2026-09-13 更正：不是两跳链**，重新下达的 New 不回引任何报文，见 §3A.10 | **已冻结**，见 §3A.11a |
| A-3 | 分配迟到，T+1 早晨才到达 | **直接对应主业务流**，见[业务目标](business-objectives.md) §3.1 | **已冻结**，见 §3A.13 |
| A-4 | 分配数量与成交总量对不上 | 制造 R1 必须捕获的差异，属注入而非正常路径 | 待解锁 |
| A-5 | 卖方主动发起分配回报（AS/AT） | 覆盖规范流程 3，方向与 A-1 相反，检验交易对手字段没写反 | 待解锁，优先级低 |
| C-1 | 逐账户确认并被接受 | 链条第四段 | **已冻结**，见 §3A.6 |
| C-2 | 确认被拒后以 Replace 更正 | 与 A-2 同形，作用在确认层，**且打掉 VC-2** | **已冻结**，见 §3A.11 |
| C-2a | 抄送确认，含技术层面拒绝 | 终态只到 Received，**与 C-2 的拒绝含义不同** | 待解锁 |
| C-2b | 状态播报（`ConfirmType = 1`） | 用 `ConfirmStatus` 报卡点，终态同样只到 Received | 待解锁 |
| C-2c | Cancel 再 New 的更正 | 与 A-2b 同形，**同样不是两跳链** | **已冻结**，见 §3A.11a |
| C-4 | 确认请求与应答（BH/AK） | `ConfirmType = 3` 的唯一出场场合 | 待解锁，优先级低 |
| C-3 | 确认迟到，跨越结算日 | 与 T+1 结算周期交互，最难的一类，**且它接到 S-2 上** | **已冻结**，见 §3A.14 |
| A-6 | 迟到的分配又被拒 | A-3 与 A-2 的组合，**两者失效路径互相掩盖** | 待解锁，见 §3A.13 |
| C-5 | 迟到的确认又被拒 | 与 A-6 同理 | 待解锁 |

**A-3 与 C-3 是这批里价值最高的两个**，因为 T+1 早晨的异常处理流是本项目唯一必须端到端跑通
的业务流。但它们都依赖 A-1 与 C-1 先成立，**顺序不能颠倒**。A-1 与 C-1 现已双双冻结，
**这个前置条件已经解除**。

**它们还有第二个前置条件，此前没有写出来：迟到量的是什么。**
**已于 2026-09-12 定案**，见 §3A.12——**会话层根本不允许迟到超过两分钟**，
所以 A-3 与 C-3 的迟到只能是批次归属之差。

**A-5 的优先级明确定为低。** 它对应的是卖方主动发起的分配流程，报文已核对但 CMOP 的业务
设定里没有这条流。**列出来是为了防止 AS 与 AT 被硬塞进 A-1**，不是为了排期。

~~**C-2 的范围比字面更宽。**~~ **原先把抄送确认与状态播报并进 C-2，理由是三者共用同一套
Cancel/Replace 恢复路径。恢复路径确实共用，终态却不同**（见 §3A.11），
把终态不同的三条流程压在一个编号下会使终态断言无法书写，故已拆为 C-2、C-2a、C-2b。

### 3A.9 现在就要回头改的地方

第二批一旦落地，下列内容必须同步，**否则文档之间会自相矛盾**：

- [合成数据生成规范](data-generation-specification.md) §6 的采样与派生划分要扩展到分配层，
  分配数量与金额多半是派生而非采样。
- ~~[验证与对账规范](validation-and-reconciliation-specification.md) §2.3 的 R1 只在 L-1
  范围内具体化，A-1 落地后要补分配侧。~~ **已于 2026-09-12 补上**，见该文 §2B.3。
  **两侧日期基准相同**，分配不跨结算日，照抄 §2.3 的 T+1 映射会把全部分配报成时点差异。
- 同文档 §6.1 的六条注入里，前三条被标注为"L-2 落地后必须删除"。**A-1 与 C-1 都不解除它们**，
  解除条件仍是 L-2，不要混淆两个扩展轴。
- §3.1 那条"4.4 是最早携带确认与分配语义的版本"的待核对标记，**已于 2026-09-10 结清**，
  见 §3A.2 末尾。
- ~~账户维度仍然缺失。~~ **已于 2026-09-10 补上**，见[合成数据生成规范](data-generation-specification.md)
  §3A。C-1 把这个缺口从"需要"提升为"卡住"，因为 AK 的 `AllocAccount` 是必填字段。
- 第二批已全部核对，**本节从"填完之后要改"变成"现在就要改"**。上面各条不再有前置条件。
- ~~[验证与对账规范](validation-and-reconciliation-specification.md) 需要新增一条确认层断言。~~
  **已于 2026-09-12 写入**，见该文 §2B.2 的 VC-1 与 VC-2，适用条件与失效场景同时给出。
  **附带发现一条推论型断言 VC-4**：各账户确认数量之和等于分配指令数量，
  它由"总分配数量等于 `Quantity`"与"每账户恰好一条确认"合成，
  **因此随 VC-2 一起在 C-2 失效，而这从它自己的形式上看不出来**。

### 3A.10 A-2：账户层拒绝后以 Replace 更正，已冻结

#### 先更正 §3A.8 原来的写法

原写法是"制造同一 `AllocID` 的多版本，检验维度与事实的版本对齐"。**规范不允许这个做法。**

V5-AI p.12 原文：`AllocID` 对所有 `AllocTransType=New` 的分配报文必须唯一。由此：

- **块层拒绝之后不可能出现同一 `AllocID` 的第二版。** 规范给出的唯一正确响应是一条全新的
  Allocation Instruction，`AllocTransType=New`，而这条报文正落在唯一性约束之内，必须换号。
- **Cancel 与 Replace 不在唯一性约束的文面之内**，规范只约束了 `New`。但 `AllocLinkID`(196)
  的字段说明写的是"链接两条各自 `AllocID` 唯一的分配报文"（V5-AI p.14），
  可见规范默认每条 J 各有各的号。

**CMOP 口径（决定，非 FIX 明确）：每条 J 各带一个新的 `AllocID`，版本关系全部由
`RefAllocID`(72) 承载。** 于是 A-2 要检验的"版本对齐"不是同键多版本的对齐，
**而是沿 `RefAllocID` 链回溯的对齐**。

**场景目标保留，机制更正。** 沿链回溯比同键分组更难写，也更贴近真实：链可以有一跳
（Replace），也可以有两跳（Cancel 再 New），**而下游只拿到一串各不相同的 `AllocID`**。
~~两跳~~ **2026-09-13 更正：Cancel 再 New 在字段层面不是两跳**，见下文"A-2 明确不做的四件事"第 2 条。

#### `AllocStatus` 实际有六个取值，§3A.5 那张表少了两个

§3A.5 的四值表抄自 V5-AIA p.21 的报文页。**Volume 6 的字段字典给的是六个**（V6 p.36）：

| 取值 | 含义 | §3A.5 是否已登记 |
|---|---|---|
| 0 | accepted | 是 |
| 1 | block level reject | 是 |
| 2 | account level reject | 是 |
| 3 | received, not yet processed | 是 |
| 4 | incomplete | **否** |
| 5 | rejected by intermediary | **否** |

**这是"按名字搜索不足以证明不存在"在 FIX 侧的同一课。** ISO 20022 那边的教训是约束名随
元素名走，必须取整表（见 §4C.6）；**这里的教训是报文页与字段字典是两份材料，报文页可以不全**。

`4 = incomplete` 对应分片：接收方收齐 `TotNoAllocs` 之前，整批尚不完整。
`5 = rejected by intermediary` 对应 `AllocIntermedReqType`(808) 那条经清算所转发的流程。
**两者 CMOP 都不生成**，但**校验层不得把 `AllocStatus` 的合法域写成四值**，
否则将来接入分片或中介流程时，合法数据会被自己的校验拒掉。

#### `AllocRejCode` 的十四个取值

V6 p.37，枚举从 0 起，共 0 至 13。**errata 把原先的 0 至 7 扩到了 13**，
Volume 6 的修订标记里还留着旧的七值声明。

| 取值 | 含义 | 取值 | 含义 |
|---|---|---|---|
| 0 | unknown account(s) | 7 | other，须在 `Text`(58) 中说明 |
| 1 | incorrect quantity | 8 | incorrect allocated quantity |
| 2 | incorrect average price | 9 | calculation difference |
| 3 | unknown executing broker mnemonic | 10 | unknown or stale `ExecID`(17) |
| 4 | commission difference | 11 | mismatched data value，须在 `Text`(58) 中说明 |
| 5 | unknown `OrderID`(37) | 12 | unknown `ClOrdID`(11) |
| 6 | unknown `ListID`(66) | 13 | warehouse request rejected |

`IndividualAllocRejCode`(776) 的取值集合与 88 完全相同，规范原文就是这么写的（V6 p.266）。
**但两者在 FIXML 里的严格程度不同**：88 声明为带 `Value (0|…|13) #REQUIRED` 的枚举，
776 声明为 `(#PCDATA)`，**不带任何取值约束**。

**后果要写死**：账户层的原因码填错，FIXML schema 不会报错，块层的会。
CMOP 的校验层必须自己对 776 做域检查，**不能指望 schema**。

#### 账户层拒绝的原因载体是"至少一个"，不是二选一

两处规定合起来读（V5-AIA pp. 21–22）：

- `AllocRejCode`(88)：`AllocStatus=1` 时必填；`AllocStatus=2` 且本报文未逐账户给出原因时必填。
- `NoAllocs`(78) 组：`AllocStatus=2` 时可选可用，**其他取值下不得填充**；填了则组内
  `IndividualAllocRejCode` 必填。

**因此 `AllocStatus=2` 的 Ack 上，两个载体至少有一个在，两个同时在并不违规。**
写成"二选一"会把合法报文判死。**这与 §4C.8 记录的银行间结算日两层元素不是同一个形状**：
那边是真正的互斥，这边只是"不得两者皆空"。

#### 逐步取值

输入是 A-1 的第 1 步与第 2 步，即一条已发出的 J 与一条 `AllocStatus=3` 的 Ack。
**A-2 从 A-1 的第 3 步分叉**：那一步不是 Accepted，而是账户层拒绝。
设 A-1 分配到 N 个账户，其中第 k 个账户号不存在。

| 步 | 报文 | 关键取值 | 之后状态 |
|---|---|---|---|
| 1 | J | 与 A-1 第 1 步完全相同，`AllocID = A1`、`AllocTransType=0`（New） | 待受理 |
| 2 | P | `AllocID = A1`、`AllocStatus=3` | 已收到 |
| 3 | P | `AllocID = A1`、`AllocStatus=2`、`NoAllocs=1`、组内 `AllocAccount` 为第 k 个账户、`IndividualAllocRejCode=0`（unknown account）、`AllocText` 给出说明；`AllocRejCode` 不填 | 账户层被拒 |
| 4 | J | `AllocID = A2`（新号）、`AllocTransType=1`（Replace）、`RefAllocID = A1`、`AllocCancReplaceReason=1`（Original details incorrect）、**其余全部字段照第 1 步重发**，仅第 k 个账户改为有效账户号 | 待受理 |
| 5 | P | `AllocID = A2`、`AllocStatus=3` | 已收到 |
| 6 | P | `AllocID = A2`、`AllocStatus=0` | 已接受，A-2 结束，C-1 接在 A2 之后 |

**第 4 步"照第 1 步重发全部字段"不是省事的写法，是规范要求。** V5-AI p.13 原文强调
Replace 必须携带替换后的**全部**数据，并把"识别哪些项发生了变化"的责任交给接收方。
**生成器若只发变更项，报文在 FIX 上就是错的**，而单看这条报文本身挑不出毛病。

`AllocCancReplaceReason`(796) 只有三个取值：1 = Original details incorrect、
2 = Change in underlying order details、99 = Other（V6 p.266）。
**A-2 取 1**，因为账户号本身填错，与上游订单无关。
**取 2 属于另一条场景**，即订单在分配之后又发生了 Cancel/Replace，那要先有 L-2。

#### A-2 明确不做的四件事，其中三件是规范里真实存在的分支

1. **块层拒绝（`AllocStatus=1`）后重发新 New。** 它比 Replace 简单，但它测不到版本链：
   两条 J 之间除了业务内容没有任何字段级引用，**`RefAllocID` 在 New 上不填**。
   登记为 A-2a，优先级低。
2. **Cancel 再 New 的路径。** 与第 4 步的 Replace 等效，规范并列给出。
   **会多产生一条 `AllocTransType=2` 的 J 和它自己的一对 Ack。**
   登记为 A-2b，**在版本链回溯的校验写好之后再解锁**。**2026-09-13 已冻结**，见 §3A.11a。

   **2026-09-13 更正：它不是两跳链，原文"链长从一跳变两跳"是错的。**
   V5-AI p.12 原文：账户层拒绝后可以先发一条 Cancel，**"referencing the original in RefAllocID"**，
   再 **"reinstated (a second new Allocation Instruction message with AllocTransType 'New')"**。
   **重新下达的那条是 New**，而 `RefAllocID`(72) 在 V6 的字段定义里限定为
   "to be used with AllocTransType (71) = Replace or Cancel"。于是：

   | 关联 | 字段层面能否到达 | 锚点档位（§4.6.6） |
   |---|---|---|
   | Cancel → 原件 | 能，`RefAllocID` 必填 | 第一档 |
   | 重新下达的 New → 原件或 Cancel | **不能**，承载元素的定义不覆盖 New | **第四档** |

   **所以 A-2b 不是 VA-11 的"第二个用例"**：VA-11 在 A-2b 上只走一跳（Cancel → 原件），
   **而重新下达的 New 自己就是根**，回溯立刻终止且合规。
   **"这条 New 是在更正哪一条"只能靠生成侧对照表核**，与 E-20（契约 S7c-5）同形。
   **与 A-2a（块层拒绝后重发 New）在字段层面完全无法区分**，区分只在前一条 Ack 的 `AllocStatus`。
   `AllocLinkID`(196) 不能拿来补这个缺口：V5-AI p.14 把它限定在外汇轧差与掉期之类的链接上。
3. **Respondent 在已发出 Accepted 之后拒绝 Cancel 或 Replace。** 规范明说这是允许的
   （V5-AI p.13），并说明此后需要人工介入。**CMOP 不生成它，但断言不得排除它**：
   任何"Replace 之后必然到达 Accepted"的写法都是错的。
4. **分片。** `TotNoAllocs`/`LastFragment` 那一套只在报文超长时出现，A-2 的 N 很小。
   **但第 4 条分片规则要记住**：接收方必须应答每一个分片且**不得拒绝非末片**，
   整批的接受或拒绝只发生在末片的应答上（V5-AI p.11）。
   **这意味着分片一旦引入，`AllocStatus` 的取值与分片序号之间产生约束**，
   而 A-2 这套三步式拒绝流程在分片下不成立。

#### A-2 带出的断言

| 编号 | 断言 | 性质 |
|---|---|---|
| VA-7 | `AllocTransType` 为 Replace 或 Cancel 的 J 必带 `RefAllocID` 与 `AllocCancReplaceReason` | FIX 明确 |
| VA-8 | `AllocStatus=2` 的 Ack 上，`AllocRejCode` 与 `NoAllocs` 组不得两者皆空 | FIX 明确 |
| VA-9 | `AllocStatus` 不为 2 的 Ack 上不得出现 `NoAllocs` 组 | FIX 明确，**方向为禁止** |
| VA-10 | Replace 型 J 携带的字段集合与被替换的 J 相同 | FIX 明确 |
| VA-11 | 沿 `RefAllocID` 回溯必须终止于一条 `AllocTransType=New` 的 J，且链上无环 | **CMOP 决定** |
| VA-12 | 不得断言 Replace ~~之后~~ **或 Cancel 之后**必然到达 `AllocStatus=0` | **规范明确否定**（V5-AI p.13 两者并列；2026-09-13 随 A-2b 补上 Cancel） |

**VA-11 是本场景引入的唯一新形状：它不是等式，是图上的可达性。**
R1 与 R2 都是按键聚合后比数值，**链式回溯不属于这一类**，校验层要为它另立一种检查形状。
写在这里是因为它的成本不在断言本身，而在于校验层此前没有这种形状。

### 3A.11 C-2：确认被拒后以 Replace 更正，已冻结，且它推翻了 §3A.5 的一句话

#### 先说被推翻的那一句

§3A.5 写的是"三种用法的成功终态都是 `AffirmStatus = 3`（Affirmed）"。
**这句话抄自规范，而规范这一句与它自己画的流程图矛盾。**

V5-CF p.54 的开头一句确实写着三种用法的成功终态都是 Affirmed。**但同一页往下**：

- **Model 2（抄送确认）的流程图只画到 `AffirmStatus = Received` 就结束**，
  正文并明说抄送件的收件方**无权因业务原因 affirm 或 reject**。
- **Model 3（状态播报）的流程图同样只画到 `Received`。**

**因此那句总述是错的，只有 Model 1 到得了 Affirmed。**
§3A.5 的写法一并更正：**Affirmed 是 Model 1 的终态，不是三种用法的共同终态。**

**这一条的后果不止于措辞。** "该笔已可进入结算"这个判据挂在 Affirmed 上，
若把它当成三种用法通用，**抄送件与状态播报会被当成结算前置条件已满足**，
而它们本来就到不了那一步。**这是 C-1 与结算段那个接口的精确边界**：
接口只对 Model 1 成立。

**顺带把 C-2 的范围拆开。** §3A.8 原来把抄送与状态播报都并进 C-2，
理由是三者共用同一套 Cancel/Replace 恢复路径。**恢复路径确实共用，终态却不同**，
把终态不同的三条流程压在一个场景编号下，**终态断言就没法写**。
抄送拆为 C-2a，状态播报拆为 C-2b。

#### 抄送件上的 `AffirmStatus = 2` 与主确认上的不是一回事

规范原文在 Model 2 里补了一句：收件方不得因业务原因拒绝，
**但技术层面的拒绝仍然可能**，例如系统故障，且这种拒绝"应读作报文传输或处理失败，
而不是对内容的拒绝"（V5-CF p.55）。

**于是同一个 `AffirmStatus = 2` 在两种流程下含义完全不同**，
而**报文里唯一能把两者分开的字段是 `CopyMsgIndicator`(797)**。

**后果要写死**：任何按 `AffirmStatus` 统计拒绝率的口径，**必须先按 `CopyMsgIndicator` 分层**。
不分层的拒绝率把传输故障和业务分歧加在一起，**数越大越没有意义**。

#### `ConfirmRejReason` 只有三个取值，这一段没法做原因分析

`ConfirmRejReason`(774)：1 = Mismatched account、2 = Missing settlement instructions、
99 = Other（V6 p.266）。**对照 `AllocRejCode` 的十四个取值（见 §3A.10）。**

**分配侧的拒绝原因是可分析的，确认侧的不是。** 确认被拒的真实原因绝大多数是净额、
毛额或费用算不平，**而这三样在词表里一个都没有**，只能落到 99 = Other 加自由文本。

**CMOP 的口径**：确认侧不建原因码分布，**只建"是否被拒"的二值口径**。
**这不是数据量不够，是词表本身不支持**，再多的样本也分不出细类。
**这一条要显式写下来**，否则下游会以为是采样问题而去加量。

#### AU 报文上的三处笔误，全部是从分配侧粘过来的

V5-CFA p.52 的字段表，Confirmation Ack 一共只有七个业务字段，其中三个的注释是错的：

| 字段 | 规范注释原文 | 错在哪 | CMOP 口径 |
|---|---|---|---|
| `ConfirmRejReason`(774) | Required for `ConfirmStatus` = 1 (rejected) | **AU 上根本没有 `ConfirmStatus`**，而且 `ConfirmStatus=1` 是 Received 不是 rejected | `AffirmStatus = 2` 时必填，已记于 §3A.4 |
| `Text`(58) | Can include explanation for `AllocRejCode` = 7 (other) | **`AllocRejCode` 是分配侧字段，AU 上没有** | `ConfirmRejReason = 99` 时用于说明 |
| `TransactTime`(60) | Date/Time **Allocation Instruction Ack** generated | 同上，粘错了报文名 | 本条 AU 的生成时刻 |

**三处笔误指向同一个来源**：Confirmation Ack 的字段表是照 Allocation Instruction Ack
改出来的，改漏了三行。**这不影响 XSD 校验，只影响读的人**，
所以它必须写在文档里而不是靠实现时"看着办"。

**errata 没有修这三处。** 本项目用的就是 with-Errata-20030618 版本，
**这些是该版本的现状，不是过期信息**。

#### FIXML 的严格程度在同类型字段之间并不一致

§3A.10 记了一条：`AllocRejCode`(88) 在 FIXML 里带枚举，
`IndividualAllocRejCode`(776) 是 `(#PCDATA)`，同一个取值域两种严格程度。
**确认侧又有一条同形的**：`LegalConfirm`(650) 是 Boolean 且带 `Value (Y|N) #REQUIRED`，
`CopyMsgIndicator`(797) 同样是 Boolean，**却声明为 `(#PCDATA)`，不带取值约束**（V6 pp. 205、267）。

**两条合起来是一个可以推广的结论**：**FIXML 的严格程度是逐字段决定的，不是由数据类型决定的。**
"这是 Boolean，schema 会挡住"这句话在 FIX 4.4 上不成立。
**校验层不能按类型推断哪些字段已被 schema 覆盖，只能逐字段查。**

**而 `CopyMsgIndicator` 恰好是上面拒绝率分层所依赖的那个字段。**
分层键本身不受 schema 保护，**这两件事必须一起看**。

#### 逐步取值

输入是 C-1 第 1 步与第 2 步，即某账户的一条 AK 与一条 `AffirmStatus=1` 的 AU。
**C-2 从 C-1 的第 3 步分叉**：那一步不是 Affirmed，而是买方拒绝。
拒绝理由取"净额算不平"，落到 99 = Other。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | AK | 卖方 → 买方 | 与 C-1 第 1 步完全相同，`ConfirmID = K1`、`ConfirmTransType=0`（New）、`ConfirmStatus=4` | 待应答 |
| 2 | AU | 买方 → 卖方 | `ConfirmID = K1`、`AffirmStatus=1`（Received） | 已收到 |
| 3 | AU | 买方 → 卖方 | `ConfirmID = K1`、`AffirmStatus=2`（Confirm rejected）、`ConfirmRejReason=99`、`Text` 说明净额差异、`MatchStatus=1`（uncompared/unaffirmed） | 已被拒 |
| 4 | AK | 卖方 → 买方 | `ConfirmID = K2`（新号）、`ConfirmTransType=1`（Replace）、`ConfirmRefID = K1`、`ConfirmStatus=4`、**其余全部字段照第 1 步重发**，净额三件套改为正确值 | 待应答 |
| 5 | AU | 买方 → 卖方 | `ConfirmID = K2`、`AffirmStatus=1` | 已收到 |
| 6 | AU | 买方 → 卖方 | `ConfirmID = K2`、`AffirmStatus=3`（Affirmed） | 该账户可进结算，C-2 结束 |

**`ConfirmID` 换号这件事，确认侧比分配侧干净。** 分配侧要靠 CMOP 定口径（§3A.10），
**确认侧规范直接写了 `ConfirmID` 是"本条报文的唯一 ID"**（V5-CF p.47），
每条报文各有各的号是字面要求。`ConfirmRefID`(772) 在 Replace 与 Cancel 上必填，
承担版本链，与分配侧的 `RefAllocID` 同形。

**第 3 步的 `MatchStatus` 是可选的，但要填。** 它在 AU 上标 N，
**填 1 才使"拒绝"这件事在字段层面自洽**；只有 `AffirmStatus=2` 而 `MatchStatus` 缺失，
下游无法从单条报文判断比对结果。**这是 CMOP 决定，不是规范要求。**

**C-2 只作用在一个账户上。** C-1 对 N 个账户各跑三步，
**C-2 让其中一个账户走六步，其余 N−1 个仍走三步**。
**这一点直接打掉 VC-2**：该账户会有两条确认，且都不是抄送。

#### C-2 明确不做的三件事

1. **Cancel 再 New 的路径**，与 A-2b 同形，登记为 C-2c，**与 A-2b 一同解锁**：
   两者共用同一条链式回溯校验，分开做没有意义。
   **2026-09-13 更正：同样不是两跳。** V5-CF p.46 写的是先发 "cancel" 再发 "new"，
   `ConfirmRefID`(772) 只在 Replace 或 Cancel 上必填，**重新下达的 New 不回引**，
   结论与 §3A.10 的 A-2b 相同。**2026-09-13 已冻结**，见 §3A.11a。
2. **技术层面拒绝的抄送件**，属 C-2a。它要的是 `CopyMsgIndicator=Y` 的报文流，
   而 C-2 全程 `CopyMsgIndicator` 不填。
3. **`ConfirmType = 3`（Confirmation Request Rejected）。**
   它只出现在应答一条 Confirmation Request 的场合，**而 CMOP 至今没有生成过 BH**。
   登记在 C-4：确认请求与应答，优先级低。

#### C-2 带出的断言

| 编号 | 断言 | 性质 |
|---|---|---|
| VC-7 | `ConfirmTransType` 为 Replace 或 Cancel 的确认必带 `ConfirmRefID`(772) | FIX 明确 |
| VC-8 | `AffirmStatus = 2` 的应答必带 `ConfirmRejReason`(774) | **CMOP 口径**，规范原文的条件写错了字段 |
| VC-9 | Replace 型确认携带的字段集合与被替换的那条相同 | FIX 明确 |
| VC-10 | 沿 `ConfirmRefID` 回溯终止于一条 `ConfirmTransType=New` 的确认，且链上无环 | **CMOP 决定**，与 VA-11 同形 |
| VC-11 | 只有 Model 1 能到达 `AffirmStatus = 3`；抄送与状态播报的终态是 `1` | FIX 明确，**且规范的总述句与此矛盾** |
| VC-12 | 按 `AffirmStatus` 统计拒绝必须先按 `CopyMsgIndicator`(797) 分层 | **CMOP 口径** |
| VC-13 | **不得**为确认侧的拒绝原因建立分布口径 | **词表明确不支持** |

**VC-11 是清单里第一条与规范原文直接冲突的断言。**
此前登记过的规范内部不一致（§4.8、§3A.3）都是两处规定互相矛盾，由 CMOP 选一边；
**这一条是一句总述与同一页的流程图矛盾，而流程图更具体**，所以按流程图写。
**选择的理由要留着**，因为下一个读那句总述的人会重新提出同样的问题。

### 3A.11a A-2b 与 C-2c：Cancel 再 New，已冻结，2026-09-13

**两条同时冻结**，理由是 §3A.11 第 1 条：共用同一条链式回溯校验。回溯校验已实现
（验证与对账规范 §2B.2 末段），**解锁条件满足**。

**先把核实过的四处原文列出来，本节所有取值都由它们推出：**

| 原文位置 | 说的是什么 | 推出什么 |
|---|---|---|
| V5-AI p.12 | 账户层拒绝后可以先发 Cancel，"referencing the original in RefAllocID"，再以一条 `AllocTransType` 为 New 的报文 "reinstated" | 撤销件回引原件，**重下件是 New** |
| V6 字段 72、772 的定义 | `RefAllocID`、`ConfirmRefID` 均为 "to be used with" Replace or Cancel | **重下件字段层面不回引**，§3A.10 第 2 条已记 |
| V5-AI p.17 报文页 `NoAllocs`(78) | 标 `Y**`，注明 "Not required for AllocTransType=Cancel" | **撤销件可以不带账户组** |
| V5-CF p.55 "Example flow using a Cancel" | 卖方连发 Cancel 与 New 两条 Confirmation，**两条之间没有买方应答**，应答只画在 New 之后 | **确认侧的撤销件在流程图上没有应答** |

**第四处与分配侧不对称，是本节最重要的发现。** 分配侧的流程图（V5 p.38）
给 Cancel 画了一对 Ack（Received、Accepted），确认侧不画。
**同一页的图注还写着 "Cancelling the original Allocation Instruction"**，
在确认流程里说分配指令，**这是 §3A.11 那三处 AU 笔误之外的第四处从分配侧粘过来的文字**。
**所以"流程图不画 AU"有可能也是粘贴时漏画的**，CMOP 不能据此断言 AU 不存在，
也不能据此断言 AU 必须存在，**只能两边都不断言**，见下文 VC-16。

#### A-2b 逐步取值

与 A-2 共用前三步：A-1 分配到 N 个账户，第 k 个账户号不存在，对方回账户层拒绝。

| 步 | 报文 | 关键取值 | 之后状态 |
|---|---|---|---|
| 1 | J | 与 A-2 第 1 步相同，`AllocID = A1`、`AllocTransType=0` | 待受理 |
| 2 | P | `AllocID = A1`、`AllocStatus=3` | 已收到 |
| 3 | P | 与 A-2 第 3 步相同：`AllocStatus=2`、`NoAllocs=1`、`IndividualAllocRejCode=0` | 账户层被拒 |
| 4 | J | `AllocID = A2`（新号）、`AllocTransType=2`（Cancel）、`RefAllocID = A1`、`AllocCancReplaceReason=1`；**报文页必填字段照第 1 步重发，`NoAllocs` 组不带** | 待受理 |
| 5 | P | `AllocID = A2`、`AllocStatus=3` | 已收到 |
| 6 | P | `AllocID = A2`、`AllocStatus=0` | **A1 已撤销** |
| 7 | J | `AllocID = A3`（新号）、`AllocTransType=0`（New）、**不带 `RefAllocID`**、全部字段照第 1 步，仅第 k 个账户改为有效账户号 | 待受理 |
| 8 | P | `AllocID = A3`、`AllocStatus=3` | 已收到 |
| 9 | P | `AllocID = A3`、`AllocStatus=0` | 已接受，A-2b 结束，C-1 接在 A3 之后 |

**第 4 步不带 `NoAllocs` 组是 CMOP 决定。** 规范只说"不要求"，没说"不得"。
取不带的理由是 **VA-10 只约束 Replace**：若撤销件也带全量账户组，
下游很容易把它误读成一次 Replace，**而撤销件上的账户组没有任何业务含义**。

**第 7 步必须晚于第 6 步。** 规范原文的次序是先撤销、后重下，流程图也按这个次序画。
**若重下件先于撤销被接受到达，同一订单会同时存在两条有效分配**，
R1 在那一刻看到的分配数量是两倍。**这是 CMOP 决定，依据是流程图的次序**，
不是规范的必填规则。

#### C-2c 逐步取值

与 C-2 共用前三步：某账户的确认被买方以净额算不平拒绝。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | AK | 卖方 → 买方 | 与 C-2 第 1 步相同，`ConfirmID = K1`、`ConfirmTransType=0` | 待应答 |
| 2 | AU | 买方 → 卖方 | `ConfirmID = K1`、`AffirmStatus=1` | 已收到 |
| 3 | AU | 买方 → 卖方 | 与 C-2 第 3 步相同：`AffirmStatus=2`、`ConfirmRejReason=99`、`MatchStatus=1` | 已被拒 |
| 4 | AK | 卖方 → 买方 | `ConfirmID = K2`（新号）、`ConfirmTransType=2`（Cancel）、`ConfirmRefID = K1`、`ConfirmStatus=4`；**其余必填字段照第 1 步** | **K1 已撤销**，不等应答 |
| 5 | AK | 卖方 → 买方 | `ConfirmID = K3`（新号）、`ConfirmTransType=0`（New）、**不带 `ConfirmRefID`**、`ConfirmStatus=4`、全部字段照第 1 步，净额三件套改为正确值 | 待应答 |
| 6 | AU | 买方 → 卖方 | `ConfirmID = K3`、`AffirmStatus=1` | 已收到 |
| 7 | AU | 买方 → 卖方 | `ConfirmID = K3`、`AffirmStatus=3` | 该账户可进结算，C-2c 结束 |

**第 4 步之后不生成 AU，照流程图。** 这是生成侧的选择，**不是校验侧的断言**，
理由见本节开头第四处原文。**确认侧的撤销因此没有"已被接受"这个时点**，
第 5 步紧随第 4 步，间隔为指数分布、均值 1 秒，**占位值**，性质同生成规范 §6.2。

**C-2c 同样只作用在一个账户上**，其余 N−1 个账户走 C-1。
**该账户会有三条 AK**，比 C-2 多一条，VC-2 早已失效，不再额外打掉什么。

#### "谁在更正谁"：只存在于生成侧对照表

A3 与 A1、K3 与 K1 之间**没有任何字段级关联**（§3A.10 第 2 条）。
**与 A-2a 在字段层面无法区分**，区分只在前一条 Ack 的状态与撤销件的存在。

**生成器必须输出两张对照表**，形状与 E-20（契约 S7c-5）相同：

| 对照表 | 列 | 用途 |
|---|---|---|
| 分配更正对照 | 重下件 `AllocID`、被撤销的原件 `AllocID`、撤销件 `AllocID` | VA-18 |
| 确认更正对照 | 重下件 `ConfirmID`、被撤销的原件 `ConfirmID`、撤销件 `ConfirmID` | VC-18 |

**对照表是校验输入，不是生产数据**：生产侧拿不到它，
**所以依赖它的检查只能证明生成器自洽，不能证明下游能还原这层关系**。
下游能还原的只到"这笔订单有一条被撤销的分配和一条后来的 New"，
**把两者配成一对是推断**，且在同一订单有多次撤销时推断不唯一。

#### A-2b 与 C-2c 带出的断言

| 编号 | 断言 | 性质 |
|---|---|---|
| VA-15 | R1 的分配侧只计有效分配：**被已接受的 Cancel 或 Replace 回引的原件不计，Cancel 件本身不计** | **CMOP 决定** |
| VA-16 | **不得断言**重下的 New 能沿字段回溯到被撤销的原件 | **规范结构上不支持** |
| VA-17 | `AllocTransType=New` 的 J 不带 `RefAllocID`(72) | 字段定义文字，第二档 |
| VA-18 | 分配更正对照表每一行：重下件与原件同一订单、`Quantity` 相等；重下件 `TransactTime` 晚于撤销件的 `AllocStatus=0` 应答 | **CMOP 决定**，只作用于生成侧 |
| VC-14 | VC-1 的"至少一条确认"按**有效确认**计：未被 Cancel 或 Replace 回引、且本身不是 Cancel | **CMOP 决定** |
| VC-15 | **不得断言**重下的 New 能沿字段回溯到被撤销的确认 | **规范结构上不支持** |
| VC-16 | **不得断言** Cancel 型确认必有应答，**也不得断言它必无应答** | **规范流程图不画，且该页有粘贴痕迹** |
| VC-17 | `ConfirmTransType=New` 的确认不带 `ConfirmRefID`(772) | 字段定义文字，第二档 |
| VC-18 | 确认更正对照表每一行：重下件与原件同一分配账户、同一 `AllocID`；重下件紧随撤销件 | **CMOP 决定**，只作用于生成侧 |

**VA-15 与 VC-14 是 A-2b 带出的真正新约束，其余七条是守边界的。**
A-2 的 Replace 链上，"取链末端"与"排除被回引者"是同一件事；
**Cancel 链的末端是 Cancel 件本身，取链末端会把一条撤销当成有效分配**。
所以有效性的定义必须写成"排除"而不是"取末端"，**这是 VA-11 回溯结果不能直接拿来当 R1 输入的原因**。

**VC-16 是清单里第一条双向否定。** 它同时挡两个合理写法，
**依据的弱点在规范自身**：流程图是唯一出处，而这张图所在的页面已有粘贴错误。
**若将来读到 FIX 后续版本或 FPL 指引明确了这一点，VC-16 应当收窄成单向。**

**VA-17 与 VC-17 按第二档报告**（验证与对账规范 §1A.4），**不是第一档**：
报文页的原文是 Replace 或 Cancel 时"必填"，**没写 New 时"不得"**，
"不得"是从字段定义的 "to be used with" 读出来的。

### 3A.12 迟到与重复：三条时间轴，两套去重键

**A-3 与 C-3 是这批里价值最高的两个**（§3A.8），两者都挂在"迟到"这个词上。
**冻结它们之前必须先把迟到量的是什么定下来。** 答案在 Volume 2 会话层，
**而且不是凭直觉猜得到的那个答案**。

#### 会话层不可能迟到超过两分钟

V2 p.42 的接收规则 n 与 o：`SendingTime`(52) 必须是 UTC，
且与原子钟时间的差在"合理范围（即 2 分钟）"之内。**超出则接收方必须发会话层 Reject**，
`SessionRejectReason = 10`（SendingTime accuracy problem），
递增入站序号，随后按规程走到 logout 与断连。

**因此"报文迟到"作为传输事件，在 FIX 会话层不存在。** 迟两分钟以上的报文进不来。

**A-3 与 C-3 说的迟到只能是另一件事**：业务事件发生在批次截止之前，
**而报文到达在截止之后**。迟的不是传输，是发送方决定发送的时刻。

**这一条要写死**，否则生成器会去做 `SendingTime` 与到达时刻的偏移，
**而那种数据在真实链路上会被对方直接拒掉**，看上去像有效样本，实际上不可能出现。

#### 三条时间轴，外加一条报文里没有的

| 轴 | 字段 | 层 | 含义 | 谁决定 |
|---|---|---|---|---|
| 业务事件时刻 | `TransactTime`(60) | 应用层 | 这件事在业务上何时发生 | 发送方的业务系统 |
| 发送时刻 | `SendingTime`(52) | 会话层 | 这条报文何时发出，**必须 UTC，且与原子钟差在两分钟内** | 发送方的 FIX 引擎 |
| 原始发送时刻 | `OrigSendingTime`(122) | 会话层 | 被重传报文的**首次**发送时刻 | 同上 |
| 摄入批次 | **无对应字段** | CMOP | 这条报文落到哪个夜间批次 | **CMOP 自己的管道** |

**第四条轴在报文里没有任何字段，它是 CMOP 加的。** 而它正是 A-3 与 C-3
**唯一能观测到迟到的地方**。

**`OrigSendingTime` 有一个陷阱。** 规范在标准头里写明：数据不可得时，
把它设成与 `SendingTime` 相同。**于是差值为零有两种截然不同的含义**——
同一秒内完成的重传，或者原始时刻根本不知道。

**CMOP 口径：只在 `PossDupFlag=Y` 且两者不等时计算该差值；相等时记为未知，不记为零。**
把未知记成零会把重传延迟的分布整体拉向左侧，**而每一条样本单独看都合法**。

规范另有一条硬约束：`OrigSendingTime` 必须小于等于 `SendingTime`，
**大于则接收方必须发 Reject**（V2 p.40 规则 f）。所以该差值不会为负。
**但"不为负"是被协议强制出来的，不是数据本身的性质**，
生成器不得因此省掉方向检查。

#### 两种重复，去重键正好相反

FIX 有两套重复机制。**它们的去重键相反**，混为一谈会同时造成漏删与误删。

| | 可能重复（Possible Duplicate） | 可能重发（Possible Resend） |
|---|---|---|
| 标志 | `PossDupFlag`(43) = Y | `PossResend`(97) = Y |
| 序号 | **与原件相同** | **是一个新序号** |
| 报文体 | 只有 CheckSum、`OrigSendingTime`、`SendingTime`、BodyLength、`PossDupFlag` 可变 | **与原件完全相同** |
| 触发 | 引擎不确定原件是否送达，或应答 Resend Request | 业务侧怀疑原件从未发出，例如订单长时间无应答 |
| 去重键 | 会话加序号，**机械可判** | **规范把责任交给应用** |
| 出处 | V2 p.5 | V2 p.5 |

可能重发那一格的规范原文是：接收方必须识别该标志，
并**检查内部字段（订单号等）**判断这一条此前是否已经收到。

**这就是本项目"重复"这一类差异的规范依据**，见[业务目标](business-objectives.md) §3.1 第 4 步。
**可能重复由管道机械去掉，可能重发去不掉**：它的去重必须落在业务键上，
而业务键随报文类型不同——分配是 `AllocID`，确认是 `ConfirmID`，成交是 `ExecID`。

**规范把这件事交给应用，等于承认协议层解决不了。**
因此 CMOP 在这一点上不是"实现规范"，**而是补规范留下的空档**，
地位与具名约束在 ISO 20022 那边相同（见 §4C.1）。

**一个后果要提前说清。** `PossResend` 的报文体与原件完全相同，**`TransactTime` 也相同**。
**所以重发件在业务时间轴上看不出是重发**，只有 `SendingTime` 与 `PossResend` 标志能区分它。
**若 Bronze 层不保留会话头，重发件与原件在 Silver 里将不可区分。**

**这是"Bronze 必须保留会话层字段"的第一个具体用例。** 此前只有"原样保留"这条原则性说法，
**原则挡不住有人在实现时把会话头当噪声删掉**，具体用例挡得住。

#### 这一节解锁了什么

- A-3 与 C-3 的"迟到"有了确切定义：**批次归属之差，不是时间戳之差**。
- "重复"这一类差异有了两条互不相同的判定路径，**且其中一条规范明说协议层解决不了**。
- Bronze 保留会话头从原则性要求变成了有具体失效场景的要求。

**还没有解锁的是重述。** 迟到的更正件到达之后要重述已发布的结果，
**而重述的版本保留机制属于 Silver 合并链**，不在本文范围，已登记在 TODO。

### 3A.13 A-3：分配迟到，T+1 早晨才到达，已冻结

**依据是 §3A.12 定下的迟到口径。** 本节只做一件规范之外的事：把它落到一条具体链上。

#### 规范先送了一份意外的佐证：必填的时间字段在两张报文上是互补的

核对 J 与 P 的字段表（V5-AI p.16、V5-AIA p.21）时出现一个此前没注意到的反转：

| 报文 | `TradeDate`(75) | `TransactTime`(60) |
|---|---|---|
| J 分配指令 | **必填** | **可选** |
| P 分配应答 | **可选** | **必填** |
| AK 确认 | **必填** | **必填** |
| AU 确认应答 | **必填** | **必填** |

**分配段的两张报文各带一半时间信息，且没有一张两样都必填。**

**后果直接落在 A-3 上：分配指令上唯一保证存在的时间信息是 `TradeDate`，而它是日期，没有时刻。**
**因此分配侧的迟到只能按天量。** §3A.12 从会话层推出"迟到 = 批次归属之差"，
**这里从字段必填性又独立得到同一个结论**，两条路径互不依赖。

**确认段两张报文都是两样必填，精度到秒。** 所以 **A-3 只能按天量，C-3 可以按秒量**，
两个场景的时间分辨率不同，**不要用同一套阈值**。

**CMOP 决定：J 上照样填 `TransactTime`，虽然规范不要求。**
理由不是合规，是可比性——不填的话，分配段与确认段的延迟统计没有共同刻度。
**这是决定，不是 FIX 明确**，任何以 J 的 `TransactTime` 为前提的断言都要标成推断。

#### 逐步取值

设成交发生在营业日 T，`SettlDate = T+1`（CMOP 口径，见 §3A.7）。
**L-1 的成交在批次 T 落地，分配三步全部落在批次 T+1。**

| 步 | 报文 | 落入批次 | 关键取值 |
|---|---|---|---|
| 0 | 8（成交回报） | **T** | L-1 终态，`TradeDate = T` |
| 1 | J | **T+1** | 与 A-1 第 1 步相同，`TradeDate = T`、`TransactTime` 取 T 日收市后 |
| 2 | P | **T+1** | `AllocStatus=3` |
| 3 | P | **T+1** | `AllocStatus=0` |

**报文本身没有任何字段说自己迟到了。** 迟到是 `TradeDate = T` 与"落入批次 T+1"这两件事
放在一起才看得出来，**而后者不是报文的属性，是管道的属性**。

#### 批次 T 报出差异是正确行为，不是缺陷

批次 T 里有成交、没有分配，**R1 必然报出差异**。**这条差异是对的。**

**A-3 要检验的不是"别报差异"，而是三件事：**

1. 批次 T 的差异**被报出来**，且归类为"缺失"而不是"金额不一致"。
2. 批次 T+1 收到分配之后，该差异**消失**。
3. 批次 T 已发布的结果**被重述，且重述前后两个版本同时保留**，
   见[业务目标](business-objectives.md) §3.1 第 5 步。

**第 3 条是 A-3 的全部价值所在。** 前两条任何一条对账都做得到，
**只有第 3 条要求版本保留**，而版本保留正是本项目的主 BO 要证的东西。

**因此 A-3 的验收判据不在对账结果上，在两个版本的可比性上。**
若实现把批次 T 的结果原地覆盖，前两条照样通过，**第 3 条静默失败**。

#### A-3 明确不做的两件事

1. **不做"迟到但仍在同一批次"。** 那不是迟到，是批次内乱序，**属另一类问题**，
   而且 §3A.12 已说明会话层不允许超过两分钟的传输延迟，批次内乱序的窗口极窄。
2. **不做迟到分配同时又被拒。** 那是 A-3 与 A-2 的组合，**两者的失效路径会互相掩盖**：
   重述会被误判为拒绝后的更正。**组合场景登记为 A-6，在两者各自的校验都跑通之后再做。**

### 3A.14 C-3：确认迟到，跨越结算日，已冻结，且它落到 S-2 上

**这是清单里最难的一个**，因为它是唯一一个跨越 FIX 与 ISO 20022 两个契约的场景。

#### 难在哪：Affirmed 是结算的前置条件

§3A.11 定下 VC-11：**只有 Model 1 到得了 `AffirmStatus = 3`**，
而规范把 Affirmed 解释为"该笔已可进入结算"。

**于是确认迟到跨越结算日会逼出一个选择**，且两条都不是无代价的：

- **照发结算指令，不等 affirm。** 结算按时完成，**但前置条件没满足**，
  这是内控问题而不是数据问题，**CMOP 不生成它**：它在数据上看不出异常，做出来也检验不到东西。
- **等 affirm，结算指令晚发。** 结算错过约定日，**落到 S-2**，
  即已冻结的"结算失败后延迟结算"（§4.6.2）。

**C-3 取第二条。** 理由是它把 FIX 段的迟到接到一条已经冻结的 ISO 20022 场景上，
**整条六段链因此第一次出现跨契约的因果**，而不只是首尾相接。

#### 逐步取值

设成交在 T，`SettlDate = T+1`。**C-1 的三步中，第 3 步的 affirm 落在批次 T+2。**

| 步 | 报文 | 落入批次 | 关键取值 |
|---|---|---|---|
| 1 | AK | T | 与 C-1 第 1 步相同，`ConfirmStatus=4`、`TradeDate=T` |
| 2 | AU | T | `AffirmStatus=1`（Received） |
| 3 | AU | **T+2** | `AffirmStatus=3`（Affirmed），`TransactTime` 在 T+2 早晨 |
| 4 | sese.023 | T+2 | 结算指令，`SttlmDt` 已过，**接 S-2 的入口** |
| 5 | — | T+2 起 | 其后完全走 S-2 已冻结的路径，本节不重复 |

**第 2 步与第 3 步之间跨了两个批次，这是 C-3 与 A-3 最实质的差别。**
A-3 的迟到发生在一段流程开始之前，**C-3 的迟到发生在一段流程中间**：
`AffirmStatus=1` 已经落库，下游看到的是一笔"已收到但未确认"的确认，
**它既不是缺失也不是错误，就是没走完**。

**这类"半完成"状态是本项目最难对的账**，因为它在任何单一批次里都看不出问题：
批次 T 里它是正常的中间态，批次 T+1 里它还是那个中间态，
**只有把"中间态停留了多久"当成一个量来看，它才异常**。

**因此 C-3 引入一条新的检查形状：状态停留时长。**
它既不是等式（R1、R2），也不是可达性（VA-11、VC-10），
**而是同一个键上两条报文的时间差与一个阈值比较**，且阈值来自业务日历而不是数据。

#### 精度：C-3 可以按秒量，但阈值只能按天设

AK 与 AU 两张报文的 `TradeDate` 与 `TransactTime` **都是必填**（见 §3A.13 的表），
所以停留时长可以算到秒。

**但阈值不能按秒设。** 判定"跨越结算日"用的是 `SettlDate`，那是一个日期；
**把秒级的停留时长与日期比较，需要先定日界，而日界是市场约定不是报文内容**。

**CMOP 口径：停留时长按秒记录，跨界判定按营业日做，两者分开存。**
合成一个字段会把"停留 23 小时但未跨日"与"停留 2 小时但跨日"混为一谈，
**而这两种在业务上是完全不同的事**。

#### C-3 明确不做的三件事

1. **不做"不等 affirm 直接结算"那一支。** 理由见上：它在数据上看不出异常。
   **登记在此是为了说明它被考虑过并被排除**，不是遗漏。
2. **不做确认迟到同时又被拒。** 与 A-6 同理，登记为 C-5。
3. **不做结算日当天的边界时刻。** 结算截止时点是市场约定，
   **CMOP 没有取得该数据**，也不打算凭印象编一个。**跨界判定只到营业日粒度。**

#### A-3 与 C-3 共同带出的断言

| 编号 | 断言 | 性质 |
|---|---|---|
| VT-8 | 分配侧的迟到只能按营业日量，**因为 J 上唯一必填的时间信息是 `TradeDate`** | FIX 明确 |
| VT-9 | 确认侧可按秒量停留时长，**但跨界判定仍按营业日** | **CMOP 口径** |
| VT-10 | 迟到导致的重述必须保留重述前后两个版本 | **CMOP 决定**，主 BO 的验收判据 |
| VT-11 | 批次 T 报出"分配缺失"是正确行为，**不得为了让批次干净而抑制它** | **CMOP 决定** |
| VT-12 | 停留时长与跨界标志**分两个字段存**，不得合成一个 | **CMOP 口径** |

## 4. ISO 20022

**第三批于 2026-09-10 开工，同日完成证券结算这一支。** 其余三支仍是待验证的起点。
**2026-09-12 追加两个场景**：S-3 撤销被执行与 S-4 撤销被拒办，见 §4.6.3 与 §4.6.4。
原登记为 S-4 的冲正改号为 S-5，理由是**撤销被拒办依赖更少而价值更高**。

| 领域 | 报文族 | 用途 | 状态 |
|---|---|---|---|
| 证券结算 | `sese` | 结算指令、状态通知、结算确认 | **已核对**，见 §4.1 起 |
| 资金账户 | `camt` | 账户报告、对账单、借贷通知 | **已核对**，见 §4A |
| 支付 | `pacs` | 资金划拨 | **已核对**，见 §4A |
| 公司行为 | `seev` | 公司行为通知与权益变动确认 | 待核对，优先级低 |

加拿大 Lynx 大额支付系统已采用 ISO 20022，其公开材料可作为本地化的出处之一。

### 4.1 出处

**出处是 ISO 20022 注册机构发布的规范 XSD，以及同一消息集的 Message Definition Report。**
消息集为 **Settlement and Reconciliation**（维护周期 2025–2026，证券 SEG 于 2026-01-27 批准，
最后更新 2026-03-17），schema 与 MDR 均由该站点直接取得。

| 出处 | 提供什么 | 可靠性 |
|---|---|---|
| 规范 XSD | 报文标识符、版本号、元素基数、枚举取值 | **规范性，无解释空间** |
| MDR Part 1 | 业务角色、业务流程、报文流、每种报文的完整实例样例 | **规范性说明文本** |
| MDR Part 2 与 Part 3 | 逐元素定义、**具名约束**与业务模型摘录 | **规范性，2026-09-12 已读完**，见 §4C |

**MDR Part 1 §5.7 的状态转移写在一张图里，不在文本里。** 该图由 SMPG 商定，**已逐块读完并
转录为 §4.4.1**。图中另有一处指向 SMPG 自己的市场实践文档，未跟进。

### 4.2 报文标识符与版本，已核对

`sese` 族在当前消息集里有 21 种 `001` 报文。**S-1 用到的三种及其邻接报文如下**，标识符与
版本号逐字取自 XSD 的 `targetNamespace`：

| 标识符 | 报文名 | 在 S-1 中的角色 |
|---|---|---|
| `sese.023.001.13` | SecuritiesSettlementTransactionInstruction | 发起结算 |
| `sese.024.001.14` | SecuritiesSettlementTransactionStatusAdvice | 状态通知 |
| `sese.025.001.13` | SecuritiesSettlementTransactionConfirmation | 结算确认 |
| `sese.026.001.12` | SecuritiesSettlementTransactionReversalAdvice | 冲正，属 S-4 |
| `sese.028.001.12` | SecuritiesSettlementTransactionAllegementNotification | 对方声称，属 S-3 |
| `sese.020.001.09` | SecuritiesTransactionCancellationRequest | 撤销请求，属 S-3 |

**每种报文有两个变体，必须选对。** `001` 是通用变体；`002` 是 ISO 15022 变体（消息集
Settlement and Reconciliation Variant 002，最后更新 2022-05-05），供 T2S 一类沿用 15022
惯例的基础设施使用。**CMOP 取 `001`**，因为项目不接任何真实市场基础设施，选变体只会引入
一套无人校验的额外约束。

**版本号是报文标识符的一部分，不是元数据。** `sese.023.001.13` 与 `sese.023.001.12` 是两个
不同的命名空间，**Bronze 落地时必须把完整标识符连同版本一起存下来**，否则日后无法判断某行
是按哪版 schema 解析的。这一条 FIX 侧不存在，FIX 的版本在会话层而非报文层。

### 4.3 结构与 FIX 根本不同，§3.3 的矩阵格式不能照搬

**FIX 是平铺的标签表，ISO 20022 是嵌套树。** §3.3 那种"标签 / 名称 / 必选"的三列矩阵在这里
表达不了东西：一个元素是否必填取决于它所在的整条路径。

**更要紧的是必填的含义不同。** `sese.023.001.13` 顶层只有五个分支是必填的：

| 路径 | 类型 | 基数 |
|---|---|---|
| `TxId` | Max35Text | 1..1 |
| `SttlmTpAndAddtlParams` | SettlementTypeAndAdditionalParameters23 | 1..1 |
| `TradDtls` | SecuritiesTradeDetails149 | 1..1 |
| `FinInstrmId` | SecurityIdentification19 | 1..1 |
| `QtyAndAcctDtls` | QuantityAndAccount117 | 1..1 |
| `SttlmParams` | SettlementDetails220 | 1..1 |

**沿这些分支往下走，真正必填的叶子只有七个**：`TxId`、`SctiesMvmntTp`、`Pmt`、
`TradDtls/SttlmDt`、`QtyAndAcctDtls/SttlmQty`、`SttlmParams/SctiesTxTp`，加上 `FinInstrmId`
这个分支本身。

**`FinInstrmId` 是最能说明问题的一个。** 它必填，但它的三个子元素 `ISIN`、`OthrId`、`Desc`
**全是可选的**（`SecurityIdentification19`）。也就是说，**一条只带空 `<FinInstrmId/>` 的结算
指令是 schema 合法的**——一条不说明结算什么证券的结算指令。**但它并不因此合规**：
MDR Part 2 有三条互补的具名约束把这条路堵死，**约束不在 XSD 里，标准校验器不会执行它们**。
见 §4C.1。

**结论要写死在这里：ISO 20022 的 schema 校验通过，几乎不说明任何业务正确性。** 一条近乎
空白的 `sese.023` 能过 XSD。**FIX 的必填列至少还挡得住一部分，ISO 20022 挡不住。**
[验证与对账规范](validation-and-reconciliation-specification.md) 因此必须为结算段单写一层
业务校验，**不能以"schema 校验通过"结案**。**该层已于 2026-09-12 写成，见该文 §2A。**
**同日读完 MDR Part 2 后，该层的一部分检查由 CMOP 决定改判为规范要求**，见 §4C.1。

### 4.4 状态不是一个字段，是三个正交的轴

**这是最容易把 FIX 经验套错的地方。** FIX 的 `OrdStatus`、`AllocStatus`、`ConfirmStatus` 都是
单字段单值。`sese.024.001.14` 不是：它顶层只有 `TxId` 必填，**四个状态元素全部可选**，而且
彼此正交。

| 轴 | 元素 | 取值结构 |
|---|---|---|
| 处理状态 | `PrcgSts` | 九选一：已接受、处理中挂起、拒绝、待修复、已撤销、撤销挂起、专有、需撤销、需修改 |
| 推断撮合状态 | `IfrrdMtchgSts` | 三选一：已撮合、未撮合、专有 |
| 市场撮合状态 | `MtchgSts` | 同上三选一 |
| 结算状态 | `SttlmSts` | 三选一：挂起、失败、专有 |

**四个轴可以同时有值。四轴全空过得了 XSD，但违反规范**：Part 2 有四条互补的具名约束
要求至少一个轴有值，见 §4C.1。
**"状态机"这个词在这里要谨慎使用**，它不是一张状态转移图。

**两个撮合轴不是重复，区别在于谁给的**（MDR Part 1 §5.7 决策图注记）：市场撮合状态是 CSD
给出的**官方**撮合状态；推断撮合状态是账务服务方**从 allegement 报告分析出来的**，原文明说
它不是官方状态、也不是市场撮合状态。**两者可以并存且可以不一致**，把它们合并成一个字段会
把"官方说法"与"我方推断"混为一谈。

**处理状态与结算状态的分工是有业务含义的**：前者说这条指令在账务服务方那里走到哪一步，
后者说钱券本身交割成没成。**一条指令可以处理状态"已接受"而结算状态"失败"**，这正是 T+1
早晨要处理的那一类。

#### 4.4.1 转移次序：已从 SMPG 决策图取得

**这一条此前登记为读不到，现已补上。** 决策图是 MDR Part 1 §5.7 内嵌的图片，由 SMPG 商定，
本轮已逐块读完。**它的组织方式不是按状态种类，而是按"这一步由谁执行"**：

| 带 | 执行方 | 该带上的过程与产出状态 |
|---|---|---|
| Common | 所有参与方均可给出 | 技术与业务校验 → 是否受理进一步处理 → **Accepted** / **Repair** / **Rejection** |
| Intermediary | CSD 以外的参与方 | 内部后续处理 → **Pending Processing** 或下一状态；推断撮合 → **Inferred Matched** / **Inferred Unmatched** |
| Market | CSD | 市场撮合 → **Matched** / **Unmatched**；结算过程 → 见下 |

**结算这一支的判定就是 S-2 要的那条规则，逐字抄录：**

1. 结算过程的第一个判定是 **"Before or After instructed settlement date?"**，即先看当前时点
   相对结算日的位置。
2. **Before** 分支进入"Pending?"判定，为是则给出 **Pending reason**，随后转入
   **Ready for settlement**。
3. **After** 分支进入"Failing?"判定，为是则给出 **Failing reason**，随后转入 **Recycled**。
4. 图注原文：**"In the Settlement process, the change from PENDING to FAILING occurs at END of
   Settlement Date."** **同一规则在 Part 2 里是带编号的具名约束 `PendingToFailingRule`**，
   并精确到日终报告过程与 `PEND`/`PENF` 两个代码，见 §4C.2。

**§4.5 那条"判定用的是结算日，不是原因本身"的推断，至此由规范原文证实**，并且精确到了时点：
**结算日结束时**，不是结算日开始时，也不是次日。

**另有三条约束同样来自图注，都会影响生成器：**

- **撮合与结算两个过程可以并行。** 并行时，未撮合的交易**只会带有属于账户持有方的挂起或
  失败原因，不带对手方的**。
- **撮合状态不是单调的。** 原文说一条已撮合、随后挂起或失败的指令**可以重新变回未撮合**，
  举的例子是对手方撤单。**把撮合状态当成只进不退的状态机是错的。**
- **交割地点决定用哪条带。** 当结算不在 CSD 而在中间机构完成时（原文举例为内部划转），
  **仍然发送 Market 状态**。

**图中有一处指向外部：** "Before or After instructed settlement date?" 的判定框注明
"(See chapter 7)"，该章不在 MDR Part 1 内，**指向的是 SMPG 自己的市场实践文档，本轮未跟进**。
判定规则本身已足够 S-2 使用，跟进只影响边界细节。

### 4.5 失败与挂起用的是同一批原因码，这直接对上主业务流

`SttlmSts` 的失败分支带 64 个原因码，挂起分支带 61 个，**两张表几乎完全重合**，
交集 57 个。逐码清点见 §4.6.2。

**重合不是冗余，是设计。** 同一个原因在结算日之前叫挂起、之后叫失败：`LACK`（券不足）、
`MONY`（款不足）、`CLAC`（对方账户余额不足）、`LATE`（迟到）、`DENO`（面额不匹配）在两张
表里都有。**判定用的是结算日，不是原因本身。**

**这一条直接落在 BO-1 上。** [业务目标](business-objectives.md) §3.1 的 T+1 早晨异常处理流
要检验的就是这个判定：**同一条原因码，在结算日前后被归入不同的状态轴**。S-2 因此是第三批
里价值最高的场景，理由与第二批的 A-3、C-3 相同。

**注意一个陷阱：这些是四字符代码，不是整数。** `LACK`、`MONY` 这类助记码不能像 FIX 的
`AllocStatus=0` 那样按序号处理，**生成器里任何"状态取值加一"式的写法在这里都无意义**。

### 4.6 S-1：最小结算生命周期，已冻结

**输入固定为 C-1 的终态**：每个账户一条 `AffirmStatus=3`（Affirmed）的确认。规范原文说
affirmed 可理解为该笔已可进入结算，见 §3A.5，**这就是第二批与第三批的接口**。

**MDR 给出的角色对与流程与此完全吻合**（Part 1 §5.1 与 §6.1）：由 **Instructing Party**
（原文举例为 investment manager）向 **Executing/Servicing Party**（原文举例为 global
custodian）发出结算指令；后者"may"回送处理状态与结算状态；交割发生后由后者发出结算确认。

**注意 MDR 用的是 "may"。** 与第二批不同——FIX 的示例流程把中间应答写成必列的一行，
**ISO 20022 的 MDR 明说状态通知是可选的**。因此 S-1 第 2 步保留是 CMOP 决定而非规范要求，
理由与 C-1 第 2 步相同：S-2 要测的失败判定必须有一根可观察的状态轴。

**S-1 对 C-1 的每一条已确认逐笔生成三步。** 取值来源分三类，与 §3A.1 同一套规则：继承的
不重编，派生的不采样，只有真正新引入的才采样。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `sese.023` | 账户持有方 → 账务服务方 | `TxId` 由种子派生；`SctiesMvmntTp` 按 L-1 的 `Side` 取 `DELI`（卖）或 `RECE`（买）；`Pmt=APMT`；`TradDt` 与 `SttlmDt` 取 L-1 交易日与其 + 1 营业日；`SctiesTxTp/Cd=TRAD`；`SttlmQty/Qty/Unit` 取该账户的 `AllocQty`；`FinInstrmId/OthrId` 用合成标的代码；`SfkpgAcct/Id` 取该分配账户；`SttlmAmt` 带 `Amt` 与 `CdtDbtInd` | 已发出 |
| 2 | `sese.024` | 账务服务方 → 账户持有方 | `TxId/AcctOwnrTxId` 回引第 1 步；`PrcgSts/AckdAccptd`；`TxDtls` 回带标的、数量、金额与两个日期 | 已受理 |
| 3 | `sese.025` | 账务服务方 → 账户持有方 | `TxIdDtls/AcctOwnrTxId` 回引第 1 步，并重复 `SctiesMvmntTp` 与 `Pmt`；`SttldAmt` 取该账户的 `AllocNetMoney`；`FctvSttlmDt` 与 `SttlmDt` 均填且相等，理由见 §4.6.2 | 已结算，S-1 结束 |

**三处取值决定已定案，理由如下：**

- **`Pmt=APMT`（against payment）而非 `FREE`。** 只有对价交割才让金额链条一路走到结算段；
  `FREE` 会把 `SttldAmt` 变成无意义字段。
- **`SctiesTxTp=TRAD`。** 44 个取值里只有它表示普通买卖交割，其余是回购、借贷、认购、
  公司行为等，均不在 CMOP 范围内。
- **`FinInstrmId` 走 `OthrId` 而不是 `ISIN`。** 标的是合成的，**填 ISIN 就是在声称一个并不
  存在的注册标识**，与账户维度 `AllocAcctIDSource` 取 99 是同一条原则，见
  [合成数据生成规范](data-generation-specification.md) §3A.6。

**`SttldAmt` 在 `sese.025` 上是可选的**（0..1），但 S-1 一律填。不填就断了金额链条，而金额
能一路对到结算段正是 BO-1 要证明的事。**这属于 CMOP 决定，不是规范要求。**

**MDR 的实例样例逐项证实了上面每一个取值选择**（Part 1 §7.16 至 §7.18）：样例用的正是
`SctiesMvmntTp=RECE`、`Pmt=APMT`、`SctiesTxTp/Cd=TRAD`，并同时填了 `TradDt` 与 `SttlmDt`、
`SfkpgAcct` 与 `SttlmAmt`。**这些字段在 schema 上都是可选的，样例却全都填了**，这正是
"schema 合法不等于业务可用"的直接例证，见 §4.3。

**样例还补出了两个 S-1 原先漏掉的必要项：**

- **`SfkpgAcct/Id`（保管账户）。** 它在 schema 上可选，但不填就说不清这笔结算属于哪个账户。
  **这是账户维度接进结算段的挂点**，见[合成数据生成规范](data-generation-specification.md) §3A。
- **`SttlmAmt/CdtDbtInd`（借贷方向）。** 它在 `AmountAndDirection94` 里是必填的 1..1，
  **取值随收付方向翻转**。**这与 `AllocNetMoney` 的符号随 `Side` 翻转是同一类坑**，见 §3A.7：
  生成器若两边同号，差错会以"金额对不上"的形式出现在很远的下游。

**2026-09-12 增补一个必填块：对手方一侧的结算方。** `sese.023` 的 C23 与 C52、
`sese.025` 的同名两条要求：不带常设结算指令时，**对手方一侧的 `Dpstry` 与 `Pty1` 都必填**。
CMOP 从不生成常设结算指令，**所以每一条都要带**。方向决定看哪一侧：

| 本笔方向 | 必填的块 | 必填的两个元素 |
|---|---|---|
| `SctiesMvmntTp=RECE`（买入、收券） | `DlvrgSttlmPties` | `Dpstry`、`Pty1` |
| `SctiesMvmntTp=DELI`（卖出、交券） | `RcvgSttlmPties` | `Dpstry`、`Pty1` |

**上面第 1 步与第 3 步的取值表因此各多一个块。** 状态序列与其余取值不变，
理由与取值口径见 §4C.7.1，**存管机构用 `PrtryId` 不用 BIC 的偏离见 §4C.7.2**。

### 4.6.1 同一个关联键，三张报文三个路径

**这是 MDR 读下来最实在的一个坑。** S-1 的三条报文靠同一个交易标识串起来，但它在三张报文里
的位置各不相同：

| 报文 | 路径 | 类型 |
|---|---|---|
| `sese.023` | `TxId` | Max35Text，直接在顶层 |
| `sese.024` | `TxId/AcctOwnrTxId` | 顶层是一个七元素的标识组 |
| `sese.025` | `TxIdDtls/AcctOwnrTxId` | 组名不同，且组内还重复 `SctiesMvmntTp` 与 `Pmt` |

**三个名字、三层深度、两种类型。** FIX 侧对应的是 `ClOrdID` 与 `AllocID` 在各报文里同名同形，
**这个习惯在 ISO 20022 不成立**。Bronze 的解析层必须为每种报文单独指定关联键路径，
**不能按字段名匹配**；Silver 拼链条时同理。

### 4.6.2 S-2：结算失败后延迟结算，已冻结

**S-2 是第三批里价值最高的场景**，理由见 §4.5：它检验的正是[业务目标](business-objectives.md)
§3.1 的 T+1 早晨异常处理流。**本节的判定规则全部来自 §4.4.1 的 SMPG 决策图，取值结构全部来自
`sese.024.001.14` 与 `sese.025.001.13` 的规范 XSD**，无一处自创。

#### 输入与覆盖面

**输入是 S-1 的第 2 步终态**，即已受理但尚未结算的指令。S-2 不新起指令，
**复用 S-1 已生成的 `sese.023` 与其 `TxId`**，与 A-1 接 L-1、S-1 接 C-1 是同一条规则：
**继承的不重编**。

覆盖面是 S-1 账户集合的一个子集，比例是自由参数，与
[合成数据生成规范](data-generation-specification.md) 的其他比例参数同列，
**本节不定具体数值**。未被选中的账户仍走 S-1 的三步。

#### 逐步取值

设 `SttlmDt` 为 S-1 指令上的约定结算日，`D` 为延迟营业日数（自由参数，最小 1）。

| 步 | 时点 | 报文 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | — | `sese.023` | **完全沿用 S-1 第 1 步，不重新生成** | 已发出 |
| 2 | — | `sese.024` | `PrcgSts/AckdAccptd`，沿用 S-1 第 2 步 | 已受理 |
| 3 | `SttlmDt` 当日，结算日结束之前 | `sese.024` | `SttlmSts/Pdg/Rsn/Cd/Cd` 取一个挂起原因码；`PrcgSts` 保持已受理 | 挂起 |
| 4 | `SttlmDt` 结束时 | `sese.024` | **同一个原因码**，改填 `SttlmSts/Flng/Rsn/Cd/Cd`；`PrcgSts` 仍保持已受理 | 失败 |
| 5 | `SttlmDt + D` | `sese.025` | `FctvSttlmDt` 取 `SttlmDt + D`，`SttlmDt` 仍填原约定日；其余沿用 S-1 第 3 步 | 已结算，S-2 结束 |

**第 3 步与第 4 步之间只变一件事：同一个原因码换了状态轴。** 这是 S-2 存在的全部理由。
决策图的原文是 **"the change from PENDING to FAILING occurs at END of Settlement Date"**，
所以**第 4 步的时点是结算日结束，不是次日开盘**，见 §4.4.1。

**`PrcgSts` 在第 3、4 步都保持"已受理"不变**，这不是疏忽。§4.4 已记：处理状态说指令在账务
服务方那里走到哪一步，结算状态说钱券交割成没成，**两者正交**。S-2 正是"处理状态已受理而
结算状态失败"的那一类。**若生成器把 `PrcgSts` 也改成拒绝或待修复，就把两个轴混成一个了。**

#### 原因码：取值范围已从 schema 精确取得

| 轴 | 元素路径 | 枚举类型 | 取值数 |
|---|---|---|---|
| 挂起 | `SttlmSts/Pdg/Rsn/Cd/Cd` | `PendingReason24Code` | **61** |
| 失败 | `SttlmSts/Flng/Rsn/Cd/Cd` | `FailingReason4Code` | **64** |

**两张表的交集是 57 个**，这是 S-2 可用的原因码池。**只在一张表里的不能用于 S-2**：

- **仅挂起有、失败无**（4 个）：`REFU`、`TAMM`、`NMAS`、`FUTU`。
- **仅失败有、挂起无**（7 个）：`BYIY`、`CLAT`、`CANR`、`OBJT`、`STCD`、`MLAT`、`CYCL`。

**§4.5 此前写的"失败 64 挂起 62"，挂起一侧应为 61**，本节以 schema 计数为准，§4.5 已同步更正。

**CMOP 取用口径：S-2 的原因码从这 57 个的交集里采样，且第 3 步与第 4 步必须同码。**
用只在一侧存在的码会让第 3 步或第 4 步无法生成，**这是 schema 层面的硬约束，不是口味问题**。
主业务流关心的那几个——`LACK` 券不足、`MONY` 款不足、`CLAC` 对方账户余额不足、`LATE` 迟到、
`DENO` 面额不匹配——**全部在交集内**，已逐一核对。

**注意这些是四字符助记码，不是整数**，见 §4.5 末尾那条陷阱。

#### 结构约束，直接来自 XSD

- `SettlementStatus30Choice` 是三选一：`Pdg`、`Flng`、`Prtry`。**一条 `sese.024` 不可能同时
  带挂起和失败**，所以第 3 步与第 4 步必须是两条报文，合并不了。
- `PendingStatus67Choice` 与 `FailingStatus13Choice` 同形，都是二选一：`NoSpcfdRsn`
  或 `Rsn`（**1..unbounded**）。**挂起或失败必须说明原因，或显式声明无原因**，
  两者都不给是 schema 非法的。这是结算段少见的一处真有约束力的地方。
- `Rsn` 可以有多条。**S-2 固定只给一条**，多原因留给更后面的场景。
- `FctvSttlmDt`（实际结算日）在 `sese.025` 里是 **1..1 必填**，而 `SttlmDt`（约定结算日）
  是 0..1 可选。**这是本节从 schema 挖到的最有用的一条**：延迟结算在数据上就表现为
  `FctvSttlmDt > SttlmDt`，而这个差值只有在两个日期都填了的时候才算得出来。
  **因此 S-1 与 S-2 的 `sese.025` 一律同时填两个日期**，S-1 里两者相等。
  这属于 CMOP 决定，理由与 §4.6 里 `SttldAmt` 一律填相同。

#### 不变量

每条都带适用条件，写法沿用 §3A.7 的教训。

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| S2-1 | 第 3 步的挂起原因码与第 4 步的失败原因码相同 | 仅 S-2；S-1 无此二步 |
| S2-2 | 失败报文的发出时点晚于挂起报文，且不早于 `SttlmDt` 结束 | 仅 S-2 |
| S2-3 | `FctvSttlmDt > SttlmDt` | 仅 S-2；S-1 下两者相等 |
| S2-4 | `PrcgSts` 在第 2 至第 4 步保持不变 | S-1 与 S-2 均成立；**S-3 破坏它**，第 6 步改为 `Canc`，见 §4.6.3；**S-4 不破坏它**，因为撤销被拒办时原指令状态不动 |
| S2-5 | 同一 `TxId` 下 `sese.024` 至少一条，可以多条 | **所有 S 场景**；S-1 恰好一条只是 S-1 的窄情形 |
| S2-6 | `sese.025` 恰好一条 | S-1 与 S-2；**部分结算与冲正会破坏它**，见下 |

**S2-6 的适用条件是本节特意标出的。** `AdditionalParameters29` 带 `PrtlSttlm`（部分结算）
与 `PrvsPrtlConfId`（前一条部分确认的标识），**schema 明说一笔指令可以有多条部分结算确认**。
S-1 与 S-2 都不产生部分结算，所以"恰好一条"在这两个场景下成立，**但它不是普遍规律**。

**2026-09-12 补：这个条件可以从场景挂到字段上。** Part 3 把 `PartialSettlementIndicator`
定义为"whether partial settlement is allowed"，**是逐笔指令上的开关**。S2-6 的适用条件因此
可改写为**"该指令未开启部分结算时"**，比"S-1 与 S-2 场景下"更准，也不必等场景扩展时重写。
用法见 §4C.3。
这是第四次遇到同一类问题，处理方式已固定：**先写普遍形式，再标窄条件**。

#### S-2 没有用到、且特意不用的东西

- **撮合状态两个轴一律不动。** 决策图说撮合与结算可并行，且撮合状态非单调（见 §4.4.1），
  但 S-2 的目的是隔离结算日判定这一条规则。**把撮合失败也掺进来会让失败原因归属不清**，
  那是更后面场景的事。
- **决策图里"未撮合的交易只带账户持有方的原因"这条约束，S-2 用不上**，因为 S-2 的指令
  是已受理且不涉及撮合分支的。登记在此，供 S-3 使用。
- **`Recycled` 状态不落报文。** 决策图里失败之后转入 Recycled，但它不是 `sese.024` 的某个
  枚举值，**是过程状态而非报文状态**。S-2 用第 5 步的实际结算日来表达同一件事。

### 4.6.3 S-3：撤销请求被执行，已冻结

**冻结日期 2026-09-12。** 出处是同一消息集的规范 XSD 与 MDR Part 2，读法与前几批相同，
**全程浏览器内存，未落盘**。

**S-3 用两种此前未读的报文**：`sese.020.001.09`（SecuritiesTransactionCancellationRequest）
与 `sese.027.001.09`（SecuritiesTransactionCancellationRequestStatusAdvice）。

#### 结构上与 S-1 最要紧的三点不同

**一、`sese.027` 的处理状态是必填的，`sese.024` 的不是。** `PrcgSts` 在 `sese.027` 上是
**1..1**，且是一个七选一：`PdgCxl` 撤销挂起、`Rjctd` 拒绝、`Rpr` 待修复、`AckdAccptd` 已受理、
`Prtry` 专有、`Dnd` 拒办、`Canc` 已撤销。**这与 §4.4 记的"四个状态元素全部可选"正相反**，
撤销状态回报**不可能没有状态**。

**因此 §2A 里为 `sese.024` 写的 V1-024-2"至少一个状态轴有值"，在 `sese.027` 上是多余的**，
schema 本身就保证了。**这是本项目第一次遇到"同族两张报文，一张需要补校验、一张不需要"**，
校验层不能按报文族一刀切。

**二、关联键又多了一层，且方向相反。** `sese.020` 的 `AcctOwnrTxId` 回引原指令，
而 `sese.027` 的 **`CxlReqRef` 是 1..1，回引的是撤销请求本身**，不是原指令。
原指令的标识在 `sese.027` 上落在可选的 `TxId` 里。

| 报文 | 必填关联键 | 指向 |
|---|---|---|
| `sese.020` | `AcctOwnrTxId`（1..1，三选一，其中一支为 `SctiesSttlmTxId`） | **原结算指令** |
| `sese.027` | `CxlReqRef`（1..1） | **撤销请求** |

**所以一条撤销链有两个锚点，缺一不可**：没有 `CxlReqRef` 拼不起撤销本身，
没有 `sese.020` 的回引就接不回原指令。**校验层要分别检查，不能合成一条。**

**三、规范给了一条 `sese.020` 专有的具名约束。** `TransactionIdentificationPresence2Rule`：
"If AccountOwnerTransactionIdentification is NONREF then at least one of the other references
must be present."。**即允许没有原始参考号，但那时必须给出别的引用**。
CMOP 一律有参考号，**这条因此不会被触发，登记备查**。

#### 逐步取值

**输入固定为 S-1 的第 2 步之后、第 3 步之前**：指令已被受理，尚未结算。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `sese.023` | 账户持有方 → 账务服务方 | 与 S-1 第 1 步完全相同 | 已发出 |
| 2 | `sese.024` | 账务服务方 → 账户持有方 | 与 S-1 第 2 步完全相同，`PrcgSts/AckdAccptd` | 已受理 |
| 3 | `sese.020` | 账户持有方 → 账务服务方 | `AcctOwnrTxId/SctiesSttlmTxId` 回引第 1 步的 `TxId`；`TxDtls` 回带标的、数量、结算日 | 撤销请求已发出 |
| 4 | `sese.027` | 账务服务方 → 账户持有方 | `CxlReqRef` 回引第 3 步；`PrcgSts/PdgCxl`，`NoSpcfdRsn=NORE` | 撤销处理中 |
| 5 | `sese.027` | 同上 | 同上回引；**`PrcgSts/Canc`，`Rsn/Cd=CANI`** | 已撤销 |
| 6 | `sese.024` | 同上 | 回引第 1 步；**`PrcgSts/Canc`** | 原指令终态，S-3 结束 |

**三处取值决定，理由如下：**

- ~~**第 5 步用 `CANI` 而不是 `CANS` 或 `CSUB`。** `CancelledStatusReason16Code` 里
  `CANI` 是 CancelledByYourself，`CANS` 是系统撤销，`CSUB` 是代理方撤销。~~
  **论证已作废，见 §4.6.6。** `Canc` 分支的词表是 `CancelledStatusReason5Code`，
  **只有 `CANI` 与 `OTHR` 两个成员**，`CANS` 与 `CSUB` 在这个分支上不存在。
  **取值不变：两个值里只有 `CANI` 有信息量。**
- **第 4 步保留，虽然它可以省。** 与 S-1 第 2 步同理：**撤销挂起是一个可观察的中间态**，
  没有它，S-3 就只剩请求与终态两点，测不出次序。**这是 CMOP 决定，不是规范要求。**
- **第 6 步必须存在。** 撤销成功后，原指令的处理状态要从 `AckdAccptd` 变成 `Canc`。
  `sese.024` 的 `PrcgSts` 正好带 `Canc` 分支。**不发第 6 步，原指令会永远停在已受理**，
  而它实际已经作废——**这正是 §4.4 说的"处理状态说这条指令走到哪一步"**。

#### S-3 明确不做的一件事，且它是规范里真实存在的分支

`sese.024` 的 `PrcgSts` 还有一个 `CxlReqd` 分支，规范定义原文：
**"Cancellation request from your counterparty for this transaction is pending waiting for
your cancellation request or consent."**

**这是双边撤销：已撮合的指令要撤销，对手方也必须请求或同意。** CMOP 的角色模型里只有
账户持有方与账务服务方（§3B），**没有建市场对手方**，因此这个分支无法生成。

**登记为已知边界，不是遗漏。** 它的代价是 S-3 只覆盖单边撤销；
**要覆盖双边，先要加对手方角色**，那是比 S-3 本身更大的一次扩展。

### 4.6.4 S-4：撤销请求被拒办，因为已经结算，已冻结

**冻结日期 2026-09-12。** S-4 原先登记的是冲正（`sese.026`），**本轮改为"撤销被拒办"**，
理由见下。

#### 为什么改

**冲正与撤销是两件事，而撤销被拒办的价值更高、依赖更少。** 冲正（`sese.026`）要与公司行为
重述交互，**依赖重述路径已经跑通**；而撤销被拒办只依赖 S-1 与 S-3，**两者都已冻结**。

**更重要的是它直接落在主业务流上。** [业务目标](business-objectives.md) §3.1 的 T+1 早晨
异常处理流里，操作员对着一条异常做的第一个动作就是"能不能撤"。
**规范对这个问题给了一个带代码的答案**：**`DeniedReason6Code`** 的 `DSET`，
定义为 DeniedSinceSettled——**因为已经结算，所以撤不了**。
**码集编号已于 §4.6.6 核实**：同族另有 `DeniedReason3/4/7Code`，码字母重合而定义不同。

**冲正没有消失，它变成 S-5**，见 §4.7。

#### 逐步取值

**输入固定为 S-1 的终态**：指令已结算，`sese.025` 已发出。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1–3 | 同 S-1 全部三步 | — | 完全继承，不重编 | 已结算 |
| 4 | `sese.020` | 账户持有方 → 账务服务方 | 回引第 1 步的 `TxId`；取值与 S-3 第 3 步相同 | 撤销请求已发出 |
| 5 | `sese.027` | 账务服务方 → 账户持有方 | `CxlReqRef` 回引第 4 步；**`PrcgSts/Dnd`，`Rsn/Cd=DSET`** | 撤销被拒办，S-4 结束 |

**两处要说清：**

- **没有 `PdgCxl` 中间态。** 已结算的指令，账务服务方一步即可判定拒办，
  **插一个撤销挂起反而不合业务**。S-3 有中间态、S-4 没有，**这个不对称是有意的**。
- **原指令的状态不变。** S-3 第 6 步要改原指令状态，S-4 **不改**：
  撤销没成功，原指令仍然是已结算。**生成器若照抄 S-3 加一条 `sese.024`，就是错的。**

#### S-4 让三条既有断言失效，必须同时改

| 断言 | 原写法 | S-4 下的问题 |
|---|---|---|
| S2-4 / V2-6 | `PrcgSts` 在同一 `TxId` 下不变 | **S-3 破坏它**（第 6 步改成 `Canc`）。S-4 不破坏，因为 S-4 不改原指令状态 |
| V2-2 | 同一 `TxId` 下 `sese.024` 至少一条 | 仍成立 |
| V2-4 | 同一 `TxId` 下报文时点严格递增 | **两个场景都要扩**：撤销链的报文也带 `TxId` 关联，**但它们的时点要与原链合并排序** |

**S-3 与 S-4 的区别本身就是一条可校验的契约**：

- **撤销成功 ⇒ 原指令必须有一条 `PrcgSts=Canc` 的 `sese.024`。**
- **撤销被拒办 ⇒ 原指令必须没有任何新的 `sese.024`。**

**这两条互为反面，合起来才完整。** 只写前一条，生成器在 S-4 上多发一条状态回报也查不出来。

### 4.6.5 S-5：冲正，已冻结，且它不依赖重述路径

**冻结日期 2026-09-12。** §4.7 原先把 S-5 标成"依赖重述路径先跑通"。
**这个依赖是记错的**：重述是公司行为侧的事实修改，冲正是结算侧的一条报文，
**两者会交互，但 S-5 的取值不需要等重述**。本轮按读到的结构直接冻结，
**与重述的交互另记为 S-7**。

#### 结构上最要紧的三点，全部来自 Part 2

**第一，冲正必须指名它冲掉的那条确认，而且是必填。**
`sese.026` 的 `ConfirmationReference <ConfRef>` 是 1..1，定义为
"Reference to the unambiguous identification of the confirmation as per the account servicer"。
**这与 S-3 撤销链的两个锚点是同一个形状**（§4.6.3），但比它更强：
撤销链里指向原指令的 `sese.020` 是一个可选链接块，**这里的确认引用是必填的**。

**第二，冲正不带任何原因。** `sese.026` 的顶层构件里**没有理由码，也没有理由文本**——
不是可选，是根本没有这个元素。对比：

| 报文 | 反向动作 | 是否带原因 |
|---|---|---|
| `sese.027` 撤销状态 | 撤销 | **带**，`Rsn/Cd`，S-3 取 `CANI` |
| `pacs.004` 退汇 | 退汇 | ~~**必须带**~~ **这一格是错的，已于 §4B.11 更正**：`GroupReturnAndReturnReasonRule` 的形式化多一个条件，理由只在已填自由文本时才必填 |
| `sese.026` 冲正 | 冲正 | **不带，结构上就没有** |

**这是一条对下游有实际后果的事实，不是趣闻。** 异常队列里一条冲正记录
**只能回答"哪条确认被冲掉了"，永远回答不了"为什么"**；
**任何声称能自动归因冲正的设计都是在编造规范没有的信息**。
原因要么来自别的渠道，要么就承认没有——这正是 BQ-1 的对账故事里
"能定位到笔，不等于能解释"那一层。

**第三，冲正是一条独立报文，不修改原确认。** 它自带完整的
`TradDtls`、`FinInstrmId`、`QtyAndAcctDtls`、`SttlmParams` 四个必填块，
**即把被冲掉的那笔完整重述一遍**。原 `sese.025` 的内容不变，
**"当前状态"由两条报文共同决定**，与 S-4 里"原指令状态不得改变"是同一条原则。

#### 逐步取值

**输入固定为 S-1 的终态**：一条已结算的确认。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `sese.026` | 账务服务方 → 账户持有方 | `TxIdDtls/AcctOwnrTxId` 回引 S-1 第 1 步的 `TxId`；**`ConfRef` 回引 S-1 第 3 步那条确认**；`SctiesMvmntTp` 与 `Pmt` 重复原值，**方向不翻转**；`FctvSttlmDt` 取原确认的同名值；`SttldQty` 与 `SttldAmt` 取原确认的同名值；对手方结算方块按 §4.6.1 的增补填 | 已冲正，S-5 结束 |

**两处决定：**

- **`SctiesMvmntTp` 不翻转。** 冲正不是反向交易，**是宣告原确认作废**。
  翻转方向会把它变成一笔新的相反交割，**那是另一回事，且会让持仓算两次**。
- **金额与数量照抄原确认，不重新采样。** 与"继承的值一律不重编"是同一条规则。

#### S-5 让两条既有断言需要加条件

| 编号 | 原状 | 本轮改动 |
|---|---|---|
| V2-2 | 同一 `TxId` 下 `sese.024` 至少一条 | 不变，**冲正不影响状态回报的数量** |
| S1-3 一类"确认恰好一条" | 按 `PrtlSttlmInd` 判定 | **仍然成立**：冲正不是确认，**`sese.026` 不计入确认计数** |
| 持仓与金额的聚合 | 按已结算确认求和 | **必须扣除被冲正的确认**，否则同一笔算两次。**这是 S-5 唯一真正难的地方**，登记为 Silver 的聚合口径要求 |

**第三条是 S-5 存在的理由。** 前两条都是"没影响"，
**只有聚合口径这一条会在任何一个求和的地方出错，而且错得很安静**。

#### S-5 特意不做的两件事

- **不生成部分冲正。** `PrevslySttldQty` 与 `RmngToBeSttldQty` 两个元素为部分冲正备着，
  **CMOP 一律不填**，理由同 §4.6.2 不生成部分结算。
- **不填 `CshSttlmSysPlc`。** 它是一个三选一：数字账本标识、BIC、LEI。
  **三个分支全部是真实世界的注册标识，没有专有标识这条出路**，
  **因此 CMOP 只能整块不填**。这与 §4C.7.2 的口径不同：那里可以改填专有标识，
  **这里没得改**。**登记为一条新的类别：没有专有出路的元素，只能整块缺席。**

### 4.6.6 第十一批：撤销两张报文的约束整表，并改正 S-3 引错的一个词表

**日期 2026-09-12。** S-3 与 S-4 冻结时只按需要读了 `sese.020` 与 `sese.027` 的结构，
**没有取约束整表，也没有把撤销原因码追到底**。本节补上，**结果推翻 §4.6.3 的一处论证**。

#### 先取整表：`sese.020` 二十五条，`sese.027` 二十六条

**两张的名字重合度很高，差异只有四处**，且四处都说明问题：

| 只在 `sese.020` | 只在 `sese.027` |
|---|---|
| `TransactionIdentificationPresence2Rule`（C25，**带形式化**） | `AdditionalReasonInforrmationRule`（C3） |
| — | `SecuritiesMarketPracticeGroupGuideline`（C24） |

**`AdditionalReasonInforrmationRule` 的名字在规范里就拼错了**，`Information` 多一个 r。
**这是"按名字搜索规范"的第六种翻车方式：名字本身是错的。**
本项目此前记过五种（§4C.10.1 与 §4B.12），这一种最简单也最难防。

C25 的形式化值得抄下来，因为它是**锚点退化但不消失**的第一个实例：

> On Condition …/TransactionIdentification is equal to value 'NONREF'
> Following Must be True /AccountServicerTransactionIdentification Must be present
> Or /MarketInfrastructureTransactionIdentification Must be present
> Or /ProcessorTransactionIdentification Must be present

配合 C12：**没有参考号时，`AcctOwnrTxId` 必须填字面量 `NONREF`。**
**`NONREF` 是规范强制的哨兵值，不是标识。** 任何按此字段做的关联都必须先排除它，
否则全部 `NONREF` 会被当成同一笔互相命中。

**至此锚点强度可以排成一条线。** 这张表此后是本项目的锚点分类基准，
**新读到的每一个关联键都要归进某一档**；**第五档于同日在 §4D.10 补上**。

| 档 | 实例 | 规范怎么说 | 判据怎么写 |
|---|---|---|---|
| 一、强制且唯一 | `EndToEndId`（§4A.6）；`CorpActnEvtId`（§4D.1） | 必填 | 直接断言命中 |
| 二、**退化但不消失** | `AcctOwnrTxId` + C12 + C25 | **可以没有，但那时必须给出替代引用** | 先判是不是哨兵值，再走替代引用 |
| 三、允许而不要求 | `TxDtls/Refs/EndToEndId`（§4B.12）；`OrgnlBizQry`（§4C.10.4） | 每一层都可选 | **先断言逐层存在，再断言命中** |
| 四、结构上不可能 | 整组退汇（§4B.11） | 承载它的元素被禁止出现 | **降级到批次级，并写明降级本身** |
| 五、**指针必填而目标可选** | `seev.037/MvmntConfId` → `seev.036/MvmntConfId`（§4D.10） | 指针 1..1，目标 0..1 | **两头都合规却接不上**，只能靠生成约定 |

**第五档最容易被漏掉**，因为看指针那一侧一切正常。

**2026-09-12 补一条正交维度：档位要按方向分别归。** 见 §4D.11.5。
同一个关联在正向可能是第四档、在反向是第三档，
**只记一个档位会让遍历的起点选反**。第四档另有两种成因：
**承载元素被约束禁止**（§4B.11），与**承载元素根本不存在**（§4D.11.3）。
**判据写法相同，可修复性不同。**

**这张表是本文四张方法基准表里的一张。** 另外三张同日建立，
放在[校验规范](validation-and-reconciliation-specification.md) §1A：
检查的五种形态、适用条件的四种来源、否定式断言的九条清单。
**四张表的分工是：本文这张管"数据里能不能接得上"，那三张管"检查该怎么写"。**
新读到的规范材料先落进这四张表之一，**再决定要不要开一个新场景**。

#### 改正：`Canc` 分支的原因词表只有两个值，不是十一个

§4.6.3 第 5 步写"用 `CANI` 而不是 `CANS` 或 `CSUB`"，并引 `CancelledStatusReason16Code`。
**引错了。** 把类型链追到底：

```
sese.027 /PrcgSts/Canc  →  CancellationStatus15Choice
                        →  Rsn (CancellationReason10)
                        →  Cd (CancellationReason21Choice)
                        →  CancelledStatusReason5Code
```

**`CancelledStatusReason5Code` 只有两个成员：**

| 码 | 名 |
|---|---|
| `CANI` | CancelledByYourself |
| `OTHR` | Other. See Narrative. |

**`CANS` 与 `CSUB` 在这个分支上根本不存在**，所以"在三者之间选 `CANI`"是一个不存在的选择。
**结论（用 `CANI`）仍然成立，论证作废。** ~~`CancelledStatusReason16Code` 里 `CANI` 是……
另两个会把撤销的发起方说错。~~ **改为：这个分支只有两个值，其中一个是 `OTHR`，
于是 `CANI` 是唯一有信息量的取值。**

**这一处与 §3A.11 记的确认拒绝词表是同一种病**：**成功侧的原因词表小到无法做原因分析。**
第二次出现，可以升格为一条读法：**看到"原因"两个字先数词表大小，再决定要不要做分析。**

#### 同一个词表，一份分发里有四个编号变体

`sese` 这一族里，**"取消状态原因"有四个码集，"拒办原因"也有四个**：

| 概念 | 码集 | 成员数 | 用在哪里 |
|---|---|---|---|
| 取消原因 | `CancelledStatusReason5Code` | **2** | **`sese.027` 的 `Canc` 分支** |
| 取消原因 | `CancelledStatusReason9Code` | 多 | 别处 |
| 取消原因 | `CancelledStatusReason12Code` | 多 | 别处 |
| 取消原因 | `CancelledStatusReason16Code` | **11** | **`sese.020` 的 `CxlRsn`** |
| 拒办原因 | `DeniedReason3Code` / `4` / `7` | 各不同 | 回购等别处 |
| 拒办原因 | **`DeniedReason6Code`** | **10** | **`sese.027` 的 `Dnd` 分支** |

**`DeniedReason4Code` 与 `DeniedReason6Code` 的码字母大量重合但名字不同**，
例如 `DSET` 在前者叫 DeniedSinceAlreadySettled、在后者叫 DeniedSinceSettled。
**按码字母搜索会搜到错的那个码集。**

**S-4 用的 `DSET` 落在 `DeniedReason6Code` 上**，原文：
"Request was denied because the instruction was settled."。**S-4 的取值不受影响，出处需更正。**

`DeniedReason6Code` 全部十个：`ADEA` 账务服务方截止时间已过、`CDCY` 币种流程受限、
`CDRE` 发行方 CSD 重整流程受限、`CDRG` 登记方流程受限、`DCAN` 已被撤销、
`DSET` 已结算、`DPRG` 结算进行中、`DREP` 回购已结束、`LATE` 市场截止时间已过、`OTHR`。

#### 撤销链上的信息量分布是不对称的，而且方向出人意料

| 位置 | 词表 | 成员数 |
|---|---|---|
| **请求方说为什么要撤** | `CancelledStatusReason16Code` | **11** |
| 服务方说撤成了，原因是 | `CancelledStatusReason5Code` | **2** |
| 服务方说撤不了，原因是 | `DeniedReason6Code` | **10** |

**请求侧和拒办侧都很细，成功侧几乎为零。**
**因此"为什么撤"这个问题只能从请求侧回答，不能从结果侧回答。**
而请求侧的 `CxlRsn` 是 **0..1**，规范不要求填。

**CMOP 的取用：`sese.020/CxlRsn/Cd` 一律必填。** 不填的情形注入为负例，
**其期望结果是只有 CMOP 判据报错**。

#### `CorpActnEvtId` 是 S-7 的接口，而它就在撤销请求里

`CancellationReason23` 除 `Cd` 外还有 **`CorporateActionEventIdentification` 0..1**。
配合 `CancelledStatusReason16Code` 的三个码：

| 码 | 含义 |
|---|---|
| `CORP` | CancelledDueToCorporateAction，因公司行为撤销 |
| `CANT` | CancelledDueToTransformation，**原交易被撤销并因公司行为替换** |
| `CANZ` | CancelledSplitPartialSettlement，**原交易被撤销并替换以允许部分结算** |
| `SCEX` | 标的不再合格；**规范明说公司行为相关的应当用 `CORP`** |

**`CANT` 正是 S-7 要的那条路径**：公司行为发生后，原指令不是被改写，
**而是被撤销并由一条新指令替换**。**这与 CMOP 的重述模型不是一回事**——
重述是同一事实的新版本，**而 `CANT` 是两条不同的交易**。

**S-7 的落点因此可以先定下来：不是改写 `sese.023`，是发 `sese.020`（`CxlRsn/Cd=CANT`，
带 `CorpActnEvtId`）再发一条新的 `sese.023`。** 仍不冻结，
理由是它要与 §7 的公司行为回放对齐，**但依赖从"重述路径"缩小为"事件标识对得上"**。

**`CANZ` 同时把部分结算的排序检查的接口也给出来了**，登记在未决项。

#### `sese.020` 的 `TxDtls` 是"可选块反面"的第二个实例

`TxDtls` 是 **0..1**，但它一旦出现：

| 元素 | 基数 |
|---|---|
| `FinInstrmId` | **1..1** |
| `SttlmDt` | **1..1** |
| `SttlmQty` | **1..1** |

**与 §4C.10.3 的 `camt.060/ReqdTxTp` 同形，本轮第二次遇到。**
**可选块的正确读法是"要么整块不给，要么整块给够"，不是"里面的字段都可以省"。**

#### 本节改动的既有条目

- §4.6.3 第 5 步的论证作废，取值不变。
- §4.6.4 的 `DSET` 出处更正为 `DeniedReason6Code`。
- S-7 的解锁条件由"重述路径跑通"改为"公司行为事件标识可用"，见 §4.7。

### 4.7 场景清单

与 L、A、C 三组一致：S-1 先冻结，其余按顺序解锁。

| 编号 | 场景 | 为什么要它 | 状态 |
|---|---|---|---|
| S-1 | 逐账户结算指令、受理、结算确认，一次通过 | 链条第五段，也是最后一段 | **已冻结**，见 §4.6 |
| S-2 | 结算失败后延迟结算 | **直接对应主业务流**，检验同一原因码在结算日前后落在不同状态轴 | **已冻结**，见 §4.6.2 |
| S-3 | 撤销请求被执行（`sese.020` 与 `sese.027`） | 制造同一 `TxId` 的多版本，并把处理状态推到终态 | **已冻结**，见 §4.6.3 |
| S-4 | 撤销请求被拒办，因为已结算 | **直接落在主业务流上**：操作员对异常做的第一个动作就是"能不能撤"，规范用 `DSET` 给了答案 | **已冻结**，见 §4.6.4 |
| S-5 | 冲正（`sese.026`） | 宣告一条已结算确认作废。**聚合口径必须扣除它，否则同一笔算两次** | **已冻结**，见 §4.6.5。**原记的"依赖重述路径"是记错的，已更正** |
| S-6 | 双边撤销（`sese.024` 的 `CxlReqd` 分支） | 已撮合指令的撤销需要对手方同意 | 待解锁，**先要加市场对手方角色**，见 §4.6.3 末段 |
| ~~S-7~~ | ~~冲正与公司行为重述交互~~ | **登记时把三条不同的路径混成了一条** | **已拆分为 S-7a／S-7b／S-7c，编号退役**，见 §4D.4 |
| S-7a | `seev.037` 过账冲正 | 九个原因码全是过账细节填错，**与事件无关** | **已冻结**，见 §4D.10 |
| S-7a′ | 冲正后重发修正的过账确认 | 判据要能区分"冲正后重发"与"重复过账" | 待解锁，见 §4D.10 |
| S-7b | `seev.039` 事件撤销与调整因子回退 | **这一条才真的依赖重述路径** | 待冻结，见 §4D.4 |
| S-7c | `sese.020` 带 `CxlRsn/Cd=CANT` 再发新指令 | **撤销并替换，不是重述** | 待冻结，见 §4.6.6 |

### 4.8 MDR 自身的两处不一致，登记而不改写

与第二批 FIX 侧同样的处理方式：**规范说什么就记什么，CMOP 的取用口径另记。**

1. **实例样例里的版本号是旧的。** §7.16 的标题写 `sese.023.001.13`，同一节的描述文字却写
   "This is done through a Securities Settlement Transaction Instruction (sese.023.001.07)"。
   §7.18 同样。**以标题与 XSD 的 `targetNamespace` 为准**，正文的版本号是遗留。
2. **各节样例之间对不上。** §7.16 的指令交易日为 2019-01-12、结算日 2019-01-15，而 §7.17
   声称是对该指令的状态回复，日期却是 2019-01-05 与 2019-01-08；§7.18 的收方链条也与 §7.16
   不同。**样例是各自独立编的，不构成一条连贯流程**，不能当作端到端流程证据使用。

**第二条的教训与第二批相同：样例可以证实单条报文的字段用法，不能证实链条。** 链条要看
Part 1 §5 与 §6 的流程图与角色表，那才是规范给的流程。

### 4.9 第三批还欠什么

- ~~状态转移次序未知。~~ **已于 2026-09-10 补上**，见 §4.4.1。决策图是图片，已逐块读完。
  遗留一处外部指针：判定框注的 "(See chapter 7)" 指向 SMPG 市场实践文档，未跟进，
  **只影响边界细节，不影响 S-2 的主判定**。
- ~~MDR Part 2 与 Part 3 未读。~~ **已于 2026-09-12 读完**，见 §4C。具名约束改判了两条
  检查的归属，并为 S-2 的时点判定提供了第二处独立出处。
- `camt` 与 `pacs` 属第四批，尚未开始。
- ~~结算段的业务校验层未写。~~ **已于 2026-09-12 写成**，见
  [验证与对账规范](validation-and-reconciliation-specification.md) §2A：三级划分、逐条检查、
  规范要求与 CMOP 决定分列、每条带适用条件。
- ~~S-1 引入了 Instructing Party 与 Executing/Servicing Party 两个角色，两层结构里没有它们。~~
  **已于 2026-09-12 定案**，见[合成数据生成规范](data-generation-specification.md) §3B：
  **两条路都不走**。账户持有方从账户函数式地推出，不新增层级；账务服务方与两个代理行合并成
  一个机构维度，**因为角色是事实侧的引用位置，不是维度侧的分类**。
## 4A. 第四批：资金报文族

**第四批于 2026-09-10 开工。** 与第三批同样的读法：先读规范 XSD 取标识符、基数与枚举，
不读 MDR 不下业务结论。**本批只做了 schema 这一层**，欠什么写在 §4A.8。

### 4A.1 出处与消息集

| 消息集 | 编号 | 最后更新 | 覆盖 |
|---|---|---|---|
| Bank-to-Customer Cash Management | 1246 | 2026-03-19 | `camt.052`、`camt.053`、`camt.054`、`camt.060` |
| Payments Clearing and Settlement | 1249 | 2026-03-19 | `pacs.002/003/004/007/008/009/010/028` |

两个消息集的 XSD 均由注册机构站点直接取得，**全程在浏览器内存中读取，未落盘**，与第三批一致。

### 4A.2 报文标识符与版本，已核对

| 报文标识符 | 根元素 | 用途 |
|---|---|---|
| `camt.052.001.14` | `BankToCustomerAccountReportV14` | 日内账户报告 |
| `camt.053.001.14` | `BankToCustomerStatementV14` | 日终对账单 |
| `camt.054.001.14` | `BankToCustomerDebitCreditNotificationV14` | 借贷通知 |
| `camt.060.001.07` | `AccountReportingRequestV07` | 报告请求 |
| `pacs.002.001.16` | `FIToFIPaymentStatusReportV16` | 支付状态回报 |
| `pacs.003.001.12` | `FIToFICustomerDirectDebitV12` | 客户直接借记 |
| `pacs.004.001.15` | `PaymentReturnV15` | 退汇 |
| `pacs.007.001.14` | `FIToFIPaymentReversalV14` | 冲正 |
| `pacs.008.001.14` | `FIToFICustomerCreditTransferV14` | 客户贷记划拨 |
| `pacs.009.001.13` | `FinancialInstitutionCreditTransferV13` | 机构间贷记划拨 |
| `pacs.010.001.06` | `FinancialInstitutionDirectDebitV06` | 机构间直接借记 |
| `pacs.028.001.07` | `FIToFIPaymentStatusRequestV07` | 状态查询 |

**版本号与第三批的 `sese` 不同步。** 同一天发布的两个消息集，版本尾号各自演进，
**不能从一个族的版本推另一个族的版本**，解析层按报文标识符逐一登记。

### 4A.3 `pacs` 是批量结构，`sese` 不是

这是第四批与第三批之间最大的结构差异，**直接影响 Bronze 的分区与关联口径**。

`pacs.008` 与 `pacs.009` 的根元素同形：

| 元素 | 类型 | 基数 |
|---|---|---|
| `GrpHdr` | `GroupHeader131` | 1..1 |
| `CdtTrfTxInf` | `CreditTransferTransaction73`（`pacs.008`）／`...79`（`pacs.009`） | **1..unbounded** |
| `SplmtryData` | `SupplementaryData1` | 0..unbounded |

**一条报文里可以装任意多笔交易。** `sese` 一条报文一笔指令，`pacs` 不是。Bronze 若按报文落行，
`pacs` 一行会藏着 N 笔业务事实；若按交易落行，又丢掉组层的 `GrpHdr`。**两者都要留**，
组层与交易层分两张表，靠 `GrpHdr/MsgId` 连接。

`GroupHeader131` 必填四项：`MsgId`、`CreDtTm`、**`NbOfTxs`**、`SttlmInf`。
**`CtrlSum` 是选填。** 批量报文强制带笔数、不强制带金额合计，
所以**"组内金额合计等于交易金额之和"这条校验只在 `CtrlSum` 出现时才可评估**，
不能写成无条件不变量——与 §3A.7 记下的同一类错误。

`SettlementInstruction15/SttlmMtd` 为 1..1，`SettlementMethod1Code` 取值为
`INDA`、`INGA`、`COVE`、`CLRG`，**这四个值在 schema 内联**。

### 4A.4 必填字段少得异常，`pacs.002` 一个都没有

| 类型 | 元素总数 | 必填数 | 必填项 |
|---|---|---|---|
| `CreditTransferTransaction73`（`pacs.008` 交易层） | 48 | 7 | `PmtId`、`IntrBkSttlmAmt`、`ChrgBr`、`Dbtr`、`DbtrAgt`、`CdtrAgt`、`Cdtr` |
| `CreditTransferTransaction79`（`pacs.009` 交易层） | 42 | 4 | `PmtId`、`IntrBkSttlmAmt`、`Dbtr`、`Cdtr` |
| `PaymentTransaction177`（`pacs.002` 交易层） | 19 | **0** | 无 |

**同为贷记划拨，客户版比机构版多三个必填项**：`ChrgBr`、`DbtrAgt`、`CdtrAgt`。
`ChargeBearerType1Code` 内联取值 `DEBT`、`CRED`、`SHAR`、`SLEV`。

**`pacs.002` 的交易层零必填**，比第三批 `sese.024` 的同类发现更极端：
根元素下 `OrgnlGrpInfAndSts` 与 `TxInfAndSts` 都是 0..unbounded，
**一条 schema 合法的 `pacs.002` 可以什么状态都不带**。结论与结算段相同：
**schema 校验在支付段几乎不证明任何事**，业务校验层必须自己写。
**该层已于 2026-09-12 写成，见[验证与对账规范](validation-and-reconciliation-specification.md) §2C。**
它不是结算段那一层的翻版：**批量结构把单报文一级拆成了两级**，理由见该文 §2C.1。

`OriginalGroupHeader22` 里只有 `OrgnlMsgId` 与 `OrgnlMsgNmId` 必填，
**`GrpSts` 是选填**——组层状态可以缺席，状态只落在交易层。

### 4A.5 本批最大的发现：状态词表不在 schema 里

`pacs.002` 中 `ExternalPaymentTransactionStatus1Code`、`ExternalPaymentGroupStatus1Code`、
`ExternalStatusReason1Code` 三个类型，**在 XSD 里的定义只是 `xs:string`，
`minLength` 1、`maxLength` 4，没有任何 enumeration**。

`pacs.002` 一张报文里这样的 `External*` 类型共 **23 个**；`camt.053` 共 **32 个**，
包括 `ExternalEntryStatus1Code`、`ExternalBalanceType1Code`、
`ExternalBankTransactionDomain1Code` 与其 Family、SubFamily。

**这与 `sese` 族不同。** 第三批里 `SecuritiesTransactionType23Code` 一类是内联枚举，
读 schema 就能拿到全部合法值。资金族把词表搬进了单独发布的 External Code Sets，
**只读 schema 无法告诉生成器哪些状态值合法**。

对 CMOP 的直接后果：

1. **资金段的枚举必须另取一份出处**。**已于 2026-09-12 取得**，见 §4A.9。
2. 在拿到词表之前，**不得编造状态码**。这一条已解除。
3. Bronze 解析层对 `External*` 字段**不能建枚举约束**，只能存字符串，
   合法性校验推到业务校验层，且该层依赖外部词表的版本。

### 4A.6 关联键：`EndToEndId` 是资金段回连证券段的唯一必填锚点

`PaymentIdentification13` 五个子元素：`InstrId`、`EndToEndId`、`TxId`、`UETR`、`ClrSysRef`，
**只有 `EndToEndId` 是 1..1**。

所以**资金段与证券结算段之间唯一保证存在的关联键就是 `EndToEndId`**。

**这个判断已在 §4B.2 收窄。** `pacs.009` 的 `UndrlygAllcn/RltdRefs` 里有专用的
`SctiesSttlmTxId`，规范本来就为回连证券段准备了字段，只是可选。**`EndToEndId` 是唯一必填的
锚点，不是唯一的锚点。**
CMOP 的取用口径：把 S 段的关联标识写进 `EndToEndId`，
`InstrId` 与 `UETR` 即便生成也只作冗余，**不作为连接依据**。

### 4A.7 `camt` 三张报表结构几乎相同，差别在基数

| | `camt.052` | `camt.053` | `camt.054` |
|---|---|---|---|
| 组头 | `GroupHeader116` | `GroupHeader116` | `GroupHeader116` |
| 主体元素 | `Rpt`（`AccountReport38`） | `Stmt`（`AccountStatement15`） | `Ntfctn`（`AccountNotification25`） |
| 主体基数 | 1..unbounded | 1..unbounded | 1..unbounded |
| 明细项类型 | `ReportEntry16` | `ReportEntry16` | `ReportEntry16` |
| `Bal` 余额 | **0..unbounded** | **1..unbounded** | **无此元素** |

**三张报表共用同一个明细项类型 `ReportEntry16`**，Bronze 的明细解析可以复用一套。

**差别在余额。** 对账单必须带至少一条余额，日内报告可以不带，通知根本没有余额元素。
这三条是 schema 直给的，构成三张报表在 CMOP 里的分工依据：
**只有 `camt.053` 能作为余额对账的基准**。

`ReportEntry16` 必填四项：`Amt`、`CdtDbtInd`、`Sts`、`BkTxCd`，
`CashBalance8` 必填四项：`Tp`、`Amt`、`CdtDbtInd`、`Dt`。
**`Sts` 与 `BkTxCd` 的取值都落在 External Code Sets 里**，见 §4A.5。

### 4A.8 第四批还欠什么

- ~~External Code Sets 未取。~~ **已于 2026-09-12 取得**，见 §4A.9。银行交易码需再走一层，
  同样已取得。
- ~~两个消息集的 MDR 未读。~~ **已于 2026-09-12 读完**，见 §4C.4 与 §4C.5。
  支付侧改述了 P1-8 的适用条件，资金管理侧给出"一条明细可覆盖二十笔支付"这一 P-4 前提。
- ~~`pacs` 批量结构的 Bronze 落地方案未定。~~ **已于 2026-09-12 定案**，见
  [批量支付报文的 Bronze 落地](../design/2026-09-12-bronze-landing-for-batch-payment-messages.md)。
  **不是两张表而是五张**：`UndrlygAllcn` 与 `pacs.002` 的两个层级都是 unbounded，
  各自成表。主键是技术键而非业务键，分区按摄取批次而非业务日期。
- ~~资金段的业务校验层未写。~~ **已于 2026-09-12 写成**，见
  [验证与对账规范](validation-and-reconciliation-specification.md) §2C。
- ~~`camt.060` 只取了根结构，请求侧未展开。~~ **已于 2026-09-12 展开**，见 §4C.10。
- ~~`seev` 公司行为族仍未开始，优先级低。~~ **已于 2026-09-12 开始**，见 §4D。
  **只读了 S-7 需要的部分**，十二张报文的约束整表仍欠。

### 4A.9 External Code Sets 已取得，词表缺口闭合

**取得日期 2026-09-12，版本 `2Q2026_externalcodesets_v3`。** 出处是注册机构 Catalogue 下
External Code Sets 页面发布的 XSD 压缩包，**与前四批一样全程在浏览器内存中读取，未落盘**。
同页说明：外部词表按季度更新，二月、五月、八月、十一月末由注册机构在 SEG 批准后发布，
**使用者必须以站点上的最新版为准**。

整份词表 **163 个 simpleType、3347 条码值**。

#### 资金段用得上的词表，逐个点清

| 类型 | 码值数 | 用在哪 |
|---|---|---|
| `ExternalPaymentTransactionStatus1Code` | 25 | `pacs.002` 交易层状态 |
| `ExternalPaymentGroupStatus1Code` | 13 | `pacs.002` 组层状态 |
| `ExternalStatusReason1Code` | **315** | `pacs.002` 状态原因 |
| `ExternalEntryStatus1Code` | **4** | `camt.052/053/054` 明细项状态 |
| `ExternalBalanceType1Code` | 10 | `camt.052/053` 余额类型 |
| `ExternalBalanceSubType1Code` | 22 | 同上 |
| `ExternalCashAccountType1Code` | 28 | 现金账户类型 |
| `ExternalReportingSource1Code` | 11 | 报表来源 |
| `ExternalCategoryPurpose1Code` | 49 | 业务类别 |
| `ExternalPurpose1Code` | 366 | 汇款用途 |
| `ExternalReturnReason1Code` | 104 | `pacs.004` 退汇原因 |
| `ExternalReversalReason1Code` | 11 | `pacs.007` 冲正原因 |
| `ExternalChargeType1Code` | 14 | 费用类型 |
| `ExternalLocalInstrument1Code` | 115 | 本地清算工具 |

**明细项状态只有四个值**，这与之前的悲观预期正相反：`BOOK` 已入账、`PDNG` 挂起、
`FUTR` 未来、`INFO` 仅供参考。**资金段最关键的那个词表反而是全份里最小的之一。**

余额类型十个值成对出现：`OPBD`/`OPAV` 期初已入账与可用、`CLBD`/`CLAV` 期末、
`ITBD`/`ITAV` 期间、`PRCD` 上期期末、`FWAV` 远期可用、`XPCD` 预期、`INFO` 参考。
**已入账与可用是两个不同的量**，`camt.053` 的余额对账要说清对的是哪一个。

支付交易状态二十五个值里，与 CMOP 相关的是 `RCVD` 已收、`ACTC` 技术校验通过、
`ACSP` 结算处理中、`ACSC` 借方账户结算完成、`ACCC` 贷方账户结算完成、`PDNG` 挂起、
`RJCT` 拒绝。**其余十八个是支票、现金提取、收款人核验等分支，不在本项目范围内。**

#### 两处必须记下来的坑

**第一，词表里有 33 条已废止码值，但它们仍然是 schema 合法的。** 全份 3347 条中
`RegistrationStatus` 为 `Obsolete` 的有 33 条，集中在 `ExternalLocalInstrument1Code`（25 条）、
`ExternalClearingSystemIdentification1Code`（4 条）、`ExternalUndertakingDocumentType2Code`（3 条）
与 `ExternalCashClearingSystem1Code`（1 条）。

**这些码在 XSD 里就是普通的 enumeration，没有任何形式上的区别**，废止只写在注解的
`RegistrationStatus` 里。**生成器若直接把 enumeration 列表当取值池，就会生成已废止的码，
而且校验不出来。** 取用口径：**解析 XSD 时必须同时读注解，只取 `Registered` 的码值。**

**第二，银行交易码根本不在这份词表里。** `ExternalBankTransactionDomain1Code`、
`ExternalBankTransactionFamily1Code`、`ExternalBankTransactionSubFamily1Code` 三个类型
在词表 XSD 里**存在但零枚举**，注解原文说它们发布在"外部银行交易码清单"里。

**这是第二层间接。** schema 指向 External Code Sets，External Code Sets 又指向另一份文件：
同页单独发布的 `BTC_Codification_30Nov2025.xlsx`，**发布日期 2025-11-30，比词表本身还旧**。
该表两张工作表，主表 **1567 行组合**（2026-09-12 逐行数过，此前记的"约 1569 行"是目测），11 个域：`PMNT` 支付、`CAMT` 资金管理、
`DERV` 衍生品、`FORX` 外汇、`LDAS` 贷款存款与银团、`CMDT` 大宗商品、`PMET` 贵金属、
`TRAD` 贸易服务、`SECU` 证券、`ACMT` 账户管理、`XTND` 扩展域。

**域、族、子族是有效组合表，不是三个独立枚举的笛卡尔积。** `ReportEntry16/BkTxCd` 必填，
所以 `camt` 的每一条明细都要给一个合法组合，**不能三层各自随机采样**。

**逐域计数（2026-09-12）：**

| 域 | 组合数 | 域 | 组合数 |
|---|---|---|---|
| `PMNT` 支付 | **433** | `SECU` 证券 | **396** |
| `LDAS` 贷款存款 | 136 | `DERV` 衍生品 | 135 |
| `TRAD` 贸易服务 | 106 | `FORX` 外汇 | 91 |
| `CMDT` 大宗商品 | 78 | `PMET` 贵金属 | 78 |
| `CAMT` 资金管理 | 59 | `ACMT` 账户管理 | 54 |
| `XTND` 扩展 | 1 | | |

**CMOP 只取 `PMNT` 与 `SECU` 两个域，共 829 行**，其余九个域与本项目无关。

#### 取用口径从"从表里取"收窄为三个具体组合

**"从合法组合里取"这句话在生成器里没法执行，本轮定死到码级：**

| 用在哪 | 组合 | 含义 |
|---|---|---|
| 付方对账单的借方明细 | **`PMNT` / `ICDT` / `FICT`** | Issued Credit Transfer / Financial Institution Credit Transfer |
| 收方对账单的贷方明细 | **`PMNT` / `RCDT` / `FICT`** | Received Credit Transfer，同一子族码 |
| 证券侧明细（将来用） | **`SECU` / `SETT` / `TRAD`** | Settlement / Trade |

**三个组合都在 1567 行里逐行核对过，不是推出来的。**
`FICT` 这个子族码在四个族下都存在——`ICDT`、`IRCT`、`RCDT`、`RRCT`——
**其中带 R 的两个是实时清算**，CMOP 不做实时，故只用 `ICDT` 与 `RCDT` 两个。

**收付两侧用不同的族码，这一点容易漏。** 同一笔划拨在付方账上是 `ICDT`、
在收方账上是 `RCDT`，**子族码相同**。**两边都填 `ICDT` 是能通过组合表校验的**，
因为那也是一个合法组合——**这类错误只有靠"方向与族码相容"这条额外检查才能发现**，
组合表本身管不到。

**表里还有一列 `Status`**，取值 `New` 1528、`Corrected` 35、`Updated` 4。
**它与词表的 `Registered`/`Obsolete` 不是一回事**，这里没有废止态，
**所以组合表不需要 §2C.7 那样的状态过滤**，只需要版本。

#### 版本化的后果

**外部词表按季度走自己的版本，与报文版本无关。** 这与项目在 FINTRAC 段落里已经提出的
问题是同一个（见 §5）：**结果必须声明它是在哪个词表版本下产生的。**

因此 Bronze 的资金段落地口径定为三条：

1. **`External*` 字段一律存字符串，不建枚举约束。** 理由已写在 §4A.5，此处不变。
2. **合法性校验放在业务校验层**，该层显式携带词表版本标识，本项目当前为 `2Q2026_v3`，
   银行交易码组合表为 `30Nov2025`。
3. **生成器的取值池与校验层共用同一份词表快照**，不各自去取。两边版本不同会产生
   一种极难查的差错：数据合法，校验说不合法，而两边都没错。

## 4B. 资金段最小生命周期 P-1，已冻结

**P-1 是六段链条的最后一段，也是把整条链闭合的那一段。** 冻结日期 2026-09-12。
取值结构全部来自 `pacs.009.001.13` 与 `pacs.002.001.16` 的规范 XSD，
取值范围来自 §4A.9 的 External Code Sets，**无一处自创**。

### 4B.1 报文选择：`pacs.009` 而不是 `pacs.008`

**这是本节唯一需要论证的选择，其余都是结构直给。**

两者根结构同形，都是组头加一个 1..unbounded 的交易列表。差别在交易层：

| | `pacs.008` | `pacs.009` |
|---|---|---|
| 交易类型 | `CreditTransferTransaction73`，48 元素 | `CreditTransferTransaction79`，42 元素 |
| 必填 | 7 项，含 `ChrgBr`、`DbtrAgt`、`CdtrAgt` | 4 项 |
| 底层分配 | **无** | **`UndrlygAllcn`，0..unbounded** |

**`UndrlygAllcn` 是决定性的。** 它的类型 `TransactionAllocation2` 五个子元素**全部必填**：

| 元素 | 类型 | 含义 |
|---|---|---|
| `Amt` | 金额 | 该账户分到的金额 |
| `CdtDbtInd` | 借贷方向 | 随收付方向翻转 |
| `Acct` | `CashAccount40` | 该账户的现金账户 |
| `Purp` | `Purpose2Choice` | 用途 |
| `Ref` | Max35Text | 引用 |

**这正是 A-1 已经生成的那张分配表。** 资金族里只有 `pacs.009` 带这个结构，
`pacs.008` 没有。CMOP 的链条是先大单后分配，**用一张报文承载整块金额并在其内部逐账户拆分，
与链条前四段的形状完全一致**；换成 `pacs.008` 就得每账户一张报文，
分配关系只能靠外部拼，白丢一个规范自带的结构。

**代价要记清楚**：`pacs.009` 是机构间划拨，参与方是金融机构而不是终端客户。
CMOP 的场景是托管行与经纪商之间的资金划拨，**这个定位是吻合的**，
但它意味着 P-1 生成的资金段里没有终端客户身份，客户身份只出现在证券段的保管账户上。
**这属于 CMOP 决定，不是规范要求。**

### 4B.2 关联键有三层，且第三层是规范专门为此设的

**这是本节从 schema 挖到的最有价值的一条。**

`References80Choice` 里第一个选项就是 **`SctiesSttlmTxId`（证券结算交易标识）**。
换句话说，**ISO 20022 早就想到了资金段要回连证券段，并给了一个专用字段**，
不需要任何自创约定。

| 层 | 路径 | 取什么 | 基数 |
|---|---|---|---|
| 整块 | `CdtTrfTxInf/PmtId/EndToEndId` | 大单层的关联键 | **1..1 必填** |
| 逐账户 | `CdtTrfTxInf/UndrlygAllcn/Ref` | A-1 的分配引用 | **1..1 必填** |
| 回连证券段 | `CdtTrfTxInf/UndrlygAllcn/RltdRefs/SctiesSttlmTxId` | **S-1 的 `sese.023` `TxId`** | 0..unbounded |

**§4A.6 此前判断 `EndToEndId` 是唯一锚点，这个判断要收窄。** 它是唯一**必填**的锚点，
是整块层的；**逐笔回连证券段有专用字段，只是可选**。CMOP 取用口径：**三层全填**。
理由与 §4.6 里 `SttldAmt` 一律填、§4.6.2 里两个结算日一律填相同——
**可选不等于可省，链条要能对上就得填。**

### 4B.3 逐步取值

**输入固定为 S-1 的终态**：一块大单下每个账户一条 `sese.025` 已结算确认。
P-1 与 S-1 是同一笔交易的券侧与款侧，**日期必须一致**，这是 DVP 的定义。

设该块共 N 个分配账户。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `pacs.009` | 付方代理行 → 收方代理行 | `GrpHdr/MsgId` 由种子派生；**`NbOfTxs=1`**；`CtrlSum` 填且等于交易金额；`SttlmInf/SttlmMtd=CLRG`；`PmtTpInf/CtgyPurp/Cd` 按方向取 `DVPM`（卖，交券收款）或 `RVPM`（买，收券付款）；**组头层** `IntrBkSttlmDt` 取 S-1 的 `SttlmDt`，**交易层同名元素一律缺席**（异或，见 §4C.8.1）；交易层 `IntrBkSttlmAmt` 为该块净额；`UndrlygAllcn` 共 N 条，每条 `Purp/Cd=SECU` | 已发出 |
| 2 | `pacs.002` | 收方代理行 → 付方代理行 | `TxInfAndSts/OrgnlEndToEndId` 回引第 1 步；**`TxSts=ACTC`**；`OrgnlGrpInf/OrgnlMsgId` 与 `OrgnlMsgNmId` 均填 | 已受理 |
| 3 | `pacs.002` | 同上 | 同上回引；**`TxSts=ACCC`**；`FctvIntrBkSttlmDt` 取实际结算日 | 已结算，P-1 结束 |

**三处取值决定已定案，理由如下：**

- **`SttlmMtd=CLRG`（通过清算系统）而非 `INDA`/`INGA`/`COVE`。** 后三者描述的是代理行账户
  或补偿路径，CMOP 的加拿大场景是 Lynx 这样的清算系统，`CLRG` 是唯一对得上的。
  四个取值在 schema 内联，见 §4A.3。
- **第 3 步用 `ACCC` 而不是 `ACSC`。** ~~两者只差一个字：`ACSC` 是借方账户结算完成~~
  **这句取自组级码集的定义，而它注解的是笔级字段，依据错了**，见 §4B.15.4。
  笔级 `ACSC` 的定义是无侧别的 "Settlement completed"。
  `ACCC` 是**贷方账户**结算完成。**只有后者证明钱到了对方**，而 BQ-1 的对账问的正是这件事。
  **结论不变，另有一条更强的理由**：笔级 `ACSC` 的定义自带 warning，
  说它不得当作财务信息，见 §4B.15.3。`ACSC` 特意不用，登记在此。
- **`CtgyPurp` 按方向取 `DVPM` 或 `RVPM`。** 两个码的名字就是 DeliverAgainstPayment 与
  ReceiveAgainstPayment，**与证券段 `SctiesMvmntTp` 的 `DELI`/`RECE` 一一对应**。
  两边由同一个 `Side` 派生，**不各自采样**。

**`CtrlSum` 在 schema 上可选，P-1 一律填。** 理由见 §4A.3：不填就没法评估组内合计，
而组内合计对不上正是批量结构最典型的差错形态。

### 4B.4 不变量

每条都带适用条件，写法沿用 §3A.7 与 §4.6.2。

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P1-1 | `NbOfTxs` 等于 `CdtTrfTxInf` 的实际条数 | **所有 `pacs` 报文**；schema 只保证字段存在，不保证一致 |
| P1-2 | `CtrlSum` 等于各 `IntrBkSttlmAmt` 之和 | **仅在 `CtrlSum` 出现时可评估**；P-1 一律填，故 P-1 下恒成立 |
| P1-3 | 各 `UndrlygAllcn/Amt` 之和等于 `IntrBkSttlmAmt` | 仅在 `UndrlygAllcn` 出现时；**schema 完全不要求，是 CMOP 约束** |
| P1-4 | 每条 `UndrlygAllcn/RltdRefs/SctiesSttlmTxId` 恰好命中一条 `sese.023` 的 `TxId` | P-1 与后续资金场景；**这是六段链条闭合的判据本身** |
| P1-5 | `UndrlygAllcn/CdtDbtInd` 与证券段 `SttlmAmt/CdtDbtInd` 方向相反 | 买卖双方各自视角下均成立 |
| P1-6 | `IntrBkSttlmDt` 等于 S-1 的 `SttlmDt` | **仅 DVP**；自由交割下款券两腿日期可以不同 |
| P1-7 | `FctvIntrBkSttlmDt` 等于 `IntrBkSttlmDt` | **仅 P-1**。2026-09-12 收窄：P-2 下成立的是 P1-9，**不是本条的放宽版**，见 §4B.8 |
| P1-9 | `FctvIntrBkSttlmDt` 等于券腿的 `FctvSttlmDt` | **仅 DVP**。2026-09-12 随 P-2 冻结新增，见 §4B.8 |
| P1-8 | 同一 `EndToEndId` 下 `pacs.002` 至少一条 | **所有资金场景**；P-1 恰好两条只是 P-1 的窄情形 |

**P1-5 是第三次遇到同一个符号坑**，前两次是 `AllocNetMoney` 随 `Side` 翻转（§3A.7）
与 `sese.025` 的 `SttlmAmt/CdtDbtInd`（§4.6）。**款券两腿方向相反是 DVP 的定义**，
生成器若两边同号，链条金额会在最后一段才对不上。

**P1-8 的写法特意用"至少一条"。** `pacs.002` 的交易层零必填（§4A.4），
一条状态回报可以什么都不带，也可以一次带多笔状态，**"恰好两条"只在 P-1 的窄条件下成立**。
这是第五次标注这类条件，处理方式已固定。

**2026-09-12 补注：P1-8 的适用条件要再收窄一层。** 支付 MDR Part 1 明说状态回报是可选的
（§4C.4），**真实世界里一条 `pacs.002` 都不发也是合规的**。P1-8 因此是**生成侧的自我约定**——
CMOP 一律产生状态回报，故在 CMOP 数据内恒成立——**不是可以拿去校验外部报文的规范不变量**。

### 4B.5 六段链条至此闭合

| 段 | 场景 | 关联键交给下一段 |
|---|---|---|
| 订单与成交 | L-1 | `ClOrdID`、成交量与均价 |
| 分配 | A-1 | `AllocID`、逐账户 `AllocQty` 与 `AllocNetMoney` |
| 确认 | C-1 | 逐账户 `AffirmStatus=3` |
| 结算 | S-1、S-2 | 逐账户 `sese.023` `TxId` |
| 清算与资金 | **P-1** | — |

**每一段都以上一段的终态为输入，继承的值一律不重编。** 这条规则从 A-1 立起，
到 P-1 没有破过例。

### 4B.6 场景清单

| 编号 | 场景 | 为什么要它 | 状态 |
|---|---|---|---|
| P-1 | 整块划拨、受理、贷方结算完成，一次通过 | 链条最后一段 | **已冻结**，见 §4B.3 |
| P-2 | **券款两腿同时延迟**，与 S-2 配对 | 检验实际结算日与预定结算日分离，**且两腿的实际日必须相等** | **已冻结**，见 §4B.8。**原描述"资金腿延迟、券腿正常"与 DVP 定义矛盾，已更正** |
| P-3 | 退汇（`pacs.004`） | 与 S-5 冲正配对：**券腿确认被冲正，已付的钱要回来** | **已冻结**，见 §4B.10 |
| P-6 | 整组退汇（`GrpRtr=true`） | 通道级故障，**且它是链条上唯一定位不到笔的一环** | **已冻结**，见 §4B.11 |
| P-4 | 日终对账单（`camt.053`） | **BQ-1 的对账故事落在这里**：一条明细可覆盖多笔支付，要靠逐笔回显定位 | **已冻结**，见 §4B.9 |
| P-5 | 未入账明细与内部账的对账 | **跨 `camt.052` 与 `camt.053` 两张报文**；锚点每一层都可选 | **已冻结**，见 §4B.12 |
| P-5a | 未入账后来被拒 | 日内报告说 `PDNG`，日终对账单里根本没有 | **已冻结**，见 §4B.13 |
| P-5a′ | 当日多份日内报告 | 与 `RptgPrd/Tp=CHNG` 一起做 | 待解锁，见 §4B.13 |
| P-5b | `FUTR` 未来日期明细 | 跨日；与起息日不同于入账日一起做 | 待解锁，见 §4B.12 末段 |
| P-7 | 报告请求与回执的配对 | **链条上第一条由账户持有方发起的报文** | 待解锁，见 §4C.10.5 |

### 4B.7 P-1 没有用到、且特意不用的东西

- **`camt` 三张报表一条都不产生。** P-1 只做划拨与状态，对账单属于 P-4。
- **`ExternalStatusReason1Code` 的 315 个码一个都不用。** P-1 一次通过，没有原因可填。
  拒绝与退汇分支要用它们，届时同样只取 `Registered` 的码，见 §4A.9。
- **银行交易码组合表 P-1 用不上**，它只在 `camt` 明细项上必填，因此推到 P-4。


## 4C. 第五批：三份 MDR 的 Part 1 至 Part 3 已读

**2026-09-12 读完三份 Message Definition Report**：Settlement and Reconciliation、
Payments Clearing and Settlement、Bank-to-Customer Cash Management。
**读法与前四批相同，全程在浏览器内存中读取，未落盘。** Part 1 是业务角色、流程与实例样例，
Part 2 是逐元素定义与**具名约束**，Part 3 是业务模型的 Excel 摘录。

**本批的价值集中在 Part 2 的具名约束上。** XSD 只表达基数与枚举，**表达不了"若 A 缺失则
B 必须存在"这类跨元素条件**，而这类条件恰好是 §4.3 与 §4.4 判定为"schema 挡不住"的那一部分。
Part 2 把它们写成了带编号的规范约束。**结论是：这些约束把此前记为 CMOP 决定的两条检查
改判为规范要求，但 §4.3 的总判断不变。**

### 4C.1 具名约束推翻了两处"schema 合法"的说法

**§4.3 说一条只带空 `<FinInstrmId/>` 的 `sese.023` 是 schema 合法的。这句话仍然成立，
但结论要收窄。** `sese.023`、`sese.024`、`sese.025` 三张报文各自带三条互补的具名约束：

| 约束名 | 原文 |
|---|---|
| `ISINPresenceRule` | If ISIN is not present then either Description or at least one occurrence of OtherIdentification must be present. |
| `DescriptionPresenceRule` | If Description is not present then either ISIN or at least one occurrence of OtherIdentification must be present. |
| `OtherIdentificationPresenceRule` | If OtherIdentification is not present then either ISIN or Description must be present. |

**三条合起来等价于"三个子元素至少有一个"。** 空 `<FinInstrmId/>` 因此**过 XSD 但违反规范
具名约束**——它不是规范允许的，只是 XSD 表达不了。**同理，§4.4 说"一条不带任何状态的
`sese.024` 是 schema 合法的"，`sese.024` 有四条互补约束把这条路堵死：**

| 约束名 | 原文 |
|---|---|
| `InferredMatchingStatusStatusPresenceRule` | If ProcessingStatus, MatchingStatus and SettlementStatus are absent, then InferredMatchingStatus must be present. |
| `MatchingStatusPresenceRule` | If ProcessingStatus, InferredMatchingStatus and SettlementStatus are absent, then MatchingStatus must be present. |
| `ProcessingStatusPresenceRule` | If InferredMatchingStatus, MatchingStatus and SettlementStatus are absent, then ProcessingStatus must be present. |
| `SettlementStatusPresenceRule` | If ProcessingStatus, InferredMatchingStatus and MatchingStatus are absent, then SettlementStatus must be present. |

**四条合起来等价于"四个状态轴至少有一个"。** 四轴全空同样是过 XSD 而违反规范。

**这不改变 §4.3 的总结论，只改变它的措辞。** 业务校验层仍然必须写，因为**具名约束不在
XSD 里，任何标准 XML 校验器都不会执行它们**；CMOP 的校验层是这些约束的唯一执行者。
改变的是归属：[验证与对账规范](validation-and-reconciliation-specification.md) §2A.3 的
V1-023-2 与 V1-024-2 此前记为 **CMOP** 决定，**现改判为规范要求**，已在该文改标。

**第三条改判是金额。** `sese.023` 带 `SettlementAmountRule`：
"If the instruction is against payment, then SettlementAmount must be present."，
条件路径为 `/SettlementTypeAndAdditionalParameters/Payment` 等于 `AgainstPaymentSettlement`。
V1-023-8 里"`SttlmAmt` 存在"这半句因此也是规范要求，**只有借贷方向相容那半句仍是 CMOP**。

**~~特意核对了一处没有改判的：`sese.025` 不带 `SettlementAmountRule`。~~
这条核对本身是错的，2026-09-12 在第六批里推翻，见 §4C.6.1。**
按名字检索约束是错的方法：`sese.025` 上的同一条约束叫 `SettledAmountRule`，
不叫 `SettlementAmountRule`。**V1-025-4 因此是规范要求，不是 CMOP 决定。**

### 4C.2 `PendingToFailingRule` 把 §4.4.1 的时点写成了规范条文

`sese.024` 的具名约束 `PendingToFailingRule` 原文：
**"A pending transaction (PEND) becomes a failing transaction (PENF) on the settlement date
instructed in the message, during the end of day reporting."**

**§4.4.1 此前只能引 SMPG 决策图的图注**（"the change from PENDING to FAILING occurs at END
of Settlement Date"）。**现在同一条规则在 Part 2 里是带编号的规范约束**，而且多给了两件事：
挂起与失败的代码是 `PEND` 与 `PENF`，翻转发生在**日终报告过程中**而非结算日任意时点。
S-2 的时点判定至此有两处独立出处，**不再依赖对一张图片的转录**。

### 4C.3 Part 3 给出 S-3 的入口，并把部分结算变成逐笔开关

Settlement and Reconciliation 的 Part 3 是业务模型的 Excel 摘录，逐条给业务元素定义。
两条对后续场景有直接影响：

- **`PartialSettlementIndicator :: Specifies whether partial settlement is allowed`。**
  部分结算是**逐笔指令上的开关**，不是市场层面的固定属性。`sese.025` 的
  `PartialSettlementGuideline` 补齐了用法：首条（可能多条）确认填 `PAIN`，
  **最后一条填 `PARC`**。**这让"一条指令恰好一条结算确认"这个条件可以挂在字段上**，
  而不是只挂在场景选择上——S-1 的这条前提因此可写成"`PrtlSttlmInd` 未开启时成立"。
- **`CancellationRequestIdentification`。** 撤销请求有自己的标识元素，
  S-3（撤销）场景的关联键不必另设。

**另有一条口径澄清**：Part 3 的 SettlementDate 定义同时覆盖实际结算日与预定结算日，
**§4.6.2 用 `FctvSttlmDt` 与 `SttlmDt` 两个元素区分二者的做法与规范口径一致**。

### 4C.4 支付 MDR：状态回报在每个场景里都是可选的

Payments Clearing and Settlement 的 Part 1 有一句直接影响 P1-8：
**"The creditor agent optionally confirms the processability ... by sending a positive
FIToFIPaymentStatusReport message."** **`pacs.002` 在规范描述的每个场景里都是可选的**，
不是流程的必经步骤；`pacs.028`（状态请求）就是为"迟迟收不到终态"这一情形设的催办报文。

**这对 §4B.4 的 P1-8 是加强而不是推翻。** P1-8 写的是"同一 `EndToEndId` 下 `pacs.002`
至少一条"，适用条件是"所有资金场景"。**按 Part 1，真实世界里零条也是合规的**，
所以 P1-8 的适用条件应改述为**"CMOP 一律产生状态回报，因此在 CMOP 数据内恒成立"**，
它是生成侧的自我约定，不是可以拿去校验外部报文的规范不变量。已在该表下补注。

**三处 P-1 取值在 Part 1 里没有样例背书，登记在此。** `ACCC`、`ACSC`、`ACTC`、`DVPM`
以及 `UndrlygAllcn` **在 Part 1 全文中一次都没出现**。它们的合法性来自 XSD 与外部词表
（§4A.9），不来自实例样例。**这不是缺陷，是出处等级的差别**：枚举取值的规范性出处是词表，
样例只证明用法习惯。**但它意味着 §4B.3 的三处取值决定没有"规范样例这么写"这一层支持**，
复核时不要去 Part 1 里找。

**样例本身也与 CMOP 的用法有出入。** Part 1 的 worked example 把 `SttlmMtd=CLRG` 与
`ClrSys/Prtry` 配对使用，**CMOP 的 P-1 只填 `SttlmMtd`，不填 `ClrSys`**。
Lynx 是否需要在 `ClrSys` 上给出系统标识未决，**登记为待验证项，不改 P-1**。

**`pacs.002` 的样例填得很满**：`StsId`、`OrgnlEndToEndId`、`OrgnlTxId`、`TxSts`，
外加一整段 `OrgnlTxRef` 回显。**这些字段没有一个是必填的**（§4A.4 已记录交易层零必填），
**样例却全都填了**——与 §4.6 里 `sese.023` 的情形完全一样，是"schema 可选、实践必填"的
又一例。P-1 的填法与样例一致，无需改动。

### 4C.5 资金管理 MDR：一条明细可以覆盖二十笔支付

Bank-to-Customer Cash Management 的 Part 1 对 P-4 有三处直接影响：

- **一条明细有三种状态**：pending、future、booked。`camt.053` 样例上是 `Sts=BOOK`。
  §4A.9 取到的 `ExternalEntryStatus1Code` 至此有了业务语义对应。
- **`BookgDt` 与 `ValDt` 在样例里是不同的日期**，样例还给出 `OPBD`/`CLBD` 期初期末余额与
  `BkTxCd` 的 `PMNT`/`RCDT`/`DMCT` 组合。**这三层结构 P-4 都要用上**，
  但 CMOP 取的子族是 `FICT` 不是 `DMCT`：**样例描述的是境内客户划拨，CMOP 是金融机构划拨**，
  见 §4A.9 定死的三个组合。
- **最要紧的一条：样例里有一条明细是 `Btch`，`NbOfTxs=20`。**
  **一条对账单明细可以对应二十笔支付**，不是一对一。P-4 的对账因此**不能假定明细与
  `pacs.009` 一一对应**，回连要走 `TxDtls` 层的 `EndToEndId`——样例正是在这一层回显它，
  与 §4A.6 认定的锚点一致。

**该 MDR 自身也有一处不一致，按 §4.8 的办法登记而不改写。** 它的 scope 明说不覆盖
金融中介之间的对账单，流程描述却又说报告适用于代理行往来账户（nostro）报告。
**两处出自同一份文档，取用时以 scope 为准**，CMOP 的 P-4 是银行对客户方向，不受影响。

### 4B.8 P-2：两腿同时延迟，已冻结，且原场景描述是错的

**冻结日期 2026-09-12。**

#### 先更正 §4B.6 原来的写法

P-2 原先写的是**"资金腿延迟，券腿正常"**，理由是"检验 DVP 两腿脱钩"。
**这句话与 DVP 的定义矛盾，本轮更正。**

**DVP 的含义就是券款同时交割**：付款没发生，交割就不发生。**一条券腿正常结算、款腿延迟的
链，在 DVP 下不可能存在**。它只能出现在自由交割（`Pmt=FREE`）下，
**而 CMOP 的全部已冻结场景都取 `APMT`**，见 §4.6。

**原描述会让生成器造出一批违反自身契约的数据，而且违反得很安静**：
每条报文单独看都合法，P1-6 又被标成"仅 DVP"因而不会对它求值，
**错误要到 §2C 的 C4 级跨段检查才暴露，那时根因已经离现场很远**。

**正确的 P-2 是：券款两腿同时延迟，与 S-2 配对。** 这既保住了 DVP 的定义，
又恰好覆盖了原描述真正想测的东西——**实际结算日与预定结算日分离**。

#### 逐步取值

**输入固定为 S-2 的终态**：券腿先挂起、后失败、最终延迟结算，
`FctvSttlmDt > SttlmDt`。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `pacs.009` | 付方代理行 → 收方代理行 | 与 P-1 第 1 步相同，**组头 `IntrBkSttlmDt` 仍取 S-2 的 `SttlmDt`（预定日，不是实际日）**；交易层同名元素缺席 | 已发出 |
| 2 | `pacs.002` | 收方代理行 → 付方代理行 | 回引第 1 步；**`TxSts=ACTC`** | 已受理 |
| 3 | `pacs.002` | 同上 | 同上回引；**`TxSts=PDNG`**，并带 `StsRsnInf` | 挂起 |
| 4 | `pacs.002` | 同上 | 同上回引；**`TxSts=ACCC`；`FctvIntrBkSttlmDt` 取 S-2 的 `FctvSttlmDt`** | 已结算，P-2 结束 |

**三处决定：**

- **第 1 步的 `IntrBkSttlmDt` 不改。** 它是**指示的**结算日，延迟不改变当初的指示。
  改了就等于事后重写了发起报文，**与"继承的值一律不重编"这条规则冲突**。
- **第 3 步的 `PDNG` 是本场景存在的理由。** `ExternalPaymentTransactionStatus1Code` 里
  `PDNG` 是挂起，与券腿的挂起状态一一对应。**款券两侧在同一时段各有一个挂起态，
  这是六段链条里唯一一处两段同时处于非终态的地方。**
- **第 4 步的 `FctvIntrBkSttlmDt` 必须等于券腿的 `FctvSttlmDt`，不是自行采样。**
  **这是 DVP 在延迟情形下的表现**，也是本场景最值得测的一条。

#### P-2 带出一条新的跨段不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P1-9 | `FctvIntrBkSttlmDt` 等于券腿的 `FctvSttlmDt` | **仅 DVP**。P-1 下两者都等于预定日，**P-2 下两者都大于预定日且彼此相等** |

**P1-7 要同时收窄。** 它原写"`FctvIntrBkSttlmDt` 等于 `IntrBkSttlmDt`，仅 P-1；延迟变体下大于"，
**现在延迟变体已经存在**，所以它的适用条件改为"仅 P-1"，
**而 P-2 下成立的是 P1-9，不是 P1-7 的放宽版**。两者是不同的断言，不要合并。

### 4B.9 P-4：日终对账单，已冻结

**冻结日期 2026-09-12。** [业务目标](business-objectives.md) BQ-1 的对账故事落在这里。

#### 一条明细不等于一笔支付，这是本场景的全部难点

MDR 样例里有一条明细是 `Btch`、`NbOfTxs=20`（§4C.5）。
**因此 P-4 不能按"一条支付对一条明细"生成，也不能按条数对账。**

**CMOP 的取用口径：同一交易日、同一方向、同一对手代理行的多笔划拨合并为一条批量明细。**
这个合并规则是 **CMOP 决定**，规范只说明细可以是批量的，不规定按什么合并。

#### 逐步取值

**输入固定为某一交易日全部 P-1 与 P-2 链的终态。**

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `camt.053` | 账务服务方 → 账户持有方 | `Bal` 至少两条：`Tp/Cd=OPBD` 期初已入账、`CLBD` 期末已入账；`Ntry` 若干条 | 日终对账单已发出，P-4 结束 |

**每条 `Ntry` 的取值：**

| 元素 | 取值 | 依据 |
|---|---|---|
| `Amt`、`CdtDbtInd` | 该批合计金额与方向 | 规范必填 |
| `Sts/Cd` | **`BOOK`** | 规范必填；四个值里只有它表示已入账 |
| `BkTxCd` | **借方 `PMNT/ICDT/FICT`，贷方 `PMNT/RCDT/FICT`** | 规范必填，**且三层必须是有效组合**；组合已定死到码级，见 §4A.9 |
| `BookgDt` | 入账日，等于该批的 `FctvIntrBkSttlmDt` | **CMOP**。schema 可选 |
| `ValDt` | 起息日，**与 `BookgDt` 可以不同** | **CMOP**。P-4 一律取相同，延迟起息留给后续场景 |
| `NtryDtls/Btch/NbOfTxs` | 该批笔数 | **CMOP**。合并成批时必填，单笔时不填 |
| `TxDtls/Refs/EndToEndId` | **逐笔回显**，每笔一条 `TxDtls` | **CMOP**，但**它是回连资金段的唯一途径**，见 §4A.6 |

**`TxDtls` 逐笔回显是 P-4 的硬要求，不是可选项。** 明细层只有合计金额，
**不逐笔回显 `EndToEndId`，对账就只能比总额，比不出是哪一笔对不上**——
而"对账不平时能定位到笔"正是主 BO 的全部内容，见
[业务目标](business-objectives.md) §1。

#### P-4 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P4-1 | `CLBD` 减 `OPBD` 等于当日全部 `Ntry` 的有符号金额之和 | 全部。**这是对账单自洽的基本判据** |
| P4-2 | 每条 `Ntry` 的 `Amt` 等于其 `TxDtls` 各笔金额之和 | **仅在 `TxDtls` 出现时**；P-4 一律给 |
| P4-3 | 每条 `TxDtls/Refs/EndToEndId` 恰好命中一条 `pacs.009` 交易行 | 全部。**这是资金段闭合的判据** |
| P4-4 | `Btch/NbOfTxs` 等于该 `Ntry` 下 `TxDtls` 的实际条数 | 仅批量明细。**与 P1-1 是同一类错误**，第三次出现 |
| P4-5 | 当日全部 `Ntry` 覆盖当日全部已结算的 `pacs.009` 交易行，**不多不少** | 全部。**漏一笔是缺失，多一笔是重复入账** |

**P4-1 是唯一一条能靠对账单自身判定的不变量**，其余四条都要对照资金段。
**这个区别有用**：P4-1 可以在只拿到对账单时先跑，**对应真实运营里"银行先到、内部账后到"
的那一段时间窗**。

#### P-4 特意不做的三件事

- **`camt.052` 与 `camt.054` 不生成。** 三张报表共用明细结构（§4A.7），
  **但只有 `camt.053` 必须带余额**，P4-1 依赖余额。
- **起息日与入账日一律相同。** 两者不同是真实现象，**但它引入的是另一类差异**，
  与本场景要测的"定位到笔"无关。
- ~~**不生成 `PDNG` 或 `FUTR` 状态的明细。** 四个入账状态里 P-4 只用 `BOOK`。~~
  **改正（§4B.12）：这不是 CMOP 的取舍，是规范的要求。** `camt.053` 的 scope 写明
  "contains information on booked entries only"，**它根本装不了未入账明细**。
  **未入账明细与内部账的对账是另一个场景**，落在 `camt.052`，登记为 P-5。

## 4C.6 第六批：撤销与冲正三张报文的具名约束，并推翻第五批的一处核对

**本批读的是 `sese.026`（冲正通知）、`sese.027`（撤销请求状态通知）与 `sese.028`
（交易通知）的 Part 2 具名约束清单**，起因是 §7 未决项里那句
"`sese.026` 至 `sese.028` 在 S-3 解锁时同样要先看 Part 2 再写检查"。
S-3 与 S-4 已于本日冻结，这笔账现在还上。

### 4C.6.1 推翻：`sese.025` 带的是 `SettledAmountRule`

§4C.1 末尾写过一句"特意核对了一处没有改判的：`sese.025` 不带 `SettlementAmountRule`"，
并据此让 V1-025-4 留在 CMOP。**这条核对是错的，本批推翻。**

`sese.025` 上有 `C56SettledAmountRule`，原文：

> "If the instruction is against payment, then SettledAmount must be present."
> On Condition `/TransactionIdentificationDetails/Payment` is equal to value
> `'AgainstPaymentSettlement'` Following Must be True `/SettledAmount` Must be present

**与 `sese.023` 的 `SettlementAmountRule` 是同一条规则的同构版本**：元素名随报文语义
从"结算金额"变成"已结算金额"，条件路径随该报文的结构从
`/SettlementTypeAndAdditionalParameters/Payment` 变成 `/TransactionIdentificationDetails/Payment`，
**规则本身一字未改**。`sese.026` 上的 `C54SettledAmountRule` 与 `sese.025` 完全相同。

**因此 V1-025-4 是规范要求，不是 CMOP 决定**，已在[校验规范](validation-and-reconciliation-specification.md)
§2A.3 改标。

**这次错误的根因值得单独记下来，因为它会再犯。** 上一批是**按约束名检索**的：
拿 `SettlementAmountRule` 这个字符串去三张报文里找，找不到就判定"没有这条约束"。
**ISO 20022 的约束名跟着元素名走，元素名跟着报文语义走**，同一条业务规则在不同报文上
叫不同的名字。**正确的方法是先列出该报文的全部具名约束，再逐条读，不能拿名字去命中。**
本批因此改成"取整张清单再逐条读"，§4C.1 至 §4C.5 里凡是"核对了某报文没有某约束"
的结论**都应当按这个方法重验**，本轮只重验了金额这一条。

### 4C.6.2 `Party2PresenceRule` 一族：结算方链条不得有洞

**四条约束，出现在本项目用到的每一张证券报文上**，包括已冻结的
`sese.023`、`sese.024`、`sese.025`：

> `Party2PresenceRule` If Party2 is present, then Party1 must be present.
> `Party3PresenceRule` If Party3 is present, then Party2 must be present.
> `Party4PresenceRule` If Party4 is present, then Party3 must be present.
> `Party5PresenceRule` If Party5 is present, then Party4 must be present.

**这四条合起来说的是一件事：结算方是一条从 1 到 5 的有序链，只能从头填，不能跳号。**
`Party3` 填了而 `Party2` 空着是违规，**哪怕两者各自都是合法的方标识**。

**这对 §3B 的方维度是一条直接约束，而 §3B 当时不知道它。**
[数据生成规范](data-generation-specification.md) §3B.1 说"角色不是实体"，
按角色槽位取方；**槽位之间原本被当作彼此独立**，现在它们不是。
生成器必须**先决定这一笔用几层结算方，再从 `Party1` 起连续填**。

**同一位置还有一条指引，说明这条链通常填到第几层：**

> `SettlementChainGuideline` SMPG recommends that at least three settlement parties
> be instructed ...; the depository, the participant of the depository (Party1) and
> the client of Party1 (Party2).

**它是 Guideline 不是 Rule，不进校验层。** 但它给了一个可用的默认值：
**存管机构加两层**，与 §3B.4"一个客户对一家机构"的简化正好相容。

### 4C.6.3 `NoAccountOwnerTransactionIdentificationRule`：缺失用哨兵值表示，不用空

> If no reference is available for the AccountOwnerTransactionIdentification, for example,
> the transaction was sent by fax, then the AccountOwnerTransactionIdentification must be `NONREF`.

**出现在 `sese.020`、`024`、`025`、`026`、`027` 等多张报文上**，包括两张已冻结的。

**这是本项目第一次遇到规范级的哨兵值。** 它的后果不在生成侧——CMOP 每一笔都有账户方引用，
**永远不会需要填 `NONREF`**——而在**读取侧与对账侧**：

- **`NONREF` 是一个合法取值，不是脏数据。** 任何"引用字段必须能连回上游"的检查
  **都必须把 `NONREF` 排除在外**，否则在外部数据上会把合规报文判成违规。
- **`NONREF` 不能参与去重与连接。** 多笔互不相关的交易可以同时填 `NONREF`，
  **按该字段连接会做出笛卡尔积**。这与 SQL 的 NULL 行为相反，容易错。
- **CMOP 自己不产生 `NONREF`，因此这条检查永远沉默。** 按 §6.2 的口径，
  **一条没有注入的断言等于没验证过**，所以它需要一条专门的注入，见校验规范 §6.4。

**这条规则同时说明了一件更一般的事**：ISO 20022 用哨兵值表达"无",
**而 CMOP 的 Silver 层用 NULL 表达"无"**。两者之间必须有一次显式转换，
**且转换必须是双向可逆的**，否则重放出去的报文与收进来的不是同一份。
登记为 Phase 1 的一项映射要求。

### 4C.6.4 `ShortLongNumberRule`：链接引用里的两个号码各有所指

> `ShortNumber` must contain the FIN message type number of the linked message.
> `LongNumber` must contain the XML message identifier of the linked message.

**出现在 `sese.020`、`021`、`022`、`023`、`027` 等报文的链接结构上。**

**它对 S-3 的撤销链有直接影响。** §4.6.3 记了撤销链的两个锚点
（`sese.020` 指向原指令、`CxlReqRef` 指向撤销请求），**但没有记链接结构里的号码字段**。
按本条：如果 CMOP 在链接里填了号码，**`LongNumber` 必须填被链报文的 XML 报文标识符**，
例如 `sese.023.001.13`，**不能填自定义编号，也不能填 FIN 报文类型号**。
`ShortNumber` 填的是 FIN 世界的报文类型号（MT 54x 一类），**CMOP 不产生 FIN 报文，
因此一律不填 `ShortNumber`**——这是 CMOP 决定，规范并不禁止两个都填。

### 4C.6.5 `AdditionalReasonInforrmationRule`：非结构化理由不得复述结构化字段

原文（**拼写错误在规范原文里，`Inforrmation` 双 r，照录不改**）：

> `AdditionalReasonInforrmationRule` The AdditionalReasonInformation element must not
> contain information that can be provided in a structured field unless bilaterally agreed.

**出现在 `sese.022`、`024`、`027` 等带理由码的报文上**，即 S-2 与 S-3 都会碰到。

**它是一条对生成器的约束，而且方向与直觉相反。** 直觉是"自由文本里多写点更真实"，
**规范说的恰好是反面**：理由码已经表达的内容，**自由文本里不得重复**。
CMOP 目前在 `StsRsnInf` 上只填码不填文本，**本条因此自动满足**；
它真正的价值是**挡住一类后续改动**——"给理由加一段人话好看些"这种改动，
如果那段人话复述了理由码，**就是违规的**。

登记为生成规范的一条否定性约束，与 §4.9"不生成自由文本"是同一条线。

## 4C.7 第七批：对三张已冻结报文重跑"取全清单"的方法，发现 S-1 缺一个必填块

**本批不是读新报文，是用 §4C.6.1 定下的正确方法重跑 `sese.023`、`sese.024`、`sese.025`。**
上一批的教训是"按名字检索得出的没有某约束不可信"，那么**按名字检索得出的
已经读完了同样不可信**。重跑的做法是先取出三张报文的全部具名条目再逐条看：
`sese.023` 七十一条、`sese.024` 三十一条、`sese.025` 五十五条。

**结果是 S-1 有一个必填块没生成。** 详见下。

### 4C.7.1 `DeliveringDepositoryAndParty1Rule` 与 `ReceivingDepositoryAndParty1Rule`

`sese.023` 上是 C23 与 C52，`sese.025` 上是 C15 与对称的一条。原文：

> C23 If the instruction is a receive and no standing settlement instruction applies,
> then DeliveringDepository and Party1 must be present.
> On Condition `/SettlementTypeAndAdditionalParameters/SecuritiesMovementType` is equal to
> value `'Receive'` And `/StandingSettlementInstructionDetails` is absent
> Following Must be True `/DeliveringSettlementParties/Depository` Must be present
> And `/DeliveringSettlementParties/Party1` Must be present

C52 是它的镜像：交付方向下 `ReceivingSettlementParties` 的 `Depository` 与 `Party1` 必填。

**对 CMOP 的后果是直接的，而且是本轮最贵的一条。**
CMOP 不生成 `StandingSettlementInstructionDetails`（常设结算指令），
**所以条件的后半句恒成立**；`SecuritiesMovementType` 每一笔非 `Receive` 即 `Delivery`，
**所以两条里必有一条被触发**。也就是说：

> **CMOP 的每一条 `sese.023` 与 `sese.025` 都必须带对手方一侧的
> `Depository` 与 `Party1`，二者都是有条件必填，不是可选。**

**S-1 与 S-2 的已冻结取值里没有这个块。** §4.6.1 逐步取值表只写了自身一侧的账户与方，
**对手方结算方一侧整块没有出现**。这不是写漏了一个字段，**是漏了一个结构块**，
而且是 XSD 判不出来的那一类——schema 上 `DeliveringSettlementParties` 是 0..1。

**处理方式与 §4.6.3 的做法一致：补齐，不是推翻。** 两个已冻结场景的状态序列不变，
增补的是每条 `sese.023` 与 `sese.025` 必须带的对手方结算方块。**冻结不等于不可增补**，
只是增补必须像这一条一样**有规范条文作为依据并注明日期**。

### 4C.7.2 补齐带来一个与 §3B.5 冲突的取值问题

同一处的 `DepositoryGuideline` 说：

> In a delivery, the receiving depository is to be understood as the requested depository
> of the receiving counterparty. ... The field must be populated with the BIC of a national
> or international CSD. When no CSD exists in a particular market, the stock exchange BIC is to be used.

**它要求填 BIC，而 CMOP 禁止使用 BIC**，理由见
[数据生成规范](data-generation-specification.md) §3B.5 与具名约束 `AnyBIC`
（只允许 ISO 9362 注册局已注册并公布的码，**编造的 BIC 就是违规值**）。

**这是本项目第一次出现 Rule 与 Guideline 指向不同结论的情形，处理口径在此定下：**

- **Rule 必须满足**：`Depository` 与 `Party1` 一定要填。
- **Guideline 可以不满足，但必须显式记下不满足**：CMOP 用 `PrtryId` 填存管机构，
  **不用 `AnyBIC`**。schema 上 `PartyIdentification` 的 BIC 与自定义标识是并列选择，
  **填自定义标识不违反任何 Rule**。
- **代价要写出来**：CMOP 的存管机构标识**不能与任何真实市场对上号**。
  凡是需要"按存管机构路由"的下游演示，**只能在 CMOP 内部自洽，不能声称与真实市场一致**。

**这条口径可以一般化**：本项目**凡遇 Guideline 要求填真实世界注册标识的，一律改填自定义标识，
并在该处记下偏离**。理由与 §3.1 那条可信度支点同源——**编造一个看起来像真的注册标识，
比明说这是自定义标识要糟得多**。

### 4C.7.3 `SettlementStatusAndMatchedRule`：状态缺席是有含义的

`sese.024` 的 C34：

> If settlement status/reason is present alone, then it means that the transaction is matched
> (if a matching process exists in the concerned market or at the concerned account servicer).

**这条改变的是读取语义，不是填写要求。** §4C.1 已记了四条状态存在性约束，
**它们说的是至少要有一个状态轴**；本条说的是**只有结算状态轴时，匹配状态的缺席不是未知，
是已匹配**。

**后果落在校验层与对账层：** 一条只带结算状态的 `sese.024`，
**不得判定为"匹配状态缺失"**，也不得在下游补成 NULL 后当作未匹配处理。
**这是第二次遇到"缺席带含义"**，第一次是 §4C.6.3 的 `NONREF`。
两者合起来说明一件事：**ISO 20022 的缺席不是 SQL 的 NULL**，
Bronze 到 Silver 的映射必须逐字段声明缺席的含义，不能统一映成 NULL。

**括号里的条件不要丢**："if a matching process exists"。CMOP 的所有已冻结场景都在
有匹配过程的市场里，**所以本条无条件适用；若将来加入无匹配过程的市场，本条自动失效**。

### 4C.7.4 三条限定适用范围的约束，记下来是为了挡住后续扩张

| 约束 | 原文要点 | 对 CMOP 的作用 |
|---|---|---|
| `SecuritiesFinancingSettlementRule`（023 C66） | 证券融资（回购、逆回购、借贷）场景下，结算指令**只能**用于开仓腿与平仓腿的普通结算 | **挡住"用结算指令表达回购全生命周期"这类扩张**。回购的其余环节要用别的报文 |
| `TwoLegTransactionOpeningClosing1Rule`（023 C77、024 C37、025 C62） | 两段式交易的开平仓由 `SecuritiesMovementType` 与 `SecuritiesTransactionType` 的**特定组合**确定，逐组合列出 | 若将来做回购，**组合表是现成的，不需要自己设计** |
| `WithLinkageRule`（023 C80） | 用 `WITH` 链接的若干指令**绑定执行**，一条不能执行则其余全部保持挂起；**因此 `WITH` 的使用应限于 2 至 3 笔** | **它是 S-2 挂起逻辑的一个放大版本**。CMOP 目前不生成链接，**一旦生成，挂起的传播范围就不再是单笔** |

**这三条现在都不产生检查，只产生边界。** 按 §6.2 的口径，
**没有数据就不写断言**；但**边界不写下来，下一次扩张就会在不知情的情况下越过它**。

## 4C.8 第八批：支付报文的具名约束，取全清单逐条读

**§4C.4 读支付 MDR 时用的是按名字检索，方法已在 §4C.6.1 判定不可信，本批重做。**
取全清单的结果：`pacs.009` 七十一条、`pacs.002` 二十五条、`pacs.004` 七十四条、
`pacs.007` 三十三条。**逐条读下来有一条直接推翻既有检查，两条把 CMOP 决定改判为规范要求。**

### 4C.8.1 推翻：`IntrBkSttlmDt` 不是"填就对"，它是一对互斥约束

两条约束合起来说的是一件完整的事：

> `GroupHeaderInterbankSettlementDateRule`（009 C13）If `GroupHeader/InterbankSettlementDate`
> is present, then `CreditTransferTransactionInformation/InterbankSettlementDate` is **not allowed**.
>
> `TransactionInterbankSettlementDateRule`（009 C71）If `GroupHeader/InterbankSettlementDate`
> is **not** present, then `CreditTransferTransactionInformation/InterbankSettlementDate`
> **must be present**.

**两条互为逆否，合起来是一条异或**：银行间结算日**恰好出现在一层**，
组头有则交易层禁止，组头无则交易层必填。

**校验规范的 C2-4 因此是错的。** 它写的是"交易层 `IntrBkSttlmDt` 非空，依据 CMOP，适用全部"。
**按本约束，只要组头填了日期，交易层填日期就是违规**——原检查在 CMOP 现有取值下
**恰好把合规数据判成缺失，把违规数据判成合格**，两个方向都反了。

**CMOP 的取值定在组头层，理由与代价一起写下来：**

- **取组头层**：P-1 与 P-2 的每个块 `NbOfTxs=1`，两层没有区别；
  **组头层少一层嵌套，Bronze 的五张表里日期只落在父表**，见
  [设计文档](../design/2026-09-12-bronze-landing-for-batch-payment-messages.md)。
- **代价是它锁死了一类将来**：一旦一个块里的多笔交易需要不同的结算日
  （部分延迟就会造成这种情形），**日期必须整体下移到交易层，组头层同时清空**。
  这不是加字段，**是一次跨两层的改动**，因为异或不允许两层并存。
- **`TtlIntrBkSttlmAmt` 因此也不能随便加。** `TotalInterbankSettlementAmountAndDateRule`
  （009 C67）说总额出现则结算日必须出现；CMOP 目前不填总额，**填了就把日期锁在组头层**。

### 4C.8.2 两条改判：组内合计与币种一致性是规范要求

| 约束 | 原文 | 影响 |
|---|---|---|
| `TotalInterbankSettlementAmountAndSumRule`（009 C68） | 组头总额若出现，**必须等于**各交易 `IntrBkSttlmAmt` 之和 | **与 C1-3 同形**。C1-3 查的是 `CtrlSum`，本条查的是 `TtlIntrBkSttlmAmt`，**两个不同字段各有一条同形规则**，一条是 CMOP 一条是规范 |
| `TotalInterbankSettlementAmountRule`（009 C69） | 组头总额若出现，各交易金额**必须与总额同币种** | **CMOP 的 C2-3 后半句"币种与该块一致"由此获得规范依据**，前半句"金额为正"仍是 CMOP |

**`CtrlSum` 与 `TtlIntrBkSttlmAmt` 的区别要写清楚，否则下一个人会把两条检查合并。**
`CtrlSum` 是组头的控制合计，**规范不检查它与交易金额的关系**；
`TtlIntrBkSttlmAmt` 是银行间结算总额，**规范检查它**。
**CMOP 填前者不填后者**，所以现在只有 CMOP 那条检查在跑。

### 4C.8.3 `SettlementMethod` 一族：结算方式决定哪些元素被禁止

**四条约束，全部是禁止式的**，`pacs.009` C59 至 C62：

| 结算方式 | 禁止出现的元素 | 必须出现的元素 |
|---|---|---|
| `INDA` / `INGA` | `ReimbursementAgent` 各方、`ClearingSystem` | — |
| `CLRG` | `SettlementAccount`、`ReimbursementAgent` 各方 | — |
| `COVE` | `SettlementAccount`、`ClearingSystem` | `InstructedReimbursementAgent` 或 `InstructingReimbursementAgent` |

**这对 §4C.4 里那条观察是正面回答。** 那里记过一个疑问：MDR 的样例把
`SttlmMtd=CLRG` 与 `ClrSys/Prtry` 配在一起，而 CMOP 不填 `ClrSys`。
**现在可以确定 CMOP 的取值是合规的**：`CLRG` 禁止的是结算账户与偿付代理行，
**并不要求填清算系统**。样例填了是因为样例描述的是一个具体清算系统，不是因为规则要求。

**同时得到一条 CMOP 必须遵守的禁止项**：既然取 `SttlmMtd=CLRG`，
**`SttlmAcct` 与三个 `RmbrsmntAgt` 一律不得出现**。它们在 schema 上都是可选的，
**XSD 判不出来**。

### 4C.8.4 `pacs.002` 的组状态与笔状态不是各自独立的

四条约束（002 C10 至 C13）把组状态与笔状态绑在一起：

| 组状态 | 对笔状态的约束 |
|---|---|
| `ACTC`、`ACCP`、`ACSP`、`ACSC`、`ACWC` | 笔状态**不得**为 `RJCT` |
| `PDNG` | 笔状态**不得**为 `RJCT` |
| `RJCT` | 笔状态若出现，**必须**为 `RJCT` |
| `RCVD` | 见 `GroupStatusReceivedRule`，同族 |

**CMOP 目前不填组状态，所以四条都不触发。** 但它们说明了一件对 §2C.2 分级有用的事：
**规范自己也认为组头与交易行的状态不是两个独立事实**。§2C.2 按爆炸半径把组头违规与
交易行违规分成 C1 与 C2 两级，**本族约束是这个分法在规范侧的对应物**。

**还有两条与理由码有关：**

- `StatusReasonInformationRule`（002 C28）：组状态不是 `RJCT` 也不是 `PDNG` 时，
  **`StsRsnInf/AddtlInf` 必须缺席**。**这与结算段的
  `AdditionalReasonInforrmationRule`（§4C.6.5）是同一条思路的两种写法**：
  自由文本不是想填就填的。
- `StatusReasonRule`（002 C29）：`Rsn/Cd` 取 `NARR` 时，`AddtlInf` **必须出现**。
  **CMOP 不使用 `NARR`**，因为使用它就必须写自由文本，与 §4.9 冲突。**登记为禁用码值。**

### 4C.8.5 `OriginalGroupInformation` 三条：回连锚点在两层之间二选一

> `OriginalGroupInformationAbsenceRule`（002 C20）If `OriginalGroupInformationAndStatus` is absent,
> then `TransactionInformationAndStatus[*]/OriginalGroupInformation` must be present.

**与 §4C.8.1 的日期异或是同一个形状**：回连信息**必须至少出现在一层**，
组头层缺席则交易层必填。**这是本轮第二次遇到"两层之间二选一"的结构**，
足以说明它是 `pacs` 家族的通用设计，不是个例。

**对 CMOP 的后果**：现在 `pacs.002` 只在交易层回引（C2-9），**这是合规的**，
但**它现在有了规范依据，不再只是 CMOP 决定**——若将来改成只在组头层回引，
交易层就可以不填，**C2-9 那条"不填即孤儿"的说法要同时改**。

### 4C.8.6 `TransactionIdentificationPresenceRule`：又一条二选一

> `TransactionIdentification` or `UETR` must be present. Both may be present.（009 C70）

**CMOP 填 `TxId` 不填 `UETR`，合规。** 记下来的理由是：`UETR` 是端到端唯一交易参考号，
**真实跨行支付里它才是主键**。CMOP 不用它，**是因为它的格式是 UUID v4，
生成一个看起来合法的 UETR 与编造 BIC 属于同一类问题**，见 §4C.7.2 定下的口径。

## 4C.9 第九批：资金管理报文的具名约束，并补上一条被忽略的前提

**取全清单：`camt.052`、`camt.053`、`camt.054` 各二十二条上下，`camt.060` 只有三条。**
**三张报表的清单几乎逐条相同**，只有分页那一条随报表名改名，
这从规范侧证实了 §4A.7 记的"三张报表共用明细结构"。

### 4C.9.1 最重要的一条不在资金管理报文里，在支付报文里

> `UnderlyingAllocationGuideline`（`pacs.009` C78，`camt.053` C31，两处一字不差）
> `UnderlyingAllocation` may only be present if **bilaterally agreed**.

**CMOP 把资金段与证券段连起来的全部机制，架在这个元素上。** §4B.2 选
`pacs.009`（金融机构信用划拨）而不是客户信用划拨，**唯一的结构性理由就是只有它带
`UndrlygAllcn`**；P1-3、P1-4、C2-6、C2-7、C4-1 全部依赖它。

**而规范说：这个元素只在双边约定的前提下才可以出现。**

**这不推翻任何取值，但它补上了一条一直没写出来的前提。** 处理方式：

- **CMOP 明确声明这个双边约定成立**，即两家代理行之间已就在划拨报文里携带底层分配达成一致。
  **它是一条设定，与 §3B.4 的"一个客户对一家机构"同类**。
- **对外说明时必须带上这句。** "资金段能一路对回证券段"这个结论，
  **在没有双边约定的市场里不成立**，因为那里的划拨报文根本不带底层分配。
  **不带这句就是把一个有前提的结论说成普遍结论。**
- **它同时解释了为什么这条链在真实世界里难做。** 正是因为底层分配要双边约定，
  真实对账才大量依赖端到端标识与金额凑数——**这恰好是 BO-1 想展示的困难**，
  见[业务目标](business-objectives.md)。

### 4C.9.2 `FamilyAndSubFamilyRule` 给 C2-17 补了半条规范依据

> If a specific (non-generic) `Family` code is not present, then a specific (non-generic)
> `SubFamily` code is not allowed.（053 C14）

**校验规范的 C2-17 要求银行交易码的域、族、子族构成有效组合，此前整条记为 CMOP。**
本条说明**规范自己也认为这三层不是独立的**：族不具体，子族就不许具体。

**但它只覆盖了 C2-17 的一部分，这个区别要保留：**

- **规范管的是"具体与泛化"的层级关系**，不管具体组合在不在那张约 1569 行的表里。
- **CMOP 管的是组合存在性**，那是查表，规范条文里没有。

**所以 C2-17 拆成两条比合成一条好**，与 V1-023-8 拆分是同一个处理，见 §4C.1。

**同一处还有 `DomainOrProprietaryRule`（053 C11）**：域与专有码至少有一个。
**CMOP 填域不填专有码，合规**；记下来是因为它说明 `BkTxCd` 非空还不够，
**一个内部全空的 `BkTxCd` 在 schema 上合法而在规范上违规**。

### 4C.9.3 `ReferenceGuideline`：P-4 那条硬要求有了规范侧的支持

> At least one reference **should** be present to identify the underlying transaction(s).（053 C26）

§4B.9 把"逐笔回显 `EndToEndId`"定为 P-4 的硬要求，理由是内部的：
不逐笔回显就只能比总额，而"定位到笔"是主 BO 的全部内容。

**本条说明规范也这么想**，只是它用的是 should 不是 must。
**CMOP 的做法因此是"把一条指引提升为硬要求"，而不是"自己发明了一条要求"**——
这两种说法在对外口径里差别很大，**后者听起来像在给数据加戏**。

### 4C.9.4 第三次"二选一"，以及一条读反了会出事的约束

| 约束 | 原文 | 形状 |
|---|---|---|
| `MessageOrStatementPaginationRule`（053 C23） | 消息分页与对账单分页**可以有其一，不可以两者都有** | 二选一，**允许都没有** |
| `PaymentTypeOrLocalInstrumentRule`（053 C25） | 支付类型信息与本地工具**必须有一个缺席，两个都缺席也可以** | 同上 |
| `UnderlyingCustomerAndFinancialInstitutionCreditTransferRule`（`pacs.009` C79） | 底层客户划拨与底层金融机构划拨**必须有一个缺席，两个都缺席也可以** | 同上 |

**这三条的写法都是"must be absent"，很容易读成"必须缺席"。** 原文的完整意思是
**"两者之中必须有一个缺席"，即不得同时出现**，后半句"both may be absent"才是消歧的关键。
**漏读后半句就会把一个可选元素当成禁止元素**，而这类错误在生成器里表现为
"某个字段永远是空的"，**没有任何校验会报警**。

**与 §4C.8.1 的日期异或不同**：日期那条是真异或，**恰好一个**；
本节三条是"至多一个"。**两种形状必须分开写，不能都叫二选一。**

### 4C.9.5 `EventTypeRule` 与 `ReturnReasonRule`：两条兜底码的使用限制

- `EventTypeRule`（053 C12）：`OTHR` 只在没有更合适的公司行为事件码时使用，
  `CHAN` 同理且只用于变更类事件。**CMOP 的公司行为族尚未开始**，登记备用。
- `ReturnReasonRule`（053 C28）：`Rsn/Cd` 取 `NARR` 则必须带自由文本。
  **与 `pacs.002` 的 `StatusReasonRule`（§4C.8.4）一字不差**，
  **处理相同：`NARR` 列入禁用码值**。

**两条合起来是同一条口径：兜底码不是默认值。** 生成器里凡出现"其他"一类码值，
**都要问一句是不是因为没实现具体分类才用它**——规范明说这是最后手段。

### 4B.10 P-3：退汇，已冻结，并且必须在两张"撤销类"报文里选一张

**冻结日期 2026-09-12。** 它与 S-5 冲正配对：**券腿的确认被冲正，已经付出去的钱要回来。**

#### 先决问题：`pacs.004` 退汇，还是 `pacs.007` 冲正

两张报文都做"撤销一笔已发生的支付"，规范给的定义只差一层语气：

| 报文 | 规范定义 | 原因词表 |
|---|---|---|
| `pacs.004` PaymentReturn | "sent by an agent to the previous agent in the payment chain **to undo a payment previously settled**" | `ExternalReturnReason1Code`，**104 个码** |
| `pacs.007` FIToFIPaymentReversal | 发起方自己回撤 | `ExternalReversalReason1Code`，**11 个码** |

**定案取 `pacs.004`，决定性的依据是原因词表而不是报文定义。**
`ExternalReversalReason1Code` 的十一个码逐个点过：`AC03` IBAN 错、`AC04` 账户已销户、
`AG02` 操作码无效、`AM05` 重复、`AM09` 金额错、`MD01` 无授权、`MD05` 不该收、
`MS02`/`MS03` 未说明、`RC07` BIC 错、`TM01` 超过截止时点。
**十一个全部是支付侧自身的操作性差错，没有一个能表达"券腿被冲正了"。**
用 `pacs.007` 就只能填 `MS03`（原因未说明），**等于把本场景唯一有信息量的那一位丢掉**。

`ExternalReturnReason1Code` 里有 `UPAY`——"Payment is not justified"，**这才是本场景的实情**：
付款本身没出错，**是它的依据没有了**。

#### 一个由此暴露的不对称，值得单独记

**券腿的冲正不带任何原因**（§4.6.5：`sese.026` 结构上就没有理由元素），
**款腿的退汇却必须带原因**（`GroupReturnAndReturnReasonRule`，且整组退汇时理由必填）。

**所以 CMOP 必须在款腿上填一个券腿没有给它的原因。** 这不是生成器的自由发挥，
**是两个报文族的设计差异逼出来的**，处理口径定为：

- **只用 `UPAY` 这一个码**，它是"依据不存在"的通用表达，**不声称知道更多**。
- **不填 `AddtlInf`**，与 §4C.8.4 定的禁用自由文本一致。
- **在对外口径里说明这个原因是 CMOP 补的**，不是从券腿继承的。
  **凡是拿这条链讲"能追溯原因"的说法都要在此打住。**

#### 逐步取值

**输入固定为 P-1 的终态加 S-5 的冲正。**

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `pacs.004` | 收方代理行 → 付方代理行（**与 P-1 第 1 步反向**） | `GrpHdr/MsgId` 新派生；`NbOfTxs=1`；**`GrpRtr` 取 `false`**；`SttlmInf/SttlmMtd=CLRG`；组头 `IntrBkSttlmDt` 取退汇日；交易层 `RtrdIntrBkSttlmAmt` 取原金额全额；`OrgnlEndToEndId` 回引 P-1 的同名值；`OrgnlIntrBkSttlmAmt` 与 `OrgnlIntrBkSttlmDt` 回引原值；`RtrRsnInf/Rsn/Cd=UPAY` | 已退汇，P-3 结束 |

**`GrpRtr=false` 是本场景全部结构选择的开关**，规范用四条约束把两条路分得很清：

| `GrpRtr` | `TxInf` | `NbOfTxs` | `CtrlSum` | 理由位置 |
|---|---|---|---|---|
| `true`（整组退汇） | **不允许出现** | 不与条数挂钩 | **不允许出现** | `OrgnlGrpInf/RtrRsnInf`，**必填** |
| `false`（逐笔退汇） | **至少一条** | **必须等于 `TxInf` 条数** | 可填 | 交易层 |

**取 `false` 的理由：** CMOP 的退汇永远是针对某一笔的，
**整组退汇表达的是"这一整批我都不收"**，那是通道级故障，不是本场景。
**代价是 `TxInf` 与 `NbOfTxs` 的一致性检查在这里第四次出现**——
它已经在 P1-1、C1-2、P4-4 各出现一次，**同一类错误换四个字段名**。

#### 三处必须回引原值，且它们全部是可选元素

`pacs.004` 的交易块里**只有 `RtrdIntrBkSttlmAmt` 是 1..1**，
`OrgnlEndToEndId`、`OrgnlTxId`、`OrgnlIntrBkSttlmAmt`、`OrgnlIntrBkSttlmDt`、`RtrId`
**全部是 0..1**。**一条什么都不回引、只说"退你一笔钱"的退汇报文完全合法。**

**这与 `pacs.002` 的情形一模一样**（§2C.4 的 C2-9），
**是本项目第三次遇到"回连锚点在规范上可选"**。处理相同：CMOP 一律回引，登记为 CMOP 决定。

#### P-3 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P3-1 | `RtrdIntrBkSttlmAmt` 等于原 `IntrBkSttlmAmt`，**全额，不部分退** | 全部。部分退汇是另一个场景 |
| P3-2 | `OrgnlEndToEndId` 恰好命中一条已结算的 `pacs.009` 交易行 | 全部 |
| P3-3 | 被退汇的那一笔，其券腿必须存在一条 `sese.026` 冲正 | **仅 DVP**。**这是券款两腿在反向上的对应**，与 P1-5 同源 |
| P3-4 | 退汇报文的借贷方向与原划拨相反 | 全部 |
| P3-5 | `Rsn/Cd` 取 `UPAY`，且 `AddtlInf` 缺席 | 全部。见上文口径 |
| P3-6 | `GrpRtr=false` 且 `NbOfTxs` 等于 `TxInf` 条数 | 全部 |

**P3-3 是本场景真正的跨段判据。** 其余五条在资金段内部就能判，
**只有它要求两段同时看**：**一条没有券腿冲正的退汇，在 DVP 下是凭空少了一笔钱。**

#### P-3 特意不做的两件事

- **不生成整组退汇（`GrpRtr=true`）。** 见上表，它是另一条结构路径，
  **四条约束的取值全部翻转**，写进来等于同时冻结两个场景。**登记为 P-6。**
- **不填 `UndrlygFICdtTrf`。** `pacs.004` 可以带底层金融机构划拨，
  **但 `UnderlyingFinancialInstitutionCreditTransferRule` 要求它只有在原交易里存在时才能出现**，
  而 CMOP 的原 `pacs.009` 带的是 `UndrlygAllcn`，**不是这个元素**。
  **填了就是违规**，这是本轮唯一一条靠读规范才躲开的坑。

### 4B.11 P-6：整组退汇，已冻结，且取整表的做法在这里又抓到两处

**冻结日期 2026-09-12。** 场景是通道级故障：**一整批已结算的划拨被整体退回**，
而不是某一笔出了问题。P-3 冻结时把它推迟，理由是四条约束的取值全部翻转
（§4B.10 末段），**现在把它做完**。

#### 先把 pacs.004 的约束整表取完，八十二条

**按 §4C.6 定下的方法，不按名字搜索。** `pacs.004.001.15` 的 MDR Part 2 §4.3 共列
**82 条约束**（C1 至 C82），其中**挂在报文根上的有 14 条**：
C14、C16、C17、C18、C19、C23、C25、C41、C42、C43、C67、C72、C73、C75。

**只看根上那 14 条会漏掉组头自己的三条**：C8、C71、C15。
**这次取整表抓到两处，都直接落在 P-6 上，且都推翻了此前写下的东西。**

#### 第一处：`GroupReturnAndReturnReasonRule` 的形式化与它的散文不一致

散文（C17）：

> If GroupHeader/GroupReturn is true, then OriginalGroupInformation/ReturnReasonInformation/
> ReturnReason must be present.

**同一条约束的形式化多了一个条件：**

> On Condition
>   /GroupHeader/GroupReturn is present
>   And /GroupHeader/GroupReturn is equal to value 'true'
>   **And /OriginalGroupInformation/ReturnReasonInformation[*]/AdditionalInformation[1] is present**
> Following Must be True
>   /OriginalGroupInformation/ReturnReasonInformation[*]/Reason Must be present

**多出来的那一行改变了结论。** 理由不是"整组退汇就必填"，
**而是"已经填了自由文本，就得同时给出结构化理由"**。
**一条完全不带 `RtrRsnInf` 的整组退汇，schema 合法，约束也合法。**

**§4.6.5 那张三报文对照表里 `pacs.004` 那一行因此是错的，本节更正它。**
原来写的是"必须带，`GroupReturnAndReturnReasonRule` 要求整组退汇时理由必填"，
**那是照散文写的，没有读形式化**。

**这条更正有一个反讽的后果，必须一起记。** §4B.10 已定 CMOP 一律不填 `AddtlInf`
（与 §4C.8.4 的禁用自由文本一致）。**于是 C17 的条件在 CMOP 的数据上永远不成立，
这条约束对 CMOP 从不生效。** 退汇理由完全靠 CMOP 自己的纪律，**规范一点忙都帮不上**。

**方法上的教训与 §4C.6 那次不同，值得分开记。** 上次是"名字搜索证明不了不存在"；
**这次是"散文与形式化是两份材料，散文可以不准"**。
**本项目此后引用 MDR 约束，一律以形式化为准，散文只作导航。**

#### 第二处：`C72` 与 `C73` 是相邻的两条，一条带守卫，一条不带

两条都管组头的 `TtlRtrdIntrBkSttlmAmt`：

| 约束 | 说什么 | 条件里有没有"存在交易行"这一条 |
|---|---|---|
| C72 `TotalReturnedInterbankSettlementAmountAndSumRule` | 组头总额必须等于各交易行 `RtrdIntrBkSttlmAmt` 之和 | **没有** |
| C73 `TotalReturnedInterbankSettlementAmountRule` | 各交易行的币种必须与组头总额币种相同 | **有**：`/TransactionInformation[1] is present` |

**在整组退汇下，C18 禁止出现任何交易行。** 于是 C72 的右侧是一个空和。
**要么组头总额必须等于零，要么这条约束在此处无意义**——两种读法都不可能是本意。
C73 就在它下一条，**同一个元素、同一类判断，却带了守卫**，
**这足以说明 C72 缺守卫是疏漏而不是设计**。

**CMOP 口径：整组退汇一律不填 `TtlRtrdIntrBkSttlmAmt`。**
不填就绕开了这处歧义，**而且这是唯一一个不需要在两种读法里选边的做法**。

**连带后果：C71 说组头总额出现则 `IntrBkSttlmDt` 必填。** 不填总额，
**这条也就不触发**，组头的结算日期回到可选。**CMOP 仍然填它**，理由是 P-1 到 P-4
一路都填，**保持同一族报文的字段出现模式一致比省一个字段重要**。

**于是整组退汇报文里一分钱都没有。** 退了多少，只能从被退的那一批原始报文推回去。
**这是本场景最要紧的一条事实**，下面的不变量围绕它写。

#### 逐步取值

**输入是一批已结算的 `pacs.009`**，即 P-1 那条链的批量版，设批内 M 笔。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `pacs.004` | 收方代理行 → 付方代理行 | `GrpHdr/MsgId` 新派生；**`GrpRtr=true`**；`NbOfTxs=M`（见下）；**`CtrlSum` 不填**（C8 禁止）；**`TtlRtrdIntrBkSttlmAmt` 不填**（见上）；`IntrBkSttlmDt` 取退汇日；`SttlmInf/SttlmMtd=CLRG`；**`TxInf` 一条都不出现**（C18 禁止）；`OrgnlGrpInf/OrgnlMsgId` 回引原批次报文号；`OrgnlMsgNmId` 填 `pacs.009.001.13`；`OrgnlGrpInf/RtrRsnInf/Rsn/Cd=UPAY`；`AddtlInf` 不填 | 整批已退，P-6 结束 |

**`NbOfTxs` 取 M 的依据是 C15，而 C15 是 Guideline 不是 Rule。**
按 §4C.7.2 定下的口径，**Guideline 可以不满足但必须显式记下**——
**这里选择满足它**，因为不满足就等于把唯一能表达"退了多少笔"的字段也放弃了，
而组头总额已经因为 C72 的歧义被放弃了。

**注意 C16 管不到这里。** C16 只在 `GrpRtr` 为 false 时要求 `NbOfTxs` 等于交易行条数。
**整组退汇下 `NbOfTxs` 与报文内容之间没有任何 Rule 级约束**，
它指的是原批次的笔数，**而原批次不在这条报文里**。

#### P-6 打断了链条最细的那个锚点

§4A.6 定下 `EndToEndId` 是资金段回连证券段**唯一的必填锚点**。
**整组退汇是它唯一一次不存在。** `OrgnlEndToEndId` 只活在 `TxInf` 里，
**而 C18 禁止 `TxInf` 出现**。

**于是这条报文只能回连到批次，回连不到笔。**

| | P-3 逐笔退汇 | P-6 整组退汇 |
|---|---|---|
| 回连锚点 | `OrgnlEndToEndId`，**逐笔** | `OrgnlMsgId`，**逐批** |
| 金额 | `RtrdIntrBkSttlmAmt`，逐笔全额 | **报文里没有金额** |
| 券腿对应 | P3-3 可判 | **不可判**，见下 |
| 笔数 | `NbOfTxs` 等于交易行数，Rule 级 | `NbOfTxs` 等于原批笔数，**Guideline 级** |

**P3-3 那条跨段判据在这里失效。** 它要求被退的每一笔都有对应的券腿冲正，
**而 P-6 连"哪几笔"都没说**。判据必须改写成批次级：
**原批次内的每一笔都必须有券腿冲正**，而这要先把原批次展开，
**展开靠的是 `OrgnlMsgId` 这一个字符串**。

**这是六段链条上第一次出现"锚点粒度退化"。** 此前所有跨段判据都是逐笔的，
**P-6 逼出一个逐批的**。它的代价不是判不了，**是判错了之后定位不到笔**——
主 BO 的代表性 BQ 要的正是"定位到具体事件"（见[业务目标](business-objectives.md) §3.2），
**P-6 是这条链上唯一做不到的一环，必须写明。**

#### P-6 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P6-1 | `GrpRtr=true` 时 `TxInf` 一条都不得出现 | 全部。C18，**方向为禁止** |
| P6-2 | `GrpRtr=true` 时 `CtrlSum` 不得出现 | 全部。C8，同为禁止式 |
| P6-3 | `TtlRtrdIntrBkSttlmAmt` 不填 | **CMOP 口径**，绕开 C72 的歧义 |
| P6-4 | `OrgnlMsgId` 恰好命中一批已结算的 `pacs.009` | **CMOP 决定**，规范只要求它存在 |
| P6-5 | 该批内每一笔都必须有券腿冲正 | **仅 DVP**。P3-3 的批次级改写 |
| P6-6 | `NbOfTxs` 等于原批笔数 | **Guideline 级**，CMOP 选择满足 |
| P6-7 | **不得断言**整组退汇能定位到笔 | **规范结构上不支持** |

**P6-7 是清单里第一条否定式的跨段断言。** 与 §3A.10 的 VA-12 同形：
**它要挡的不是坏数据，是一个听上去理所当然的能力声明**。

#### P-6 特意不做的两件事

1. **不做 `GrpRtr` 缺席的退汇。** `GrpRtr` 是 0..1，**缺席时 C8、C16、C17、C18、C19
   五条全部不触发**，于是一条 `NbOfTxs=5` 而一个 `TxInf` 都没有的退汇报文完全合法。
   **这是本项目第三次遇到"约束条件挂在可选元素上，元素一缺席整组约束就失效"**，
   前两次是 §4A.4 的 `pacs.002` 与 §4C.1 的结算状态。**登记为注入，不作为正常路径。**
2. **不做部分整组退汇。** 规范里没有这个概念：要么整组，要么逐笔，**没有中间态**。

### 4B.12 P-5：未入账明细的对账，已冻结，且登记时选错了报文

**冻结日期 2026-09-12。** 场景登记时写的是"用上 `PDNG` 与 `FUTR` 两个入账状态"，
落点默认在 `camt.053`（§4B.9 末段）。**这个落点是错的，而且错在规范正文里写着的一句话上。**

#### `camt.053` 装不了未入账明细，这是 scope 里的一句话

MDR Part 2 §3.1 `camt.053.001.14` 的 Usage 段：

> It contains information on **booked entries only**.

同一份文件 §2.1 `camt.052.001.14` 的 Usage 段：

> It can be used to: - **report pending and booked items**; - provide balance information.
> For a statement, the Bank-to-Customer Account Statement message should be used.

**两句话把分工定死了：未入账明细只能出现在 `camt.052`，`camt.053` 只装已入账。**
§4A.7 记过"三张报表结构几乎相同，差别在基数"，**这次补上一条更要紧的差别：
差别还在 scope，而 scope 不是结构**。

#### 而这条 scope 没有任何约束在守它

`camt.053.001.14` 的 §3.3 约束共 **31 条**（C1 至 C31），**整表取完**，
**没有一条提到 `Sts`**。逐条核对后可以断言：

- **只有 C23 一条带形式化**（`MessageOrStatementPaginationRule`：`MsgPgntn` 与
  `StmtPgntn` 不得同时出现），其余 30 条全是散文。
  **这与 `pacs.004` 的 82 条形成对照**（§4B.11），那里形式化很常见。
- 其中 **C1 至 C7、C16 是数据类型级的通用校验**（币种、BIC、国别、IBAN、小数位），
  与本报文的业务语义无关。
- **C26 `ReferenceGuideline`：At least one reference should be present to identify the
  underlying transaction(s)。** 它是 **Guideline，用 should**，不是 Rule。

**结论：一份把 `Sts/Cd` 填成 `PDNG` 的 `camt.053`，XSD 过、31 条约束全过，
但违反报文自己的 scope。** 这是本项目遇到的**第四类缺口**：
前三类是散文与形式化不一致（§4B.11）、约束挂在可选元素上（§4B.11）、
词表不在 schema 里（§4A.5），**这一类是 scope 禁止而约束不管**。

#### 取整表的第五种翻车方式：搜到的是同名的另一个码

在 MDR 全文里搜 `BOOK`，命中两处，**两处都不是入账状态**：

> BOOK BookTransfer Payment through internal book transfer.

这是 `ClearingChannel2Code` 的成员。**`PDNG`、`FUTR`、`INFO` 在全文里一次都搜不到**——
入账状态词表是 External Code Set，MDR 只写到
`ExternalEntryStatus1Code ... Type: CodeSet minLength 1 maxLength 4`，
值要去 External Code Sets 取（§4A.9 已取得）。schema 侧同样只有
`xs:string` 加 1–4 长度，**没有枚举**。

**方法上记一笔：按名字搜规范，既可能搜不到（因为在别的文件里），
也可能搜到同名的另一个东西。**

#### 重写后的 P-5

**P-5 = 同一笔资金在日内报告里未入账、在日终对账单里已入账，两份报文加内部账三方对账。**
它因此是**跨两张报文的场景**，与 C-3 跨两份契约同形（§3A.14）。

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `pacs.009` | 付方代理行 → 收方代理行 | 与 P-1 第 1 步相同 | 已发起 |
| 2 | `camt.052` | 账务服务方 → 账户持有方 | `Rpt/Ntry/Sts/Cd=`**`PDNG`**；`BookgDt` 填**预计**入账日；`ValDt` 填**预计**起息日；`TxDtls/Refs/EndToEndId` 回显 | 日内报告已发出，该笔未入账 |
| 3 | `pacs.002` | 收方代理行 → 付方代理行 | ~~`TxSts=ACSC`~~ **`TxSts=ACCC`** | 已结算。**已于同日改，见 §4B.15.3** |
| 4 | `camt.053` | 账务服务方 → 账户持有方 | 同一 `EndToEndId` 出现在一条 `Sts/Cd=`**`BOOK`** 的 `Ntry` 上；`BookgDt` 填**实际**入账日 | 已入账，P-5 结束 |

**第 2 步的 `BookgDt` 与第 4 步的 `BookgDt` 语义不同，这是本场景的全部难点。**
MDR §3.4.2.15.6 的 Usage：

> Booking date is the **expected** booking date, unless the status is booked,
> in which case it is the **actual** booking date.

**同一个元素，状态一变含义就变。** `ValDt` 同理（§3.4.2.15.7）：

> If entry status is pending and value date is present, then the value date refers to an
> **expected/requested** value date.

**因此"第 2 步与第 4 步的 `BookgDt` 应当相等"是一条假不变量，不能写进判据。**
两者之差是**预测误差**，是产出，不是错误。

#### 锚点在这里比 P-6 更脆，脆在它每一层都可选

回连资金段要走 `Ntry/NtryDtls/TxDtls/Refs/EndToEndId`。**这条路径上四层全是可选：**

| 层 | 元素 | 基数 |
|---|---|---|
| 1 | `Ntry` | 0..* |
| 2 | `Ntry/NtryDtls` | 0..* |
| 3 | `NtryDtls/TxDtls` | 0..* |
| 4 | `TxDtls/Refs` | 0..1 |
| 5 | `Refs/EndToEndId` | 0..1，**且 `Refs` 下 16 个引用载体全部可选** |

**`EntryTransaction16` 的 29 个元素没有一个必填。**
这是本项目**第二次**遇到整块零必填，第一次是 `pacs.002` 的交易块（§4A.4）。

**规范唯一的推力是 C26，而 C26 是 Guideline。**
**所以 P-5 的锚点完全由 CMOP 约定支撑，规范一点都不保证。**
与 P-6 的对照值得写下来：

| | P-6 整组退汇 | P-5 未入账对账 |
|---|---|---|
| 锚点为什么弱 | **规范结构上不允许**逐笔（C18 禁止 `TxInf`） | 规范**允许**逐笔，但**一层都不要求** |
| CMOP 能不能补救 | **不能** | **能，靠生成约定** |
| 判据怎么写 | 降级到批次级 | **先断言锚点存在，再断言锚点命中** |

**"先断言锚点存在"是新增的一种判据形态。** 此前三种是等式、引用链可达性、
状态停留时长（§3A.14）。**这一种是"结构存在性"**：它要挡的是生成器悄悄少填一层，
**而少填一层在规范眼里完全合法**。

#### 一条散文禁令，同样没有约束在守

MDR §3.4.2.15.7 `ValDt` 的 Usage 还有一句：

> For entries subject to availability/float and for which availability information is
> provided, the **value date must not be used**.

**用词是 must not，但 31 条约束里没有对应条目。** CMOP 的取用：
**`Avlbty` 与 `ValDt` 一律不同时出现**，并把"同时出现"注入为负例。
**注意它的期望结果是沉默**——XSD 与约束都不会报错，只有 CMOP 自己的判据会。

#### 冲正明细的方向是反的，写在这里备用

MDR §3.4.2.15.4 `RvslInd` 的 Usage：

> If the CreditDebitIndicator is CRDT and ReversalIndicator is Yes, the original operation
> was a debit entry.

**即 `CdtDbtInd` 描述的是冲正这一条明细自己的方向，不是被冲正的那一条。**
于是**按 `CdtDbtInd` 有符号求和是对的**（P4-1 因此成立），
**而按条数统计"当日几笔支付"会把一笔算成两条**。S-7 会用到这一条。

#### 余额侧：`camt.053` 必须带余额，`camt.052` 不必

整表核对三张报表的余额基数：

| 报文 | `Bal` | `TxsSummry` | `Ntry` |
|---|---|---|---|
| `camt.052` | **0..\*** | 0..1 | 0..* |
| `camt.053` | **1..\*** | 0..1 | 0..* |
| `camt.054` | **不存在** | 0..1 | 0..* |

**因此 P-5 的余额判据只能挂在第 4 步的 `camt.053` 上**，第 2 步的 `camt.052`
可以一条余额都不给。**CMOP 仍然给**：日内报告带 `ITBD` 与 `XPCD` 各一条。
**两条的差就是当日未入账金额**，见 §4B.15.5。
~~只带 `ITBD`，用来支撑"未入账金额 = 已入账余额与内部账之差"。~~
**已于同日改**：只带 `ITBD` 时那条判据必须依赖内部账，**只有两方**。

#### P-5 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P5-1 | 第 2 步每条 `Sts/Cd=PDNG` 的明细，其 `EndToEndId` 必须在第 4 步以 `Sts/Cd=BOOK` 出现 | 全部。**这是本场景的主判据** |
| P5-2 | 第 4 步的 `camt.053` 里**不得**出现 `Sts/Cd` 非 `BOOK` 的明细 | 全部。**依据是 scope，不是约束** |
| P5-3 | 从 `Ntry` 到 `EndToEndId` 的五层路径每一层都必须存在 | 全部。**结构存在性判据**，规范不要求 |
| P5-4 | 第 2 步的 `BookgDt` 与第 4 步的 `BookgDt` **允许不等**，差值记为预测误差 | 全部。**这是一条禁止断言，不是断言** |
| P5-5 | `Avlbty` 与 `ValDt` 不同时出现 | 全部。**CMOP 决定**，散文禁令无约束支撑 |
| P5-6 | 内部账当日未入账金额 = 第 2 步 `PDNG` 明细有符号金额之和 | 全部。**这是三方对账的第三方** |
| P5-7 | 第 4 步 `CLBD` 减 `OPBD` 等于当日全部 `Ntry` 有符号金额之和 | 全部。**与 P4-1 同式**，在此复用 |

**P5-2 与 P5-4 都是否定式。** 全部否定式已归入
[校验规范](validation-and-reconciliation-specification.md) §1A.3，此处不再计数。
**它们共同的特点是：要挡的不是坏数据，是一个看上去合理的写法。**

**P5-2 的依据已于同日升级，见 §4B.14.3。** 它原先只有 scope 散文，
**现在外部词表里的码值定义把它补上了一半**。

#### P-5 特意不做的三件事

1. ~~**不做未入账后来被拒的分支。**~~ **已于同日冻结，见 §4B.13。**
   推迟的理由（需要 `pacs.002` 的 `RJCT` 与 `camt.052` 联动）在 P-5 冻结的同时就已具备。
2. ~~**不做 `FUTR`。**~~ **已于同日冻结，见 §4B.14。**
   登记时把 `PDNG` 与 `FUTR` 并列，**这个并列本身是错的**，见 §4B.14.2。
3. **不做 `camt.054`。** 它没有余额（见上表），**P5-6 与 P5-7 都挂不上去**。

### 4B.13 P-5a：日内报告说未入账，日终对账单里根本没有，已冻结

**冻结日期 2026-09-12。** P-5 冻结时把它推迟（§4B.12 末段），
理由是"需要日内报告由 `pacs.002` 驱动"。**该依赖在 P-5 冻结的同时已经具备**，
本节把它做完。

#### 这个场景的判据是一条"缺席"，而缺席是最难判的一类

P-5 的主判据 C4-17 是：**每条 `PDNG` 明细都要在当日对账单里以 `BOOK` 出现**。
**P-5a 是它的合法反例**：这一笔就是不会出现，**因为它被拒了**。

**于是 C4-17 必须带条件，而条件在另一张报文上。**
**这是本项目第一次出现"判据的适用条件由第三张报文决定"**：
此前的条件都取自被判报文自身的字段（如 `PrtlSttlmInd`、`GrpRtr`）。

| 判据形态 | 条件来自 | 实例 |
|---|---|---|
| 无条件 | — | P4-1 |
| 条件在本报文 | 自身字段 | V2-3（`PrtlSttlmInd`） |
| 条件在同链另一报文 | 同 `TxId`／同 `EndToEndId` | C4-5 |
| **条件在第三张报文，且该报文可以不存在** | `pacs.002` 的 `TxSts` | **C4-17，P-5a 逼出来的** |

**最后一行的"可以不存在"是要害。** 规范不要求发状态回报（契约 §4C.4），
**所以"没有 `RJCT`"既可能是没被拒，也可能是被拒了但没回报**。
**判据必须把这两种情形分开**，否则生成器少发一条 `pacs.002` 就能让任意一笔凭空消失。

#### 逐步取值

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `pacs.009` | 付方代理行 → 收方代理行 | 与 P-1 第 1 步相同 | 已发起 |
| 2 | `camt.052` | 账务服务方 → 账户持有方 | `Ntry/Sts/Cd=`**`PDNG`**；`TxDtls/Refs/EndToEndId` 回显；`BookgDt` 填预计入账日 | 日内报告已发出，该笔未入账 |
| 3 | `pacs.002` | 收方代理行 → 付方代理行 | **`TxSts=RJCT`**；`OrgnlEndToEndId` 回引第 1 步；`StsRsnInf/Rsn/Cd` 取一个已注册的外部原因码 | 已拒绝 |
| 4 | `camt.053` | 账务服务方 → 账户持有方 | **该 `EndToEndId` 不出现**；其余明细照常 | 日终对账单已发出，P-5a 结束 |

**三处取值决定：**

- **第 4 步不发冲正明细。** 一条从未入账的明细**没有什么可冲正的**：
  `RvslInd` 描述的是"本条明细是一次冲正的结果"（§4B.12），
  **而冲正的前提是原来那一笔已经入账**。**未入账的笔直接消失是正确表示。**
- **不发第二份 `camt.052`。** 真实运营里当日会发多份日内报告，
  **后一份里该笔已经不在**。CMOP 只发一份，**理由是"消失"这件事在第 4 步已经能判**，
  再加一份只增加数据量不增加判据。**登记为 P-5a′，与 `RptgPrd/Tp=CHNG` 一起做。**
- **原因码取一个已注册的外部码，不取 `NARR`。** 与 §2C.9 记的
  `Rsn/Cd=NARR` 要求自由文本同理：**CMOP 不生成自由文本**。

#### P-5a 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P5a-1 | 日内报告里的 `PDNG` 明细未在对账单出现时，**必须**存在一条同 `EndToEndId` 的 `pacs.002` 且 `TxSts=RJCT` | 全部。**这是 C4-17 的适用条件本身** |
| P5a-2 | 被拒的那一笔**不得**出现在对账单上，无论什么状态 | 全部。**否定式** |
| P5a-3 | 被拒的那一笔**不得**产生冲正明细 | 全部。**否定式**。**依据已于同日从 CMOP 升级为规范**，见 §4B.14.3 |
| P5a-4 | `RJCT` 的时点必须晚于第 2 步日内报告的 `CreDtTm` | 全部。**先报未入账、后被拒，次序反了就是另一个场景** |
| P5a-5 | 对账单的 `CLBD` 减 `OPBD` 不包含被拒那一笔 | 全部。**P4-1 在 P-5a 下自动成立**，写出来是为了挡"把被拒的笔补进余额"这种修补 |
| P5a-6 | 三方对账里，内部账当日未入账金额**必须**扣除被拒的那一笔 | 全部。**这是 P5-6 在 P-5a 下的修正**，不修正就会长期挂账 |

**P5a-6 是本场景对主业务目标的贡献。**
[业务目标](business-objectives.md) §3.1 的 T+1 早晨异常处理流里，
**"日内说在途、日终没到账"正是操作员要处理的那一类异常**。
**规范给了它一个带代码的答案**：去看 `pacs.002` 的 `RJCT` 与原因码。
**答不上来就只能人工追**，而那正是主 BO 要消除的动作。

#### P-5a 与 S-4 是同一种判据，登记为一对

| | S-4 撤销被拒办 | P-5a 支付被拒 |
|---|---|---|
| 问的问题 | 能不能撤 | 为什么没到账 |
| 规范的答案 | `DeniedReason6Code` 的 `DSET` | `ExternalStatusReason1Code` 的一个成员 |
| 判据形态 | **原指令不得有新状态回报**（否定式） | **该笔不得出现在对账单**（否定式） |

**两者都是"什么都没发生"型的判据**，而这类判据在没有配对注入时**看起来永远是通过的**。
**因此两者的注入都必须成对**：一条制造违规，一条制造合法的沉默。

### 4B.14 P-5b：`FUTR` 与起息日晚于入账日，已冻结，并改正三处

**这一节的材料不在报文规范里，在外部词表里。**
`camt.053.001.14` 的 XSD 把 `Sts/Cd` 的类型写成 `ExternalEntryStatus1Code`，
**而那个类型在报文 XSD 里是这样定义的**：

```xml
<xs:simpleType name="ExternalEntryStatus1Code">
    <xs:restriction base="xs:string">
        <xs:minLength value="1"/>
        <xs:maxLength value="4"/>
    </xs:restriction>
</xs:simpleType>
```

**没有枚举。任何一到四个字符都合法。**

#### 4B.14.1 这不是个例：`camt.053` 的 32 个外部码集，32 个都没有枚举

逐个数过：`camt.053.001.14` 的 XSD 里共有 **32 个 `External*Code` 简单类型**，
**其中带 `xs:enumeration` 的有 0 个**。清单包括
`ExternalEntryStatus1Code`、`ExternalBankTransactionDomain1Code` 及其族与子族、
`ExternalBalanceType1Code`、`ExternalPurpose1Code`、`ExternalReturnReason1Code`
这些本项目已经在用的。

**这条把 §2C.7 从"一条正交维度"抬成"这张报文外部词表面的全部"。**
说"这份 `camt.053` 通过了 schema 校验"时，**32 个码集一个都没被校验过**。
XSD 只保证了长度，**而全部相关码值恰好都是四个字符**，
所以长度检查在这里等于什么都没做。

**同时再次证实 §2C.7 的第四句（分发格式）。** 外部词表的 XSD 分发里
**没有 `Status` 元素**，`Registered` 与 `Obsolete` 的区分只存在于 XLSX 分发。
**只拿 XSD 做词表校验，33 条已废止码值会全部放行。**

#### 4B.14.2 四个入账状态的定义，逐字取自外部词表

| 码 | 名称 | 定义（规范原文摘要译） | 是否在账上 |
|---|---|---|---|
| `BOOK` | Booked | 资金在账户服务方与账户持有人之间的划转**已完成** | 是 |
| `FUTR` | Future | **分录已在账户服务方账上**，价值将在**未来某个日期与时点**加于账户持有人 | **是** |
| `PDNG` | Pending | 账户服务方账簿上的入账**尚未完成** | **否** |
| `INFO` | Information | 分录**仅供参考**，账户服务方账簿上未做任何入账 | 否 |

**`PDNG` 与 `FUTR` 并列是错的，两者不在一个维度上。**
`PDNG` 说的是"还没上账"，`FUTR` 说的是"已经上账，只是价值日在将来"。
**四个值真正的划分是"在不在账上"：`BOOK` 与 `FUTR` 在，`PDNG` 与 `INFO` 不在。**

**由此得到 P-5b 的核心问题。** `camt.053` 的 scope 原话是
"It contains information on booked entries only"，
**而 `FUTR` 的定义第一句就是"Entry is on the books"**。
**`FUTR` 到底算不算 booked，规范两处措辞打架，没有任何一条约束裁决。**

**本项目的口径：`FUTR` 可以出现在 `camt.053`。**
理由是词表定义比 scope 散文更具体，**且这是唯一能让"今天记账、后天起息"这件事
在日终对账单上表达出来的方式**。**这个选择必须写进对外口径**，
因为它不是从规范判出来的，**是在规范的两句话之间选了一句**。

#### 4B.14.3 三处依据升级：两条原记为 CMOP 的判据其实有规范支撑

**这是本节最有价值的部分，且全部来自同一个词表文件。**

**一、`PDNG` 的定义里有一条条件性义务，正是 C4-17。** 原文：

> If booking takes place, the entry will be included with status Booked in
> subsequent account report or statement.

**"If booking takes place" 就是本项目独立推出来的那个适用条件。**
§4B.13 里 C4-17 的条件是从 `pacs.002` 的 `RJCT` 反推的，
**而规范早就把这个条件写在码值定义里了，只是写在报文规范之外的文件里。**
**C4-17 与 P5-1 由 CMOP 升级为规范。**

**二、`PDNG` 的定义最后一句：`Status Pending cannot be reversed.`**
**三、`BOOK` 的定义最后一句：`Status Booked is the only status that can be reversed.`**

**两句独立地支撑同一条判据。** P5a-3 与 C4-28（"被拒的那一笔不得产生冲正明细"）
**原先记为 CMOP，现在记为规范。** 更强的是第三句：
**冲正只能针对 `BOOK`**，所以对 `FUTR` 与 `INFO` 的冲正同样违规，
**而这两种情形此前根本没被想到。**

**这三处升级的共同教训要单独记住：**

> **一条判据被记为"本项目自己的口径"，可能只是因为依据不在读过的那份文件里。**
> **外部词表的码值定义带业务规则，而它既不在报文 XSD 里，也不在 MDR 里。**

**因此定一条方法规矩：凡把某条判据标为 CMOP 之前，
必须先查一遍相关码值在外部词表里的定义文字。**
**此前所有标为 CMOP 的判据都要按这条重查一遍**，登记为未结事项。

#### 4B.14.4 P-5b 的六步与两个日期

| 步 | 报文 | 内容 |
|---|---|---|
| 1 | `pacs.008` | D 日发起，约定起息日为 D+2 |
| 2 | `camt.053`（D 日） | 一条 `Sts/Cd=FUTR` 明细，`BookgDt=D`，`ValDt=D+2` |
| 3 | `camt.053`（D+1 日） | 同一 `EndToEndId` 仍为 `FUTR`，两个日期不变 |
| 4 | `camt.053`（D+2 日） | 同一 `EndToEndId` 转为 `BOOK`，`BookgDt=D`，`ValDt=D+2` |
| 5 | 余额 | D 与 D+1 的 `CLBD` **不含**这一笔，D+2 的含 |
| 6 | 内部账 | D 与 D+1 计入"未起息"科目，D+2 转出 |

**第 4 步的 `BookgDt` 与第 2 步相等，这一点与 P-5 相反。**
P-5 里 `BookgDt` 会变，因为在 `PDNG` 下它是预期入账日，在 `BOOK` 下是实际入账日
（§4B.12）。**而 `FUTR` 本来就已经入账**，所以入账日在第 2 步就是实际值。
**同一个元素、同一条链，在两个场景里一个允许变、一个禁止变。**
**这是本项目第一次遇到"同一条不变量在两个场景下方向相反"。**

**第 5 步是余额判据的关键。** `FUTR` 在账上但价值未加于账户持有人，
**所以它不进当日的 `CLBD`**。P5-7（`CLBD` 减 `OPBD` 等于当日全部 `Ntry` 之和）
**在 P-5b 下会失败**，必须改成只对 `Sts/Cd=BOOK` 的分录求和。
**这是 P5-7 第一次需要限定条件**，而 P-5 与 P-6 下它是无条件的。

#### 4B.14.5 P-5b 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P5b-1 | `FUTR` 明细的 `ValDt` 必须晚于其 `BookgDt` | 全部。**否则它不该是 `FUTR`** |
| P5b-2 | `FUTR` 明细的 `BookgDt` 在转为 `BOOK` 后**不得**改变 | 全部。**与 P5-4 方向相反**，见 §4B.14.4 |
| P5b-3 | 同一 `EndToEndId` 在 `ValDt` 当日必须以 `BOOK` 出现 | 全部。**主判据**，形状同 P5-1 |
| P5b-4 | `CLBD` 减 `OPBD` 只对 `Sts/Cd=BOOK` 的分录求和 | **P-5b 及此后所有含 `FUTR` 的日** |
| P5b-5 | `FUTR` 明细**不得**带 `RvslInd=true` | 全部。**否定式**。**依据是规范**：只有 `BOOK` 可冲正 |
| P5b-6 | 一笔在 `ValDt` 之前**不得**从 `FUTR` 直接转 `PDNG` | 全部。**否定式**。**CMOP**：那是账上退回账下，词表没说不行 |
| P5b-7 | 内部账"未起息"科目余额 = 全部 `FUTR` 明细有符号金额之和 | 全部。**三方对账的第三方**，形状同 P5-6 |

**P5b-5 与 P5b-6 是两条新的否定式**，前者有规范支撑，后者纯属 CMOP。
**两者并列写出来正是 §1A.3 那张分类表要的东西**：
同一节里两条形状一样的否定式，**对外能说的话完全不同**。

#### 4B.14.6 P-5b 特意不做的两件事

1. **不做 `INFO`。** 它不在账上也不待入账，**三方对账的任何一方都挂不上它**。
   它的用途是提示，**而提示类分录在本项目里没有下游**。
2. **不做起息日早于入账日。** 那是回溯起息，**在加拿大 T+1 下需要一整套
   补息计算才有意义**，而补息不在本阶段范围内。

### 4B.15 按新规矩把用到的码值定义扫了一遍，命中五处

**这一节是 §4B.14.3 那条规矩的第一次执行。** 做法：
把三份需求文档里出现过的全部四字母码值取出来（**103 个**），
在外部词表 `2Q2026_externalcodesets_v3` 的 XSD 分发里逐个查定义文字，
**筛出定义里含 cannot／must／only／always／never 一类措辞的**。

**命中 7 条，其中 5 条要改动既有内容，2 条只是措辞。**
**命中率不高，但改动率高**：命中的 7 条里有 5 条推翻或加强了既有条目。
**这说明这条规矩值得对全部标 CMOP 的判据跑一遍，而不是只在遇到问题时查。**

#### 4B.15.1 `CLBD` 的定义写着 P4-1，而且比 P4-1 更严

> Balance of the account at the end of the pre-agreed account reporting period.
> It is the sum of the opening booked balance at the beginning of the period and
> **all entries booked** to the account during the pre-agreed account reporting period.

**P4-1 由 CMOP 升级为规范。** 更要紧的是最后四个字：
**"all entries booked"，不是 all entries。**

**所以 §4B.14.4 里那条限定（只对 `BOOK` 求和）不是给 P4-1 打的补丁，
是 P4-1 一开始就该有的写法。** P4-1 原来的无条件版本**在读到 `FUTR` 之前就是错的**，
只是当时数据里没有非 `BOOK` 的分录，**错误因此不可见**。

**这件事的教训与否定式那条同构：** 一条判据长期通过，
**可能是因为能证伪它的数据从没被生成过**。

#### 4B.15.2 `OPBD` 与 `PRCD` 各自写了一条跨日不变量，本项目一条都没有

> `OPBD`：Book balance of the account at the beginning of the account reporting period.
> **It always equals the closing book balance from the previous report.**

> `PRCD`：Balance of the account at the previously closed account reporting period.
> **The opening booked balance for the new period has to be equal to this balance.**

**两条独立地说同一件事：今日期初已入账余额 = 昨日期末已入账余额。**

**本项目至今没有任何一条跨日判据。** §4B.12 到 §4B.14 的余额判据全部在单日之内，
**而这条是资金段第一条跨报告期的等式**，登记为 P4-2。

**它的价值不在于难**，等式本身很简单，**在于它是唯一一条能发现"整整一天的对账单丢了"
的判据**。单日自洽的判据对一份缺失的对账单一律沉默：**没有那份报文，就没有人去判它。**
**跨日等式把缺失变成不等式**，因为下一天的期初对不上上上天的期末。

**`PRCD` 是可选的第三条腿。** 它允许在同一份报文里带上"上期期末"，
**于是缺一天时，第三天的报文自己就能指出中间断了一天**，不必依赖历史库。
**CMOP 决定生成 `PRCD`**，理由就是这一条。

#### 4B.15.3 `ACSC` 的定义带两条限制，而本项目在 P-5 里正好踩了一条

`ExternalPaymentTransactionStatus1Code` 的 `ACSC`：

> Settlement completed. Usage: this can be used by a Market Infrastructure reporting to
> Infrastructure Participant or an Account Servicer to Account Owner to report that the
> transaction account entry has been completed.
> **Warning: this status is provided for transaction status reasons, not for financial
> information. It can only be used after bilateral agreement.**

**两条限制：不得当作财务信息；只能在双边协议之后使用。**

**§4B.12 的 P-5 第 3 步用的正是 `ACSC`，并在"之后状态"一栏写"已结算"。**
**"已结算"就是财务信息**，这正是 warning 挡的那个用法。
**改为 `ACCC`**，与 P-1 第 3 步一致（§4B.3）。

**P-1 当初避开 `ACSC` 用的是另一个理由**（借方侧对贷方侧，§4B.3），
**理由不同而结论相同**。**两个理由都要留着**：
一个说它证明不了钱到了对方，一个说它根本不该被当作证明。

**"只能在双边协议之后使用"这一句本项目无法判定。** 双边协议不在数据里。
**处理办法与 `SCEX` 的 should 级选码指引相同：不生成，于是不需要判。**

#### 4B.15.4 同一个 `ACSC`，在两个码集里定义不同，而本项目抄错了那一份

| 码集 | `ACSC` 的定义 |
|---|---|
| `ExternalPaymentGroupStatus1Code` | **Settlement on the debtor's account** has been completed |
| `ExternalPaymentTransactionStatus1Code` | **Settlement completed**（无账户侧限定，另加双边协议限制） |

**§4B.3 写"`ACSC` 是借方账户结算完成"，取的是组级那一份定义，
而它注解的是笔级字段。** 结论（改用 `ACCC`）碰巧不受影响，**依据是错的**。

**这是 §2C.7 第五句最强的一个例子**：此前三处同字母不同物
（`BOOK`、`UPAY`、`DSET`）都跨族或跨领域，**这一处在同一个报文族内、
同一个业务概念上、只差码集名一个词**。
**"写码集名"这条规矩到这里才真正证明了自己的必要性。**

#### 4B.15.5 `ITBD` 与 `XPCD`：P-5 的三方对账可以少依赖一方

| 码 | 定义要点 |
|---|---|
| `ITBD` | 日内计算的余额，**基于当期已入账（booked）的借贷项** |
| `XPCD` | **由已入账分录与计算时点已知的待处理项组成**，用以预测日终余额 |

**`ITBD` 只含已入账，`XPCD` 含已入账加待处理。**
**于是 `XPCD` 减 `ITBD` 就是当日未入账金额**，两个数在同一份 `camt.052` 里。

**P-5 原来的写法（§4B.12）是"未入账金额 = 内部账 - 已入账余额"**，
**它必须依赖内部账才能算出未入账那一侧。**
**改为同时生成 `XPCD`**，于是同一件事有两条独立算路：
一条只用报文，一条用报文加内部账。**两条都算、结果必须相等**，
**这才是真正的三方对账**；原来的写法只有两方。

**`ITBD` 保留。** 它是 `XPCD` 的被减数，**去掉它 `XPCD` 就无法拆开。**

#### 4B.15.6 两处只改措辞的

- `ExternalCorporateActionEventType1Code` 的 `OTHR`：
  "use **only** when no other event type applies"。**should 级，与 `SCEX` 同类。**
  处理办法相同：**不生成 `OTHR`**，于是不需要判。
- `ExternalEntryStatus1Code` 的 `INFO`：定义已在 §4B.14.2 记过，**此处不重复**。

#### 4B.15.6a 同一规矩对证券与公司行为族内联码集跑了一遍：没有新规则

证券结算与公司行为两族的码集**不在外部词表里**，定义写在各自 MDR Part 2 正文中。
把需求文档里用到的这两族码值（**47 个**）逐个在两份 MDR 里定位，**找到 45 个**，
`MODF` 与 `XTND` 两个在正文里没有"码加名称"的定义行，未能核对。

**定义里带规则措辞的只有两条**：

- `SCEX`：已在 §4D.11.1 记过，should 级选码指引。
- `REFU`：公司行为族里的 Refunded，"Applicable only in the frame of a partial defeasance
  PDEF corporate action event"。**它是证券标识类码，与 §4.6 挂起原因里的 `REFU` 不是同一个码**。
  **又一处同字母不同物**，但本项目不生成部分废止事件，**不改动任何判据**。

**这个否定结果本身要记住：** 外部词表的码值定义带业务规则（资金段命中 7 条，改动 5 处），
**而内联码集的定义基本只是名称的展开**。**所以这条规矩的收益集中在资金段**，
证券段此后只在新引入码值时查，不必再整表重跑。

#### 4B.15.7 P-4 补一条不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| P4-2 | 今日 `camt.053` 的 `OPBD` = 昨一营业日 `camt.053` 的 `CLBD` | **凡存在前一营业日对账单**。**规范**：`OPBD` 与 `PRCD` 的定义各说一遍 |
| P4-3 | 若报文带 `PRCD`，其值必须等于 `OPBD` | 仅当 `PRCD` 出现。**规范**：`PRCD` 的定义原话 |
| P4-4 | 一段连续营业日的 `camt.053` 不得缺日 | **CMOP**。**P4-2 只能发现缺日的后果，发现不了缺日本身** |

**P4-4 与 P4-2 的分工要写清楚。** 缺了一天时，P4-2 在下一天报不等式，
**但它报的是"余额对不上"，不是"少了一份报文"**。
**只有 P4-4 能说出后一句**，而它靠的是营业日历，不是报文。
**两条都要，理由与 §2C.6 里 C4-26 和 C3-3 并存的理由相同。**

## 4C.10 第十批：资金管理族四张报文的约束整表横向比对，并展开 `camt.060` 请求侧

**冻结日期 2026-09-12。** 上一节冻结 P-5 时只取了 `camt.053` 一张的约束整表。
**本节把同一消息集另外三张也取完，横向比对。** 这是"取全清单"方法第一次用于
**同族多张报文之间**，此前都是单张报文内部。

### 4C.10.1 四张的约束条数与差异

| 报文 | 约束条数 | 带形式化的条数 |
|---|---|---|
| `camt.052` 日内报告 | **31** | 1（C23） |
| `camt.053` 日终对账单 | **31** | 1（C23） |
| `camt.054` 借贷记通知 | **30** | 1（C22） |
| `camt.060` 报告请求 | **9** | 0 |

**`camt.052` 与 `camt.053` 的三十一条名字逐条相同，只有一条例外：**

| 编号 | `camt.052` | `camt.053` |
|---|---|---|
| C23 | `MessageOrReportPaginationRule` | `MessageOrStatementPaginationRule` |

**同一条规则，因为它约束的元素在两张报文里叫不同名字，规则也就跟着改名。**
`camt.054` 里它叫 `MessageOrNotificationPaginationRule`，编号还从 C23 挪到 C22。
**这正是"取全清单"方法当初立起来的理由**（§4.6.3）：**按名字搜索无法证明不存在**，
因为名字本身是跟着元素走的。**本节是这条方法第一次在同族报文之间得到验证。**

**`camt.054` 少的那一条是 C15 `ForwardBalanceAndAvailabilityRule`。**
原因是它根本没有余额块。**这条差异从约束清单和从结构表两条独立路径得到同一结论**，
可以互为佐证：

| 报文 | `Bal` | `TxsSummry` | `Ntry` |
|---|---|---|---|
| `camt.052` | 0..* | 0..1 | 0..* |
| `camt.053` | **1..*** | 0..1 | 0..* |
| `camt.054` | **不存在** | 0..1 | 0..* |

**四张里没有任何一条约束提到入账状态。** §4B.12 已就 `camt.053` 记过这一点，
**现在可以把结论放大到整族：`camt.052` 只装未入账与已入账、`camt.053` 只装已入账
这个分工，在整个消息集里没有一条约束在守。**

### 4C.10.2 `camt.060` 展开：九条约束全是通用校验，一条业务规则都没有

九条依次是 `ActiveOrHistoricCurrency`、`AnyBIC`、`BICFI`、`Country`、
`CurrencyAmount`、`IBAN`、`IdentificationAndProxyGuideline`、
`IdentificationOrProxyPresenceRule`、`SupplementaryDataRule`。
**前六条是数据类型级，后三条挂在账户与补充数据上。**
**请求本身的语义一条都没有约束。**

结构上要紧的四处：

| 元素 | 基数 | 为什么要紧 |
|---|---|---|
| `RptgReq/ReqdMsgNmId` | **1..1，`Max35Text`** | **要请求哪张报文是自由文本，不是码表。** 填一个不存在的报文名，XSD 过、九条约束全过 |
| `RptgReq/Acct` | **0..1** | **可以不说要哪个账户。** `AcctOwnr` 才是 1..1 |
| `RptgPrd/FrToDt/ToDt` | **0..1** | **区间可以不封口**，起始日必填而结束日不必 |
| `RptgPrd/Tp` | 1..1，`QueryType3Code` | 三个值：`ALLL` 全量、`CHNG` 自上次同类请求以来新增、`MODF` 自上次请求以来变更 |

### 4C.10.3 想按状态过滤，就必须同时指定方向，而且一次只能要一种状态

`ReqdTxTp` 是 **0..1**，但它一旦出现：

| 元素 | 基数 |
|---|---|
| `ReqdTxTp/Sts` | **1..1**，且是 `EntryStatus1Choice`，**不可重复** |
| `ReqdTxTp/CdtDbtInd` | **1..1** |

**于是三件事同时成立：**

1. **要不带过滤，拿全量；要带过滤，就得同时钉死状态和方向。** 中间态不存在。
2. **一次请求只能要一种状态。** `Sts` 不可重复，"把未入账和已入账一起给我"要发两条。
3. **一次请求只能要一个方向。** 借贷两侧要发两条。

**要"未入账加已入账、借加贷"，需要四条请求，或者干脆不带 `ReqdTxTp`。**

**这是"约束挂在可选元素上"这一模式的第四次出现，但方向相反。**
前三次（`pacs.002` 交易块、结算状态轴、`pacs.004` 的 `GrpRtr`）都是
**元素一缺席，一整组约束跟着失效**；**这一次是元素一出现，两个子元素立刻变成必填**。
**记为同一模式的反面：可选块不是"可填可不填"，是"要么整块不填，要么整块填够"。**

### 4C.10.4 请求与回执的配对锚点在回执侧是可选的

`camt.052`、`camt.053`、`camt.054` 的组头都带
`OrgnlBizQry` **0..1**，其内 `MsgId` 1..1、`MsgNmId` 0..1、`CreDtTm` 0..1。

**即：一张报告可以完全不说自己在答复哪一条请求。**
**这与 §4B.12 记下的明细锚点是同一形状**——规范允许逐条回引，但一层都不要求。

**CMOP 的取用：凡由 `camt.060` 触发的报告，`OrgnlBizQry/MsgId` 必填。**
不填的情形另作注入，**其期望结果是只有 CMOP 自己的判据报错**。

### 4C.10.5 本批带出的新场景与新断言

**登记 P-7：报告请求与回执的配对。** 账户持有方先发 `camt.060` 要当日未入账明细，
账务服务方回 `camt.052`。**它是六段链条上第一条由持有方主动发起的报文**，
此前全部是服务方单向推送。**暂不冻结**，理由是它需要先有 P-5 的日内报告生成器。

新增断言，落在[验证与对账规范](validation-and-reconciliation-specification.md) §2C.6：

| 编号 | 检查 |
|---|---|
| C4-23 | 每张由请求触发的报告，`OrgnlBizQry/MsgId` 命中一条 `camt.060` 的 `GrpHdr/MsgId` |
| C4-24 | `ReqdMsgNmId` 的取值必须是本项目实际生成的三个报文标识符之一 |
| C4-25 | `ReqdTxTp` 出现时，回执里的明细状态与方向必须与请求一致 |

**C4-24 挡的是自由文本字段。** 规范把要请求的报文名做成 `Max35Text`，
**于是拼错一个字符在规范眼里完全合法**，而回执方无从判断该回什么。

## 4D. 第十二批：公司行为族，S-7 的落点由此定死

**日期 2026-09-12。** §4A.8 挂了很久的"`seev` 公司行为族仍未开始"在此开始。
读的是消息集 1241 Corporate Actions（2025–2026 维护版）的 MDR Part 2 与规范 XSD，
**全程浏览器内存，未落盘**。**这一批只读 S-7 需要的部分，不求覆盖全族。**

族内十三张报文：`seev.031` 通知、`seev.032` 事件处理状态、`seev.033` 指令、
`seev.034` 指令状态、`seev.035` 预告、`seev.036` 过账确认、**`seev.037` 过账冲正**、
`seev.038` 叙述、**`seev.039` 事件撤销通告**、`seev.040` 指令撤销请求、
`seev.041` 指令撤销请求状态、`seev.042` 指令结单、`seev.044` 预告撤销。

### 4D.1 公司行为事件标识是必填的，这是本项目至今唯一一个强锚点

`CorporateActionGeneralInformation` 在每张报文上都是 1..1，其内：

| 元素 | 基数 | 说明 |
|---|---|---|
| `CorpActnEvtId` | **1..1**，`Max35Text` | **账务服务方指派**，"unambiguously identify a corporate action event" |
| `OffclCorpActnEvtId`（COAF） | **0..1** | 官方中央机构指派的全市场唯一号 |
| `EvtTp` | **1..1** | 事件类型 |

**必填的那个只在本账务服务方内部唯一，全市场唯一的那个可选。**
**这是本轮第四次遇到同一形状**（§4B.12 明细锚点、§4C.10.4 请求配对、§4.6.6 的 `NONREF`），
**但这一次强的那一头是必填的**，所以公司行为侧比资金侧和撤销侧都好办。

**规范对 COAF 的唯一约束是 C16，内容是"SMPG 发布了市场实践建议"**——
**一条只给出外部指针的约束**，与 §4C.1 记的 SMPG 决策图同源。

**CMOP 的取用：`CorpActnEvtId` 用作公司行为回放的主键，COAF 不生成。**
理由是本项目只有一个账务服务方，**全市场唯一性没有对手可比**。

### 4D.2 规范自己确认了 CMOP 独立写下的那条业务不变量

`CorporateActionEventType40Code` 里两个拆股码的定义原文：

> **SPLF** StockSplit — Increase in a corporation's number of outstanding equities
> **without any change in the shareholder's equity or the aggregate market value**
> at the time of the split. Equity price and nominal value are reduced accordingly.
>
> **SPLR** ReverseStockSplit — Decrease in a company's number of outstanding equities
> **without any change in the shareholder's equity or the aggregate market value**
> at the time of the split. Equity price and nominal value are increased accordingly.

[数据生成规范](data-generation-specification.md) §7 第 3 条写的是"数量乘 F、
成本基础除以 F，且账户层面的总成本基础不变"。**这条当初是从会计一致性推出来的，
不是从规范抄的。** 规范的定义与它逐字对应：数量变、单价反向变、总额不变。

**记为一次独立验证。** 这类验证很少，值得单独写：**项目自己推出的不变量与规范的定义相符，
说明推导的前提没错**，而不是两边抄同一个来源。

### 4D.3 C12 的散文点了一个这张报文里根本不存在的元素

`seev.037` 的 C12 `IntermediateSecuritiesDistribution1Rule`，散文：

> If CorporateActionGeneralInformation/EventType/Code is RHDI, then
> CorporateActionDetails/**IntermediateSecuritiesDistributionType** must be present. (MT 566 NVR C5)

形式化：

> On Condition /CorporateActionGeneralInformation/EventType/Code is equal to value
> 'IntermediateSecuritiesDistribution'
> Following Must be True /CorporateActionDetails Must be present
> And /CorporateActionDetails/**FollowingEventTypeIndicator** Must be present

**两个名字不一样，而且散文点的那个元素在 `seev.037` 的结构表里搜不到。**
结构表里有的是 `CorporateActionDetails/FollowingEventTypeIndicator`（0..1）。

**这是散文与形式化不一致的第二次，且比第一次严重。** 第一次是 `pacs.004` 的 C17，
形式化多了一个条件（§4B.11）；**这一次是散文点错了元素**。
散文末尾带 `(MT 566 NVR C5)`，**说明它是从 ISO 15022 的 MT 报文规则搬过来的，搬的时候没改名**。

**§4B.11 定下的读法在此再次生效并可以加强：**
**引用 MDR 约束一律以形式化为准，散文只作导航；散文里出现的元素名要回结构表核对。**

### 4D.4 决定性发现：过账冲正不是事件撤销，S-7 原来的设想是错的

`seev.037` 的 `RvslRsn/Rsn/Cd` 用 `CorporateActionReversalReason3Code`，**九个值**：

| 码 | 含义 |
|---|---|
| `DCBD` | 计息基准差异 |
| `FNRC` | 资金未收到 |
| `IRED` | 权益登记日不正确 |
| `IETR` | 事件级税率不正确 |
| `IPCU` | 支付币种不正确 |
| `IPRI` | 价格不正确 |
| `IVAD` | 起息日不正确 |
| `UPAY` | 不应支付 |
| `OTHR` | 其他 |

**九个全部是"这笔过账的某个细节填错了"，没有一个是"事件本身被取消或重述"。**

**因此 `seev.037` 冲正的是一笔过账，不是一个事件。** 事件级的撤销另有其人：
`seev.039` CorporateActionCancellationAdvice，其 scope 原文是
"to cancel a previously announced corporate action event **in case of error from the
account servicer or in case of withdrawal by the issuer**"。

**S-7 原先登记为"冲正与公司行为重述交互"，落点默认在 `sese.026` 与重述路径。**
**现在可以说清楚它其实是三条不同的路径，而且此前把它们混成了一条：**

| 路径 | 报文 | 撤的是什么 | 与 CMOP 重述模型的关系 |
|---|---|---|---|
| 一 | `seev.037` | **一笔过账** | 无关。过账细节填错，重发一笔 |
| 二 | `seev.039` | **一个已公告的事件** | **这才是重述**：事件不成立，依赖它的调整全部回退 |
| 三 | `sese.020` + `CxlRsn/Cd=CANT` + 新 `sese.023` | **一条结算指令** | **不是重述，是两条不同的交易**（§4.6.6） |

**三条路径的下游后果完全不同**：路径一只动一笔现金或证券过账；
**路径二要把该事件在所有账户上的调整因子回退，正是 §7 第 3 条的反向**；
路径三根本不产生调整因子。

**S-7 因此拆成三个场景，原编号退役：**

| 编号 | 内容 | 状态 |
|---|---|---|
| ~~S-7~~ | ~~冲正与公司行为重述交互~~ | **已拆分，编号退役** |
| S-7a | `seev.037` 过账冲正 | 待冻结，**依赖最少** |
| S-7b | `seev.039` 事件撤销与调整因子回退 | 待冻结，**这一条才依赖重述路径** |
| S-7c | `CANT` 撤销并替换 | 待冻结，见 §4.6.6 |

**S-5（`sese.026` 结算冲正）与三条都不同，它已冻结，不受影响。**

### 4D.5 又一次同名不同物：`UPAY`

`CorporateActionReversalReason3Code` 的 `UPAY` 是 UnduePayment，"Payment is not due"。
**P-6 里整组退汇用的 `UPAY` 是 `ExternalReturnReason1Code` 的成员**（§4B.11），
**两者码字母相同、所属码集不同、语义相近但不等价。**

**这是本轮第三次遇到同名不同物**（前两次是 `BOOK` 在 §4B.12、
`DeniedReason` 四个变体在 §4.6.6）。**登记为词表检查必须带码集名的又一条理由**，
见[验证与对账规范](validation-and-reconciliation-specification.md) §2C.7。

### 4D.6 本批特意没做的三件事

1. ~~**没有取十三张报文的约束整表。** 只取了 `seev.037` 的 24 条。~~
   **已于同日补齐，见 §4D.7。** 全族 496 条，形式化 51 条。
2. ~~**没有展开 `seev.031` 通知与 `seev.033` 指令。**~~ **2026-09-13 纳入范围，见 §4D.12。**
   原先的理由（只做拆股与合股，没有选择权）在范围扩大后不再成立。
3. **没有生成 COAF。** 理由见 §4D.1。

### 4D.7 十三张的约束整表横向比对：四百九十六条，形式化只有五十一条

**按 §4C.10 对资金族用过的做法，对公司行为族做一遍。**

| 报文 | 约束条数 | 带形式化 | 挂在报文根上 |
|---|---|---|---|
| `seev.031` 通知 | **118** | **28** | 37 |
| `seev.032` 事件处理状态 | **7** | 0 | 0 |
| `seev.033` 指令 | 31 | 1 | 6 |
| `seev.034` 指令状态 | 38 | 7 | 11 |
| `seev.035` 预告 | **84** | 8 | 13 |
| `seev.036` 过账确认 | **77** | 3 | 10 |
| `seev.037` 过账冲正 | 24 | 1 | 4 |
| `seev.038` 叙述 | 14 | 0 | 0 |
| **`seev.039` 事件撤销通告** | **14** | **0** | **0** |
| `seev.040` 指令撤销请求 | 22 | 1 | 3 |
| `seev.041` 指令撤销请求状态 | 29 | 1 | 2 |
| `seev.042` 指令结单 | 23 | 1 | 3 |
| `seev.044` 预告撤销 | 15 | 0 | 0 |
| **合计** | **496** | **51** | **89** |

**形式化占比约一成。** 对照此前几族：`camt` 四张 31/31/30/9 条里只有 3 条形式化，
`pacs.004` 82 条里形式化很常见。**`seev.031` 一张就占了全族形式化的一半以上。**

**条数与消息重要性不成正比，这一点要写下来。** `seev.031` 通知 118 条，
**而 `seev.039` 事件撤销通告只有 14 条，且一条形式化都没有**——
**撤销一个已公告事件的后果，规范一个字都没约束。**

`seev.039` 的十四条逐条看过，**全部是通用校验**：`AnyBIC`、`Country`、
`DescriptionPresenceRule`、`DescriptionUsageRule`、`EventTypeRule`、`ISINGuideline`、
`ISINPresenceRule`、`OfficialCorporateActionEventReference`、
`OtherIdentificationPresenceRule`、`SafekeepingAccountOrBlockChainAddress` 三条、
`SafekeepingPlaceRule`、`SupplementaryDataRule`。

**结论：S-7b 的全部业务语义——事件被撤销后，由它导出的调整因子必须全部回退——
在规范里没有任何依据，是 CMOP 自己的不变量。** 这与 §4B.12 记的
"scope 禁止而约束不管"不同：**那里至少还有一句 scope，这里连一句都没有。**

### 4D.8 `seev.039` 的三处结构决定了 S-7b 长什么样

**一、撤销原因只有两个值，且它们的下游后果不同。**

| 码 | 含义 |
|---|---|
| `WITH` | Withdrawal，**发行人撤销了该公司行为事件** |
| `PROC` | Processing，**账务服务方处理出错** |

`CxlRsnCd` 是 **1..1，必填**——**与 `sese.020` 的 `CxlRsn` 0..1 正相反**（§4.6.6）。
**这一次规范强制说明原因，只是词表只有两个值。**

**两个值对 CMOP 的意义不同**：`WITH` 是市场事实变了，
**回退之后不应当再有该事件**；`PROC` 是本方公告错了，
**回退之后该事件可能以修正后的形式重新公告**。
**因此 S-7b 必须两条都做，而不是挑一条。**

**二、撤销可以只针对部分账户。**

`AcctsDtls` 是 1..1 的二选一：

| 分支 | 基数 |
|---|---|
| `ForAllAccts` | 1..1 |
| `AcctsList` | **1..*** |

**即一个事件可以在某些账户上被撤销、在另一些账户上仍然有效。**
**这直接打掉一个想当然的写法：把撤销当成事件级的开关。**
**CMOP 的取用：只生成 `ForAllAccts`**，部分撤销登记为注入，
**其期望结果是判据必须按账户判定，而不是按事件判定**。

**三、撤销通告仍然必须声明事件的完整性与确认状态。**

| 元素 | 基数 | 值 |
|---|---|---|
| `EvtCmpltnsSts` | **1..1** | `COMP` 完整 / `INCO` 不完整 |
| `EvtConfSts` | **1..1** | `CONF` 已确认 / `UCON` 未确认 |

**一边说这个事件撤销了，一边还要说它是否已确认发生过。**
**这不是冗余：`WITH` + `CONF` 与 `WITH` + `UCON` 是两回事**——
前者是"确实发生过、但发行人撤回"，后者是"本来就没确认过"。
**CMOP 的取用：`WITH` 配 `CONF`，`PROC` 配 `UCON`**，
其余两种组合登记为注入。

### 4D.9 S-7b 的不变量草案，尚未冻结

**不冻结的理由只有一个：它需要 §7 的公司行为回放先把调整因子物化出来。**
但不变量可以先写，**因为它们不依赖实现方式**：

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| S7b-1 | 每条 `seev.039` 的 `CorpActnEvtId` 必须命中一条此前发出的公司行为公告 | 全部。**这是唯一的锚点，而它是必填的**（§4D.1） |
| S7b-2 | 撤销后，该事件在受影响账户上的调整因子必须回退，数量与成本基础复原 | 全部。**这是 §7 第 3 条的反向，规范无依据** |
| S7b-3 | 依赖该事件的已发布结果必须被重述，且旧版本保留 | 全部。**与 A-3 的验收判据同形**（§3A.13） |
| S7b-4 | `WITH` 之后不得再出现同一 `CorpActnEvtId` 的新公告 | **仅 `WITH`**。`PROC` 恰恰允许重新公告 |
| S7b-5 | 撤销的作用范围按账户判定，不得按事件判定 | 全部。**`AcctsList` 分支使部分撤销合法** |
| S7b-6 | **不得断言**撤销之后该事件从未存在 | 全部。**否定式**：审计要求撤销本身留痕 |

**S7b-3 把公司行为侧接回主业务目标。** 分配迟到（A-3）与事件撤销（S-7b）
**是两条完全不同的路径，却要求同一件事：已发布结果被重述且旧版本保留**。
**两条路径共用一个验收判据，这比只有一条路径时更有说服力。**

**S7b-6 是清单里第五条否定式**，前四条见 §4B.12 末段。

### 4D.10 S-7a：公司行为过账冲正，已冻结

**冻结日期 2026-09-12。** 场景是：一次拆股的证券过账已确认，
**随后发现该笔过账的某个细节填错，账务服务方冲正它**。
**事件本身依然成立**，这是它与 S-7b 的全部区别（§4D.4）。

#### 指针是必填的，被指的那个标识却是可选的

| 报文 | 元素 | 基数 |
|---|---|---|
| `seev.036` 过账确认 | `MovementConfirmationIdentification` | **0..1** |
| `seev.037` 过账冲正 | `MovementConfirmationIdentification` | **1..1** |

**冲正必须说自己冲的是哪一条确认，而确认可以不给自己编号。**

**这是本项目遇到的第五种锚点形状，而且方向与前四种都不同。** 此前四种（§4.6.6 的表）
说的都是"指针本身强不强"；**这一种是指针必填而目标可选**，
**于是冲正可以指向一个从未被声明过的标识，两头都合规。**

**规范唯一相关的约束是 C49 `PaginationRule`：**

> On Condition /Pagination is present
> Following Must be True /MovementConfirmationIdentification Must be present

**即只有分页时才强制编号。** 不分页的单页确认可以匿名。
**CMOP 的取用：`seev.036/MvmntConfId` 一律必填**，
不填的情形注入为负例，**期望结果是只有 CMOP 判据报错**。

#### 逐步取值

**输入固定为某个 `EvtTp/Cd=SPLF` 的拆股事件，比例 F，已在账户 A 上过账。**

| 步 | 报文 | 方向 | 关键取值 | 之后状态 |
|---|---|---|---|---|
| 1 | `seev.036` | 账务服务方 → 账户持有方 | `MvmntConfId` 新派生；`CorpActnGnlInf/CorpActnEvtId` 回引该事件；`EvtTp/Cd=SPLF`；`AcctDtls/Bal/ConfdBal` 填过账后持仓；`SctiesMvmntDtls` 一条，`CdtDbtInd=CRDT`、`PstngQty` 填新增股数、`DtDtls/PstngDt` 填过账日 | 已过账 |
| 2 | `seev.037` | 同上 | `MvmntConfId` **回引第 1 步**；`RvslRsn/Rsn/Cd` 取九个值之一；`CorpActnGnlInf` 与第 1 步完全一致；`SctiesMvmntDtls` 与第 1 步同量同向；`OrgnlPstngDt` 回填第 1 步的 `PstngDt` | 该笔过账已冲正，S-7a 结束 |
| 3 | `seev.036` | 同上 | 新 `MvmntConfId`；其余按修正后的值重发 | **不属于 S-7a**，登记为可选后继 |

**四处取值决定：**

- **原因码取 `IPRI` 价格不正确。** 九个值里（§4D.4），
  `FNRC`、`IPCU`、`IVAD`、`DCBD`、`IETR` 都是现金侧的概念，
  **拆股是纯证券过账，没有现金腿**；`IRED` 权益登记日不正确会连带改变受影响持仓，
  **那是另一个场景**；`UPAY` 不应支付同样是现金语义。
  **`IPRI` 与 `OTHR` 是仅有的两个说得通的**，取 `IPRI`。
- **`OrgnlPstngDt` 必填，虽然规范是 0..1。** 不填的话，
  **冲正与被冲正的过账只靠 `MvmntConfId` 一根线连着**，
  而那根线在第 1 步本来可以不存在（见上）。
- **`CorpActnGnlInf` 与第 1 步逐字一致。** 规范没有这条约束，
  **但两条报文对同一事件给出不同的 `EvtTp` 在业务上不可能**。
- **第 3 步不做。** 重发修正后的确认会与第 1 步同 `CorpActnEvtId`、
  不同 `MvmntConfId`，**判据必须能区分"冲正后重发"与"重复过账"**，
  这需要先有 E-9 通过。**登记为 S-7a′。**

#### S-7a 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| S7a-1 | 每条 `seev.037` 的 `MvmntConfId` 命中一条 `seev.036` 的 `MvmntConfId` | 全部。**规范只保证指针存在，不保证目标存在** |
| S7a-2 | 冲正与被冲正过账的 `FinInstrmId`、`PstngQty`、`CdtDbtInd` 三者一致 | 全部。**CMOP**，规范无约束 |
| S7a-3 | `OrgnlPstngDt` 等于被冲正过账的 `PstngDt` | 全部。**CMOP**，规范是 0..1 |
| S7a-4 | 冲正**不得**触发该事件的调整因子回退 | 全部。**这就是 E-9**，与 S-7b 的 E-2 互为反面 |
| S7a-5 | 账户持仓在冲正后回到过账前的数量 | 全部。**账户级，不是过账级** |
| S7a-6 | 冲正之后该事件仍然存在且仍然确认 | 全部。**否定式的正面写法**：挡的是把 S-7a 当成 S-7b |

**S7a-4 与 S7a-6 说的是同一件事的两面**，都保留：
前者管调整因子，后者管事件本身的存在性。
**生成器最容易犯的错是把两张报文的处理路径合并**，而合并之后这两条会同时失败，
**同时失败正是要的信号**。

#### 本节顺带记下的两处，与 S-7a 无关但值得写

**一、同一条约束在两张报文上犯同一个错。** `seev.036` 的 C35 与 `seev.037` 的 C12
是同一条 `IntermediateSecuritiesDistribution1Rule`，**散文与形式化的元素名不一致
（§4D.3），而且两张报文上的文字逐字相同。**
**说明它不是排版事故，是源头的一处错误被分发到了每一张引用它的报文上。**

**二、拼错的名字与正确的名字在同一份清单里共存。** `seev.036` 的 C2 是
`AdditionalInformationRule`（拼写正确，报文级），C3 至 C6 是
`AdditionalInforrmationRule`（多一个 r，字段级）。
**两者散文几乎相同，是两条不同的约束。**
**按任一个名字搜索，都只能搜到一半。** 这是 §4.6.6 记的第六种翻车方式的最强证据。

### 4D.11 S-7c：公司行为引发的撤销并重发，已冻结

**这一档是 S-7 拆出的第三块**，与 S-7a（过账冲正）、S-7b（事件撤销）都不同：
**被撤销的不是过账，也不是事件，是一条结算指令**，而撤销的起因在公司行为段。
**所以它的报文全在 `sese` 族，判据却要跨到 `seev` 族取事件**。

#### 4D.11.1 撤销原因码里有两个公司行为码，含义不同

从 `sese.020.001.09` 与 `sese.024.001.14` 的 XSD 直接读出，
**不经散文**：

| 码 | 名称 | 定义（规范原话译） |
|---|---|---|
| `CANT` | CancelledDueToTransformation | 原交易**因公司行为被撤销并重发** |
| `CORP` | CancelledDueToCorporateAction | 原交易**因公司行为被撤销** |
| `CANZ` | CancelledSplitPartialSettlement | 原交易**被撤销并重发**，以允许部分或拆分结算 |

**`CANT` 与 `CORP` 的差别只有"并重发"三个字，而这三个字决定后面有没有第二条指令。**
**误用的代价是对账口径直接反过来**：按 `CORP` 处理时该笔就此消失是正确的，
按 `CANT` 处理时该笔就此消失是漏了一条。
**规范没有任何一条约束把这两个码与"是否存在后继指令"绑定起来。**

`SCEX`（证券不再合格）的定义里还带一句选码指引：
"For corporate action related cancellation, CORP should be used."
**这是本项目读到的第一条写在码定义里的选码指引**，且用 should 不用 must，
**不是约束，是市场惯例的书面化**。

#### 4D.11.2 四个撤销原因码集，成员数 2／11／11／不适用

**上一批把这件事记在散文上，这一批从 XSD 逐个证实**，并改正一处计数：

| 码集 | 用在哪 | 成员数 | 含 `CANT` |
|---|---|---|---|
| `CancelledStatusReason16Code` | `sese.020` 撤销请求；`sese.024` 状态回报 | **11** | 是 |
| `CancelledStatusReason5Code` | `sese.027` 的 `Canc`（撤销已执行） | **2**（`CANI`、`OTHR`） | **否** |
| `CancelledStatusReason12Code` | 其他状态报文 | 11 | 是 |
| `CancelledStatusReason9Code` | 其他状态报文 | 11 | 是 |

**上一批从 PDF 抄出的 9Code 二十个成员与 16Code 十三个成员都是错的**，
错因是 PDF 正文里码集与码集首尾相接，**按码字母做正则会一路吃到下一个码集**。
**XSD 的枚举有明确边界，此后码集成员一律以 XSD 为准，PDF 只用来取定义文字。**

**由此得到本节最重要的一条结构结论：**

> **撤销的原因在请求上有十一种，在"撤销已执行"的回报上只剩两种。**
> **`CANT` 不在这两种之内。**

也就是说，**一次因公司行为而起的撤销，走完全程之后，
终态报文上再也读不到它是因公司行为而起的**。
**这不是漏填，是码集不给。**

#### 4D.11.3 重发的那一条指向不了被撤销的那一条

`sese.024.001.14` 共 56 个元素名，**没有一个能承载"替代交易的标识"**：
既没有 `RplcmntTxId` 之类的元素，也没有 `CorpActnEvtId`。
**`CANT` 说"已撤销并重发"，而说这句话的报文没有地方写重发的是哪一条。**

**这是锚点第四档（结构上不可能）的第二种成因。** §4B.11 记的整组退汇是
"承载元素被约束禁止出现"，**这一处是承载元素压根不存在**。
**两种成因的判据写法相同（降级并写明降级），但可修复性完全不同**：
前者换一种报文形态就能拿回锚点，**后者除非改标准，否则永远拿不回来**。

#### 4D.11.4 反方向能连，但连法本身是误用，而且有一个会死锁的写法

`sese.023.001.13`（结算指令）有 `Lnkgs`，`[0..*]`，内含 `Ref` `[1..1]`。
所以重发的那条指令**可以**回指被撤销的那条。三处障碍：

**一、`Lnkgs` 的定义说的不是来历，是次序。** 规范原话：
"Link to another transaction that must be processed after, before or at the same time."
**它是一个处理顺序元素，被拿来记录"我是谁的替代品"属于借用。**

**二、`Ref` 是七选一。** `References41Choice` 给的是
`SctiesSttlmTxId`、`IntraPosMvmntId`、`IntraBalMvmntId`、`AcctSvcrTxId`、
`MktInfrstrctrTxId`、`PoolId`、`OthrTxId`。
**即使 `Lnkgs` 在，判据也必须先判分支选对了没有**，
而七个分支的类型全是 `Max35Text`，**填错分支在 XSD 上看不出来**。

**三、`PrcgPos` 用错码会把重发的那条永久挂起。** 这是 C80 `WithLinkageRule`：

> If Code WITH is used, then the one or more instruction which are linked become bound
> and which must be executed together. Even if one single
> transactions/instructions/notifications can not be executed, then all the other
> transactions/instructions/notifications must also be kept pending.

**被链接的那条已经撤销，永远不会执行。** 于是按 C80，
**重发的那条必须一直挂着**。`ProcessingPosition3Code` 四个值里，
`AFTE`、`BEFO`、`WITH` 都在断言一个与已撤销交易的执行次序关系，
**只有 `INFO`（"linked for information purposes only"）是安全的**，
而 `PrcgPos` 本身是 `[0..1]`。

**这是本项目至今最典型的一个"看上去最自然的写法恰好是最坏的写法"。**
"把替代指令和原指令绑在一起执行"听起来正是想要的语义，
**而规范给这句话的后果是永久挂起**。

**`WITH` 在本项目里的第三种含义。** 公司行为段是 Withdrawn（事件撤销），
外部词表里另有一处，**这里是 Processing Position 的 With（与被链接指令一同执行）**。
**三处同字母不同物，`WITH` 因此进入 §2C.7 第五句的强制带码集名清单。**

#### 4D.11.5 锚点的方向性：本项目第一次需要这个维度

S-7c 逼出一个此前没有的区分：

| 方向 | 能不能连 | 档位 |
|---|---|---|
| 被撤销的 → 重发的（正向） | **不能**，报文里没有承载元素 | 第四档，成因二 |
| 重发的 → 被撤销的（反向） | 能，但每一层可选且分支要选对 | 第三档 |

**锚点强度表（§4.6.6）此后要按方向分别归档。**
一个关联在一个方向上是第四档、在另一个方向上是第三档，**这很常见，
而只记一个档位会让判据写反**：正向不可达时，遍历必须从重发的那条起步，
**不能从被撤销的那条起步再报"找不到后继"**。

#### 4D.11.6 S-7c 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| S7c-1 | 原因码为 `CANT` 的撤销，必须存在一条回指它的重发指令 | 全部 S-7c。**CMOP**，规范无约束 |
| S7c-2 | 原因码为 `CORP` 的撤销，**不得**存在回指它的重发指令 | 全部。**否定式**，与 S7c-1 互为反面 |
| S7c-3 | 重发指令的 `Lnkgs/Ref` 必须走 `SctiesSttlmTxId` 分支 | 仅当 `Lnkgs` 出现。**CMOP**，七选一里只有它对 |
| S7c-4 | 重发指令的 `Lnkgs/PrcgPos/Cd` 必须是 `INFO` | 仅当 `PrcgPos` 出现。**依据是 C80**，其余三值会按规范挂起 |
| S7c-5 | 撤销与重发必须落在同一个 `CorpActnEvtId` 之下 | 全部。**CMOP**，两张 `sese` 报文都没有这个字段，靠生成侧记账 |
| S7c-6 | `sese.027` 的 `Canc` 分支上**不得**期待读到 `CANT` | 全部。**否定式**，`CancelledStatusReason5Code` 只有两个值 |
| S7c-7 | 重发指令的数量与原指令的数量之和守恒，除非事件本身改变数量 | 仅当事件类型不改变数量。**CMOP** |

**S7c-6 是这一批新增的否定式，编号进 §1A.3。**
它挡的写法是"从终态报文回读撤销原因"，**那个写法在别的段落一直成立**，
**只有在这里，码集把原因删掉了**。

**S7c-5 的实现代价要写明。** 两张 `sese` 报文都不带事件标识，
**这条不变量在报文层面不可验证**，只能靠 CMOP 自己在生成时留一张对照表。
**对外口径必须说清楚这一条是本项目的记账，不是从数据里判出来的。**

### 4D.12 S-8：带选择权的公司行为，2026-09-13 纳入范围并冻结

**范围决定来自 2026-09-13 的用户确认。** 此前只做拆股与合股，
两者对持有人都没有选择；**选择权事件的全部难点都在"持有人说了什么、没说什么"上**，
而那恰好是对账与异常处理的主场。

**本节材料全部从 `seev.031.001.16`、`seev.033.001.14`、`seev.034.001.16`、
`seev.036.001.17` 的 XSD 读出**，定义文字与约束取自公司行为 MDR Part 2。

#### 4D.12.1 事件分三类，而且字段是必填的

`CorpActnGnlInf/MndtryVlntryEvtTp` 在通知里是 **1..1**，取值三个：

| 码 | 规范定义（摘译） | 需不需要持有人指令 |
|---|---|---|
| `MAND` | 参与是强制的，**不需要**持有人进一步指令 | 不需要 |
| `CHOS` | 参与是强制的，**需要**持有人指令，**除非已指定默认选项** | 需要，有默认兜底 |
| `VOLU` | 参与是自愿的，想参加就必须给指令 | 需要，没有兜底 |

**拆股与合股是 `MAND`。本节新增的是 `CHOS` 与 `VOLU`。**
**`CHOS` 的定义里那句 "unless a default option has been specified" 是整个场景的枢纽**：
不给指令的持有人，结果取决于有没有默认选项。

**但指令报文 `seev.033` 的 `CorpActnGnlInf` 里没有这个字段**，只有事件标识、事件类型与标的。
**所以判断"这条指令是不是必须发的"只能回到通知上去看**，适用条件又一次落在另一张报文上。

#### 4D.12.2 选项的锚点是编号不是类型，而且规范在三张报文上用了三套类型码

通知里每个选项（`CorpActnOptnDtls`，**0..\***）有两个必填字段：
`OptnNb`（**恰好三位数字**）与 `OptnTp`。

**三张报文的选项类型码集不同**，逐个从 XSD 取枚举：

| 报文 | 码集 | 成员数 | 与通知相比 |
|---|---|---|---|
| `seev.031` 通知 | `CorporateActionOption15Code` | **22** | — |
| `seev.033` 指令 | `CorporateActionOption16Code` | **26** | 多 `CERT`、`MKDW`、`MKUP`、`TAXI` |
| `seev.036` 确认 | `CorporateActionOption12Code` | **23** | 多 `MKDW`、`MKUP`，**少 `BOBD`** |

**一个选项在生命周期里走过三张报文，它的类型码可能在第三张上根本不存在。**
**所以"通知、指令、确认三者的 `OptnTp` 相等"不是一条可以写的不变量。**

**规范自己也说要用编号**，但三处的强度不同：

| 报文 | 约束 | 措辞 |
|---|---|---|
| `seev.031` | C88 `OptionNumberGuideline` | it is **recommended** to use the OptionNumber |
| `seev.033` | C20 `OptionNumber1Rule` | the OptionNumber **must** be used，且每个选项编号必须互不相同 |

**同一件事，发出选项的通知是建议，引用选项的指令是强制。**
**这是本项目第一次看到同一条规则在兄弟报文之间强度不同。**
生成侧必须按强的那一边做：**通知里的选项编号一律唯一**。

**编号在确认上是 `OptionNumber1Choice`**，可以是三位数字，也可以是码 `UNSO`。
`seev.033` 的 C21 规定：**指令在没有通知在先时，编号必须填 `UNSO`**（unsolicited）。
**所以 `UNSO` 是一个合法的"没有锚点"的声明**，与 §4.6.6 的 `NONREF` 同形。
**锚点强度表第二档（退化但不消失）因此多一个实例。**

#### 4D.12.3 默认选项：每个选项都必须表态，但全事件有几个默认规范不管

通知里每个选项的 `DfltPrcgOrStgInstr` 是 **1..1**，它是一个二选一：

| 分支 | 定义（摘译） |
|---|---|
| `DfltOptnInd` | 持有人**不给指令时**，该选项是否被默认选中 |
| `StgInstrInd` | 持有人是否已下了**长期指令**选这个选项；长期指令能不能被覆盖取决于账户或事件条款 |

**二选一的后果**：一个选项不能同时声明"我是默认"与"有长期指令选我"。
**而全事件范围内有几个 `DfltOptnInd=true`，没有任何约束。**
约束整表里与默认有关的只有 C12：默认选项不得同时是 `ApldOptnInd=true`。
**零个默认与多个默认在规范上都合法**，前者意味着 `CHOS` 退化成必须指令，
后者意味着"不给指令"的结果不确定。

**本项目口径：每个 `CHOS` 事件恰好一个默认选项，每个 `VOLU` 事件零个。**
**这是 CMOP，不是规范**，而且是本节后果最重的一条 CMOP：
它决定了 S-8 里所有沉默持有人的结果。

**默认被执行时，结果落在 `seev.034` 上**：`InstrPrcgSts` 有专门的
`DfltActn`（"Default action is taken"）与 `StgInstr`（"Standing instruction has been applied"）
两个分支，**都不带原因码**。**而 `seev.034` 的 `InstrId` 是 0..1**，
所以一条"默认已执行"的状态回报可以不指向任何指令，**这恰好是它该有的样子**：
沉默的持有人本来就没有指令。

#### 4D.12.4 截止时间可以不给

通知里选项的 `DtDtls` 下的日期**本轮查到的全部是 0..1**，与截止相关的两个：

| 元素 | 定义（摘译） |
|---|---|
| `MktDdln` | 发行人或其代理人设定的回复截止 |
| `RspnDdln` | **账户服务方**设定的回复截止 |

**一个 `CHOS` 或 `VOLU` 事件可以一个截止时间都不公布**，而没有截止时间，
"迟到"与"沉默后执行默认"就都无从判定。**本项目口径：`CHOS` 与 `VOLU` 事件两个都给，
且 `RspnDdln` 早于 `MktDdln`。** 顺序也是 CMOP：规范只说一个是服务方的、一个是市场的。

**迟到的两个拒绝码也分这两层**（`RejectionReason89Code`）：

| 码 | 定义（摘译） |
|---|---|
| `ADEA` | 晚于**账户服务方**截止；**按双方服务协议处理** |
| `LATE` | 晚于**市场**截止 |

**`ADEA` 的定义带一句"按双边协议处理"**，与 §4B.15.3 的 `ACSC` 同类，
**本项目判不了双边协议，因此 `ADEA` 之后的处理结果不做断言**，只断言拒绝码与时点一致。

#### 4D.12.5 改指令：一条跨报文的指引，加一条同报文的规则

`seev.033` 有 `ChngInstrInd`（0..1，"本指令替换一条此前已撤销的指令"）。

- **C6 `ChangeInstructionIndicatorGuideline`**：只有当**此前收到的通知**里
  `WdrwlAllwdInd=false` 且 `ChngAllwdInd=true` 时才可以用。
  **这是一条指引而不是规则，而且适用条件在另一张报文上**。
- **C16**：`ChngInstrInd=true` 时，`InstrCxlReqId` **必须**出现。
- 通知侧 **C98 `RevocabilityPeriodRule`**：`WdrwlAllwdInd` 或 `ChngAllwdInd` 为真时，
  必须给出可撤回期间。

**本项目本轮不生成改指令**，理由见 §4D.12.8。

#### 4D.12.6 与既有公司行为模型的关系：调整因子在这里不成立

§7 第 3 条（数量乘 F、成本基础除以 F、总成本基础不变）是为 `MAND` 拆合股写的。
**选择权事件的结果取决于每个账户选了什么**：选现金的账户持仓减少、现金增加，
选证券的账户按比率换股。**同一事件在不同账户上没有同一个 F。**
**所以第 3 条对 S-8 不适用，必须按选项分别求值**，登记为 S8-6 与 S8-7。

#### 4D.12.7 S-8 的最小生命周期

**事件**：一个 `CHOS` 事件，两个选项。`001`=`CASH`（现金），`002`=`SECU`（证券），
**`002` 为默认**。`RspnDdln` 为 D，`MktDdln` 为 D+1，支付日为 D+3。三个账户：

| 步 | 报文 | 账户 | 内容 |
|---|---|---|---|
| 1 | `seev.031` | 全部 | `NtfctnTp=NEWM`，两个选项，`002` 的 `DfltOptnInd=true` |
| 2 | `seev.033` | 甲 | D 日之前，`OptnNb=001`，数量等于全部可选余额 |
| 3 | `seev.034` | 甲 | `AccptdForFrthrPrcg`，`InstrId` 回引第 2 步 |
| 4 | `seev.033` | 丙 | **D 之后、D+1 之前**，`OptnNb=001` |
| 5 | `seev.034` | 丙 | `Rjctd`，原因码 `ADEA` |
| 6 | `seev.034` | 乙、丙 | `DfltActn`，**不带 `InstrId`** |
| 7 | `seev.036` | 甲 | `CorpActnConfDtls/OptnNb=001`，现金入账 |
| 8 | `seev.036` | 乙、丙 | `OptnNb=002`，证券入账 |

**乙从头到尾没有说话；丙说了，但说晚了。两者结果相同，路径不同。**
**区分这两条路径正是本场景对主业务目标的贡献**：
T+1 早晨的异常处理里，"客户说选现金、实际收到股票"的投诉，
**答案要么是没收到指令，要么是指令迟到被拒**，两个答案对应两个责任方。

#### 4D.12.8 S-8 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| S8-1 | 每条 `seev.036` 的 `OptnNb` 命中该事件通知里的某个 `OptnNb` | 全部，**除非 `OptnNb=UNSO`**。**规范**：`seev.033` C20 要求按编号区分 |
| S8-2 | 同一事件的通知里 `OptnNb` 互不相同 | 全部。**规范在指令侧是 must、在通知侧是 recommended**，按强的做 |
| S8-3 | `CHOS` 事件恰好一个选项 `DfltOptnInd=true`；`VOLU` 事件零个 | 全部。**CMOP**，规范不管数量 |
| S8-4 | 一个账户在截止前有被接受的指令时，确认的 `OptnNb` 等于指令的 `OptnNb` | 仅当存在 `AccptdForFrthrPrcg` |
| S8-5 | 一个账户在截止前没有被接受的指令时，确认的 `OptnNb` 等于默认选项，且存在一条 `DfltActn` | 仅 `CHOS`。**依据是 `CHOS` 的码值定义** |
| S8-6 | 选现金的账户：持仓减少量 = 指令数量，现金增加 = 数量 × 公布价 | 仅 `CASH` 选项 |
| S8-7 | 选证券的账户：按公布比率换股，**§7 第 3 条按该选项的比率单独求值** | 仅 `SECU` 选项 |
| S8-8 | `Rjctd` 的原因码为 `ADEA` 时，指令时点晚于 `RspnDdln`；为 `LATE` 时晚于 `MktDdln` | 仅被拒指令 |
| S8-9 | **不得**断言通知、指令、确认三者的 `OptnTp` 相等 | 全部。**否定式**：三张报文的类型码集不同 |
| S8-10 | `DfltActn` 状态回报**不得**被要求带 `InstrId` | 全部。**否定式**：沉默的持有人没有指令可引 |

#### 4D.12.9 本轮特意不做

1. **不做 `VOLU` 的完整生命周期。** 它与 `CHOS` 的唯一差别是沉默的结果（不参加 vs 默认），
   **S8-3 与 S8-5 已经把这个差别写成判据**；生成只需把默认去掉，不另开场景。
2. **不做改指令与撤回。** C6 是跨报文的指引，C16 与 C98 是规则，
   **三者组合的合法空间要先把 `seev.040`／`seev.041` 读到与撤销族同样的深度**，登记为 S-8a。
3. **不做 `UNSO`。** 它是锚点第二档，生成它等于把 S8-1 的适用条件切掉一块，
   **本轮只作注入**。
4. **不做按比例分配（`PROR`）与超额认购（`OVER`）。** 两者会让 S8-6 的等式变成不等式。

### 4D.13 S-9：部分结算与拆分重发，2026-09-13 冻结

**这一节把 §4.6.6 里 `CANZ` 留下的未决项收掉。** 材料取自结算族的
`sese.023.001.13`、`sese.024.001.14`、`sese.025.001.13` 的 XSD 与 MDR Part 2。

#### 4D.13.1 "部分结算"在规范里是两套机制，共用一个名字

| 机制 | 怎么发生 | 报文形状 |
|---|---|---|
| **原生部分结算** | 一条指令，开关打开，结算方分多次交付 | **一条 `sese.023`，多条 `sese.025`** |
| **拆分重发（`CANZ`）** | 原指令撤销，由若干条新指令替换 | **一条被撤销的 `sese.023`，若干条新的 `sese.023`** |

**两者对账口径完全不同**：前者数量守恒在同一个 `TxId` 下，
后者数量守恒跨多个 `TxId`，**而新旧指令之间的连接方式与 S-7c 完全相同**
（§4D.11.4：`Lnkgs`、`SctiesSttlmTxId` 分支、`PrcgPos=INFO`）。

#### 4D.13.2 开关的四个值

`PrtlSttlmInd` 用 `SettlementTransactionCondition5Code`，四个值：

| 码 | 定义（摘译） |
|---|---|
| `NPAR` | 不允许部分结算 |
| `PART` | 交易将分多次结算 |
| `PARC` | 允许部分结算，**但每次须满足现金价值下限** |
| `PARQ` | 允许部分结算，**但每次须满足证券数量下限** |

**`PARC` 与 `PARQ` 的下限在这三张报文里没有找到承载元素。** 所以"每次部分结算的量不低于下限"
**在报文层面判不了**，与 §4D.11.6 的 S7c-5 同类。

#### 4D.13.3 同一张报文里 `PARC` 有两个意思，这是目前最强的同字母不同物

`sese.025` **同时**带着两个元素：

| 元素 | 码集 | `PARC` 的意思 |
|---|---|---|
| `PrtlSttlmInd` | `SettlementTransactionCondition5Code` | **允许部分结算，有现金下限** |
| `PrtlSttlm` | `PartialSettlement2Code` | **本次是最后一次部分确认，此后不再结算** |

**一条结算确认上可以同时出现两个 `PARC`，意思完全无关。**
此前五处同字母不同物跨族、跨领域或跨码集，**这一处在同一张报文里**。
§2C.7 第五句（必须写码集名）到这里已经不是谨慎，是必需。

#### 4D.13.4 确认序列：规范给了次序，没给连接

`sese.025` 的 C30／C32 `PartialSettlementGuideline`：
首条（可以多条）确认填 `PAIN`，**最后一条**确认剩余部分时填 `PARC`。**是 guideline，不是 rule。**

`PartialSettlement2Code` 两个值的定义：

| 码 | 定义（摘译） |
|---|---|
| `PAIN` | 本次确认是部分结算，**交易仍有部分未结算** |
| `PARC` | 本次确认是部分结算，**此后不再结算** |

**`PARC` 的定义与 guideline 不完全一致。** guideline 说它确认"剩余部分"，
定义只说"不再结算"。**两者在"剩余部分被放弃"这种情形下分歧**：
按定义可以用 `PARC` 收尾而总量不足，按 guideline 不行。
**本项目口径：`PARC` 收尾时累计结算量必须等于指令数量。** 这是 CMOP，理由是
按定义那一读会让 V2-3 的数量守恒失去依据，而"放弃剩余"应当走撤销。

**连接字段全部可选**：`PrvsPrtlConfId`（上一条部分确认的标识）、
`RmngToBeSttldQty`、`RmngToBeSttldAmt`，**全部 0..1**。
**所以确认之间是一条可以不连的链**，锚点第三档。

#### 4D.13.5 S-9 的最小生命周期

**两条独立的支线，共用一个起点。**

**S-9a 原生部分结算**：指令数量 1000，`PrtlSttlmInd=PART`。

| 步 | 报文 | 内容 |
|---|---|---|
| 1 | `sese.023` | `SttlmQty=1000`，`PrtlSttlmInd=PART` |
| 2 | `sese.025` | `SttldQty=600`，`PrtlSttlm=PAIN`，`RmngToBeSttldQty=400` |
| 3 | `sese.025` | `SttldQty=400`，`PrtlSttlm=PARC`，`PrvsPrtlConfId` 回引第 2 步，`RmngToBeSttldQty=0` |

**S-9b 拆分重发**：指令数量 1000，`PrtlSttlmInd=NPAR`，因头寸不足被拆。

| 步 | 报文 | 内容 |
|---|---|---|
| 1 | `sese.023` | `SttlmQty=1000`，`PrtlSttlmInd=NPAR` |
| 2 | `sese.024` | `Canc`，原因码 `CANZ` |
| 3 | `sese.023` ×2 | 数量 600 与 400，各带 `Lnkgs/Ref/SctiesSttlmTxId` 回引第 1 步，`PrcgPos=INFO` |
| 4 | `sese.025` ×2 | 各自一条，**均不带 `PrtlSttlm`**：对各自的指令而言是全额结算 |

**S-9b 第 4 步是本节最容易写错的地方**：两条确认合起来是原指令的部分，
**但对各自的指令都是全额**，所以不填 `PAIN`／`PARC`。

#### 4D.13.6 S-9 的不变量

| 编号 | 不变量 | 适用条件 |
|---|---|---|
| S9-1 | `PrtlSttlmInd=NPAR` 的指令下**不得**出现带 `PrtlSttlm` 的确认 | 全部。**否定式** |
| S9-2 | 同一 `TxId` 下带 `PrtlSttlm` 的确认，按时点排序后前若干条为 `PAIN`，**恰好最后一条**为 `PARC` | 仅 `PrtlSttlmInd` ∈ {`PART`,`PARC`,`PARQ`} 且有多条确认。**规范 guideline** |
| S9-3 | `PARC` 收尾时，同一 `TxId` 累计 `SttldQty` = `SttlmQty` | 同上。**CMOP**，见 §4D.13.4 |
| S9-4 | 若 `PrvsPrtlConfId` 出现，它命中同一 `TxId` 下时点更早的一条确认 | 仅当出现。**第三档锚点** |
| S9-5 | `CANZ` 撤销后，回指它的新指令数量之和 = 原指令数量 | 全部 S-9b。**CMOP**，规范无约束 |
| S9-6 | S-9b 的新指令各自的确认**不得**带 `PrtlSttlm` | 全部 S-9b。**否定式** |
| S9-7 | 判定 `PARC` 时**必须**同时给出元素名或码集名 | 全部。**§4D.13.3 的同报文冲突** |

**V2-3（同一 `TxId` 下 `sese.025` 恰好一条）的适用条件由此闭合**：
它在 `PrtlSttlmInd=NPAR` 时成立，在另外三个值下由 S9-2 与 S9-3 接管。
**S-9b 下它对每一条新指令各自成立**，不受拆分影响。

## 5. FINTRAC

已降级为业务语义与审计依据，不形成报送契约。本阶段只需回答一个问题：

**结果如何声明它是在哪个规则版本下产生的。** 规则版本标识、生效区间、以及结果对规则
版本的引用方式，这三项定下来即可，不需要吃透具体报告类型的全部字段。

## 6. 结算周期

加拿大自 2024-05-27 起为 **T+1**，美国次日跟进。所有报文时序、迟到窗口与对账截止时点
以 T+1 为准，文档中不得再出现 T+2 表述。

## 7. 出处登记

填写字段时同步登记出处，避免事后无法复核。

| 标准 | 版本 | 出处 | 获取日期 |
|---|---|---|---|
| FIX | 4.4 with 20030618 Errata | [FIX Trading Community 完整规范包](https://fixtrading.org/packages/fix-4-4-specification-with-20030618-errata/)，Vol. 1–7 加勘误单，7.5 MB；Volume 1 Instrument/OrderQtyData，Volume 4 订单报文与 Order State Change Matrices，**Volume 5 分配与确认**，Volume 6 字段枚举 | 2026-09-09 初次，2026-09-10 重新取得 |
| ISO 20022 证券 | Settlement and Reconciliation 消息集，维护周期 2025–2026，证券 SEG 于 2026-01-27 批准，最后更新 2026-03-17 | [ISO 20022 报文定义目录](https://www.iso20022.org/iso-20022-message-definitions)，`sese` 族规范 XSD 与 **MDR Part 1、Part 2、Part 3** 逐条取得 | 2026-09-10 初次，**Part 2 与 Part 3 于 2026-09-12 读完** |
| ISO 20022 资金 | Bank-to-Customer Cash Management（消息集 1246）与 Payments Clearing and Settlement（消息集 1249），均于 2026-03-19 最后更新 | 同上目录，`camt` 与 `pacs` 共十二种报文的规范 XSD 与**两个消息集的 MDR** | 2026-09-10 初次，**MDR 于 2026-09-12 读完** |
| ISO 20022 外部词表 | `2Q2026_externalcodesets_v3`，季度更新 | [External Code Sets 页面](https://www.iso20022.org/catalogue/additional-content-messages/external-code-sets) 发布的 XSD 压缩包；163 个类型、3347 条码值，其中 33 条已废止 | 2026-09-12 |
| ISO 20022 银行交易码 | `BTC_Codification_30Nov2025` | 同页单独发布的 XLSX；11 个域、约 1569 行有效组合 | 2026-09-12 |
| FINTRAC | | | |

**FIX 本地副本**：`~/Downloads/fix-4-4-spec/`，文件名形如 `fix-44_VOL-5_w_Errata_20030618.pdf`。
**不入库**：规范文本属第三方版权材料，仓库只保留引用，不保留 PDF。

**ISO 20022 未落盘**：`sese`、`camt`、`pacs` 的 XSD 与 MDR 全部在浏览器内存中读取，
本机无副本，仓库只保留核对结论与引用。
