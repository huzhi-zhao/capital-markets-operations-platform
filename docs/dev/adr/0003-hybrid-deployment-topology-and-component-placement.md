# ADR 0003: Hybrid Deployment Topology and Component Placement

> **Status**: Proposed · **Date**: 2026-09-02
>
> **Related architecture**: [Platform architecture](../platform-architecture.md)
>
> **Capacity basis**: [Data volume baseline](../data-volume-baseline.md)
>
> **Logical data layers**: [ADR 0002](0002-transaction-centric-lakehouse-layering.md)

## Context

CMOP 使用已经就位的家庭 NAS、按需上线的 MacBook Pro 和 OCI Montreal 常驻节点。
Bronze/Silver 预计接近 TB 级，而 Gold 是面向查询的聚合数据。家庭与云之间通过 WireGuard
连接，跨隧道的小对象往返延迟比顺序传输带宽更危险。

[ADR 0002](0002-transaction-centric-lakehouse-layering.md) 已把 Silver 的逻辑访问需求分为
宽扫描与定点追溯。这里进一步决定它们的物理执行路径：前者要求计算靠近 NAS，后者可以
接受跨隧道访问经过元数据裁剪后的少量对象。这意味着没有必要为了“下钻”在 16 GB NAS
上常驻 Trino。

## Options considered

### A. 所有组件运行在 NAS

数据本地性最好，但 4 核 8 线程、16 GB 内存不适合同时承载对象存储、Spark、Trino 和
控制面，也会让存储故障与计算故障共享爆炸半径。

### B. 所有数据和计算迁入 OCI

组件管理简单，但免费节点只有 200 GB 本地盘，无法容纳目标数据规模，扩容会改变成本
边界。历史生成与扫描也会把大量数据搬过公网。

### C. NAS 运行存储和 Trino，MBP 运行 Spark，OCI 只作公网入口

宽扫描与定点查询都靠近存储，但 NAS 内存不足，常驻查询引擎会争夺对象存储资源。
Silver 的宽扫描本来就由 Spark 完成，新增 Trino 的收益有限。

### D. 家庭侧承担大数据存储与批计算，OCI 承担控制面和服务面

TB 级读写留在千兆局域网；跨隧道只传作业控制、元数据、聚合后的 Gold 和有界下钻。

## Proposed decision

采用方案 D，当前组件落位如下：

| 节点 | 角色 | 组件与数据 |
|---|---|---|
| NAS，4C/8T、16 GB、8 TB 可扩 | 7×24 存储节点 | S3-compatible object storage；Bronze 与 Silver；当前存储候选为 SeaweedFS |
| MacBook Pro，规格待补 | 按需批处理节点 | 数据生成与批处理角色；宽扫描 EDA 与特征工程；本地 NVMe shuffle/spill；当前批处理候选为 Spark |
| OCI Montreal，4C、24 GB、200 GB | 7×24 控制面与服务面 | 编排、Catalog、Gold、交互查询、可选窄流处理、BI、血缘、监控和公网入口 |

具体职责约束：

1. NAS 不运行批处理或交互查询引擎。对象存储实现必须提供项目所需的 S3 与表格式兼容性；
   SeaweedFS 是当前偏好，但不由本 ADR 单独接受。
2. 批处理 driver 与 worker 都留在家庭侧。使用 Spark 时必须采用 cluster mode。OCI 编排器
   只远程提交作业并轮询状态，不在自身进程内遍历 Bronze/Silver 对象。
3. 家庭侧批处理引擎在局域网读取 Silver、构建 Gold，再将小得多的 Gold 批次写到 OCI。
4. Trino 的主要服务对象是 OCI 本地 Gold；它可以为受限的合规下钻读取 Silver，但查询
   必须带主键、事件 ID 或有界时间谓词，不允许多年宽扫描。
5. Silver 的 EDA、特征工程和多年聚合由 MBP 上的批处理引擎完成，不为此在 NAS 安装
   Trino 或其他常驻查询引擎。
