# 在共享主机上启用 Iceberg：Spark 运行时、独立 Trino Catalog 与运行版本取证

> **Status**: Draft · **Date**: 2026-09-12
>
> **关联需求**：[技术选型评估](../requirements/technology-selection-evaluation.md) §2.4、
> §2.5、§7.1.2
>
> **关联 ADR**：[ADR 0003 混合部署拓扑](../adr/0003-hybrid-deployment-topology-and-component-placement.md)、
> [ADR 0004 语言与运行时边界](../adr/0004-language-and-runtime-boundaries.md)
>
> **执行状态**：**未执行。** 本文是上线计划，不是上线记录。实际执行时按
> [Launch Records](../launch/README.md) 的准入条件另建 launch record，
> 文件名 `YYYY-MM-DD-shared-host-iceberg-enablement.md`。
>
> **排期**：**由用户择期统一执行，日期未定（登记于 2026-09-12）。**
> 本文是全项目所有"必须在真机上验证才能收口"事项的唯一集合点。
> 新出现的同类事项一律并入本文，**不单独安排、不拆散执行、不逐项催办**。

## Problem

Phase 0B-1 剩下的四项工作全部落在同一台机器上，而**这台机器不属于本项目独占**。

`oracle-super-node-4c24g` 是 4 核 aarch64、Ubuntu 24.04、23974 MB 内存、175 GB 根分区的
OCI 实例，上面跑着 26 个容器，是兄弟项目 UOIP 与若干个人服务的完整栈，
详见[技术选型评估](../requirements/technology-selection-evaluation.md) §7.1.2。

四项工作：

| 编号 | 工作 | 是否影响 UOIP |
|---|---|---|
| T1 | 把这台机器加进 SSH 配置，使其可按名字寻址 | 否，纯本地 |
| T2 | 按实际运行版本收集 JDK 与兼容性证据 | 否，只读 |
| T3 | 给共享 Spark 装 Iceberg 运行时，匹配 3.5.1 与 Scala 2.12 | **是，改镜像并重启** |
| T4 | 为本项目单开 Trino catalog，不改动指向 UOIP Hive Metastore 的现有 catalog | **是，需重启** |

**T3 与 T4 需要停机窗口，所有者当前没有时间。** 因此本文的作用是：
把这四项写成可以在一个窗口内照着做完的计划，**并把不需要这个窗口的部分识别出来先做掉**。

## Constraints

1. **不得破坏 UOIP。** 共享的是别人在用的容器，任何改动都要能在窗口内回滚。
2. **catalog 必须独立。** 理由是命名空间隔离而非资源，见技术选型评估 §7.1.2 结论二。
   **不共用 UOIP 的 Hive Metastore。**
3. **不得引入 filesystem 与 Hadoop catalog。** 见技术选型评估 §2.4 第二条后果，
   失败方式是并发下静默丢提交。
4. **窗口内只做一件性质的事。** T3 与 T4 都需要重启，但它们的失败面不同，
   分两个门禁而不是一次全推。
5. **本项目 2026 年不搭建管道组件**，见 [roadmap](../roadmap.md)。
   T3 与 T4 属于**为 probe 准备环境**，落在已放宽的边界内，不含生成器与管道本身。

## 已核实的版本事实

**以下取自各项目自己的文档，2026-09-12 核实，可直接作为计划输入。**

| 事实 | 出处 |
|---|---|
| Spark 3.5 在 Iceberg 的引擎生命周期里是 **Maintained**，最新支持版本 **1.11.0** | Iceberg Multi-Engine Support |
| Spark 3.5 + Scala 2.12 的运行时 jar 名为 **`iceberg-spark-runtime-3.5_2.12`** | 同上 |
| classpath 上**只能放 runtime jar**，`iceberg-core`、`iceberg-parquet` 等必须排除，否则版本冲突 | 同上 |
| **Spark 3.x 上 Iceberg 存储过程只有加载 SQL extensions 才存在**，Spark 4.0 才原生 | Iceberg Spark Procedures |
| Spark 3.5.1 支持 **Java 8/11/17**，且明确支持 **ARM64** | Spark 3.5.1 Overview |
| **Java 11 下必须设 `-Dio.netty.tryReflectionSetAccessible=true`**，否则 Arrow 走 Netty 时抛 `UnsupportedOperationException` | 同上 |
| **Trino 451 要求 Java 22，且只要 22**：Java 8、11、17、21 均不工作，Java 23 未测试 | Trino 451 Deploying |

### 由此提前得到一个证据：运行时分裂不只是被允许，而是被强制

**Spark 3.5.1 的上限是 Java 17，Trino 451 的下限是 Java 22。** 两个区间不相交。

