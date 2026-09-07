# ADR 0002: Transaction-Centric Logical Data Layering

> **Status**: Proposed · **Date**: 2026-09-02
>
> **Related requirements**: [Project overview](../requirements/project-overview.md),
> [Business objectives](../requirements/business-objectives.md)
>
> **Related architecture**: [Platform architecture](../platform-architecture.md)

## Context

CMOP 需要先定义不依赖具体机器、中间件和部署位置的逻辑数据契约。否则 Bronze、Silver、
Gold 只是三个目录名，后续每个 BO 都可能重新解释各层应该保存什么。

业务查询大多命中 Gold，并不能说明 Silver 没有价值。Silver 的首要逻辑职责是为 Gold
重建提供已标准化但仍保留明细粒度的事实基础；业务口径变化时，应从 Silver 重算，而不是
重新摄取或重新生成 Bronze。Silver 还需要支持新问题探索、特征工程和逐笔追溯。

金融运营场景要求一项异常、预警或对账差异能够返回支撑它的原始记录。本 ADR 只决定
各层的语义、粒度和消费者类型，不决定它们存在哪台机器、由哪个引擎读写，或 NAS 是否
部署查询引擎。物理部署与中间件职责由 [ADR 0003](0003-hybrid-deployment-topology-and-component-placement.md)
决定。

## Options considered

### A. 只保留原始层与汇总层

从 Bronze 直接构建 Gold，减少一份存储。代价是每次口径变化都重复解析、去重和规范化，
并使不同 Gold 作业各自实现一套清洗逻辑。

### B. 以行情为中心组织湖仓

适合研究价格与收益，但交易、清算、资金与持仓被降为附属数据，无法形成运营事实链。

### C. 交易中心的 Bronze/Silver/Gold 分层

Bronze 保存来源语义，Silver 形成可复用的明细事实与一致业务键，Gold 提供固定口径的
运营、监管和风险输出。

## Proposed decision

采用方案 C，并提出以下层级契约：

| 层级 | 主要职责 | 主要消费者 |
|---|---|---|
| Bronze | 保留生成或摄取时的事件形态、到达顺序、原始标识和异常；支持重新处理 | 标准化作业、审计追溯 |
| Silver | 去重、标准化、关联主数据，保留接近来源的交易明细粒度和修正历史 | Gold 派生作业、EDA、特征工程、定点下钻 |
| Gold | 固定业务口径的对账、异常、监管、风险和展示结果 | BI、监管与运营使用方、外部演示 |

补充约束：

1. 核心事实围绕订单、成交、资金、清算和持仓组织，行情与公司行为作为参考数据接入。
2. 三层是逻辑契约，不等同于物理 bucket、warehouse、节点或特定中间件。
3. Gold 从 Silver 派生；Silver 从 Bronze 与经过批准的参考数据派生。Gold 口径变化默认
   从 Silver 重建，不重新取得全部来源。
4. Silver 保留接近来源的明细粒度、稳定业务键、到达信息和修正关系，不预先承诺某一种
   Gold 聚合方式。
5. Silver 同时支持宽扫描和定点追溯两类访问需求；具体执行引擎和位置不在本 ADR 决定。
6. 每项 Gold 结果必须保留能够返回 Silver/Bronze 支撑记录的业务键、批次和规则版本。
7. 公司行为、迟到确认和更正必须产生可解释的重述，而不是静默覆盖历史。
8. 后续选择的表格式必须满足本逻辑契约要求的版本、更新、重述和可追溯能力；具体产品
   选型另行决策。

## Consequences

### Positive

- 清洗和业务键只实现一次，多个 Gold 输出共享同一明细基础。
- 业务口径变化可以从 Silver 回算，避免重新生成或摄取所有来源。
- 宽扫描和定点追溯被识别为两类逻辑需求，物理架构可以据此安排不同执行路径。
- 分层契约独立于当前家庭硬件，未来更换节点或中间件不需要推翻本 ADR。

### Negative and risks

- Bronze、Silver、Gold 会产生存储放大，需要文件大小、compaction 和 snapshot 生命周期治理。
- Silver 粒度如果过早聚合，后续 BO 无法回推；如果完全不建业务键，又只是一份换格式的
  Bronze。
- 跨层追溯需要稳定事件 ID 和 lineage contract，不能等 Gold 完成后再补。
- 逻辑契约本身不能保证性能，需要物理分区、表格式和执行架构继续落实。

## Open questions

- Bronze 对 FIX/ISO 20022 原始 payload 的保留边界，以及解析后字段与原报文的关联方式。
- positions 是逐事件推导、每日快照，还是两种形态都保留。
- 公司行为重述需要保存哪些成本基础版本与会计口径。
- Silver 的共享事实边界必须在主 BO 与监管字段研究后才能冻结。
- 哪些表格式能力是硬要求，哪些只是当前实现偏好。
