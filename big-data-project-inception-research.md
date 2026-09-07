# 大数据项目从 0 到 1：企业真的有一套标准流程吗？

讨论一个大数据平台时，人很容易从产品名单开始：对象存储选什么，Kafka 还是 Redpanda，
Spark 还是 Flink，要不要部署 Trino。组件都有名字、参数和 benchmark，看起来比“业务目标”
更具体，也更像工程工作。

但一个更基础的问题是：北美企业从零启动数据项目时，真的会按照“先业务、再数据、再
架构、最后选技术”的顺序工作吗？还是这只是咨询式话术，或者某几个架构师的个人经验？

对 NIST、TOGAF、AWS、Microsoft 和金融数据管理框架 DCAM 进行交叉比较后，结论可以
概括为一句话：

> 没有一份所有企业统一执行的“大数据项目 SDLC”，但存在一套相当稳定、跨框架重复
> 出现的共同骨架。

这套骨架不仅适用于湖仓、流处理和数据治理。在传统电商系统里，它同样可以用于订单、
库存、支付、推荐、履约和风控平台。

## 一、最强的厂商中立证据：NIST 从用例推导架构

NIST Big Data Interoperability Framework 并不是从 Hadoop、Spark 或某个云服务开始。
其工作组先收集了 51 个来自商业、政府、医疗、科研、能源等领域的大数据用例，再从用例
中提取通用需求，最后使用这些需求构造厂商和基础设施中立的参考架构。[NIST Volume 3][1]

NIST 的整套文档也体现了相同顺序：定义与分类、用例与通用需求、安全与隐私、参考架构、
标准路线和采用现代化。参考架构负责提供共同语言和组件模型，并不替项目决定具体产品。
[NIST Reference Architecture][2]

这说明至少在正式的大数据标准化工作中，“use case → requirement → architecture”不是
临时发明的表达方式，而是一条明确的方法链。

## 二、企业架构方法：TOGAF 把技术架构放在业务和数据之后

TOGAF 是企业架构方法，不是专门的大数据开发流程，但它提供了更完整的组织视角。
Architecture Development Method 从 Architecture Vision 开始，先确定范围、利益相关者、
业务要求与约束，随后形成业务架构、数据和应用架构，再进入技术架构、解决方案、迁移
计划和实施治理。[TOGAF][3]

这里最容易被误解的一点是：TOGAF 并不要求团队先写完一大摞文档再开始下一阶段。
它明确把架构开发描述为阶段内部和阶段之间都可迭代的过程，早期产物可以随着后续发现
继续修订。[TOGAF ADM][4]

因此，“业务先于技术”表达的是因果依赖，不等于一次性冻结，更不等于瀑布开发。

## 三、云厂商的共同警告：不要先做功能对比

AWS Data Analytics Lens 给出的数据发现顺序非常具体：

1. 定义业务价值；
2. 识别数据消费者；
3. 识别数据源；
4. 定义存储、Catalog、治理与访问需求；
5. 定义数据处理需求。

这些步骤会收集用户、时效、并发、数据格式、批流模式、摄取速率、容量、监管、灾难恢复
和转换频率等信息。[AWS Data Analytics Lens][5]

在流式架构指南中，AWS 更直接指出：先比较 Technical Feature A 和 Feature B、再确定
工作负载要求，是错误顺序。吞吐量、延迟、SLA、RPO/RTO、技能和安全要求明确后，技术
比较才有判据。[AWS Streaming Guidelines][6]

这条原则在电商里同样成立。若不知道库存更新允许延迟几秒、是否要求事件顺序、订单事件
能否重复、峰值流量是多少，“Kafka 还是其他 broker”就没有业务上的正确答案。

## 四、Microsoft：架构风格先于产品，PoC 是证据而不是生产代码

Microsoft Azure Architecture Center 要求从业务目标、功能需求和非功能需求出发，将工作
负载分解为用户流、数据流和系统活动；然后确定架构风格、数据模型和设计模式，最后再选择
compute、data store、messaging 等具体技术。[Azure Architecture Fundamentals][7]

这并不意味着所有技术决定都能靠文档完成。Microsoft 建议架构师使用 PoC 为设计规格提供
证据，验证真实实现是否可行；但同时强调 PoC 往往缺少完整安全、日志和错误处理，应该被
视为可丢弃实验，而不是直接复制进生产代码。[Azure PoC Guidance][8]

这里实际上存在两条不同的“开始写代码”边界：

- 架构 probe：为了关闭一个具体风险而写，范围小、限时、默认丢弃；
- 正式实现：按照已建立的需求、架构、测试和运维标准编写，需要长期维护。

把两者混在一起，容易出现“PoC 已经能跑，所以就在上面继续加功能”的路径依赖。

## 五、金融数据管理：business case 仍然在技术架构之前

