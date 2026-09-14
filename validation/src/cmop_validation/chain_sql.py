"""VA-11 / VC-10 的 SQL 版本，在 DuckDB 上执行，与 chain.py 对照。

SQL 文件在 validation/sql/chain_traversal/，语法限定在 DuckDB 与 Spark SQL 3.5 的交集内；
驱动只负责替换表名、按轮数重复执行第 2 步并逐轮物化。PySpark 驱动将按同一顺序执行同样三份文件。
"""
import math
from pathlib import Path

SQL_DIR = Path(__file__).resolve().parents[2] / "sql" / "chain_traversal"


def _load(name):
    return (SQL_DIR / name).read_text()


def rounds(n):
    return math.ceil(math.log2(max(n, 2))) + 1


def traverse(con, src):
    """con 是 duckdb 连接，src 是含 (id, trans_type, ref_id) 的表或视图名。

    返回 (id, verdict, root, depth) 的行列表。
    """
    n, distinct = con.execute(f"SELECT COUNT(*), COUNT(DISTINCT id) FROM {src}").fetchone()
    if n != distinct:
        raise ValueError("报文标识不唯一，回溯前提不成立（契约 §3A.10：每条报文各带新号）")

    con.execute(f"CREATE OR REPLACE TEMP TABLE chain_base AS {_load('01_base.sql').format(src=src)}")
    con.execute("CREATE OR REPLACE TEMP TABLE chain_r0 AS SELECT id, nxt, dist FROM chain_base")
    prev = "chain_r0"
    for k in range(1, rounds(n) + 1):
        cur = f"chain_r{k}"
        con.execute(f"CREATE OR REPLACE TEMP TABLE {cur} AS {_load('02_round.sql').format(prev=prev)}")
        con.execute(f"DROP TABLE {prev}")
        prev = cur
    rows = con.execute(_load("03_verdict.sql").format(base="chain_base", prev=prev)).fetchall()
    con.execute(f"DROP TABLE {prev}")
    con.execute("DROP TABLE chain_base")
    return rows
