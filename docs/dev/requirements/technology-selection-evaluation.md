# Technology Selection Evaluation Requirement

> **Status**: Draft · **Date**: 2026-09-12
>
> **Decision state**: 本文规定**怎样评估**，不选择任何产品。执行入口条件是 **workload
> envelope 就绪**，不是 BO baseline 冻结——§5 的七个代表性负载全部引自
> [工作负载基线](../workload-baseline.md) §5，没有一个引自 FIX 或 ISO 20022，因此再读多少
> 报文规范也不会改变哪个候选能做好带主键的历史改写。该条件已于 2026-09-09 满足，评估随
> Phase 0B-1 开始执行，见[立项与就绪度](../project-inception-and-readiness.md) §6。
>
> **2026-09-12 重排**：候选组织单位由"按决策逐行"改为"按组合"（§2.7）。三条既有判定各自
> 抽掉了原排序的一根支柱，**默认栈不再是假定起点，改为最后测且只作对照**。评估结果与 ADR
> 的对应关系同时定案：五个 ADR 对五组绑死的问题，其中计算分工一篇已可起草。
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

**本表是按决策逐行列的，已于 2026-09-12 被 §2.7 的组合清单取代。** 它保留下来说明每一行
有哪些备选，**但不再是评估的组织单位**——逐行挑最优正是 §1 禁止的做法。

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

**已于 2026-09-12 核实，见 §2.5。** 结论是单机方案不能承担 W2 与 W6，
但否掉的理由与这里预设的不同：**写入是有的，缺的是写入之后的维护。**

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
### 2.5 已核实：单机方案的 Iceberg 写入成熟度，以及它为什么不足以承担 W2 与 W6

**核实日期 2026-09-12，证据取自各项目自己的文档，不采信博客与厂商材料，符合 §6。**
§2.2 提出的问题是"写入成熟度"，核实下来**这个提法本身不够精确**：写入是有的，
**缺的是写入之后的维护**。

#### DuckDB：写得进去，管不起来

DuckDB 的 `iceberg` 扩展（1.5 版文档）**通过 REST catalog 支持完整的 DML**：
`CREATE TABLE`、`INSERT`、`UPDATE`、`DELETE`、`MERGE INTO`，以及分区与 schema 演进。
**路径式的 `iceberg_scan` 是只读的，写入必须挂 catalog**，这与本项目 §2.4 已定的
独立 REST catalog 方向一致。

**但它自己列的三条限制，每一条都打在本项目的要害上：**

| DuckDB 文档原文的限制 | 对本项目的后果 |
|---|---|
| `UPDATE` 与 `DELETE` **只写 positional delete，不支持 copy-on-write** | W2 与 W6 每一批都在堆积 delete 文件 |
| 表若把 `write.update.mode` 或 `write.delete.mode` 设成 merge-on-read 以外的值，**操作直接失败** | 见下方"跨引擎陷阱" |
| 分区表上 `write.target-file-size-bytes` 与 `write.parquet.row-group-size-bytes` **不生效，且会报错** | 小文件治理失去唯一的表级控制手段 |

**跨引擎陷阱要单独记。** Iceberg 的 `write.delete.mode` 与 `write.update.mode`
**默认值是 copy-on-write**。也就是说，一张由 Spark 按默认配置建出来的表，
**DuckDB 连 `UPDATE` 都执行不了，会直接失败**。两个引擎写同一批表时，
表属性必须显式设成 merge-on-read，**这是配置约束，不是偏好**。

**真正致命的是维护面。** DuckDB `iceberg` 扩展提供的函数只有八个：
`iceberg_scan`、`iceberg_metadata`、`iceberg_snapshots`、表与 schema 的属性读写、
以及导出到 DuckLake。**没有 compaction，没有快照过期，没有孤儿文件清理，没有 manifest 重写。**

**W3 就是 compaction。** 一个只能产生 delete 文件、无法合并 delete 文件、
也无法过期快照的引擎，**跑不了 W3，而 W3 是 §5 的七个代表性负载之一**。

#### Polars：只有 append 与 overwrite，且标注为 unstable

Polars 的两个写入入口 `DataFrame.write_iceberg` 与 `LazyFrame.sink_iceberg`，
**`mode` 参数只接受 `append` 与 `overwrite` 两个值**，两者的文档都带
"currently considered unstable" 的警告。**没有 upsert、没有 merge、没有按条件删除。**

