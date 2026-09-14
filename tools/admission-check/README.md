# 写入路径准入检查

实现[写入路径准入检查](../../docs/dev/design/2026-09-12-write-path-admission-checks.md)的第一层
（A1 至 A5）、第二层（建表属性断言，报告为 `L2`）与表清单一致性（A6、A7）。第三层在线巡检等 catalog 部署后再做。

## 运行

```bash
python3 tools/admission-check/check.py
python3 -m pytest tools/admission-check/tests
```

**新增、删除或改动建表定义后**，先重写表清单再提交：

```bash
python3 tools/admission-check/check.py --write-inventory
```

检查只需 Python 3.11 及以上的标准库；测试需要 `pytest`。

## 作用域

**只读仓库根下 `config/` 目录与表清单文件。** 兄弟项目的配置即使被复制进仓库做参考，
只要不在 `config/` 下就不会被扫到，测试 `test_case7_hive_metastore_outside_scope_passes` 钉住这一点。

| 路径 | 规则 |
|---|---|
| `config/spark/*.conf` | A1、A2、A4。仅对值为 `SparkCatalog` 的 catalog 生效 |
| `config/trino/catalog/*.properties` | A3。仅对 `connector.name=iceberg` 生效 |
| `config/iceberg/dual-write-tables.toml` | A5，及清单内每张表的 L2 |
| `config/iceberg/tables/<namespace>.<table>.sql` | 建表定义，文件名即表名；A7 要求显式 `LOCATION` |
| `data/reference/iceberg/table-inventory.tsv` | A6，表清单与建表定义一致，`last_known_metadata` 列不比对 |

## 双写表清单格式

```toml
[[table]]
name = "silver.example"
maintenance_period = "P1D"   # ISO 8601 期间，留空即失败
```
