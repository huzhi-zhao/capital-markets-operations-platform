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
| 第二批 | FIX 分配指令与确认 | 未开始，是 BO-1 链条上的下一段 |
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

1. **后台覆盖面是决定性的。** BO-1 的链条包含确认这一环，而确认报文 Confirmation 在
   4.2 中不存在，分配指令的字段与应答机制也是 4.4 才理顺。只要项目要讲"从订单一路对到
   确认"，4.2 即出局。**此条仍待核对**：第一批只读了订单生命周期，确认报文属第二批。
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
| FIX | 4.4 with 20030618 Errata | [FIX Trading Community 完整规范包](https://fixtrading.org/packages/fix-4-4-specification-with-20030618-errata/)；Volume 1 Instrument/OrderQtyData，Volume 4 订单报文与 Order State Change Matrices，Volume 6 字段枚举 | 2026-09-09 |
| ISO 20022 | | | |
| FINTRAC | | | |