`sink_iceberg` 的参数说明里写着它使用 "the local pyiceberg writer"，
**也就是说 Polars 的写入能力上限就是 PyIceberg 的能力**。

#### PyIceberg：有 upsert，没有 compaction

PyIceberg 是 Polars 写入路径的实际执行者，因此单独核实：

- **有 `upsert`**，按 schema 里声明的 identifier field 做主键匹配，返回更新与插入行数。
  **这是单机路径上唯一够得着 W2 的接口**，但它要求主键在表 schema 上声明为 identifier field。
- **有 `overwrite` 加 `overwrite_filter`**，可作条件覆盖。
- **维护只有快照过期一项**，`table.maintenance.expire_snapshots()`。
- **没有数据文件 compaction。** 文档在讲 fast append 时明说
  "Compaction is planned and will automatically rewrite all the metadata when a threshold is hit"，
  **"planned" 就是还没有，而且这句讲的是 metadata 的重写，不是数据文件的合并。**
- **没有孤儿文件清理**，全文检索不到相关接口。

#### 对照：Spark 侧的 Iceberg 维护过程共二十一个

Iceberg 1.11.0 的 Spark 过程清单里，与本项目直接相关的有：
`rewrite_data_files`（W3）、`rewrite_position_delete_files`（消化 merge-on-read 的欠债）、
`expire_snapshots`、`remove_orphan_files`、`rewrite_manifests`、
`rollback_to_snapshot` 与 `rollback_to_timestamp`（W6 的回退路径）、
`create_changelog_view`（重述前后比较）、`register_table`（见 §2.6）。

**注意一条版本条件：Spark 3.x 上这些过程只有加载 Iceberg SQL extensions 才可用**，
Spark 4.0 才原生支持。共享 Spark 是 3.5.1，**因此 extensions 是必配项，不是可选项**。

#### 结论

**§2.2 的问题有答案了：单机方案不能承担 W2 与 W6，理由不是写不进去，是维护不了。**

| 候选 | 追加 | 主键改写 | compaction | 快照过期 | 结论 |
|---|---|---|---|---|---|
| Spark + Iceberg | 是 | `MERGE INTO` | `rewrite_data_files` | 有 | **W1–W7 全覆盖** |
| DuckDB | 是 | `MERGE INTO`，仅 merge-on-read | **无** | **无** | 跑不了 W3 |
| Polars | 仅 append/overwrite，unstable | **无** | **无** | **无** | 连 W2 都够不着 |
| PyIceberg | 是 | `upsert` | **无** | 仅快照过期 | 跑不了 W3 |

**因此 Spark 是被证据选中的，不是被默认选中的**，这正是 §2.2 要求写进 ADR 的区别。

**但结论要限定范围，不能扩大。** 上面否掉的是"用单机方案替代 Spark 承担全部写入负载"，
**没有否掉单机方案在其他位置的价值**：

- **W4 与 W5 是读负载**，DuckDB 与 Polars 的读取早已成熟，本节不涉及。
- **生成器侧的 Parquet 产出不经过 Iceberg**，不受本节结论约束。
- **本地开发与探索**用 DuckDB 挂同一个 REST catalog 读生产表，是本节结论的自然用法。

**还有一条要写进 ADR 的约束**：只要 DuckDB 会写这批表，
**表属性就必须显式设成 merge-on-read**，且**必须由 Spark 定期跑
`rewrite_position_delete_files` 与 `rewrite_data_files`** 把 DuckDB 留下的 delete 文件消化掉。
**两个引擎共写一批表是可行的，但维护责任只能落在 Spark 这一侧。**

### 2.6 Catalog 后端重建：路径存在，但目录清单本身不在对象存储里

**§2.4 遗留的"重建未验证"这一项，本轮取得了规范层面的答案，仍需实测计时。**

**存在一条官方重建路径。** Iceberg 的 Spark 过程 `register_table` 的定义是
"Creates a catalog entry for a metadata.json file which already exists but does not have a
corresponding catalog identifier"，输入是表名与 metadata 文件路径，
输出包含当前快照 ID、总记录数与数据文件数。**逐表重新登记是可行的。**