**这不推翻任何已有决策。** [ADR 0004](../adr/0004-language-and-runtime-boundaries.md)
Java runtime policy 第 4 条已经写明"不强求所有第三方数据组件运行在与自研 Java 服务相同的
JDK"，Consequences 里也写了"不强制统一第三方组件 JDK"。
**该 ADR 从一开始就没有假设存在统一的平台 JDK。**

**新增的是把"允许"变成"必需"的实测级证据，以及一个此前没有记录的具体数字：**
Trino 451 要求的 Java 22 **不是 LTS**，而 ADR 0004 第 1 条要求正式 Java 模块只用 LTS。
两条并不冲突——第 1 条约束的是自研模块，Trino 是第三方组件——
**但这说明第三方组件那一侧可能被迫长期停在非 LTS 上**，
这个代价 ADR 0004 的 Negative and risks 里只写了"独立 JDK 运行时可能增加镜像与漏洞修复工作"，
没有写"其中一个运行时可能根本没有 LTS 可选"。

[ADR 0003 的 2026-09-09 修订](../adr/0003-hybrid-deployment-topology-and-component-placement.md)
已记录 Spark 侧是 JDK 11，并要求"兼容性证据必须针对这些具体版本收集"。
**本文补上的是 Trino 那一侧的同类证据。**

**这一条不需要停机窗口就能确定**，是本轮的意外收获。

## Plan

**五个阶段，前两个不需要窗口，后三个需要。每个阶段有独立的通过门禁。**

### Stage 0：窗口外，本地准备（T1）

| 步 | 动作 | 验证 |
|---|---|---|
| 0.1 | 在 `~/.ssh/config` 加 `oracle-super-node-4c24g` 的 Host 块 | `ssh -G` 解析出预期的 HostName 与 User |
| 0.2 | 免密登录连通性检查 | `ssh <host> true` 返回 0 |

**不碰远端任何状态。** 密钥由所有者自行装入 agent，本计划不涉及口令。

**门禁**：能按名字连上。连不上则后续全部阻塞。

### Stage 1：窗口外，只读取证（T2）

**全部只读，不改任何文件，不重启任何容器。** 目的是把"文档说什么"换成"这台机器上是什么"。

| 步 | 采集项 | 为什么要 |
|---|---|---|
| 1.1 | 各容器镜像标签与 digest | 版本证据的锚点，见技术选型评估 §6 |
| 1.2 | Spark 容器内 `java -version` 与 `spark-submit --version` | 确认 Spark 3.5.1、Scala 2.12、JDK 实际版本 |
| 1.3 | Spark 容器 classpath 上是否已有任何 iceberg jar | 确认"完全没有 Iceberg 支持"这个前提是否仍成立 |
| 1.4 | Trino 容器 `java -version` 与 Trino 版本 | 验证 Java 22 这条要求在实机上成立 |
| 1.5 | Trino 现有 catalog 目录清单与挂载方式 | 决定 Stage 3 是加文件还是改挂载 |
| 1.6 | Hive Metastore 的归属与连接串 | 确认不会误连 UOIP 的元数据 |
| 1.7 | 内存与磁盘复测 | §7.1.2 记的可回收量是计划不是测量，部署前必须复测 |
| 1.8 | 容器编排方式与配置文件位置 | 决定改动落在哪、怎么回滚 |

**门禁**：1.2 与 1.4 的实测版本与本文"已核实的版本事实"一致。
**若不一致，Stage 2 与 3 的 jar 版本与 Java 版本结论作废，需要重算再进窗口。**

### Stage 2：窗口内，第一个重启（T3，Spark）

**改动内容**：向 Spark 的 classpath 加入两样东西，其余不动。

1. `iceberg-spark-runtime-3.5_2.12` 的 **1.11.0** 版 jar。
2. `spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions`。

**若实测 JDK 为 11**，同时加 `-Dio.netty.tryReflectionSetAccessible=true`。

| 步 | 动作 | 回滚 |
|---|---|---|
| 2.1 | 备份现有 Spark 配置与 compose/编排定义 | 备份即回滚点 |
| 2.2 | 落 jar，**只落 runtime jar**，不落 `iceberg-core` 等 | 删除 jar |
| 2.3 | 加 `spark.sql.extensions` 与（按需）Netty 反射开关 | 还原配置文件 |
| 2.4 | 重启 Spark 容器 | 还原后再重启 |
| 2.5 | **UOIP 冒烟**：跑一个 UOIP 侧已有的 Spark 作业 | 失败即执行 2.1 的备份还原 |
| 2.6 | **CMOP 冒烟**：`spark-sql` 里 `SHOW FUNCTIONS` 能看到 Iceberg 过程 | — |

