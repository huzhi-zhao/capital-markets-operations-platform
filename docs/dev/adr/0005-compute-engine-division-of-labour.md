# ADR 0005: Compute Engine Division of Labour

> **Status**: Proposed · **Date**: 2026-09-12
>
> **Related requirement**: [技术选型评估](../requirements/technology-selection-evaluation.md) §2.5、§2.6、§2.7
>
> **Related architecture**: [平台架构](../platform-architecture.md)、[工作负载基线](../workload-baseline.md)

## Context

CMOP 的写入负载分布极不均匀。[工作负载基线](../workload-baseline.md) §5 给出的首次回填是
800 GB 至 1.5 TB，日增量只有 200 至 360 MB，**两者相差三个数量级**。为一个一次性负载常驻
一整套分布式引擎，按该文 §5.8 "一个兼职的人"的运维口径衡量是亏的；反过来，把全部写入交给
单机引擎，则要先证明单机引擎撑得住按主键改写历史分区。

[技术选型评估](../requirements/technology-selection-evaluation.md) §2.2 因此要求把这件事当成
真实的开放选择，**并明确要求区分"Spark 被证据选中"与"Spark 被默认选中"**。该文 §2.5 已完成
核实，§2.7 已把候选重排为组合。本 ADR 回答其中"计算分工"这一个单元：

**谁跑回填、compaction 与历史重述，谁跑日增量改写，以及这些引擎是常驻还是按需。**

三件事绑在一起，不能分开推翻：把日增量挪给单机引擎，就必须同时安排谁来消化它留下的
delete 文件。只改一半会得到一张没人维护的表。

## Options considered

**一、全部交给常驻 Spark。** 一个引擎覆盖 W1 至 W7 的全部写入与维护，分工问题不存在。

**二、全部交给单机引擎。** DuckDB、Polars 或 PyIceberg 承担全部写入，不部署 Spark。

**三、按负载切分：重写与维护交给按需 Spark，日增量交给单机引擎。**
分布式算力只在回填、compaction 与重述时起来，平时不占常驻资源。

**四、按负载切分，但日增量也留给 Spark，Spark 常驻。**
切分只发生在"按需算力节点"与"常驻节点"之间，不发生在引擎之间。

## Decision

**选项二否决。选项一、三、四之间的取舍留给实测，但本 ADR 先固定三条约束，
三条都不依赖任何性能数字。**

### 决定一：单机引擎不得独占一批 Iceberg 表的写入责任

理由**不是写不进去，是写完之后维护不了**。核实结果见评估文 §2.5，逐项如下：

| 候选 | 追加 | 主键改写 | compaction | 快照过期 |
|---|---|---|---|---|
| Spark 加 Iceberg | 是 | `MERGE INTO` | `rewrite_data_files` | 有 |
| DuckDB | 是 | `MERGE INTO`，仅 merge-on-read | **无** | **无** |
| Polars | 仅 append 与 overwrite，且标为 unstable | **无** | **无** | **无** |
| PyIceberg | 是 | `upsert` | **无** | 仅快照过期 |

**W3 是这张表上唯一一条谁都躲不开的负载。** 没有 compaction 路径的引擎不能成为一批表的
唯一写入方，**因为 merge-on-read 的欠债只会累积，不会自己消失**。

### 决定二：单机引擎参与写入时，表属性必须显式为 merge-on-read，且维护责任归 Spark

**这两句是一件事的两半，缺一半就是决定一里那张没人维护的表。** 落地形式已成文，见
[写入路径准入检查](../design/2026-09-12-write-path-admission-checks.md)：
双写表的 `write.delete.mode`、`write.update.mode`、`write.merge.mode` 三项必须为
`merge-on-read`，且建表时必须填写维护周期，留空即失败。

**由 Spark 定期执行 `rewrite_position_delete_files` 与 `rewrite_data_files`** 消化 delete 文件。
**两个引擎共写一批表是可行的，但维护责任只能落在 Spark 这一侧。**

### 决定三：Spark 侧必须加载 Iceberg SQL extensions

共享主机上的 Spark 是 3.5.1。**Spark 3.x 上 Iceberg 的维护过程只有加载 SQL extensions 才可用**，
Spark 4.0 才原生支持。因此 `spark.sql.extensions` 必须包含 `IcebergSparkSessionExtensions`，
**它是必配项，不是可选项**——缺了它，决定二里那条维护路径根本调不出来。
同样已做成准入检查的 A4 条。

### 本 ADR 不决定的事

- **常驻还是按需**，即选项一、三、四之间的选择。它取决于 W2 在按需 Spark 上的启动开销
  与 PyIceberg `upsert` 的实测表现，属评估文 §2.7.3 次序 1。
- **交互查询用什么**。那是另一个可以独立被推翻的问题，见评估文 §2.7.5。
- **单机引擎在读侧与开发侧的用法**。W4、W5 是读负载，生成器的 Parquet 产出不经过 Iceberg，
  本地用 DuckDB 挂同一个 REST catalog 读生产表也不受本文约束。

## Consequences

### Positive

- **Spark 的地位由证据确立，不由惯例确立。** 这正是评估文 §2.2 要求写进 ADR 的区别：
  否掉单机方案的是 compaction 与快照过期两列全空，不是"大家都用 Spark"。
- **轻量组合没有被一并否掉。** 决定一否的是"单机引擎独占写入责任"，
  评估文 §2.7.2 的 K4 与 K5 把 W3 划给按需 Spark，因此仍然成立，**不被本文误杀**。
- **两条配置约束已有执行形式**，不依赖任何人记得，见决定二与决定三引的准入检查。

### Negative and risks

- **决定二引入了一个跨引擎的时间耦合。** delete 文件的累积速度取决于单机引擎的写入频率，
  而消化它的 Spark 作业按固定周期跑。**周期定得不对，表会在两次维护之间退化**，
  而退化表现为查询变慢，不是报错。维护周期的具体数值待实测，**建表时必须填，不得留空**。
- **决定三把一条 Spark 版本事实变成了长期约束。** Spark 升到 4.0 后 extensions 不再必需，
  届时准入检查的 A4 条会从"必须包含"退化为噪声。**这是可预见的过期，登记在此**，
  不提前处理。
- **按需 Spark 的路径还没有被任何一次运行证实。** K4 与 K5 都押在"重写负载可以离线成批地做"
  这一个前提上。**该前提若被次序 1 的实测推翻，选项三与四同时失效，只剩选项一**，
  本 ADR 届时要修订而不是补注。

### 对其他决策的影响

- [ADR 0003](0003-hybrid-deployment-topology-and-component-placement.md) 的节点分工不受影响：
  本文切的是引擎责任，不是节点责任。
- [ADR 0004](0004-language-and-runtime-boundaries.md) 的运行时边界不受影响：
  本文提到的引擎都是第三方组件，落在该文第 2 节第 4 条"不强求统一 JDK"的范围内。
