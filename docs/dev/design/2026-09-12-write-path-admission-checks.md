# 写入路径准入检查：catalog 类型与表属性

> **Status**: Draft · **Date**: 2026-09-12
>
> **关联需求**：[技术选型评估](../requirements/technology-selection-evaluation.md) §2.4 后果二、
> §2.5 跨引擎陷阱与结论段
>
> **关联 ADR**：[ADR 0002 事务中心的湖仓分层](../adr/0002-transaction-centric-lakehouse-layering.md)、
> [ADR 0003 混合部署拓扑](../adr/0003-hybrid-deployment-topology-and-component-placement.md)、
> [ADR 0005 计算引擎分工](../adr/0005-compute-engine-division-of-labour.md)
>
> **执行状态**：**第一层与第二层已于 2026-09-13 实现**，见
> [`tools/admission-check/`](../../../tools/admission-check/README.md)。验收第 1 至 7 条有对应测试，
> 第 8 条（第三层）仍等 catalog。

## Problem

有两条配置约束已经由规范核实定案，但**目前只存在于评估文档的正文里，没有任何机制保证它们成立**。

**2026-09-12 补：其中两条已由 [ADR 0005](../adr/0005-compute-engine-division-of-labour.md)
升格为决策。** 该 ADR 的决定二与决定三分别对应本文的 merge-on-read 表属性与
`spark.sql.extensions` 两项，**本文因此从"把评估结论做成门禁"变成"把 ADR 决定做成门禁"**，
检查内容一条未改。

| 约束 | 出处 | 违反后的表现 |
|---|---|---|
| 不得使用 filesystem 或 Hadoop catalog | §2.4 后果二 | **并发下静默丢提交，不报错** |
| DuckDB 会写的表必须显式设 merge-on-read | §2.5 跨引擎陷阱 | DuckDB 的 `UPDATE` 直接失败 |

**这两条的共同点决定了它们必须做成检查而不是文档条目：**

1. **发作的地方离犯错的地方很远。** 配错的是建表或建 catalog 的那一刻，
   出事的是几周后某次并发提交或某次 DuckDB 写入。
2. **一条根本不报错。** filesystem catalog 在单写入方下工作正常，
   **它只在并发时丢数据，而丢掉的提交不会留下痕迹**。
3. **默认值站在错误的一边。** Iceberg 的 `write.delete.mode` 与 `write.update.mode`
   **默认是 copy-on-write**。什么都不写，得到的就是 DuckDB 写不了的表。

**问题：用什么机制、在什么时点、以什么代价，保证这两条在每一张表和每一个作业上都成立？**

## Constraints

1. **检查不能依赖记忆，也不能只在 code review 里存在。** 这是本文存在的全部理由。
2. **不能误伤兄弟项目。** 共享主机上 UOIP 的现有 Trino catalog 用的是
   `iceberg.catalog.type=hive_metastore`，见 [ADR 0003 的 2026-09-09 修订](../adr/0003-hybrid-deployment-topology-and-component-placement.md)。
   **该配置合法且不归本项目管。检查的作用域必须限定在 CMOP 自己的 catalog 与表上。**
3. **"哪些表 DuckDB 会写"无法推断，只能声明。** 引擎不会预告自己将来写什么。
   因此必须有一份显式的双写表清单，**清单本身也要被检查**。
4. **检查要能在没有 catalog 服务的情况下跑一部分。** REST catalog 尚未部署，
   见[共享主机启用计划](2026-09-12-shared-host-iceberg-enablement.md) Open questions 第 1 条。
   **完全依赖在线查询的检查在窗口之前一天都跑不了。**
5. **失败必须是硬失败。** 警告会被忽略，而这两条的代价是静默丢数据。

## Plan

**分三层，覆盖三个不同的时点。前两层现在就能实现，第三层要等 catalog 存在。**

### 第一层：静态配置检查，进 CI

**输入是仓库里的配置文件，不连接任何服务。**

| 编号 | 规则 | 判定方式 |
|---|---|---|
| A1 | CMOP 的 Spark catalog 配置里，`spark.sql.catalog.<name>.type` 只能是 `rest` | 键值匹配 |
| A2 | 同上，出现 `hadoop`、`hive`，或 `catalog-impl` 指向 `HadoopCatalog`、`HadoopTables` 的，一律失败 | 键值匹配 |
| A3 | CMOP 的 Trino catalog properties 里，`iceberg.catalog.type` 只能是 `rest` | 键值匹配 |
| A4 | 已加载 Iceberg SQL extensions，即 `spark.sql.extensions` 含 `IcebergSparkSessionExtensions` | 键值匹配 |
| A5 | 双写表清单文件存在、可解析，且其中每一项都能对应到一份建表定义 | 交叉引用 |

**A4 不是本文的两条约束之一，但同属"配置错了很晚才发作"的同一类**：
Spark 3.x 上没有它，所有 Iceberg 存储过程都不存在，
见[技术选型评估](../requirements/technology-selection-evaluation.md) §2.5 末尾。
**W3 会在跑不动的时候才暴露这个问题。**

**作用域的判定：只检查路径落在本项目配置目录下的文件。** 兄弟项目的配置不在仓库里，
天然不会被扫到，但规则仍要写明作用域，防止将来有人把主机上的配置复制进来做参考。

### 第二层：建表时的属性断言，进建表代码路径

**每一张属于双写清单的表，建表语句必须显式带上三个属性。**

