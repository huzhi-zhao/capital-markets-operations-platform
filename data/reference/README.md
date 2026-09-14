# Reference Data

本目录保存**已钉住的真实公开数据**，它们为合成数据生成器提供锚点，并支撑开发文档中引用
的实测数字。这里不放合成数据，也不放 Bronze/Silver/Gold 的任何产物。

| 子目录 | 内容 | 来源 | 抽取工具 |
|---|---|---|---|
| `sec/` | 公司行为事件：拆股与合股、分红、退市、代码全集、更名 | 美国证监会结构化接口 | [tools/sec-extract](../../tools/sec-extract/README.md) |
| `iceberg/` | Iceberg 表清单：表名、位置、最近已知 metadata 文件，**catalog 后端丢失时的重建起点** | 本项目建表定义 | [tools/admission-check](../../tools/admission-check/README.md) |

## 规矩

- **`manifest.json` 是产物的凭证。** 它记录抽取日期、接口、时间窗口、逐季度条数与汇总
  统计。文档里引用的每个实测数字都应能在其中找到对应项。
- **原始响应钉住不动。** 上游数据会随补充申报而变化，重跑得不到同一批数字。需要新一轮
  抽取时另起一份带日期的 manifest，不覆盖旧的。
- **只放小体量参考数据。** 当前 SEC 产物约 2 MB。若某个源超过约 50 MB，改为不提交并在
  本文件登记获取方式，不要让仓库承载事实数据。
- 使用条款逐源记录在各自工具的 README 中。
- **`iceberg/` 不是外部数据**，放在这里是因为它与参考数据同属不可替代、需随仓库备份的一类，
  见[技术选型评估](../../docs/dev/requirements/technology-selection-evaluation.md) §2.6.1。