**但这条路径有三个缺口，缺口本身就是风险。**

**一、"哪些表存在"这份清单不在对象存储里。** `register_table` 一次登记一张表，
需要调用方已经知道表名与 metadata 文件路径。**catalog 后端丢失时，丢的正是这份清单。**
重建要靠遍历对象存储的目录结构去反推，而目录布局是可配置的：
`write.data.path` 与 `write.metadata.path` 都可以被改到表位置之外。

**二、"哪个 metadata.json 是最新的"没有规范级的判定方式。** 每个 metadata.json 内部带一条
metadata log，可以**向后**追溯历史版本；`write.metadata.previous-versions-max` 默认 100，
`write.metadata.delete-after-commit.enabled` 默认 false，所以历史文件通常还在。
**但没有任何文件指向"当前"。** 挑错一个就是静默回退到旧快照，**失败方式与 §2.4 第二条后果同类**。

**三、文档自己给了警告。** 原文：同一份 metadata.json 在多个 catalog 里注册
"can lead to missing updates, loss of data, and table corruption"，
**只应在表已不在任何 catalog 中、或正在迁移 catalog 时使用**。
重建场景符合这个前提，但它说明这个过程**没有幂等保护，重复执行会出事**。

**因此结论是有条件的：重建路径存在，但它不是一条可以事后临时拼出来的路径。**
要让它成为真正的恢复手段，必须先有两样东西：

1. **一份与 catalog 后端分离保存的表清单**，至少含表名与表位置。它很小，
   适合与[工作负载基线](../workload-baseline.md) §5.6 已判定不可替代的参考数据放在一起。
2. **一次实测演练**，测出 N 张表的重建耗时，以及最新 metadata.json 的判定方法是否可靠。

**在这两样东西到位之前，catalog 后端的恢复仍然只是假设，不是手段。** 这与 §2.4 的原判一致，
本轮只是把假设的形状描清楚了。

### 2.7 候选重排序：以组合为单位，轻重并排，默认栈不再是起点

**重排日期 2026-09-12。** §1 早就写明"评估必须以组合为单位"，但 §2.1 的候选清单仍是**按决策
逐行列的**，一行一格挑最优。本节把它改成组合清单，并说明为什么原来的排序已经失效。

#### 2.7.1 三条既有判定各自抽掉了原排序的一根支柱

| 判定 | 出处 | 它拿掉了什么 |
|---|---|---|
| OCI 默认组合实测常驻约 7.6 GB，24 GB 里绰绰有余 | §7.1.2 | **内存不再是筛子。** 原排序里"轻量组合因为装得下而领先、默认栈因为装不下而出局"这条逻辑，两头同时作废 |
| 单机引擎写得进去但维护不了，跑不了 W3 | §2.5 | **轻量组合不能靠整体替换 Spark 成立。** 它只剩一条路：重新划分谁跑什么，而不是换掉谁 |
| Trino 451 要求 Java 22，而 Java 22 不是 LTS | [ADR 0004](../adr/0004-language-and-runtime-boundaries.md) 2026-09-12 修订 | **默认栈里最重的组件带上了一项此前没记的长期代价**，这项代价不出现在任何性能数字里 |

**净效果：没有一个组合是被资源或成熟度当场判定的。** 三条判定合起来不指向任何一个赢家，
只是把此前的捷径全部堵死。**因此全部组合必须按 §4 的五条轴并排评估，谁都不带先手。**

**这一点要写死：默认栈的优势曾经是"资源塞得下且大家都这么用"，前半句已被实测取消，
后半句按 §6 本来就不是证据。** 它现在与其他组合同一起跑线。

#### 2.7.2 组合清单

**每个组合必须能独立跑完 W1 至 W7，否则不是候选。** 下表的"谁跑"一列因此是完整分工，
不是偏好。