| 属性 | 必须取值 | 为什么 |
|---|---|---|
| `write.delete.mode` | `merge-on-read` | 默认 copy-on-write，DuckDB 的 `DELETE` 会失败 |
| `write.update.mode` | `merge-on-read` | 同上，`UPDATE` 会失败 |
| `write.merge.mode` | `merge-on-read` | `MERGE INTO` 走的是这一条 |

**三条一起设，不能只设其中一条。** DuckDB 的限制是按操作分别检查的，
漏设任何一个，对应的那一类语句就在运行时失败。

**不在双写清单上的表不受此约束**，它们可以留在 copy-on-write 默认值上，
**那对只由 Spark 写的表是更好的选择**：不产生 delete 文件，也就不需要消化。

**一条连带责任必须同时登记。** 凡设成 merge-on-read 的表，
**Spark 侧必须有对应的 `rewrite_position_delete_files` 与 `rewrite_data_files` 排期**，
见 §2.5 结论段。**没有排期的 merge-on-read 表 = 无限堆积的 delete 文件。**
因此双写清单的每一项都要带一个维护排期字段，**留空即检查失败**。

### 第三层：在线巡检，等 catalog 存在后再实现

**输入是 catalog 里的实际表属性，与清单比对。** 它覆盖前两层覆盖不到的那种情况：
表是被别的途径建出来的，或者属性事后被改过。

| 编号 | 规则 |
|---|---|
| B1 | 清单上的每一张表，在 catalog 里实际的三个 mode 属性都是 merge-on-read |
| B2 | catalog 里存在但不在清单上的表，其属性可以是默认值，**但要报告出来供人确认** |
| B3 | 清单上的每一张表，最近一次 delete 文件重写的时间在排期允许的范围内 |

**B3 依赖能读到快照与文件统计，因此它同时也是 delete 文件堆积速度的观测手段**，
而那正是[共享主机启用计划](2026-09-12-shared-host-iceberg-enablement.md)里被窗口阻塞的一项。
**第三层与那个窗口绑定，前两层不绑定。**

### 分区表的一条已知残缺，不做检查只做记录

DuckDB 在分区表上**忽略 `write.target-file-size-bytes` 与
`write.parquet.row-group-size-bytes` 并报错**，见 §2.5 的限制表。
**这意味着分区表上唯一的表级文件大小控制手段对 DuckDB 无效。**

**这条不做成检查**，因为没有可判定的正确值可断言。它的后果是小文件治理只能靠
Spark 侧的 compaction 兜底，**这一点已经包含在第二层的维护排期要求里**。

## Rejected options

| 被否方案 | 理由 |
|---|---|
| 只写进文档，靠 review 把关 | 这正是当前状态。两条约束的失败方式都是延迟且静默的，review catch 不住配置默认值 |
| 只做在线巡检，不做静态检查 | catalog 还不存在，且巡检发现问题时表已经建好、数据已经写进去 |
| 只做静态检查，不做在线巡检 | 静态检查看不到运行时实际拼出来的配置，也看不到事后被改的属性 |
| 所有表统一设成 merge-on-read，取消清单 | 会给只由 Spark 写的表凭空引入 delete 文件与维护负担，**用正确性换取省事，代价方向错了** |
| 用警告代替失败 | 见 Constraints 第 5 条 |
| 等实现阶段再说 | 建表定义一旦写出来就会被复制，**错误的默认值传播得比修正快** |

## Acceptance criteria

**全部二值。**

1. 双写表清单文件存在，格式固定，每项带表名与维护排期。
2. A1 至 A5 五条静态规则实现，在 CI 中运行，任一条失败则构建失败。
3. 故意构造一份 filesystem catalog 配置，CI 失败。
4. 故意构造一张缺 `write.delete.mode` 的清单内表，CI 失败。
5. 故意构造一项排期留空的清单条目，CI 失败。
6. 不在清单上的表使用默认属性，CI 通过。
7. 兄弟项目风格的 `hive_metastore` 配置放在作用域外时，CI 通过。
8. B1 至 B3 三条在线规则有明确的实现计划与依赖声明，**实现本身可以等窗口**。

## Open questions

1. ~~**清单用什么格式，放在哪里。**~~ **2026-09-13 定案：独立文件 `config/iceberg/dual-write-tables.toml`。**
   选独立文件是为了一次检视全貌；"不同步"的风险由 A5 交叉引用兜住。
   **选 TOML 不选 YAML**：Python 3.11 起标准库可读，检查脚本因此零依赖。
2. **维护排期字段是写周期还是写触发条件。** 周期简单但与实际堆积速度无关，
   触发条件更准但需要第三层先跑起来。**实现按倾向先写周期**（字段名 `maintenance_period`，ISO 8601），
   目前只检查非空，不检查格式；等 B3 有数据后再改。
3. ~~**静态检查用什么实现。**~~ **2026-09-13 定案：Python 标准库脚本**，与
   [ADR 0004 的 2026-09-13 修订](../adr/0004-language-and-runtime-boundaries.md)一致。
   失败行格式为 `FAIL <规则> <位置>: <说明>`，**与数据质量框架对齐的事仍未做**，等那个框架选定。
   第二层的失败报告为 `L2`。
4. **第三层归谁调度。** 它是一项周期性作业，与 W3 的 compaction 排期天然相邻，
   **可能应该合并成同一个维护作业**。未决。
