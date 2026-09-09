# Project Inception and Readiness

> **Status**: Draft · **Date**: 2026-09-07
>
> 本文定义 CMOP 从项目边界到正式实现的内部阶段方法、阶段门禁和当前就绪度。它不是
> 面向外部使用者的操作指南，也不替代具体 requirement、ADR 或 roadmap。

## 1. 为什么需要这份文档

CMOP 会经历较长的业务目标、监管规范、数据契约和架构探索期。项目暂停数周或数月后，
仅看架构图容易从组件继续讨论，却忘记组件选择依赖哪些尚未成立的业务和工作负载条件。

本文提供一个稳定的恢复入口，用来回答：

1. 从项目边界到正式编码应经过哪些阶段；
2. 当前在哪个阶段；
3. 哪些产物已经存在，哪些入口条件仍未满足；
4. 什么情况下可以开始产品比较、选型 probe 和正式实现。

具体事实仍由各规范文档维护。本文只链接事实源，不复制完整 BO、schema、容量数字或
架构决定。

## 2. 方法依据

北美企业没有一份名称和步骤完全统一的 “Big Data Project SDLC”，但多个独立体系形成了
稳定的共同顺序：先定义业务价值和用例，再发现数据与工作负载需求，然后形成逻辑架构、
比较技术并用受限实验关闭高风险假设，最后进入正式实现。

