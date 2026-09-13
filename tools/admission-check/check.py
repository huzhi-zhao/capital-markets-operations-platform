#!/usr/bin/env python3
"""写入路径准入检查，第一层与第二层。

设计见 docs/dev/design/2026-09-12-write-path-admission-checks.md。
只读仓库内 config/ 目录下的文件，不连接任何服务。任一条失败退出码为 1。
"""
import argparse
import re
import sys
import tomllib
from pathlib import Path

MOR_KEYS = ("write.delete.mode", "write.update.mode", "write.merge.mode")
ICEBERG_SPARK_CATALOG = "org.apache.iceberg.spark.SparkCatalog"
ICEBERG_EXTENSIONS = "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions"
FORBIDDEN_IMPLS = ("HadoopCatalog", "HadoopTables")


def parse_kv(text, sep_pattern):
    out = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("!"):
            continue
        parts = re.split(sep_pattern, line, maxsplit=1)
        if len(parts) == 2:
            out[parts[0].strip()] = parts[1].strip()
    return out


def check_spark(path, fail):
    conf = parse_kv(path.read_text(encoding="utf-8"), r"\s*=\s*|\s+")
    catalogs = [k.split(".")[3] for k, v in conf.items()
                if re.fullmatch(r"spark\.sql\.catalog\.[^.]+", k) and v == ICEBERG_SPARK_CATALOG]
    for name in catalogs:
        prefix = f"spark.sql.catalog.{name}"
        impl = conf.get(f"{prefix}.catalog-impl", "")
        ctype = conf.get(f"{prefix}.type")
        if any(f in impl for f in FORBIDDEN_IMPLS):
            fail("A2", path, f"{prefix}.catalog-impl 指向 {impl}")
        elif ctype in ("hadoop", "hive"):
            fail("A2", path, f"{prefix}.type={ctype}")
        elif ctype != "rest" and not impl.endswith("RESTCatalog"):
            fail("A1", path, f"{prefix}.type 必须为 rest，实际为 {ctype!r}")
    if catalogs and ICEBERG_EXTENSIONS.rsplit(".", 1)[1] not in conf.get("spark.sql.extensions", ""):
        fail("A4", path, "spark.sql.extensions 未包含 IcebergSparkSessionExtensions")


def check_trino(path, fail):
    conf = parse_kv(path.read_text(encoding="utf-8"), r"\s*=\s*")
    if conf.get("connector.name") != "iceberg":
        return
    ctype = conf.get("iceberg.catalog.type")
    if ctype != "rest":
        fail("A3", path, f"iceberg.catalog.type 必须为 rest，实际为 {ctype!r}")


def table_properties(sql):
    m = re.search(r"TBLPROPERTIES\s*\((.*?)\)\s*;?\s*$", sql, re.S | re.I)
    if not m:
        return {}
    return dict(re.findall(r"'([^']+)'\s*=\s*'([^']*)'", m.group(1)))


def check_dual_write(config, fail):
    listing = config / "iceberg" / "dual-write-tables.toml"
    if not listing.exists():
        fail("A5", listing, "双写表清单文件不存在")
        return
    try:
        data = tomllib.loads(listing.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        fail("A5", listing, f"无法解析：{e}")
        return
    tables = data.get("table", [])
    if not isinstance(tables, list):
        fail("A5", listing, "[[table]] 必须是数组")
        return
    seen = set()
    for i, entry in enumerate(tables):
        name = entry.get("name", "")
        where = f"{listing}#table[{i}]"
        if not name:
            fail("A5", where, "缺表名")
            continue
        if name in seen:
            fail("A5", where, f"{name} 重复登记")
        seen.add(name)
        if not str(entry.get("maintenance_period", "")).strip():
            fail("L2", where, f"{name} 的维护排期留空")
        ddl = config / "iceberg" / "tables" / f"{name}.sql"
        if not ddl.exists():
            fail("A5", where, f"{name} 找不到建表定义 {ddl.name}")
            continue
        props = table_properties(ddl.read_text(encoding="utf-8"))
        for key in MOR_KEYS:
            if props.get(key) != "merge-on-read":
                fail("L2", ddl, f"{key} 必须为 merge-on-read，实际为 {props.get(key)!r}")


def run(root):
    config = Path(root) / "config"
    failures = []

    def fail(rule, where, msg):
        failures.append((rule, str(where), msg))

    for p in sorted((config / "spark").glob("*.conf")):
        check_spark(p, fail)
    for p in sorted((config / "trino" / "catalog").glob("*.properties")):
        check_trino(p, fail)
    check_dual_write(config, fail)
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="仓库根目录，只检查其下的 config/")
    args = ap.parse_args(argv)
    failures = run(args.root)
    for rule, where, msg in failures:
        print(f"FAIL {rule} {where}: {msg}")
    print(f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
