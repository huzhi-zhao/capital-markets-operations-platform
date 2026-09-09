# Data Volume Baseline

> **Status**: Draft · **Date**: 2026-09-09
>
> 当前数字是规划假设，不是实测基线。Phase 1 后必须用生成器和真实文件测量结果替换。

## 1. 目标规模

项目目标总量为 **800 GB–1.5 TB**。这个区间的目的，是让分区裁剪、小文件、增量处理、
shuffle spill、批次恢复和容量治理变成实际约束。

| 数据集 | 来源 | 当前规模假设 |
|---|---|---|
| orders / trades | 合成 | 400–700 GB，约 20–50 亿行 |
| positions snapshots | 由流水推导 | 100–200 GB |
| customer / account master | 合成 | 小于 1 GB |
| security master / corporate actions | 真实公开数据（SEC 结构化接口、GLEIF） | 数百 MB，其中 SEC 抽取实测 6 MB |
| daily market data | **合成**，见来源清单 §5.4 | 1–3 GB |
| SEC EDGAR XBRL | 真实公开数据 | 20–50 GB（**Later，可整体舍弃**，见下） |
| FX / interest-rate curves | 真实公开数据 | 小于 1 GB |

标的数量不再是自由参数。公司行为采用一对一别名绑定后，标的宇宙等于十年窗口内的真实申报人
集合。四十个季度全量抽取实测为 **12505 个**，其中 7294 个在十年窗口内至少发生过一次公司
行为。按目标成交量摊平后每个标的每个交易日几十到两百笔，该密度直接约束标的维度上的分区
与文件大小设计，见[原始数据源清单](requirements/raw-data-source-inventory.md) §5.6 与 §5.7。

这些数字尚未闭合到 800 GB–1.5 TB 的完整层级放大模型。Bronze/Silver 重复、Iceberg
metadata、snapshot、删除文件和 Gold 都需要在原始数据估算之外单独计算。

SEC EDGAR XBRL 不服务于暂定主 BO 的交易生命周期对账，其半结构化解析价值已由 FIX 与
ISO 20022 报文覆盖。它排在最后阶段，时间不足时整体舍弃，且不得进入任何前置阶段的
依赖链。

**这一条只针对批量解析财报 XBRL 这类工作负载。** 通过 SEC 的 `frames` 与 `submissions`
接口针对性抽取公司行为，体量在数十 MB 量级，角色是维度与参考数据而非 Bronze 事实，
不受本条约束，见[原始数据源清单](requirements/raw-data-source-inventory.md) §5.3。

## 1.1 日增量规模

按十年历史、每年 250 个交易日摊平：

| 数据集 | 全量假设 | 摊到单个交易日 |
|---|---|---|
| 交易生命周期事件 | 400–700 GB | 约 160–280 MB |
| 持仓快照 | 100–200 GB | 约 40–80 MB |
| 合计 | | **约 200–360 MB** |

日增量约为目标总量的万分之四。这个结论支撑
[平台架构](platform-architecture.md) §4.1：常驻日增量可以在 NAS 上执行，MBP 只承担
首次回填、全量重算和 compaction。

该摊平假设默认批次间分布大致均匀。真实的日内与季节性波动会产生峰值批次，峰值倍数需要
在 Phase 1 用生成器实测，不能沿用平均值做容量承诺。

## 2. 为什么不更小或更大

| 规模 | 工程含义 |
|---|---|
| 小于 10 GB | 单机 dataframe 工具即可完成，许多湖仓设计无法被真实检验 |
| 约 100 GB | 开始需要认真处理分区与列裁剪，但错误设计仍可能被硬件掩盖 |
| 500 GB–2 TB | 分区、小文件、增量、spill 和重跑成本开始形成明确反馈 |
| 大于 10 TB | 在当前目标下主要增加时间、硬件和费用，不明显增加新的工程问题 |

## 3. 存储预算

### NAS

- 物理容量：8 TB 起步，可扩展。
- 主要内容：Bronze、Silver、Iceberg metadata、snapshot 和必要备份。
- 8 TB 是容量上限，不是可用预算；必须预留 compaction、重述和恢复操作空间。

### OCI

- 本地盘：200 GB。
- Gold 初始预算：**40 GB**。
- Gold 预期远小于 Silver。超过 40 GB 时，首先检查是否混入明细粒度、snapshot 保留失控
  或表设计重复，而不是直接提高预算。
- **已挂号的例外一项：异常解释表。** 它是明细粒度的，由
  [平台架构](platform-architecture.md) §5.1 的下钻边界决定所要求。其行数由异常条数而非
  事实条数决定，量级远小于事实表，但必须单独监控行数、字节数与增长率，不得并入 Gold
  总量后失去可见性。
- 现有磁盘清理曾估算可回收约 60–70 GB，但该数字来自规划期环境盘点，CMOP 使用前必须
  重新测量，不能视为已承诺容量。

## 4. Phase 1 必测指标

| 指标 | 用途 |
|---|---|
| 各事件类型原始 bytes/row | 从目标行数推导生成量 |
| Parquet 压缩后 bytes/row | 推导 Bronze/Silver 实际容量 |
| 每个 partition 的文件数与中位文件大小 | 判断小文件和 compaction 需求 |
| Iceberg manifest 与 metadata 增长 | 估算规划开销 |
| Snapshot 与删除文件增长率 | 制定保留和过期策略 |
| Spark shuffle read/write、spill 与峰值本地盘 | 验证 MBP NVMe 容量 |
| Silver → Gold 输出比例 | 验证跨隧道 Gold 写入和 40 GB 预算 |
| 单个日增量批次的行数、字节数与峰值倍数 | 验证 NAS 常驻增量的可行性与内存分配 |
| 各关键批次运行时间与峰值内存 | 验证按需计算和 OCI 常驻预算 |

每个数字必须记录测量日期、生成器版本或数据提交、Spark/Iceberg/Parquet 配置，以及运行
节点。没有这组上下文的压缩比和吞吐量不能进入容量决策。

## 5. 尚未计入

- 复制因子或备份策略带来的额外容量。
- SeaweedFS、Garage、RustFS 等实现各自的内部开销。
- 公司行为重述期间同时保留的新旧数据文件。
- 流式 demo 的 Kafka retention 与 checkpoint。
- 日志、Marquez、Grafana 和 Airflow metadata 的长期增长。
- Gold snapshot 保留窗口和临时写入峰值。