- NIST NBDIF 先收集大数据用例并提取通用需求，再用这些需求形成参考架构：
  [Use Cases and General Requirements](https://www.nist.gov/publications/nist-big-data-interoperability-framework-volume-3-use-cases-and-general-requirements-0)、
  [Reference Architecture](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1500-6r2.pdf)。
- TOGAF ADM 从 Architecture Vision、业务架构推进到数据、应用和技术架构，再进入方案、
  迁移与实施；整个过程允许跨阶段迭代：
  [TOGAF](https://www.opengroup.org/togaf)、
  [ADM introduction](https://www.opengroup.org/architecture/togaf7-doc/arch/p2/p2_intro.htm)。
- AWS Data Analytics Lens 将数据发现排列为业务价值、用户角色、数据源、存储与访问需求、
  处理需求，并明确要求先确定工作负载要求再比较技术：
  [Characteristics](https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/characteristics.html)、
  [Streaming application guidelines](https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/reference-architecture-2.html)。
- Microsoft 从业务目标及功能和非功能需求推导架构风格与技术选择，并把 PoC 定义为用于
  影响设计、但不得直接演变为生产代码的一次性实验：
  [Azure application architecture fundamentals](https://learn.microsoft.com/en-us/azure/architecture/guide/)、
  [Architect collaboration and PoCs](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/collaboration)。
- 金融数据管理领域的 DCAM 同样把数据战略与 business case 放在数据和技术架构、质量、
  治理与控制之前：[DCAM](https://edmcouncil.org/frameworks/dcam/)。

这些资料的适用范围不同：NIST 是厂商中立参考框架，TOGAF 是企业架构方法，AWS 和
Microsoft 是工作负载设计实践，DCAM 是数据管理能力框架。本文采用的是它们的共同交集，
不是宣称任何一套框架单独规定了 CMOP 的研发流程。

## 3. CMOP 的阶段模型

阶段表达依赖关系，不是不可回退的瀑布。后续证据可以修改前期 Draft 和 Proposed 产物，
但不得跳过上游约束直接接受产品选型。

| 阶段 | 关键问题 | 主要产物 | 退出条件 |
|---|---|---|---|
| 0A-1 项目边界 | 为什么做、服务谁、什么不做、如何判断成功 | 项目概览、系统上下文、主 BO 候选 | 范围、目标用户和成功方向能够约束后续讨论 |
| 0A-2 业务基线 | 谁基于什么信息采取什么行动 | 主 BO、支持性 BO、BQ、业务口径、成功指标 | 主 BO baseline 已形成，至少一个代表性 BQ 可验收 |
| 0A-3 数据发现 | 数据从哪来、能否使用、格式和质量怎样 | Source inventory、数据分类、监管与行业数据契约 | 主要 source class、到达模式、权利和敏感性已知 |
| 0A-4 工作负载刻画 | 数据有多大、多快、多晚，怎样读写和恢复 | Functional/NFR、workload envelope、验证策略 | 容量、时效、访问模式、保留、RPO/RTO 和约束足以制定评价标准 |
| 0A-5 逻辑架构 | 语义、数据流和职责怎样划分 | 逻辑分层、数据流、关键契约、Proposed ADR | 架构不依赖尚未证明的具体产品能力 |
| 0B-1 方案评估 | 哪些候选满足需求，各自代价是什么 | 评价矩阵、风险清单、Proposed ADR | 候选与评价标准能追溯到 BO 和 workload requirements |
| 0B-2 受限 probe | 哪些关键假设无法通过资料可靠判断 | 一次性实验、测量结果、结论或开放风险 | 高风险假设已有证据，结果写回 ADR 或需求 |
| 0B-3 开工就绪 | 实现团队是否知道要造什么、怎样验收 | Accepted ADR、架构规格、验证计划、实施 roadmap | 不存在会推翻最小纵向切片的未决问题 |
| 1 正式实现 | 最小端到端链路是否真正回答主 BO | 可维护代码、测试、可复现数据与运行证据 | 以 [roadmap](roadmap.md) 的 Phase 1 退出条件为准 |

下面这张图给出从 BO 到各类工程文档的落点关系，与[开发文档索引](README.md)的路由顺序一致：
[BO 到技术文档流程](../images/bo-to-technical-documentation-flow.drawio)（draw.io 源文件）。

## 4. BO baseline 的最小含义

技术评估不要求 BO 永久冻结，也不要求每个原始字段提前确定。进入组件比较前，至少需要：

- 一个主 BO、目标使用者和可观察的成功结果；
- 至少一个代表性 BQ 或关键业务流；
- 主要 source class、格式、批流到达方式和数据权利边界；
- 数据量、到达速度、freshness、访问模式、并发、保留和恢复目标的合理区间；
- 硬件、网络、预算、合规和维护能力约束。

在这些条件成立前，SeaweedFS、Garage、RustFS、Kafka、Redpanda、Flink、Spark 等内容
可以作为候选资料研究，但不能形成可接受的产品选择。

BO baseline 不是一次写成的。假设、取证、修正的循环，以及"全量回填必须在冻结之后"
这条次序约束，见 [BO 收敛循环](../images/bo-convergence-loop.drawio)（draw.io 源文件）。

## 5. 受限选型 probe 的边界

Probe 属于架构验证，不等于正式实现，也不自动放宽整个阶段的代码限制。每个 probe 必须：

1. 关联一个会影响架构决定的具体风险或假设；
2. 事先写明输入、代表性 workload、成功阈值和停止条件；
3. 限时、限资源，只实现回答该问题所需的最小范围；
4. 默认视为可丢弃代码，不从实验仓促扩建生产管道；
5. 保存环境、版本、数据规模、配置和关键测量值；
6. 将结论写回 requirement、容量基线或 Proposed ADR。

如果 2026 年继续维持完全不写代码的时间边界，0B 阶段可放在 2027 年初；在 probe 完成前，
依赖实测证据的产品 ADR 保持 `Proposed`。

## 6. 当前就绪度

当前处于 **Phase 0A：项目边界、业务基线与数据发现**。状态按本文链接的事实源判断。

| 能力 | 当前状态 | 事实源或缺口 |
|---|---|---|
| 文档边界与索引规则 | 已建立 | [开发文档索引](README.md) |
| 项目定位与系统范围 | Draft，主要边界已形成 | [项目概览](requirements/project-overview.md)、[ADR 0001](adr/0001-project-boundaries-and-system-context.md) |
| 主 BO 与代表性 BQ | Draft，已有暂定排序，baseline 未冻结 | [业务目标](requirements/business-objectives.md) §2.1 |
| 原始数据 source inventory | Draft | [原始数据源清单](requirements/raw-data-source-inventory.md)；证券主数据与公司行为的获取渠道未闭合 |
| 监管与行业数据契约 | 未建立 | 规划中的 `requirements/regulatory-data-contracts.md` |
| 合成数据契约 | 未建立 | 规划中的 `requirements/data-generation-specification.md` |
| 验证与对账规范 | 未建立 | 规划中的 `requirements/validation-and-reconciliation-specification.md` |
| 数据规模模型 | Draft，只有容量假设 | [容量基线](data-volume-baseline.md) 尚缺 velocity、freshness、访问模式、并发和 RPO/RTO |
| 逻辑数据分层 | Proposed | [ADR 0002](adr/0002-transaction-centric-lakehouse-layering.md) |
| 物理拓扑与组件落位 | Proposed，节点职责已细化 | [ADR 0003](adr/0003-hybrid-deployment-topology-and-component-placement.md)、[平台架构](platform-architecture.md) §4.1–4.2 |
| 语言与运行时边界 | Proposed，只有原则 | [ADR 0004](adr/0004-language-and-runtime-boundaries.md)；具体模块映射与 JDK 尚待 BO 和兼容性证据 |
| 完整技术选型评估 | 尚不具备执行入口 | 可先设计评估范围；执行依赖 BO baseline、source inventory 和 workload envelope |
| 选型 probe | 未开始 | 进入 Phase 0B 后按风险触发 |
| 正式实现 | 禁止进入 | 以 [roadmap](roadmap.md) 的 Phase 0 退出条件为准 |

## 7. 恢复工作时的顺序

中断后返回 CMOP，按以下顺序恢复上下文：

1. 阅读本页的“当前就绪度”，确认阶段是否已由后续提交更新；
2. 阅读 [roadmap](roadmap.md) 的当前阶段和退出条件；
3. 打开表中第一个未满足项的事实源，而不是从组件候选继续讨论；
4. 仅在 BO baseline、数据发现和 workload envelope 足以提供评价标准后，立项完整选型评估；
5. 通过 Proposed ADR 和受限 probe 保存选型过程，达到门禁后再接受决定并开始正式实现。

项目级近期任务维护在仓库根目录的 [TODO](../../TODO.md)。该文件可以频繁变化；本文只在
阶段模型、门禁、事实源或就绪判断发生变化时更新。
