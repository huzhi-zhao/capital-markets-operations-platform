# 同类开源项目盘点

> **Status**: Draft · **Date**: 2026-09-14 · **检索日期**: 2026-09-14
>
> **用途**: 方案评审前的对照清单。它是可更新的事实依据，不是选型结论；具体技术选择及其
> 取舍仍然进入 [ADR](../adr/README.md)，评估门槛见[技术选型评估要求](technology-selection-evaluation.md)。

## 1. 总结论

**没有任何一个公开项目覆盖 CMOP 的全貌。** 现有项目分成四类各自成立的局部：行业领域
模型、报文读写库、玩具规模的对账实现、通用湖仓脚手架。把"交易生命周期 + 目标规模的
湖仓 + 逐笔差异归因 + 历史重述"串成一条的实现没有检索到。

这既是差异化，也是一条需要正视的反证：一件事没人做，有时是因为它没有价值。这里的判断
是价值存在但产物不会开源——每家机构后台都在做同一件事，而它们的实现是私有资产。该判断
是推理，不是证据，评审时可以质疑。

盘点它们的用途只有两个：**省掉重复工作**，以及**在评审时对照自己的设计是否漏了什么**。
不据此修改本仓库已有结论，除非对方提供了可复核的证据。

## 2. 行业领域模型与标准

优先级最高的一类：它们定义的是业务概念，而 CMOP 的 Silver 建模正需要一个外部参照。

| 项目 | 与 CMOP 的关系 | 可借鉴 | 不可借鉴 |
|---|---|---|---|
| FINOS Common Domain Model | 行业级交易生命周期标准模型，多家投行参与联合建模试点 | Silver 的事件粒度与状态划分可对照它的概念命名；能在文档中声明对应关系 | 它的完整覆盖面远超本项目范围，不整体引入 |
| [FINOS Legend](https://www.finos.org/press/goldman-sachs-open-sources-its-data-modeling-platform-through-finos) | 高盛 2020 年开源的数据建模与治理平台，五个模块进入 FINOS；有与 lakehouse 的集成实践 | 金融数据模型与治理的组织方式 | 平台本身过重，不进入本项目技术栈 |
| Morphir | 摩根士丹利开源，业务逻辑即代码 | 与"结论必须追溯到当时生效的规则版本"是同一问题域，见[业务目标](business-objectives.md) §2 | 同上 |

## 3. 报文读写

用于生成器与 Bronze 解析的对照，具体报文子集以
[监管与行业数据契约](regulatory-data-contracts.md)为准。

| 项目 | 说明 |
|---|---|
| [moov-io/iso20022](https://github.com/moov-io/iso20022) | Go 的 ISO 20022 读写与校验，带 HTTP API；Moov 生态还包含 ACH 与 Fedwire |
| [pain001](https://github.com/sebastienrousseau/pain001) | 从 CSV、SQLite、JSON 或 Parquet 生成 ISO 20022 支付报文，带 XSD 与 SEPA 校验，含 camt.053 解析。**与本项目生成器的现金腿职责重叠最多的一个**，值得精读其 schema 校验组织方式 |
| [yudaprama/iso20022](https://github.com/yudaprama/iso20022) | Go 的 ISO-20022 数据目录解析，覆盖证券交易与结算 |
| [da4089/simplefix](https://github.com/da4089/simplefix) | Python 的 FIX 编解码，不含 session 层，正好匹配批量生成场景 |
| [FIX Trading Community](https://fixtrading.org/sharing-fix-resources-in-github/) | 规范资源的权威出处 |

## 4. 对账实现

| 项目 | 说明 |
|---|---|
| [recon-engine](https://github.com/DanyaYen/recon-engine) | 支持 MT940 与 camt.053 的对账引擎，1:1 匹配 |
| [transaction-reconcile](https://github.com/lakshya-sr/transaction-reconcile) | **方法论最接近的一个**：多来源合成数据加主动注入噪声，包括费用、延迟结算、损坏的流水号、缺失单据、批量结算与拆分。与本项目的四类差异注入是同一思路，但规模是玩具级，且没有血缘与重述 |

`transaction-reconcile` 的价值在于它是一个现成的对照物：同样的想法在小数据上成立时是
什么样，可以用来说明本项目多出来的部分究竟是什么。

## 5. 湖仓工程脚手架

只借环境与配置，不借项目叙事。

| 项目 | 说明 |
|---|---|
| [thekaveh/data-eng-lab](https://github.com/thekaveh/data-eng-lab) | Iceberg、Spark、Trino、Airflow、Redpanda 加 Docker Compose 的分层实验环境。**与本项目候选技术栈高度重合**，可省去搭环境时间 |
| [exastore-medallion-project](https://github.com/John-Eke11/exastore-medallion-project) | Iceberg 加 Glue、S3 Tables、Athena，用到 snapshot 与 time travel |
| [medallion-architecture](https://github.com/topics/medallion-architecture)、[apache-iceberg](https://github.com/topics/apache-iceberg) | GitHub topic 入口，用于持续发现 |

**风险提示**：这一类中的绝大多数是"把管道跑通"的演示，数据量小、没有业务不变量、没有
重述也没有血缘。那正是[业务目标](business-objectives.md) §1 要求避免的退化形态。抄配置
可以，不要抄叙事。

## 6. 评审时怎么用这份清单

1. 先看第 2 节。领域模型是唯一一类可能改变本项目设计的参考，其余三类只影响实现成本。
2. 对照检查：本项目的设计里，有没有对方处理了而我们没想到的情况。有则作为待办录入，
   不直接改结论。
3. 反向检查：对方没做而我们做了的部分，能否说清楚为什么值得做。说不清的部分是范围膨胀。
4. 引用其中任何结论时，按仓库规矩给出可公开复核的来源，并记录检索日期。