**门禁**：2.5 必须先过，2.6 才算数。**兄弟项目的作业跑不通，本项目的能力再全也要回滚。**

**观察窗口**：重启后 24 小时内 UOIP 的日常作业至少完整跑过一轮。

### Stage 3：窗口内，第二个重启（T4，Trino）

**改动内容**：新增一个 catalog properties 文件，**不触碰现有 catalog**。

- 连接器为 Iceberg 连接器，catalog 类型指向**本项目自己的 REST catalog**。
- **明确不使用 filesystem 与 Hadoop catalog**，见 Constraints 第 3 条。

| 步 | 动作 | 回滚 |
|---|---|---|
| 3.1 | 备份 Trino catalog 目录 | 备份即回滚点 |
| 3.2 | 新增 CMOP 的 catalog properties 文件 | 删除该文件 |
| 3.3 | 重启 Trino | 删文件后再重启 |
| 3.4 | **UOIP 冒烟**：现有 catalog 的表仍可查 | 失败即删文件还原 |
| 3.5 | **隔离性验证**：两个 catalog 互相看不到对方的表 | — |

**门禁**：3.4 先过，3.5 才算数。**3.5 是这一步存在的理由**，见 Constraints 第 2 条。

**前置依赖**：Stage 3 需要 REST catalog 服务已经在跑。
**该服务本身的部署不在本文范围内**，见 Open questions 第 1 条。

### Stage 4：窗口内收尾

| 步 | 动作 |
|---|---|
| 4.1 | 建 launch record，记实际步骤、偏差、实测数字与观察项 |
| 4.2 | 把 1.2 与 1.4 的实测版本回填进 ADR 0004 的证据快照 |
| 4.3 | 把内存与磁盘复测结果回填进技术选型评估 §7.1.2 |

## Rejected options

| 被否方案 | 理由 |
|---|---|
| 复用 UOIP 的 Hive Metastore | 会把两个项目的表搅在一起，隔离性是 catalog 独立的**唯一**理由，见 §7.1.2 结论二 |
| 另起一整套栈只服务 CMOP | 容量可回收后重新可行，但重活在笔记本上，OCI 引擎多数时间空闲，第二套部署赚不到东西，见 ADR 0003 修订 |
| T3 与 T4 合并成一次重启 | 两者失败面不同：Spark 的失败面是作业，Trino 的失败面是查询。合并会让回滚时分不清是哪一步引起的 |
| 用 filesystem 或 Hadoop catalog 图省事 | 规范例外条款正是这条，失败方式是并发下静默丢提交而非报错 |
| 升级 Spark 到 4.0 以获得原生存储过程 | 共享容器，升级影响 UOIP，代价远大于加载 SQL extensions |
| 为统一 JDK 而降级 Trino | Trino 451 明确不支持 21 及以下；降级换来的"统一"仍然不是 LTS |

## Acceptance criteria

**全部为二值判定，且 UOIP 侧的判据优先于 CMOP 侧。**

1. 该主机可按名字 SSH 连上。
2. 实测的 Spark、Scala、JDK 与 Trino 版本已记录，并与本文的版本事实核对过。
3. **UOIP 的 Spark 作业在改动后仍能跑通。**
4. **UOIP 的 Trino 查询在改动后仍能返回。**
5. Spark 侧可以调用 Iceberg 存储过程，`rewrite_data_files` 与 `expire_snapshots` 可解析。
6. Trino 侧 CMOP 的 catalog 可列出自己的 namespace。
7. **两个 catalog 互不可见。**
8. 任一步失败时，备份还原后系统回到改动前状态。

## Open questions

1. **REST catalog 服务本身部署在哪、用什么后端存储。** Stage 3 依赖它，但它是一个独立决策，
   回滚成本为中，见技术选型评估 §3 的表。**本文不替它做决定。**
2. **停机窗口多长。** 两次重启加冒烟，粗估一小时量级，但**未实测**，
   且取决于 UOIP 作业跑一轮要多久。
3. **窗口选在什么时候。** 取决于 UOIP 的批次节奏，所有者定。
4. **内存与磁盘的可回收量是否属实。** §7.1.2 明记那是计划不是测量，Stage 1.7 复测。
5. **Iceberg 1.11.0 在 aarch64 上是否有额外注意事项。** Spark 文档确认支持 ARM64，
   Iceberg 侧未见相关声明，视为无特殊要求，**若 Stage 2.6 出现异常再回来查**。

## 这个窗口阻塞了什么

**下面这些不是本次上线的内容，而是"必须等本次上线做完才能开始"的工作。**
把它们列在这里，是为了让窗口的价值可衡量：窗口本身不产出任何结论，
**它解锁的是下面这五项**。