6. 若 BO 证明需要流式切片，broker 与流处理角色只承载窄演示或回放窗口，不承载十年
   历史生成。Kafka、Redpanda、Flink、Spark Structured Streaming 均尚未在本 ADR 选定。
7. CMOP 使用独立的表格式 Catalog 和元数据库，不复用 UOIP Hive Metastore，避免两个
   项目共享元数据爆炸半径；REST Catalog 是当前实现候选，不是本 ADR 的独立选型结论。
8. Pipeline 以可整体重跑的批次为基本执行单位，不依赖 MBP 7×24 在线或真实时间持续推送。

WireGuard 隧道只允许四类预期流量：作业提交与状态、Gold 批次、Catalog 元数据、
带强谓词的 Silver 下钻。Spark 对 Bronze/Silver 的批量扫描不得穿越隧道。

## Technology selection boundary

本 ADR 接受的对象是**角色与物理节点的映射**，不是表格中出现的全部产品名。只要仍然
满足“NAS 存储、MBP 批处理、OCI 控制与服务”的边界，SeaweedFS 换成其他 S3-compatible
实现、Spark 换成其他批处理引擎，都不需要 supersede 本 ADR。

产品选择只有在存在真实替代方案、评价标准和较高改变成本时才建立独立 ADR。预计在编码前
至少评估以下决策轴，但评估不等于每项都必须产出 ADR：

| 决策轴 | 候选示例 | 独立记录的触发条件 |
|---|---|---|
| 对象存储 | SeaweedFS / Garage / RustFS | S3/Iceberg 兼容性、恢复或迁移成本形成长期约束 |
| 表格式与 Catalog | Iceberg / 其他表格式；REST Catalog / HMS / 其他 Catalog | 版本、更新、隔离和多引擎契约需要冻结 |
| 事件 broker | Kafka / Redpanda / 不设 broker | BO 确认需要持久流式事件通道 |
| 流处理引擎 | Flink / Spark Structured Streaming / 不设流处理层 | BO 确认需要独立流处理语义 |
| 查询引擎 | Trino / 其他服务引擎 | 引擎选择出现真实替代方案且改变接口或运维边界 |

[Platform architecture](../platform-architecture.md) 是完整技术栈的常青总览；独立 ADR 只
保存值得长期追溯的选型理由。若多项技术确实作为一个不可拆分的组合被比较和替换，可以
建立组合 ADR，但不能仅为了减少篇数把能够独立变化的产品塞进同一篇。

## Consequences

### Positive

- TB 级扫描、shuffle 和 spill 全部留在家庭局域网与 MBP 本地 NVMe。
- OCI 只承载体量较小但需要常驻和公网访问的服务，符合现有免费资源边界。
- NAS 保持单一职责，避免 16 GB 内存同时服务对象存储和查询引擎。
- Gold 与 Trino 同机降低交互查询延迟，同时 Gold warehouse 仍可通过 Catalog 配置迁移。
- 独立 Catalog 隔离 CMOP 与 UOIP 的元数据和误操作风险。

### Negative and risks

- 跨隧道下钻延迟高于本地 Gold，必须通过查询门禁和 Iceberg manifest 裁剪控制对象数。
- MBP 不在线时无法进行宽扫描、生成、回填或 Gold 重建。
- OCI 24 GB 内存余量有限，编排、可选流处理、查询和可观测组件不能无约束扩张。
- Gold 跨隧道写入虽然远小于 Silver，仍需要幂等提交、失败恢复和可观测状态。
- 家庭存储是关键真相源，需要独立备份与恢复方案；8 TB 容量本身不等于数据安全。

## Open questions

- MBP 的具体 CPU、内存与本地 NVMe 可用空间。
- Airflow 复用既有实例还是为 CMOP 独立部署。
- Iceberg snapshot 保留窗口与 `expire_snapshots` 调度。
- Gold 重建的提交协议、失败恢复和触发入口。
- OCI 清理后可持续提供给 Gold 的真实磁盘与内存余量。
- SeaweedFS、Garage、RustFS 等候选的兼容性、维护状态与恢复演练结果。
- 编码前技术选型审查中，哪些决策达到独立 ADR 的准入门槛。
