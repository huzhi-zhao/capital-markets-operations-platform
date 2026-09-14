# Requirements

本目录保存 CMOP **当前有效**的项目需求及其事实依据。它们是常青文档：业务目标、外部
规范或验收约束发生变化时原地更新，历史由 git 保存。

## 边界

这里回答“系统要解决什么问题、产出必须满足什么条件”，不回答某次代码变更怎样实现。

适合放在这里的内容包括：

- 项目 vision、系统边界、明确的 in-scope / out-of-scope。
- BO、BQ、成功指标与验收标准。
- FINTRAC、FIX、ISO 20022、CIRO 等公开规范推导出的数据契约。
- 合成数据必须满足的分布、业务不变量、脏数据类型与可复现要求。
- 对账、回溯、幂等性、迟到数据和数据质量的验收约束。
- 会随上游资料变化而更新、并直接支撑上述需求的研究证据。

**具体的技术选择**及其取舍进入 [ADR](../adr/README.md)；一次实现方案进入
[design](../design/README.md)。**评估要求本身**留在这里，因为它规定的是证据门槛而不是
选择结果，见[技术选型评估要求](technology-selection-evaluation.md)。详细的个人求职与就业市场调研不属于系统需求；
`project-overview.md` 只保留解释项目定位所需的简短结论。

## 规范文档与当前状态

原则是有实际内容时逐篇创建，不提前放空壳。最初规划的六篇已全部创建，之后按同一原则
逐篇增补：

| 文件 | 预期内容 |
|---|---|
| [project-overview.md](project-overview.md) | 项目定位、系统边界、目标用户、范围与成功定义；当前为 Draft |
| [problem-in-plain-language.md](problem-in-plain-language.md) | 用日常语言讲清楚这个项目替谁解决什么问题，供不熟悉资本市场后台的读者入门；不重复任何口径与数字 |
| [business-objectives.md](business-objectives.md) | BO/BQ、业务口径、优先级与验收标准；当前为 Draft |
| [raw-data-source-inventory.md](raw-data-source-inventory.md) | 原始数据源分类、获取方式、格式、到达方式、质量风险与敏感度；当前为 Draft |
| [regulatory-data-contracts.md](regulatory-data-contracts.md) | 公开监管与行业标准推导出的 schema、代码表和校验规则；当前为骨架 Draft |
| [data-generation-specification.md](data-generation-specification.md) | 合成事实数据的统计特征、业务不变量与脏数据契约；当前为 Draft，公司行为部分已由实测支撑 |
| [validation-and-reconciliation-specification.md](validation-and-reconciliation-specification.md) | 对账口径、可重跑验证、故障注入与验收门禁；当前为 Draft，阈值待实测 |
| [technology-selection-evaluation.md](technology-selection-evaluation.md) | 选型评估的范围、决策轴、代表性工作负载与证据要求；当前为 Draft，执行入口未开 |
| [prior-art-and-reference-implementations.md](prior-art-and-reference-implementations.md) | 同类开源项目盘点，方案评审前的对照清单；是事实依据而非选型结论 |

BO/BQ 使用稳定 ID 在文档内部管理，不机械地“一条 BQ 一篇文件”。只有内容拥有独立的
维护周期或已经大到影响阅读时才拆分。

## 当前索引

- [项目概览](project-overview.md)：项目定位、范围边界、目标数据规模与成功定义。
- [这个项目解决谁的什么问题](problem-in-plain-language.md)：面向非专业读者的大白话入口。
- [业务目标](business-objectives.md)：候选主 BO、支持性 BO、BQ 与验收方向。
- [原始数据源清单](raw-data-source-inventory.md)：合成、真实与推导三类数据源及其获取方式，含取证记录。
- [监管与行业数据契约](regulatory-data-contracts.md)：FIX、ISO 20022、FINTRAC 的最小子集与出处。
- [合成数据生成规范](data-generation-specification.md)：可复现性契约、标的维度、公司行为实测分布与脏数据契约。
- [验证与对账规范](validation-and-reconciliation-specification.md)：四对比对关系、时点基准、差异分类与门禁语义。
- [技术选型评估要求](technology-selection-evaluation.md)：评估范围、决策轴、代表性工作负载与证据要求。
- [同类开源项目盘点](prior-art-and-reference-implementations.md)：领域模型、报文库、对账实现与湖仓脚手架四类参考，含使用规矩。
