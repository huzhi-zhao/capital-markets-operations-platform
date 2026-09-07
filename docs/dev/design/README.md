# Design Docs

一篇 design doc 记录一次非平凡变更**打算怎样实现**：问题、约束、方案、被否决的选项
和验收判据。它不是每项 requirement 的强制附件。

## 什么时候建立

满足以下任一条件时再写 design doc：

- 变更跨越多个组件、数据层或多个 PR。
- 包含迁移、回填、历史重述、schema 演进或复杂失败路径。
- 实现前需要评审边界、顺序、风险或验收方法。
- 仅靠 ADR 不能表达这一次落地方式。

局部实现、逐文件修改清单、任务进度和代码行讨论分别留在 PR、issue 与 code review。
当前 BO 和架构探索阶段预计很少产生 design doc。

## 与 ADR 的边界

ADR 决定“为什么长期选择 A”；design doc 说明“这次怎样把 A 做出来”。Design 中引用
相关 ADR，不复制完整选型论证。一个 ADR 可以指导多篇 design，多项需求也可以共享
一篇 design。

## 生命周期与命名

- `Draft`：评审中，可以修改。
- `Accepted`：实施基线已经确定，正文冻结；实际偏差记入对应 launch record。
- `Superseded` / `Abandoned`：保留历史，不删除。
- 文件名使用 `YYYY-MM-DD-kebab-case-topic.md`。

每篇至少包含 Problem、Constraints、Plan、Rejected options、Acceptance criteria 和
Open questions，并在顶部链接相关 requirement 与 ADR。

## 当前索引

目前没有 design doc。
