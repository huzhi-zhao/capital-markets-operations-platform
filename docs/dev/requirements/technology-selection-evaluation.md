# Technology Selection Evaluation Requirement

> **Status**: Draft · **Date**: 2026-09-09
>
> **Decision state**: 本文规定**怎样评估**，不选择任何产品。执行入口依赖 BO baseline 冻结；
> source inventory 与 workload envelope 已就绪，因此评估范围可以现在设计，见
> [立项与就绪度](../project-inception-and-readiness.md) §6。
>
> **Related**: [工作负载基线](../workload-baseline.md)、[平台架构](../platform-architecture.md)、
> [ADR 索引](../adr/README.md)

## 1. 本文的作用与边界

本文规定一项技术选择在被接受之前必须拿出什么证据。**它自己不做任何选择**，具体决定进入
ADR。

写成横切一份而不是每个组件一份，是因为组件之间互相制约：分别按各自最优挑选，很容易得到
一套彼此不兼容的栈。**评估必须以组合为单位，不以组件为单位。**

## 2. 评估范围

| 决策 | 当前状态 | 事实源 |
|---|---|---|
| 对象存储实现 | Proposed 偏好 SeaweedFS，未验证 | [平台架构](../platform-architecture.md) §4 |
| 表格式与 catalog | Iceberg 加独立 REST Catalog，未实测 | [ADR 0002](../adr/0002-transaction-centric-lakehouse-layering.md) |
| 批计算引擎 | Spark，未实测 | [ADR 0003](../adr/0003-hybrid-deployment-topology-and-component-placement.md) |
| 交互查询引擎 | Trino，未实测 | 同上 |
| 编排 | Airflow，是否复用既有实例未定 | [平台架构](../platform-architecture.md) §4.2、§10 |
| 流式组件 | Kafka 与 Flink，仅窄窗口演示 | [平台架构](../platform-architecture.md) §7 |
| 血缘 | OpenLineage 与 Marquez | [平台架构](../platform-architecture.md) §9 |
| 语言与 LTS JDK | 只有原则，模块映射未定 | [ADR 0004](../adr/0004-language-and-runtime-boundaries.md) |

## 3. 评估深度与回滚成本挂钩

**投入的评估深度必须与决策的回滚成本成正比。** 对一个改起来只需换配置的选择做 probe，是把
预算花在错误的地方。

| 回滚成本 | 含义 | 要求 |
|---|---|---|
| 高 | 需要重写全部数据或改变分层语义 | 必须独立 ADR，必须实测 probe |
| 中 | 需要迁移但数据可原样搬 | 独立 ADR，可用兼容性验证替代完整 probe |
| 低 | 换配置或换进程即可 | 不单独立 ADR，记在架构文档即可 |

初判：表格式为高；对象存储为中，前提是 S3 兼容性成立，**而这个前提本身就是要验的头号问题**；
查询引擎与编排为低。

## 4. 决策轴

每个候选按同一组轴描述，避免用各自最擅长的维度自说自话：

1. 与 Iceberg 及 S3 API 的实际兼容程度，不是文档声称的程度。
2. 在 16 GB NAS 与按需 MBP 这两种极不对称的节点上的资源占用。
3. 失败与恢复行为：进程被杀、磁盘写满、网络中断之后的状态。
4. 运维负担，按一个兼职的人衡量，见[工作负载基线](../workload-baseline.md) §5.8。
5. 可观测性：是否能吐出可查询的结构化指标，而不是只有日志。

## 5. 代表性工作负载

**候选必须在这些负载上测，不接受通用基准。** 它们全部来自工作负载基线 §5，不是另设的
微基准。

| 编号 | 负载 | 来源 |
|---|---|---|
| W1 | 首次回填，800 GB–1.5 TB 写入 Bronze 与 Silver | §5.1 |
| W2 | 日增量按主键 `MERGE INTO` 已有历史分区，200–360 MB | §5.1 |
| W3 | compaction，与 W2 错开排期 | §5.4 |
| W4 | Gold 交互查询，有界聚合与主键查找，秒级 | §5.3 |
| W5 | 局域网多分区宽扫描 | §5.3 |
| W6 | 反向合股导致的历史分区重述 | §5.5 |
| W7 | 跨隧道 Gold 写入，回填一次性 40 GB 与每批约 16 MB | §5.7 |

**W2 与 W6 是区分度最高的两个。** 纯追加写入几乎所有候选都能过，按主键改写历史分区并保留
可比较版本才是真正的分水岭。只跑 W1 和 W4 的评估等于没评估。

## 6. 证据要求

- **必须在本项目的硬件上测。** 厂商基准、他人博客数字与会议演讲一律不作为证据。
- 每个数字必须记录：版本、配置、数据版本、运行节点、日期。缺任一项的数字不进入决策。
- **必须包含失败路径。** 只测顺利路径的评估会系统性地偏向那些失败得最难看的候选。
- GitHub 星数、社区热度与"业界都在用"不是证据。恢复能力与兼容性优先，见
  [平台架构](../platform-architecture.md) §4。
- 允许得出"两个候选没有可测量差异"的结论。此时按运维负担选，并把这个理由写进 ADR。

## 7. 未决项

- 各 probe 的时间盒长度。
- W1 是否允许用缩小比例的数据代跑，以及缩放后结论的有效范围。
- 评估结果与 Proposed ADR 的对应关系：一个 ADR 对一个决策，还是一个 ADR 覆盖一组组合。