EDM Association 的 DCAM 主要用于评估组织的数据管理能力，并非软件项目 SDLC。但它
对金融行业尤其有参考价值：数据战略和 business case、经营模型与资金属于基础能力，
之后才是业务与数据架构、数据与技术架构、数据质量、治理和控制。[DCAM][9]

EDM Association 的 2026 benchmark 覆盖 435 家以上、分布在 50 多个国家的组织，并指出
金融机构在多数 DCAM 能力上整体领先非金融机构。这不能证明每家北美公司使用同一流程，
但可以证明数据战略、治理、架构和可审计证据已经形成广泛的企业实践语言。[DCAM Benchmark][10]

## 六、把不同框架压缩成一套共同骨架

这些来源的目的并不相同：NIST 提供厂商中立参考模型，TOGAF 管理企业架构，AWS 和
Microsoft 指导工作负载设计，DCAM 衡量数据管理能力。正因为它们并非来自同一个体系，
重复出现的顺序才更值得注意。

将共同部分压缩后，可以得到以下流程：

| 阶段 | 需要回答的问题 | 典型产物 |
|---|---|---|
| 立项与边界 | 为什么做、谁负责、什么不做、如何衡量价值 | Vision、charter、scope |
| 业务用例 | 谁基于什么信息采取什么行动 | Business objective、use case、critical flow |
| 数据发现 | 数据从哪来、能否使用、质量和敏感性怎样 | Source inventory、classification、data contract |
| 工作负载刻画 | 有多大、多快、多晚，怎样访问和恢复 | Functional/NFR、workload envelope |
| 逻辑架构 | 数据如何流动，语义和职责如何划分 | Context、data flow、logical architecture |
| 方案评估 | 哪些候选满足需求，各有什么代价 | Evaluation matrix、risk register、Proposed ADR |
| 受限实验 | 哪些关键假设不能可靠地纸上判断 | Probe、benchmark、measured evidence |
| 开工就绪 | 团队是否知道要造什么以及怎样验收 | Accepted ADR、design specification、test strategy |
| 正式实现 | 最小纵向切片能否真正产生业务结果 | Production code、tests、operational evidence |

这个模型不是新的标准名称，而是对多个成熟框架共同部分的归纳。企业可以把它嵌入 Scrum、
Kanban、SAFe 或传统项目治理中，也可以在发现新事实时回到前一阶段。

## 七、BO 到底要“定”到什么程度？

技术评估开始前，业务目标不需要永久冻结，原始 schema 也不必精确到每一个字段。真正的
入口条件，是形成足以约束技术的业务与工作负载 baseline：

- 主业务目标、目标使用者和可观察的成功结果；
- 至少一个代表性查询、决策或关键业务流；
- 主要数据源类别、格式、批流模式和使用权边界；
- 容量、速度、freshness、访问模式、并发、保留和恢复目标；
- 安全、合规、预算、硬件、网络与团队技能约束。

如果这些内容尚不清楚，产品调查仍然有学习价值，却不具备闭环选型的条件。此时最诚实的
状态是 candidate 或 Proposed，而不是 Accepted。

## 八、开始正式编码前的最小检查表

一个数据平台不需要模仿大型企业的委员会和审批层级，但至少应能回答：

- [ ] 项目边界、目标用户和成功标准是否明确？
- [ ] 主用例是否能推导出至少一个可验收结果？
- [ ] 主要数据源、权利、敏感性和质量风险是否已知？
- [ ] 数据量、速度、时效、访问模式和恢复目标是否形成区间？
- [ ] 逻辑架构是否可以脱离具体产品解释？
- [ ] 技术候选是否按照需求和约束评价，而不是只比较功能表？
- [ ] 高风险决定是否有必要的 probe 或实测证据？
- [ ] ADR、验证策略和最小实施路线是否足以指导第一条纵向链路？

对于大数据项目，真正有价值的“企业级”并不是组件数量，而是每个重大决定都能追溯到
业务目标、数据事实、工作负载要求和验证证据。这种思想并不属于某个云时代：从传统电商
到现代湖仓，它一直成立。

## References

[1]: https://www.nist.gov/publications/nist-big-data-interoperability-framework-volume-3-use-cases-and-general-requirements-0
[2]: https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.1500-6r2.pdf
[3]: https://www.opengroup.org/togaf
[4]: https://www.opengroup.org/architecture/togaf7-doc/arch/p2/p2_intro.htm
[5]: https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/characteristics.html
[6]: https://docs.aws.amazon.com/wellarchitected/latest/analytics-lens/reference-architecture-2.html
[7]: https://learn.microsoft.com/en-us/azure/architecture/guide/
[8]: https://learn.microsoft.com/en-us/azure/well-architected/architect-role/collaboration
[9]: https://edmcouncil.org/frameworks/dcam/
[10]: https://edmcouncil.org/innovation/research/benchmarks/

