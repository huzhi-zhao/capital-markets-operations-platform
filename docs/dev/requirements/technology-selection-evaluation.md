# Technology Selection Evaluation Requirement

> **Status**: Draft · **Date**: 2026-09-09
>
> **Decision state**: 本文规定**怎样评估**，不选择任何产品。执行入口条件是 **workload
> envelope 就绪**，不是 BO baseline 冻结——§5 的七个代表性负载全部引自
> [工作负载基线](../workload-baseline.md) §5，没有一个引自 FIX 或 ISO 20022，因此再读多少
> 报文规范也不会改变哪个候选能做好带主键的历史改写。该条件已于 2026-09-09 满足，评估随
> Phase 0B-1 开始执行，见[立项与就绪度](../project-inception-and-readiness.md) §6。
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
| 表格式 | Iceberg，未实测 | [ADR 0002](../adr/0002-transaction-centric-lakehouse-layering.md) |
| Catalog 实现 | **只定了"独立 REST Catalog"，具体实现未定** | 同上 |
| 批计算引擎 | Spark，未实测 | [ADR 0003](../adr/0003-hybrid-deployment-topology-and-component-placement.md) |
| 交互查询引擎 | Trino，未实测 | 同上 |
| 编排 | Airflow，是否复用既有实例未定 | [平台架构](../platform-architecture.md) §4.2、§10 |
| 流式组件 | Kafka 与 Flink，仅窄窗口演示 | [平台架构](../platform-architecture.md) §7 |
| 血缘 | OpenLineage 与 Marquez | [平台架构](../platform-architecture.md) §9 |
| 语言与 LTS JDK | 只有原则，模块映射未定 | [ADR 0004](../adr/0004-language-and-runtime-boundaries.md) |

**Catalog 实现是新拆出来的一行。** 原来它和表格式合并在一格里，"Iceberg 加独立 REST
Catalog"读起来像已经定了，实际上定的只是接口形态，背后是哪一个实现完全没选。两者的回滚成本
也不同，合并会让深度要求跟着错。

### 2.1 候选清单

上表每一行原本只写了一个倾向值。**只有一个候选的评估不是评估**，因此 0B-1 先把真实备选摆出来。
下表的"候选属性"一律是**待核实的说法，不是已确认的事实**，核实本身就是 0B-1 的工作。

| 决策 | 候选 | 先淘汰谁，为什么 |
|---|---|---|
| 对象存储 | SeaweedFS、Garage、MinIO、RustFS、直接用文件系统 | 直接用文件系统会让 §5 的 W7 跨隧道写入失去可测对象，保留但排在最后 |
| 表格式 | Iceberg、Delta Lake、Hudi | 不重开。三者都支持按主键改写，Iceberg 的多引擎中立性是本项目 Spark 写、Trino 读拓扑的直接需求 |
| Catalog | REST Catalog 的各实现、JDBC catalog | JDBC catalog 部署最轻，但会把 catalog 绑死在一个数据库实例上 |
| 批计算 | Spark、DuckDB、Polars | 见 §2.2 |
| 交互查询 | Trino、DuckDB、其他 MPP | 见 §2.3 |
| 编排 | Airflow、Dagster、Prefect、cron 加脚本 | 见 §2.3 |
| 流式 | Kafka 加 Flink、Redpanda、不上流式 | 用途只有窄窗口演示，按 §3 属低回滚成本 |
| 血缘 | Marquez、把 OpenLineage 事件直接落表 | 落表方案省掉一个常驻 web 应用与一个 Postgres |

### 2.2 单机方案必须被认真对待，不能默认 Spark

回填量是 800 GB–1.5 TB，日增量只有 200–360 MB。**这两个数字之间差了三个数量级**，而
[平台架构](../platform-architecture.md) §4.1 已经据此判定日增量不需要按需算力节点。同样的
逻辑往前推一步：如果只有 W1 首次回填真正需要分布式,那么为一个一次性负载常驻一整套 Spark
运维负担,按 §4 第 4 条"一个兼职的人"衡量是亏的。

必须验的是 DuckDB 或 Polars 对 Iceberg 的**写入**成熟度,不是读取。读取早已可用,写入才是
W2 与 W6 的前提。如果写入不成熟,Spark 就是被证据选中的,而不是被默认选中的。这个区别会写进
ADR。

### 2.3 OCI 常驻内存预算是第一道横切筛子

[平台架构](../platform-architecture.md) §8 已经指出 24 GB 要同时装下多个常驻组件,现有约
21 GB 是粗略预算,缺实测。**这一条应当先于任何单组件评测执行**,因为它一次同时约束四个决策:
编排、交互查询、流式、血缘。

