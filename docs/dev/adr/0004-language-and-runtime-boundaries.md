# ADR 0004: Language and Runtime Boundaries

> **Status**: Proposed · **Date**: 2026-09-07 · **Amended**: 2026-09-12
>
> **Related architecture**: [Platform architecture](../platform-architecture.md)
>
> **Readiness method**: [Project inception and readiness](../project-inception-and-readiness.md)

## Context

CMOP 是金融数据工程项目，但同时承担作品集目标：证明作者能在九年 Java 8 经验的基础上，
设计和交付现代企业级 Java 系统。项目也天然需要适合统计生成、数据探查、分布式处理、
关系型转换和基础设施配置的其他语言。若把全部任务强制交给 Java，会偏离各组件的原生
生态；若 Java 只出现在一个没有业务责任的演示接口中，又不能形成可信的现代化证据。

语言边界还会影响模块接口、序列化、构建和测试工具、容器运行时、依赖治理、人员认知
负担以及故障定位方式。一旦正式实现后再重划，改变成本高，符合 ADR 准入条件。

本 ADR 的问题是：**CMOP 依据什么原则在实现语言和运行时之间分配长期职责，以及何时
冻结这些边界？** Java、Python 和 SQL 是当前已知实例，不构成标题或未来范围的上限。
新增语言、DSL 或运行时可以在本文仍为 `Proposed` 时增量评估；本文不会为了提前容纳
未知技术而决定其用途。

主 BO、source inventory 和完整 workload envelope 尚未收敛，因此当前只能提出边界原则
和候选职责，不能接受最终组件映射、JDK 版本或代码模板。本文保持 `Proposed` 直到
Phase 0B 的兼容性与选型证据足以支持正式实现。

## Evidence snapshot, 2026-09-07

### Java release line