| 编号 | 组合 | W1/W3/W6 重写与维护 | W2 日增量 | W4/W5 查询 | 编排 | 流式与血缘 |
|---|---|---|---|---|---|---|
| K1 | 全量默认栈 | 常驻 Spark | 常驻 Spark | Trino | Airflow | Kafka 加 Flink，Marquez |
| K2 | 默认栈去掉窄用途常驻件 | 常驻 Spark | 常驻 Spark | Trino | Airflow | 有界文件回放代替流式；OpenLineage 事件直接落表 |
| K3 | 无 Trino 组合 | 常驻 Spark | 常驻 Spark | **DuckDB 挂同一 REST catalog** | Airflow | 同 K2 |
| K4 | 按需 Spark 组合 | **MBP 按需 Spark**，仅在回填、compaction 与重述时起 | 常驻 Spark | Trino | Airflow | 同 K2 |
| K5 | 极轻组合 | **MBP 按需 Spark** | **PyIceberg `upsert`** | DuckDB | cron 加脚本 | 同 K2 |
| K6 | 复用 UOIP 既有实例 | 该机已在跑的 Spark | 同左 | 该机已在跑的 Trino | 该机已在跑的 Airflow | 同 K2；catalog 仍独立 |

**六个组合共用的部分不再重复评估**：表格式一律 Iceberg（§2.1 已判定不重开）、
catalog 一律独立 REST（§2.4 与 §7.1.2 第 2 条）、对象存储候选与计算组合正交，
**单独按 multipart upload 行为评估，不参与本排序**。

**K5 是唯一一个没有常驻计算引擎的组合。** 它把 W2 交给 PyIceberg 的 `upsert`，
**这正是 §2.5 判定"跑不了 W3"的那个候选**——K5 之所以仍然成立，是因为 W3 被移到了按需
Spark 上。**§2.5 的结论否掉的是"用单机方案替代 Spark 承担全部写入负载"，不是 K5 这种分工。**
这条要说清，否则 K5 会被 §2.5 误杀。

**K6 不是"省事的那个"。** [平台架构](../platform-architecture.md) §4.3 已把复用列为需要
论证的取舍。它在本表里的位置与其他五个相同：**拿同一组轴测，不因为组件已经在跑就跳过**。
它真正的区别是**共享失败域**：UOIP 的一次重启会同时打断 CMOP 的作业，这在 §4 第 3 条轴上。

#### 2.7.3 测试次序按区分度排，不按熟悉度

**先测最早能证伪的，不是先测最可能赢的。** 一个组合被排在前面的理由只能是"它若失败，
会一次淘汰多个组合"。

| 次序 | 测什么 | 它能一次证伪什么 |
|---|---|---|
| 1 | **W2 与 W6 在 K5 上** | K5 若在按主键改写上失败，**K4 与 K5 的"按需 Spark"思路一起受影响**，因为两者共用同一个前提：重写负载可以离线成批地做 |
| 2 | **W4 在 K3 上** | DuckDB 若做不到秒级有界聚合，**K3 与 K5 同时出局**，Trino 的 Java 22 代价也就变成必须接受的代价而非可选项 |
| 3 | **W7 跨隧道写入** | 它与计算引擎无关，**任何一个组合过不了都是存储或网络问题**，先测可以避免把网络问题记到引擎账上 |
| 4 | **W1 与 W3 在 K1 上** | 默认栈的基线数字；**放在最后**，因为它不淘汰任何人，只提供对照 |

**次序 4 放在最后是本次重排最实质的改动。** 原先的隐含次序是"先把默认栈跑通，再看有没有
更轻的"，那等于让默认栈先占住"可行"这个位置，后来者必须证明自己更好。**改成最后测之后，
默认栈也要拿数字说话，且它的数字只当对照。**

#### 2.7.4 淘汰判据，二值

**每条判据必须能用一次运行判定，不接受"总体感觉更好"。**

1. **W2 在该组合上跑不完，或结果与 Spark 的 `MERGE INTO` 不一致** → 该组合出局，不进入后续轮次。
2. **W3 在该组合上没有可执行的 compaction 路径** → 出局，除非该组合已显式把 W3 划给按需 Spark（K4、K5）。
3. **W6 之后无法取到重述前后的可比较版本** → 出局。这是表格式承诺的核心能力，做不到就不必比性能。
4. **W4 中位延迟超过秒级** → 该组合的查询侧出局，但允许换查询引擎后重新入场。
5. **一次进程被杀后需要人工介入才能恢复到一致状态** → 出局，见 §4 第 3 条。
6. **常驻峰值合计超过 24 GB 的 80%** → 出局。**该阈值保留，但按 §7.1.2 已不再预期有人触发它**，
   它现在是护栏，不是筛子。

