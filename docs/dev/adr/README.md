# Architecture Decision Records

ADR 记录会长期指导 CMOP 后续开发的决策：**背景、候选方案、决定、后果**。
它保存的是为什么这样选，不是具体实现步骤。

## 准入边界

满足以下至少一项，并且确实存在有意义的替代方案时，才建立 ADR：

- 改变系统边界、核心数据流、组件职责或部署拓扑。
- 建立跨模块、跨阶段都必须遵守的数据契约、业务语义或工程约束。
- 影响安全、可靠性、可追溯性、性能、成本等关键质量属性。
- 一旦开始实施就代价较高、难以撤销，后续开发必须在其基础上继续。
- 推翻或取代一项已接受的长期决策。

局部且容易撤销的实现选择、依赖版本、普通重构、单次实验结果和纯资料摘录不写 ADR。
BO/BQ 本身属于 [requirements](../requirements/README.md)；只有项目边界或业务语义已经
成为后续架构必须遵守的稳定约束时，相关决定才进入 ADR。

一篇 ADR 只回答一个**可以独立被推翻的问题**。判据不是篇幅，而是：如果未来只改变
其中一部分、其余部分仍成立，那么这些部分应当拆成不同 ADR。

## 当前阶段与状态生命周期

CMOP 在相当长一段时间内会以 BO、选型和架构讨论为主。ADR 正是这些讨论的工作载体，
但“讨论稿”和“历史决定”必须通过状态区分：

| 状态 | 是否可修改 | 含义 |
|---|---|---|
| `Proposed` | **可以反复修改** | 正在收集证据和讨论；可以重写背景、候选方案、决定草案和后果 |
| `Accepted` | 正文冻结 | 决策已经成为后续开发约束；改变结论必须写新 ADR 并 supersede 旧 ADR |
| `Rejected` | 冻结 | 方案经过讨论但未采用，保留理由以免重复争论 |
| `Superseded by NNNN` | 冻结 | 已被后续 ADR 取代，旧文仍保留历史上下文 |

因此，当前阶段的 ADR 默认保持 `Proposed`，允许随着 BO、实测证据和架构方案反复修订。
只有决定已经足够稳定、后续工作可以依赖它时才标为 `Accepted`。冻结不排斥更正：数字或
引用错误可以追加带日期的更正，但不能悄悄改掉当时的决策与依据。

## 命名与必填字段

- 文件名：`NNNN-kebab-case-title.md`，编号四位连续递增。
- 顶部字段：`Status`、`Date`；接受后补充 `Deciders`，取代旧决策时补充 `Supersedes`。
- Proposed 阶段尽量保持编号稳定；标题变化导致重命名时，同步修复全部链接。
- 每篇至少包含：Context、Options considered、Decision、Consequences。
- 新增 ADR 时必须在本页索引登记。

## 首批决策

这四篇均为 `Proposed`，是当前讨论载体，不代表已经定案：

| ADR | 决策问题 | 状态 | 日期 |
|---|---|---|---|
| [0001](0001-project-boundaries-and-system-context.md) | CMOP 证明什么、处理什么业务事实、明确排除什么 | Proposed | 2026-09-02 |
| [0002](0002-transaction-centric-lakehouse-layering.md) | 为什么以交易流水为核心，以及 Bronze/Silver/Gold 各自承担什么契约 | Proposed | 2026-09-02 |
| [0003](0003-hybrid-deployment-topology-and-component-placement.md) | NAS、临时 Mac 算力与 OCI 节点如何分工，组件按什么原则落位 | Proposed | 2026-09-02 |
| [0004](0004-language-and-runtime-boundaries.md) | 实现语言和运行时按什么原则准入、分配职责并在何时冻结 | Proposed | 2026-09-07 |
| [0005](0005-compute-engine-division-of-labour.md) | 谁跑回填、compaction 与历史重述，谁跑日增量改写，以及维护责任归谁 | Proposed | 2026-09-12 |
| [0006](0006-fix-single-version-baseline.md) | CMOP 以哪一个 FIX 版本为准，是否允许混用，以及何时才可以引入第二个版本 | Proposed | 2026-09-12 |
| [0007](0007-external-interactive-scope-reads-gold-only.md) | 对外交互路径能读到哪一层，差异的解释链在什么时候算 | Proposed | 2026-09-12 |

0005 是第一篇由选型证据直接催生的 ADR，**它只固定不依赖性能测量的那部分结论**；
常驻还是按需、交互查询用什么，都留在
[技术选型评估](../requirements/technology-selection-evaluation.md) §2.7 等实测。

具体对象存储实现如果能够独立替换，就不强塞进 0003；当其兼容性、迁移成本或治理约束
使它成为独立且难撤销的决定时，再建立新的 ADR。

本表同时是当前 ADR 索引。新增 ADR 时按编号追加，不按主题另建编号序列。