- Oracle 将 Java 8、11、17、21 和 25 列为 LTS。JDK 19 属于 18–20 非 LTS 发布线，已经
  被后续功能版本取代；截至本记录日期，JDK 25 是最新 LTS，JDK 21 是上一版 LTS：
  [Oracle Java SE Support Roadmap](https://www.oracle.com/europe/java/technologies/java-se-support-roadmap.html)。
- 当前 Spring Boot 4.1.1 至少要求 Java 17，并声明兼容至 Java 26：
  [Spring Boot system requirements](https://docs.spring.io/spring-boot/system-requirements.html)。
- 运行时兼容性不能只由 Java 应用框架决定。Flink 2.x 当前默认并推荐 Java 17，对 Java 21
  的支持仍列为 experimental；PySpark 当前也要求 Java 17 或更高：
  [Flink Java compatibility](https://nightlies.apache.org/flink/flink-docs-stable/docs/deployment/java_compatibility/)、
  [PySpark installation](https://spark.apache.org/docs/latest/api/python/getting_started/install.html)。

因此，“北美企业已经转向 JDK 19 来拥抱 AI”不是可用于本项目选型的准确表述。现代 Java
和 Java AI 集成是两个相关但不同的问题，企业运行时仍应从 LTS、组件兼容性、支持周期和
许可策略出发。

### Financial-sector signal

以下公开职位是当前市场信号，不是完整劳动力市场统计：

- Scotiabank 的加拿大 Java 职位要求或偏好 Java 17+、Spring Boot、REST、Kafka、测试、
  容器和 CI/CD；另有岗位同时列出 Java 8 与 17，显示遗留系统和现代化并存：
  [Java Developer](https://jobs.scotiabank.com/job/Toronto-Java-Developer-ON-M5H1B6/601957917/)、
  [Global Payments Technology](https://jobs.scotiabank.com/job/Toronto-Software-Engineer%2C-Global-Payments-Technology-%28Java-Developer%29-ON-M1L4S2/601753317/)。
- Citi 的加拿大 Markets Treasury 职位要求 Java 17+ 和 Spring Boot；另一个 Java 与 AI
  岗位仍以 Java/Spring Boot 后端为主体，再集成 Agent 和模型能力：
  [Markets Treasury Java Developer](https://jobs.citi.com/job/mississauga/apps-dev-programmer-analyst-officer/287/94522344704)、
  [Java and AI Development](https://jobs.citi.com/job/mississauga/senior-software-engineer-java-and-ai-development-vice-president/287/99451041920)。
- JPMorgan Chase 的工程招聘将 Java 和 Python 同时列为后端技能：
  [Experienced Software Engineer Hiring](https://careers.jpmorgan.com/us/en/students/programs/software-engineer-cohort)。

这些证据支持“现代 Java 对北美金融后端仍有直接求职价值”，但不支持把所有数据工程任务
统一改写为 Java，也不构成在 BO 之前增加 AI 功能的理由。

### Java and AI

Spring AI 和 LangChain4j 已为 Java 提供模型 API、tool calling、RAG 和向量存储等集成，
二者以 Java 17+ 为基础：
[Spring AI](https://github.com/spring-projects/spring-ai)、
[LangChain4j](https://docs.langchain4j.dev/get-started/)。

CMOP 的定位仍是金融数据工程而非 AI 量化研究。除非未来 BO 产生明确、可验收的 AI 用例，
AI 库不进入语言边界的决定或组件清单。现代 Java 的主要证明对象是领域建模、API、事件
处理、安全、可靠性、可观测性、测试和运行治理。

## Options considered

### A. Java-first single-language implementation

除 SQL 和组件配置外，生成器、批处理、API 与事件处理全部使用 Java。它能集中展示既有
经验并减少应用语言数量，但会牺牲 Python 的统计与数据工具生态，也可能把项目重心从数据
工程转向 Java 重写工作。

### B. Python and SQL data platform with a thin Java demonstration

生成、处理和编排使用 Python/SQL，只增加一个轻量 Java REST API。它符合许多数据工具的
原生生态，但 Java 若不拥有业务关键路径，会成为作品集装饰，无法证明企业级交付能力。

### C. Explicitly bounded polyglot implementation

根据业务责任和组件原生生态分配语言，让 Java 拥有至少一条真实关键路径，Python 处理
统计与数据工程胶水，SQL 表达关系型数据处理；其他语言按证据准入。

### D. Defer every language decision until coding starts

保持最大灵活性，但模块边界、接口和模板会在实现中偶然形成，容易出现重复工具链和局部
偏好主导架构，也无法在开工门禁前验证运行时兼容性。

## Proposed decision

采用方案 C，并接受以下原则；具体模块映射仍是候选，等待 BO 和 Phase 0B 证据。

### 1. Language admission and ownership

1. 每种实现语言必须拥有清晰、长期的责任边界。不能仅为了简历关键词或单个方便脚本引入
   一套新的生产运行时。
2. Java 必须拥有至少一个生产级、架构上有意义的业务关键职责，而不是只提供 health check
   或对其他组件的无逻辑包装。候选包括：
   - 交易或清算事件接入、校验、幂等和消息发布；
   - 对账异常、监管证据和有界下钻 API；
   - BO 确认需要实时语义时的 Java/Flink 处理。
3. Java 最终承担哪条路径由主 BO、访问模式和选定组件决定。不得为了满足本条要求创造
   不必要的微服务、broker、流处理层或 AI 功能。
4. Python 的候选职责是合成数据生成、统计分布调参、source profiling、数据探查、受限
   probe，以及 Python-native 编排和质量工具的扩展。进入生产的数据逻辑仍需版本化、测试
   和可观测，不能以“脚本”为理由降低工程标准。
5. SQL 是 Bronze/Silver/Gold 关系型转换、对账聚合、数据质量断言和查询的首选表达方式，
   前提是所需语义能够由目标引擎一致支持。Spark SQL 与 Trino SQL 的方言差异必须显式
   测试，不能假设可移植。
6. Spark transformation 优先使用 SQL/DataFrame API。driver 语言根据任务、库生态、类型
   价值和维护成本决定，不把 Java 或 Python UDF 作为默认实现。
7. Scala、TypeScript、Rust、Go 或其他语言默认不进入生产代码。只有当已确认的职责无法由
   现有语言合理承担，或目标组件的原生生态带来明确收益时，才在本文 `Proposed` 阶段加入
   评估；若本文已经 `Accepted`，则按 ADR 规则另写决定并 supersede 或扩展既有边界。
8. YAML、HCL、Shell 等配置和基础设施表达不自动视为新的应用运行时，但仍需限制用途、
   接受 lint/test，并避免承载复杂业务逻辑。

### 2. Java runtime policy

1. 正式 Java 模块只选择 LTS JDK，不以 JDK 19 或其他已被取代的非 LTS 版本作为基线。
2. 默认不依赖 preview feature。若未来存在不可替代的收益，必须单独记录兼容、升级和退出
   代价。
3. JDK 21 与 JDK 25 是当前候选，不在 BO 和组件边界确定前接受其中一个。选择至少依据：
   - Spring Boot、Spark、Flink、Iceberg、驱动和测试容器的支持矩阵；
   - macOS ARM64、NAS/OCI Linux 和容器基础镜像的一致性；
   - LTS 支持周期、OpenJDK distribution 与许可策略；
   - 依赖扫描、运行监控、构建工具和 CI 可用性；
   - 项目真正需要的语言特性，而不是版本号本身。
4. 不强求所有第三方数据组件运行在与自研 Java 服务相同的 JDK。若 Flink 等组件的推荐
   运行时落后于应用服务，可以用独立容器和兼容性矩阵隔离，但要衡量运维成本。
5. 现代 Java 能力优先通过稳定特性和完整工程链路展示，例如 records、sealed types、
   pattern matching、在合适的 I/O 工作负载中使用 virtual threads，以及 Spring Boot、
   OpenAPI、JUnit 5、Testcontainers、安全、metrics/tracing 和 CI/CD；不以堆叠语言特性
   代替业务价值。

### 3. Decision timing and templates

1. 当前只接受边界原则，不创建 Java service、Python job、Spark job 或 API 模板。
2. 主 BO baseline、代表性 BQ、主要 source class 和 workload envelope 成立后，补充候选
   组件到语言的映射。
3. Phase 0B 使用受限 probe 验证 JDK、框架、序列化、连接器和部署兼容性；实验代码默认
   丢弃。
4. 正式实现前再冻结精确 JDK、Python 版本、框架主版本、构建工具和模板最低能力。模板
   属于实现标准或 design；只有会改变本文长期边界的部分才回写 ADR。
5. 本 ADR 只有在上述映射与运行时证据足以指导第一条纵向链路时才能转为 `Accepted`。

## Amendment 2026-09-12: 两个数据引擎的实测运行时证据

**本修订只增加证据和一条风险，不改变第 2 节的任何原则。**
2026-09-07 的证据快照写的是 Flink 与 PySpark 的通用要求；本次补的是本项目**实际要用的
那两个引擎的具体版本**，出处见
[在共享主机上启用 Iceberg](../design/2026-09-12-shared-host-iceberg-enablement.md)
的"已核实的版本事实"。

| 引擎 | Java 要求 | 出处 |
|---|---|---|
| Spark 3.5.1 | 支持 Java **8 / 11 / 17**，明确支持 ARM64 | Spark 3.5.1 Overview |
| Trino 451 | 要求 Java **22，且只要 22**。Java 8、11、17、21 均不工作，Java 23 未测试 | Trino 451 Deploying |

[ADR 0003 的 2026-09-09 修订](0003-hybrid-deployment-topology-and-component-placement.md)
另已记录共享主机上的 Spark 实际跑在 **JDK 11** 上。

### 这对第 2 节第 4 条意味着什么

**第 4 条从"允许"变成"必需"。** 它原本写的是"不强求所有第三方数据组件运行在与自研 Java
服务相同的 JDK"，是一条许可。两个引擎的支持区间不相交——上限 17 对下限 22——
**所以现在不存在任何一个 JDK 能同时服务两端，分开运行不再是可选项。**

**这不推翻该条，也不推翻第 1 条。** 第 1 条约束的是正式 Java 模块，即自研代码，
JDK 21 与 25 仍是那一侧的候选。Trino 是第三方组件，不在第 1 条辖内。

### 补一条 Negative and risks 里缺的代价

**Trino 451 要求的 Java 22 不是 LTS。** 原文只写了"独立 JDK 运行时可能增加容器镜像和
漏洞修复工作"，那是把独立运行时当成一件多花力气的事。实际情况更硬：
**其中一个运行时可能根本没有 LTS 可选**，只能在非 LTS 上长期运行，
或者被迫跟随该组件的版本节奏升级。

两条可行的应对，**均未决定**：

1. **接受非 LTS，把该组件的升级节奏纳入运维计划。** 前提是它跑在容器里、
   不承载自研代码、故障面限于查询。
2. **换一个 Java 要求更宽的查询引擎版本或产品。** 代价是重做选型，
   且当前没有证据说明存在更优解。

**这个选择不必现在做。** 它属于[技术选型评估](../requirements/technology-selection-evaluation.md)
的候选重排序，而那一项本身还没做。此处只保证代价被记下来，
**不让它在实现阶段以意外的形式出现**。

### 对 Open questions 的影响

原有的"JDK 21 与 25 在最终 Spring Boot、Spark/Flink 和容器组合中的兼容性结果"仍然开放，
但**范围收窄了**：Spark 那一侧的上限已确认是 17，因此 21 与 25 的评估只对自研 Java 模块
和 Spring Boot 有意义，**不能顺带假设 Spark 也能跟上**。

## Consequences

### Positive

- Java 获得真实金融业务和运行责任，可以证明从 Java 8 到现代企业 Java 的迁移能力。
- Python、SQL 和组件原生接口仍能用于其最自然的工作负载，避免以作品集目标损害数据工程
  质量。
- 语言准入、JDK 和模板具有明确门禁，不会在 BO 未定时过早搭建脚手架。
- 不强制统一第三方组件 JDK，保留适配 Spark/Flink 实际支持矩阵的空间。
- 标题和问题范围不绑定当前三种语言，`Proposed` 阶段可以容纳后续发现。

### Negative and risks

- 多语言仓库增加依赖升级、CI、镜像、测试和本地环境维护成本。
- Java 关键职责尚未确定；若 BO 不需要 API、事件入口或实时处理，需要找到不造假需求的
  实质角色，或重新审视作品集约束。
- 独立 JDK 运行时可能增加容器镜像和漏洞修复工作。**且不止于工作量**：见 2026-09-12 修订，
  查询引擎那一侧可能根本没有 LTS 可选。
- Python 脚本容易绕过工程门禁，需要与生产 Java 模块采用同等清晰的输入输出契约。
- 过度强调 Java 可能把 CMOP 从数据工程项目变成微服务项目，必须由 ADR 0001 的项目边界
  持续约束。

## Open questions

- 主 BO 最终需要哪一种可独立部署的业务服务或事件边界。
- 是否需要持久 broker 和流处理；若不需要，Java 的关键路径是否以审计/对账 API 为主。
- Spark driver 使用 Python 还是 Java，以及是否存在值得使用 typed Dataset 的任务。
- JDK 21 与 25 在最终 Spring Boot 和容器组合中的兼容性结果。**Spark 那一侧已收口**：
  3.5.1 的上限是 17，见 2026-09-12 修订。
- 查询引擎停在非 LTS 上是否可接受，还是要为此重做该组件的选型。见 2026-09-12 修订。
- OpenJDK distribution、构建工具和依赖锁定策略。
- Python 环境、包管理和生产脚本门禁。
- 模块间数据契约采用 Avro、Protobuf、JSON Schema、OpenAPI 还是组合方案。
- 什么规模的前端或运维 UI 才足以引入 TypeScript 运行时。