**允许出现"全部通过"的结果。** 此时按 §6 最后一条处理：按运维负担选，理由写进 ADR。
**也允许出现"全部不通过"**，那说明 §5 的负载定义或硬件前提有问题，届时回到工作负载基线，
不在本文里放宽判据。

#### 2.7.5 一个 ADR 覆盖一组绑死的决策，不是一个决策一篇

**§8 最后一条未决项在此定案。** 判据用 [ADR 索引](../adr/README.md) 的原话：
一篇 ADR 只回答一个**可以独立被推翻的问题**。据此分区：

| ADR 单元 | 覆盖 | 为什么绑在一起 |
|---|---|---|
| **计算分工** | 谁跑 W1/W3/W6、谁跑 W2、常驻还是按需 | 三者不能分开推翻：把 W2 挪给单机引擎就必须同时安排 W3 的维护方，见 §2.5 |
| **交互查询引擎** | Trino 还是 DuckDB 还是其他 | 回滚成本低（§3），只读 Gold，可以单独推翻 |
| **对象存储实现** | 四个候选加文件系统 | 与计算组合正交，判据只有 multipart upload 与失败恢复 |
| **Catalog 实现与后端** | REST 实现选型、后端存储、表清单的分离保存 | §2.6 已证明后端与重建手段是同一个问题的两面 |
| **编排与窄用途常驻件** | Airflow 还是 cron；流式与血缘是否常驻 | 回滚成本低，且它们一起构成"常驻多少个进程"这一个问题 |

**因此不是六个 ADR 对六个组合，也不是九个 ADR 对九行决策，而是五个 ADR 对五组绑死的问题。**
组合编号 K1 至 K6 只是评估用的载具，**不进入 ADR 标题**——一个组合赢了，写进 ADR 的是
它在这五个单元上的取值，不是"选 K3"。

**其中"计算分工"这一个单元现在就可以起草**，因为 §2.5 与 §2.6 已经给了它需要的全部证据，
**而它的结论不依赖任何一次性能测量**。见
[ADR 0005](../adr/0005-compute-engine-division-of-labour.md)。**其余四个单元等测量。**


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

**为什么拆成两级**：[roadmap](../roadmap.md) 的 Phase 0 原本写明 2026 年不搭建管道组件，
部署组件测 RSS 与之冲突，因此先做不触碰边界的纸面筛。纸面筛的结果反过来构成了放宽边界的
理由，边界已于 2026-09-09 为一次性 probe 有界放宽，**P-1b 现已解除阻塞**。

### 7.1 P-1a 纸面筛，已完成

只用各项目自己发布的内存口径做加法。目的不是得到准确数字，而是回答两个问题：默认组合是否
已经装不下，以及哪些候选可以在不部署的前提下就被排除。

