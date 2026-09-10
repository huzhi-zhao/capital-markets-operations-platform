# Regulatory and Industry Data Contracts

> **Status**: Draft · **Date**: 2026-09-09
>
> **Decision state**: **FIX 版本已定为 4.4**（§3.1）。第一批五种报文的候选字段矩阵已按
> FIX 4.4 with 20030618 Errata 核对（§3.2 至 §3.3.1）；第一条最小订单生命周期 L-1
> 已填实（§3.4 至 §3.6）。本批次未扩展到撤单、改单和拒绝场景的完整状态机。
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
| 第三批 | ISO 20022 结算报文族 | 未开始 |
| 第四批 | ISO 20022 资金报文族 | 未开始 |
| 第五批 | FINTRAC，仅取规则版本化所需语义 | 未开始，已降级 |
| 不做 | CIRO 深入报送规格、SEC EDGAR XBRL | 排除 |

## 3. FIX

### 3.1 版本决定：FIX 4.4

**已定案：全项目统一使用 FIX 4.4 with 20030618 Errata，不混用版本。** 勘误版是取证时实际
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

`AllocStatus`(87) 的四个取值与语义，逐条抄自 V5-AIA p.21：

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

**三种用法的成功终态都是 `AffirmStatus = 3`（Affirmed）**，规范原文说这可以理解为该笔已可
进入结算。**这句话就是 C-1 与结算段之间的接口**，第三批的 ISO 20022 结算报文接在这里。

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
| A-2 | 分配被拒后更正重发 | 制造同一 `AllocID` 的多版本，检验维度与事实的版本对齐 | 待解锁 |
| A-3 | 分配迟到，T+1 早晨才到达 | **直接对应主业务流**，见[业务目标](business-objectives.md) §3.1 | 待解锁 |
| A-4 | 分配数量与成交总量对不上 | 制造 R1 必须捕获的差异，属注入而非正常路径 | 待解锁 |
| A-5 | 卖方主动发起分配回报（AS/AT） | 覆盖规范流程 3，方向与 A-1 相反，检验交易对手字段没写反 | 待解锁，优先级低 |
| C-1 | 逐账户确认并被接受 | 链条第四段 | **已冻结**，见 §3A.6 |
| C-2 | 确认被拒后重发 | 与 A-2 同理，作用在确认层 | 待解锁 |
| C-3 | 确认迟到，跨越结算日 | 与 T+1 结算周期交互，最难的一类 | 待解锁 |

**A-3 与 C-3 是这批里价值最高的两个**，因为 T+1 早晨的异常处理流是本项目唯一必须端到端跑通
的业务流。但它们都依赖 A-1 与 C-1 先成立，**顺序不能颠倒**。A-1 与 C-1 现已双双冻结，
**这个前置条件已经解除**。

**A-5 的优先级明确定为低。** 它对应的是卖方主动发起的分配流程，报文已核对但 CMOP 的业务
设定里没有这条流。**列出来是为了防止 AS 与 AT 被硬塞进 A-1**，不是为了排期。

**C-2 的范围比字面更宽。** 除了被拒后重发，规范给出的抄送确认（`CopyMsgIndicator = Y`）与
状态播报（`ConfirmType = 1`）也归在 C-2，因为三者共用同一套 Cancel/Replace 恢复路径。

### 3A.9 现在就要回头改的地方

第二批一旦落地，下列内容必须同步，**否则文档之间会自相矛盾**：

- [合成数据生成规范](data-generation-specification.md) §6 的采样与派生划分要扩展到分配层，
  分配数量与金额多半是派生而非采样。
- [验证与对账规范](validation-and-reconciliation-specification.md) §2.3 的 R1 目前只在 L-1
  范围内具体化，A-1 落地后要补分配侧。
- 同文档 §6.1 的六条注入里，前三条被标注为"L-2 落地后必须删除"。**A-1 与 C-1 都不解除它们**，
  解除条件仍是 L-2，不要混淆两个扩展轴。
- §3.1 那条"4.4 是最早携带确认与分配语义的版本"的待核对标记，**已于 2026-09-10 结清**，
  见 §3A.2 末尾。
- ~~账户维度仍然缺失。~~ **已于 2026-09-10 补上**，见[合成数据生成规范](data-generation-specification.md)
  §3A。C-1 把这个缺口从"需要"提升为"卡住"，因为 AK 的 `AllocAccount` 是必填字段。
- 第二批已全部核对，**本节从"填完之后要改"变成"现在就要改"**。上面各条不再有前置条件。
- [验证与对账规范](validation-and-reconciliation-specification.md) 需要新增一条确认层断言：
  每个分配账户至少一条确认，且 C-1 范围内恰好一条。**这条的适用条件必须一起写进去**，
  否则 C-2 落地时它会开始误报。

## 4. ISO 20022

未开始。以下报文族为待验证的起点，**报文标识符与版本号均需核对**。

| 领域 | 候选报文族 | 用途 | 状态 |
|---|---|---|---|
| 证券结算 | `sese` | 结算指令、状态通知、结算确认 | 待核对 |
| 资金账户 | `camt` | 账户报告、对账单、借贷通知 | 待核对 |
| 支付 | `pacs` | 资金划拨 | 待核对 |
| 公司行为 | `seev` | 公司行为通知与权益变动确认 | 待核对 |

加拿大 Lynx 大额支付系统已采用 ISO 20022，其公开材料可作为本地化的出处之一。

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

**本地副本**：`~/Downloads/fix-4-4-spec/`，文件名形如 `fix-44_VOL-5_w_Errata_20030618.pdf`。
**不入库**：规范文本属第三方版权材料，仓库只保留引用，不保留 PDF。
| ISO 20022 | | | |
| FINTRAC | | | |