理由是 §1 已经写明的"评估必须以组合为单位"。逐个组件挑最优,再发现总和装不下 24 GB,等于把
四轮评测全部作废重来。**先测常驻占用,再测性能**,顺序反了代价很高。

因此 0B-1 的第一个动作不是选对象存储,而是给出一份 OCI 常驻组件的实测内存清单,并据此决定
哪些候选在进入性能评测之前就已经出局。

### 2.4 已核实：独立 REST Catalog 确实免除了对象存储的条件写入要求

**结论成立，但风险是转移而不是消失。** 核实日期 2026-09-09，证据取自规范本身，不采信博客与
厂商材料，符合 §6 的证据要求。

**证据一，表规范对文件系统的要求只有三条。**
[Iceberg 表规范](https://github.com/apache/iceberg/blob/main/format/spec.md)写明 Iceberg
只要求文件系统支持 in-place write、seekable reads、deletes 三种操作，并明确 "Tables do not
require rename"，唯一例外是 "except for tables that use atomic rename to implement the
commit operation for new metadata files"。**条件写入与原子重命名都不是规范级要求，而是某一类
提交实现的要求。**

**证据二，隔离性的基础是元数据指针的原子交换。** 同一份规范称 "atomic swap of one table
metadata file for another provides the basis for serializable isolation"，写入方通过
"swapping the table's metadata file pointer from the base version to the new version" 提交，
冲突时 "the writer must retry the update based on the new current version"。**规范没有规定这个
交换由谁执行。**

**证据三，REST catalog 把交换执行在服务端。**
[REST Catalog OpenAPI](https://github.com/apache/iceberg/blob/main/open-api/rest-catalog-open-api.yaml)
的 UpdateTable 请求携带一组 requirements，定义为 "assertions that will be validated before
attempting to make and commit changes"，例如 `assert-table-uuid` 与 `assert-ref-snapshot-id`；
断言不成立时服务端返回 409 CommitFailedException，客户端可重试。**这就是 CAS，位置在 catalog
服务端，不在对象存储。**

三条合起来：本项目采用独立 REST Catalog，因此对象存储只需提供上述三种操作，不需要条件写入。

#### 由此产生的三条后果

**一、原子性搬进了 catalog 的后端存储，那里成了提交路径上的单点。** 它必须进入 §2.3 的 OCI
常驻清单，也必须重新进入恢复讨论：[工作负载基线](../workload-baseline.md) §5.6 原本判定只有
参考数据与别名映射不可替代，现在要重新判断 catalog 后端算不算第三项。它**理论上**可以从对象
存储里的 metadata 文件重建，但重建过程本身没有验证过，**未验证的重建不能当作已有的恢复手段**。

**二、必须在配置层禁止 filesystem 与 Hadoop catalog 路径。** 规范的例外条款正是这条：用原子
重命名提交的表仍然需要重命名语义。任何一个作业被配成 filesystem catalog，就把重命名或条件
写入的要求悄悄放了回来，**而且失败方式是并发下静默丢提交，不是报错**。这条要成为配置门禁，
不能靠记得。

**三、S3 兼容性的真实考点换了。** 不再是条件写入，而是 multipart upload。S3FileIO 使用渐进式
分片并行上传，默认分片 32 MB、阈值为分片大小的 1.5 倍。Iceberg 的 AWS 文档只讨论原生 S3，
**不讨论任何第三方兼容实现**，因此候选存储对 multipart 的支持程度必须自己测，拿不到任何背书。

#### 对候选范围的影响

**放宽。** 规范要求的三种操作每个 S3 兼容实现都具备，§2.1 的对象存储候选不因条件写入被淘汰。
区分度转移到 multipart upload 行为与失败恢复上，正好落在 §4 第 3 条已经要求的轴上。

## 3. 评估深度与回滚成本挂钩

**投入的评估深度必须与决策的回滚成本成正比。** 对一个改起来只需换配置的选择做 probe，是把
预算花在错误的地方。

| 回滚成本 | 含义 | 要求 |
|---|---|---|
| 高 | 需要重写全部数据或改变分层语义 | 必须独立 ADR，必须实测 probe |
| 中 | 需要迁移但数据可原样搬 | 独立 ADR，可用兼容性验证替代完整 probe |
| 低 | 换配置或换进程即可 | 不单独立 ADR，记在架构文档即可 |

初判已复核并细化如下，作为 0B-1 的执行依据：

| 决策 | 回滚成本 | 依据 |
|---|---|---|
| 表格式 | 高 | 换格式要重写全部 Bronze 与 Silver 数据 |
| 对象存储 | 中 | 数据可原样搬，前提是 S3 兼容性成立 |
| Catalog 后端存储 | 中 | 提交路径的单点，见 §2.4 |
| Catalog 实现 | 中 | 元数据可重建，但全部表指针要迁移 |
| 批计算引擎 | 中 | 换引擎要重写处理代码,数据不动 |
| 交互查询引擎 | 低 | 只读 Gold,换掉不影响任何已写入数据 |
| 编排 | 低 | 换调度器要重写 DAG 定义,不触及数据 |
| 流式组件 | 低 | 只承载窄窗口演示 |
| 血缘 | 低 | 事件格式是 OpenLineage,消费端可换 |

**相对初判改了两处。** 批计算引擎从"未列"补为中,因为 §2.2 把它变成了真实的开放选择,而换
引擎意味着重写全部处理代码,这不是低成本。对象存储的 S3 兼容性风险等级下调,该判断已由 §2.4
核实成立:提交原子性由 REST Catalog 承担,对象存储不需要条件写入,候选范围相应放宽,而头号
兼容性问题改为 multipart upload。

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

## 7. Probe P-1：OCI 常驻内存预算

按[立项与就绪度](../project-inception-and-readiness.md) §5，每个 probe 必须事先写明风险、
输入、成功阈值与停止条件。本节是 P-1 的章程。

**关联风险**：[平台架构](../platform-architecture.md) §8 记的约 21 GB 是粗略预算，缺实测。
若真实占用超过 24 GB，编排、交互查询、流式、血缘四个决策同时失效。

**为什么拆成两级**：[roadmap](../roadmap.md) 的 Phase 0 写明 2026 年不搭建管道组件。实际
部署组件测 RSS 与这条边界冲突。因此 P-1 分为纸面筛与实测两级，**纸面筛不触碰该边界，现在
即可执行**；实测需要先就边界作出决定。

### 7.1 P-1a 纸面筛，已执行

只用各项目自己发布的内存要求做加法，目的不是得到准确数字，而是回答"是否已经装不下"。

| 组件 | 官方口径 | 出处 |
|---|---|---|
| Trino | 部署文档给出的起步值是 `-Xmx16G`；Kubernetes 部署中 coordinator 与 worker 各自典型 8 GB | [Deploying Trino](https://trino.io/docs/current/installation/deployment.html)、[Trino on Kubernetes](https://trino.io/docs/current/installation/kubernetes.html) |
| Airflow | 至少 4 GB，建议 8 GB | [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) |
| Kafka、Flink、Superset、Marquez 及其 Postgres、Catalog 后端 | 待查 | — |

**结论已经可以下了，不需要补齐其余行。** 仅 Trino 取 Kubernetes 的典型 8 GB、Airflow 取
最低 4 GB，两项就占掉 24 GB 的一半，而这还没算流式、BI、血缘、两个数据库和操作系统本身。

**因此 §8 的约 21 GB 预算不成立。** 它不是偏乐观，而是没有把各组件自己声明的要求加起来过。
这条现在就要写回平台架构，不必等实测。

**同时得出一个方向性判断**：候选里最省的组合值得优先评估，而不是把 Trino 加 Airflow 加
Kafka 加 Flink 当成默认起点再想办法塞进去。§2.1 里的 cron 加脚本、DuckDB、以及把
OpenLineage 事件直接落表这三个"轻"候选，从此不是陪跑项。

### 7.2 P-1b 实测，待边界决定后执行

- **输入**：每个候选组件的最小可用配置，逐个部署，不一次性全上。
- **测量**：空载 RSS，以及在 §5 的 W4 负载下的峰值 RSS；每个数字附版本、配置、日期。
- **成功阈值**：一套完整组合的常驻峰值合计不超过 24 GB 的 80%，留出操作系统与突发余量。
- **停止条件**：单个组件空载即超过 6 GB 时停止该候选，不再测其性能。
- **产物**：写回本文 §7.1 的表与[平台架构](../platform-architecture.md) §8。
- **可丢弃**：部署产物一律视为一次性，不演变为 Phase 1 的部署基线。

## 8. 未决项

- P-1b 实测能否在 2026 年执行，取决于 roadmap 的"不搭建管道组件"边界是否放宽，见 §7。
- Catalog 后端存储能否从对象存储中的 metadata 文件重建，以及重建耗时。§2.4 已确认它是提交
  路径上的单点，但重建路径未验证。
- 禁止 filesystem 与 Hadoop catalog 的配置门禁做成什么形式，见 §2.4。
- DuckDB 或 Polars 的 Iceberg 写入成熟度，见 §2.2。
- 各 probe 的时间盒长度。
- W1 是否允许用缩小比例的数据代跑，以及缩放后结论的有效范围。
- 评估结果与 Proposed ADR 的对应关系：一个 ADR 对一个决策，还是一个 ADR 覆盖一组组合。
