# Documentation Images

This directory holds diagrams and other visual assets referenced by project
documentation.

- Use English kebab-case file names.
- Every image must be referenced by at least one Markdown document.
- Keep an editable source beside a rendered asset when the diagram is not
  reasonably maintainable in its rendered format.
- Update the source and rendered asset together.
- Do not store screenshots, drafts, or unused alternatives here.

## 当前资产

| 文件 | 内容 | 被引用于 |
|---|---|---|
| `bo-to-technical-documentation-flow.drawio` | BO、BQ、业务需求到 ADR/design/launch 的落点与反馈路径 | [项目立项与就绪度](../dev/project-inception-and-readiness.md) |
| `bo-convergence-loop.drawio` | BO 假设、取证、修正的收敛循环与冻结门禁 | [项目立项与就绪度](../dev/project-inception-and-readiness.md)、[业务目标](../dev/requirements/business-objectives.md) |

两个文件都是 draw.io 源文件，可用 diagrams.net 直接打开编辑。尚未导出渲染版本；
若后续在文档中需要内联展示，再按上面的规则同步导出 `.drawio.svg`。
