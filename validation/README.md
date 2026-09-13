# CMOP 校验层

语言归属见 [ADR 0004 的 2026-09-13 修订](../docs/dev/adr/0004-language-and-runtime-boundaries.md)：
校验的正式形态是 SQL，由 PySpark 作业执行。**本目录放的是参考实现**，用来钉住判据语义与边界情形，
SQL 版本必须在同一组测试用例上给出相同结论。

## `chain.py`：引用链回溯，VA-11 与 VC-10

判据见[验证规范](../docs/dev/requirements/validation-and-reconciliation-specification.md) §2B.2：
沿 `RefAllocID` 或 `ConfirmRefID` 回溯，必须终止于一条 New，且链上无环。

| 结论 | 含义 |
|---|---|
| `ok` | 到达 New 根，给出根标识与跳数 |
| `root_not_new` | 到达终点，但终点不是 New |
| `missing_reference` | 本条非 New 却不带引用，自己就是那个错误终点 |
| `dangling_reference` | 链上某处的引用指向不存在的报文 |
| `cycle` | 在环上或挂在环上，**有限轮内判出，不会死循环** |

**算法是指针倍增**：根与断链点自指，每轮 `dist ← dist + dist[nxt]`、`nxt ← nxt[nxt]`，
`ceil(log2 n) + 1` 轮后收敛。**翻成 Spark 3.5 SQL 时每一轮是一次自连接**：

```sql
-- 第 k 轮，edges_k(id, nxt, dist)
SELECT a.id, b.nxt, a.dist + b.dist AS dist
FROM edges_k a JOIN edges_k b ON a.nxt = b.id
```

轮数由表行数的上界决定，**不需要递归 CTE**（Spark 3.5 没有）。

**Cancel 再 New 不是两跳。** 重新下达的 New 不带引用，回溯零跳即终止，见契约 §3A.10 第 2 条的
2026-09-13 更正。它与被更正报文之间的对应只能靠生成侧对照表核。

```bash
python3 -m pytest validation/tests
```

测试含 200 组随机图与朴素逐跳回溯的对照。