**下表里不带文档名的小节号，一律指
[技术选型评估](../requirements/technology-selection-evaluation.md)。**

| 阻塞项 | 依赖本文的哪个阶段 | 为什么必须实机 |
|---|---|---|
| W1 至 W7 七个代表性负载 | Stage 2、Stage 3 | [技术选型评估](../requirements/technology-selection-evaluation.md) §6 要求必须在本项目硬件上测，厂商基准不作证据 |
| multipart upload 兼容性 | Stage 2 | Iceberg 的 AWS 文档不讨论任何第三方兼容实现，拿不到背书，只能自己测，见 §2.4 |
| catalog 后端重建演练与计时 | Stage 3，且需 REST catalog 已部署 | 重建路径已在规范层面确认存在，但"最新 metadata.json 如何判定"必须实测，见 §2.6 |
| delete 文件清理节奏 | Stage 2 | DuckDB 只产 delete 文件不能消化，Spark 侧 `rewrite_position_delete_files` 的跑法与频率要按实际堆积速度定，见 §2.5 |
| 内存与磁盘可回收量复测 | Stage 1.7 | §7.1.2 明记那是所有者的计划不是测量 |
| 参考数据在主机侧的落位与访问路径 | Stage 2 | 产物目前只在开发机工作区，Spark 侧要读到它，而那一侧的 Iceberg 运行时还没装，见 [SEC 抽取 launch record](../launch/2026-09-09-sec-reference-extraction.md) |
| 主机侧抽取脚本的速率与联系邮箱配置 | Stage 2 | 若将来在主机上重跑抽取，这两项必须先在那一侧确认，否则会以项目名义违反证监会公平访问政策 |

**一条推论：窗口迟一天，Phase 0B-2 就迟一天。** 前五项全部属于 0B-2 的实测环节，
没有一项能用读资料替代。后两项不属于 0B-2，但同样只能在主机上收口，
**所以一并等这个窗口，而不是另开一次接触主机的动作**。

## 不卡在本窗口的待办

**这是一份快照，不是任务队列。** 任务队列是仓库根的 [TODO](../../../TODO.md)，
两处不一致时以 TODO 为准。列在这里只为回答一个问题：
**没有窗口的时候，还能往前推什么。**

按价值排：

1. ~~把两侧的具体 JDK 证据补进 ADR 0004。~~ **已完成，见该 ADR 的
   [2026-09-12 修订](../adr/0004-language-and-runtime-boundaries.md)。**
   它没有改动任何原则，只把"允许分别固定 JDK"变成"被迫分别固定"，
   并补上原文缺的那条代价：**第三方组件那一侧可能没有 LTS 可选**。
2. ~~写表属性与 catalog 的准入检查。~~ **计划已成文，见
   [写入路径准入检查](2026-09-12-write-path-admission-checks.md)，实现未做。**
   前两层不依赖本窗口，**第三层的在线巡检依赖 catalog 存在，因此绑在本窗口上**。
3. ~~写结算段的业务校验层。~~ **已完成，见
   [验证与对账规范](../requirements/validation-and-reconciliation-specification.md) §2A。**
   **资金段的同一层还没写**，且不能假定可以照搬，那一侧的必填字段更少。
4. ~~定批量支付报文的 Bronze 落地方案。~~ **已完成，见
   [批量支付报文的 Bronze 落地](2026-09-12-bronze-landing-for-batch-payment-messages.md)。**
   结论比原先设想的多三张表，**因为重复结构不止一层**。
5. ~~确认层断言进验证与对账规范。~~ **已完成，见该文
   [§2B](../requirements/validation-and-reconciliation-specification.md)。**
   范围扩到整个分配与确认段，每条断言同时带适用条件与失效场景。
6. ~~读两个资金消息集的 MDR，以及结算 MDR 的 Part 2 与 Part 3。~~ **已完成，见
   [监管与行业数据契约](../requirements/regulatory-data-contracts.md) §4C。**
   收获在 Part 2 的具名约束：**两条此前记为 CMOP 的校验改判为规范要求**，
   S-2 的时点判定多了一处独立出处，P1-8 的适用条件被收窄。
7. ~~候选重排序，让轻量组合与重量组合并排评估，默认栈不再是假定起点。~~ **已完成，见
   [技术选型评估](../requirements/technology-selection-evaluation.md) §2.7。** 候选改按组合
   组织，共六个；**默认栈改为最后测且只作对照**；测试次序按区分度排；ADR 分区同时定案，
   其中计算分工一篇已起草为 [ADR 0005](../adr/0005-compute-engine-division-of-labour.md)。

**第 1、2 两项与本文关系最近**：它们的证据就是写本文时取得的，
**且都属于"现在不写下来，进窗口时就会忘"的那一类**。