| 组件 | 官方口径 | 计入 | 出处 |
|---|---|---|---|
| Trino | 部署文档起步值 `-Xmx16G`；Kubernetes 部署中 coordinator 与 worker 各自典型 8 GB | 8 GB | [Deploying Trino](https://trino.io/docs/current/installation/deployment.html)、[Trino on Kubernetes](https://trino.io/docs/current/installation/kubernetes.html) |
| Airflow | 至少 4 GB，建议 8 GB | 4 GB | [Running Airflow in Docker](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html) |
| Flink | 默认 `jobmanager.memory.process.size` 1600 MB、`taskmanager.memory.process.size` 1728 MB | 3.3 GB | [Set up JobManager Memory](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/memory/mem_setup_jobmanager/)、[Set up TaskManager Memory](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/memory/mem_setup_tm/) |
| Kafka | **不给固定值**，见下 | 见下 | [Hardware and OS](https://kafka.apache.org/43/operations/hardware-and-os/) |
| Superset、Marquez 及各自的 Postgres、Catalog 后端 | 未查到官方最小值 | 未计入 | — |

**已计入的四项合计约 15.3 GB。** §7.2 的阈值是 24 GB 的 80%，即 19.2 GB。**剩下不到 4 GB**
要装下 Superset、Marquez、两个 Postgres、catalog 后端和操作系统本身。装不下，而且这个结论
是在把每一项都取其官方口径下限、并把未查到的几项按零计入之后得出的。

#### Kafka 那一行：原判定过强，已按实测下调

原文写的是"把 Kafka 放进常驻集与它唯一明确的资源要求直接冲突，不需要实测"。**实测不支持这个
强度。** Kafka 在同一台机器上实际占用 936 MB，机器仍有 5.4 GB 的 buff/cache。

站得住的部分是：Kafka 文档确实不给固定堆大小，而是按写入吞吐乘 30 秒缓冲估算，并要求依赖
操作系统 page cache。**因此它的内存需求随吞吐增长，不是一个常数。** 这在本项目里影响有限，
因为 [平台架构](../platform-architecture.md) §7 已限定它只承载窄窗口演示，吞吐本来就低。

**结论从"淘汰"改为"随吞吐复核"。** 若将来 Kafka 的用途超出窄窗口演示，这条要重新评估。

#### 本节的结论已被 §7.1.2 的实测推翻，保留作为方法教训

纸面筛当时得出"默认组合已在纸面出局"。**实测证明这个结论是错的**，Trino 实际占用 2.68 GB
而非表中的 8 GB，差了三倍。

**错在把两类数字当成了一类。** 各项目文档给的是**按生产吞吐量的容量建议**，不是空载常驻
占用。用容量建议做加法去判断"装不装得下"，系统性地高估，而且高估幅度随组件而异，连相对
排序都不可信。

保留本节不是为了结论，是为了这条教训：**纸面筛可以用来发现风险，不能用来淘汰候选。** 它能
说"这里可能有问题，去测"，不能说"这个不行"。

### 7.1.1 只读盘点的结果：24 GB 那台机器不在手上

2026-09-09 对 SSH 配置中两台 Oracle 主机做了只读盘点。**两台都不是架构文档描述的那台。**

| 项 | 架构文档假设 | oracle-portal 实测 | oracle-db 实测 |
|---|---|---|---|
| 核数 | 4 | 2 | 2 |
| 内存总量 | 24 GB | 956 MB | 956 MB |
| 内存可用 | — | 381 MB | 473 MB |
| 根分区 | 200 GB | 97 GB，已用 12 GB | 97 GB，已用 16 GB |
| 现有负载 | 无 | minio、docker、nginx | minio、docker、x-ui、redis 等 |

**三条结论。**

**一、内存差了一个数量级。** 24 GB 与 956 MB 不是余量问题。§7.1 整节都在讨论如何把组件塞进
24 GB，而手上这两台连 §7.1 表里最小的一项都装不下。

**二、两台都不是空的。** 都跑着 MinIO、Docker 与 web 服务，其中一台还有 Redis 与其他常驻
进程。在其上部署一次性 probe 会挤占现有服务。

**三、块存储配额可能已经用完。** 两台各占 97 GB 根分区，合计 194 GB，与架构文档给 CMOP
规划的 200 GB 数量接近。若三者同属一个免费额度，则 CMOP 那台的存储配额已所剩无几。

**这不是评估问题，是前提问题。** 在确认 4 核 24 GB 的实例是否真实存在之前，P-1b 不能执行，
[平台架构](../platform-architecture.md) §4 与 §8 的全部容量推导也都悬空。

### 7.1.2 P-1b 实测结果：那台机器在跑，而且跑的正是这套栈

2026-09-09 连上 `oracle-super-node-4c24g` 后，P-1b **不需要部署即已完成**：CMOP 计划安装的
组件几乎全部已经在这台机器上运行，因此测到的是真实运行实例的常驻占用，不是实验室数字。

规格：4 核 aarch64、Ubuntu 24.04、内存 23974 MB、根分区 175 GB。**§7.1.1 记录的"该实例不
存在"随之作废**，它存在，只是不在 SSH 配置里。

| 组件 | 纸面口径 | 实测常驻 | 偏差 |
|---|---|---|---|
| Trino | 8 GB | 2.68 GB | 高估 3.0 倍 |
| Airflow，三个容器合计 | 4 GB | 1.55 GB | 高估 2.6 倍 |
| Flink，JM 加 TM | 3.3 GB | 1.53 GB | 高估 2.2 倍 |
| Kafka 加 ZooKeeper | 无口径 | 1.33 GB | — |
| Superset | 无口径 | 0.30 GB | — |
| Postgres | 无口径 | 0.20 GB | — |

**默认组合的实测合计约 7.6 GB，在 24 GB 里绰绰有余。** §7.1 的淘汰结论作废。

#### 但真正的约束换了位置，而且更紧

这台机器上跑着 26 个容器，是 UOIP 及若干个人服务的完整栈：Trino、Airflow、Spark、Hadoop
五件套、Flink、Kafka、ZooKeeper、Superset、Hive Metastore、Postgres、MongoDB、MySQL、
Grafana 等。

| 资源 | 总量 | 已用 | 可用 |
|---|---|---|---|
| 内存 | 23974 MB | 16112 MB | **7862 MB** |
| 根分区 | 175 GB | 143 GB | **32 GB** |

**以上是当日实测，不是可用上限。** 所有者 2026-09-09 说明：这些占用可回收——OCI 上没有
存储业务数据，清理可释放 100 GB 以上；内存可通过下掉未使用的容器、并把 ghostfolio 与
ToucanShelf 迁走腾出。**该回收量未经测量，是所有者依据自身部署给出的计划，条件是现有架构
不变。** 本文按计划记录，不按证据记录，实际回收结果应在部署前复测。

因此容量不作为阻塞项。**但它也不再构成任何结论的论据**：下一节原本据此推出"只能复用"，
该推论随之作废。

#### 由此得出的两条

1. **复用变成一个需要论证的取舍，不是被资源逼出来的结论。** 容量可回收后，另起一套栈重新
   可行，因此"是否复用 UOIP 既有实例"必须按利弊决定，见
   [平台架构](../platform-architecture.md) §4.3。实测唯一确立的事实是：那些组件确实在跑、
   版本可查，复用的对象是具体存在的，不是假设。
2. **Catalog 必须独立，这条不受容量影响。** §7 的"CMOP 使用独立 REST Catalog，不与 UOIP
   共用 Hive Metastore"成立理由是命名空间隔离，不是资源。那台机器上的 Hive Metastore 属于
   UOIP，共用会把两个项目的表搅在一起。

### 7.2 P-1b 原章程，保留备查

**范围已被 §7.1 大幅收窄。** 默认组合无需实测即已出局，因此 P-1b 不再遍历 §2.1 的全部候选。

- **输入**：仅测两类——文档不给数字的组件（Superset、Marquez、catalog 后端、Kafka），
  以及轻候选组合的整体占用。逐个部署，不一次性全上。
- **测量**：空载 RSS，以及在 §5 的 W4 负载下的峰值 RSS；每个数字附版本、配置、日期。
- **成功阈值**：一套完整组合的常驻峰值合计不超过 24 GB 的 80%，留出操作系统与突发余量。
- **停止条件**：单个组件空载即超过 6 GB 时停止该候选，不再测其性能。
- **产物**：写回本文 §7.1 的表与[平台架构](../platform-architecture.md) §8。
- **可丢弃**：部署产物一律视为一次性，不演变为 Phase 1 的部署基线。

## 8. 未决项

- ~~Catalog 后端存储能否从对象存储中的 metadata 文件重建。~~ **规范层面已答，见 §2.6**：
  路径存在，但缺表清单与最新版本判定。**重建耗时仍需实测**，且需先落地一份分离保存的表清单。
- 禁止 filesystem 与 Hadoop catalog 的配置门禁做成什么形式，见 §2.4。
  **§2.5 又加了一条同类门禁**：只要 DuckDB 参与写入，表属性必须显式设为 merge-on-read，
  两条门禁形式相同，宜合并为一份表属性与 catalog 配置的准入检查。
- ~~DuckDB 或 Polars 的 Iceberg 写入成熟度。~~ **已核实，见 §2.5。**
- 各 probe 的时间盒长度。
- W1 是否允许用缩小比例的数据代跑，以及缩放后结论的有效范围。
- ~~评估结果与 Proposed ADR 的对应关系：一个 ADR 对一个决策，还是一个 ADR 覆盖一组组合。~~
  **已定案，见 §2.7.5**：五个 ADR 对五组绑死的问题，组合编号不进入 ADR 标题。
  其中计算分工一篇已起草，其余四篇等测量。
- **K5 的 W2 路径未验证。** PyIceberg 的 `upsert` 在 200–360 MB 日增量上的正确性与耗时，
  是 §2.7.3 次序 1 要回答的问题，也是 K4 与 K5 共同的前提。
