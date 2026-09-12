# 开发文档

本目录保存 CMOP 的需求、当前架构和长期有效的工程决策。正文以中文为主，文件名使用
English kebab-case。面向外部读者与操作者的当前使用方法放在
[../guide/](../guide/README.md)。

## 两种生命周期

写文档前先判断它描述的是**当前事实**，还是**一次历史事件**。

| 常青文档：描述当前有效状态，原地更新 | 事件文档：记录某次决策或事件，达到冻结条件后保留历史 |
|---|---|
| [roadmap.md](roadmap.md)：能力阶段与交付顺序 | [adr/](adr/README.md)：长期指导后续开发的决策 |
| [project-inception-and-readiness.md](project-inception-and-readiness.md)：从项目边界到正式实现的阶段方法、门禁与当前就绪度 | — |
| [platform-architecture.md](platform-architecture.md)：当前系统边界、数据流与部署拓扑 | [design/](design/README.md)：一次非平凡变更计划怎样实施 |
| [workload-baseline.md](workload-baseline.md)：容量、到达速率、新鲜度、访问模式、并发、保留与恢复目标 | [launch/](launch/README.md)：一次高风险变更实际上线的结果 |
| [requirements/](requirements/README.md)：当前需求、BO/BQ、数据契约与验收约束 | [postmortem/](postmortem/README.md)：已造成实际影响的事故复盘 |
| [collaboration.md](collaboration.md)：项目文档与私人笔记的边界、通道选择与内容路由规则 | — |

roadmap、project-inception-and-readiness、platform-architecture、workload-baseline
四篇当前均为草稿，`collaboration.md` 已生效。它们不套 `architecture/` 或 `planning/`
目录，因为每类当前都只有一个规范入口。

## 文档路由顺序

自上而下判断，第一个满足的条件就是落点：

1. 描述项目现在要解决什么、必须满足什么，或为需求提供持续更新的事实依据：
   `requirements/`。
2. 记录一个会长期约束后续开发、存在真实取舍且改变成本较高的决策：`adr/`。
3. 记录一次非平凡变更打算怎样实现：`design/`。
4. 记录一次高风险、跨环境或产生不可重建证据的变更实际上线情况：`launch/`。
5. 记录已经造成数据、结论、服务或合规影响的事故：`postmortem/`。
6. 描述当前可重复执行的安装、运行、回填或排障步骤：`../guide/`。
7. 都不满足：先不要写入仓库。若同类内容反复出现，再评估是否形成新的正面类别。

这些目录不是需求生命周期的强制流水线。一个需求可以产生多个 design，多项需求也可以
共享一次 launch；普通变更可能只需要 PR 和测试，不需要任何事件文档。

## 不进入开发文档的内容

| 内容 | 规范位置 |
|---|---|
| 本次修改了哪些文件、如何验证 | PR 描述 |
| 针对具体代码行的讨论 | Code review |
| 一次提交做了什么 | Commit message |
| 当前跨会话任务队列 | 仓库根 [TODO](../../TODO.md) |
| 更细的临时进度、排期、阻塞和催办 | 作者的私人笔记，见 [ToucanShelf 协作约定](collaboration.md) |
| 个人学习笔记、面试准备、求职语境 | 同上 |
| 可重复执行的当前操作步骤 | `guide/`，后续规模足够时可形成 runbooks |

`roadmap.md` 可以表达能力阶段和依赖顺序，但不承担每日任务状态。文档中的数字、结论和
失败归因必须留下最小可复核证据：测量日期、执行入口、环境或数据版本，以及必要的关键值。
不粘贴整段终端输出。

## 已评估但暂不建立的目录

下面这些目录在企业项目中都有合理用途，但 CMOP 目前没有足够内容支撑。它们不是禁用，
也不是“不知道放哪”的兜底目录；达到启用条件后再建立，并在本页登记边界。

| 候选目录 | 何时启用 | 当前默认去向 |
|---|---|---|
| `architecture/` | 出现至少数篇独立维护、生命周期不同的常青架构文档 | `platform-architecture.md`；取舍进入 ADR，单次方案进入 design |
| `research/` | 形成被多个需求或决策复用、拥有独立更新周期的证据库 | 需求依据进入 `requirements/`，选型证据进入对应 ADR |
| `runbooks/` | 安装、部署、回填、恢复等可执行操作形成稳定文档集合 | 先放 `guide/`；启用时优先建为 `guide/runbooks/` |
| `archive/` | 仅在一次明确的文档迁移中需要临时中转 | 过时内容由 git history 保存；事件文档使用 Superseded 状态 |
| `notes/` | 不会启用。个人笔记已有明确落点，见 [ToucanShelf 协作约定](collaboration.md) | 按上面的路由规则归类；个人学习笔记进私人笔记 |

判断不清时，先回来检查这张表和路由顺序。真正出现新的稳定文档性质时再扩展体系，
不要为了安置单篇材料创建目录。
