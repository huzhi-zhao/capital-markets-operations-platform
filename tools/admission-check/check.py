#!/usr/bin/env python3
"""写入路径准入检查，第一层与第二层，外加表清单一致性（A6、A7）。

设计见 docs/dev/design/2026-09-12-write-path-admission-checks.md。
读仓库内 config/ 目录与 data/reference/iceberg/table-inventory.tsv，不连接任何服务。
任一条失败退出码为 1。--write-inventory 按建表定义重写表清单，保留已知 metadata 文件列。
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
INVENTORY = Path("data") / "reference" / "iceberg" / "table-inventory.tsv"
INVENTORY_COLUMNS = ("name", "location", "last_known_metadata", "writer", "maintenance_period")
UNKNOWN = "-"
INVENTORY_HEADER = (
    "# CMOP Iceberg 表清单，与 catalog 后端分离保存。技术选型评估 §2.6.1。\n"
    "# 由 tools/admission-check/check.py --write-inventory 按 config/iceberg/tables/ 生成；CI 检查一致性（A6）。\n"
    "# last_known_metadata 由在线层回填，重新生成时保留；未知记为 -。\n"
    "#" + "\t".join(INVENTORY_COLUMNS) + "\n"
)


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


def ddl_location(sql):
    m = re.search(r"\bLOCATION\s+'([^']+)'", sql, re.I)
    return m.group(1) if m else None


def ddl_table_name(sql):
    m = re.search(r"CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([\w.`]+)", sql, re.I)
    return m.group(1).replace("`", "") if m else None


def load_listing(config):
    try:
        data = tomllib.loads((config / "iceberg" / "dual-write-tables.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    tables = data.get("table", [])
    if not isinstance(tables, list):
        return {}
    return {e.get("name"): str(e.get("maintenance_period", "")).strip() for e in tables if e.get("name")}


def read_inventory(path):
    rows = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.startswith("#"):
            continue
        cols = raw.split("\t")
        rows.setdefault(cols[0], []).append(cols)
    return rows


def expected_inventory(root, fail):
    """按建表定义推出清单行。A7：每份建表定义必须显式给出 LOCATION，且语句内表名与文件名一致。"""
    config = Path(root) / "config"
    listing = load_listing(config)
    rows = []
    for ddl in sorted((config / "iceberg" / "tables").glob("*.sql")):
        name = ddl.stem
        sql = ddl.read_text(encoding="utf-8")
        stated = ddl_table_name(sql)
        if stated != name:
            fail("A7", ddl, f"语句内表名 {stated!r} 与文件名 {name!r} 不一致")
        location = ddl_location(sql)
        if location is None:
            fail("A7", ddl, "未显式给出 LOCATION，表清单无法记录表位置")
        dual = name in listing
        rows.append([name, location or UNKNOWN, UNKNOWN, "dual" if dual else "spark",
                     (listing[name] or UNKNOWN) if dual else UNKNOWN])
    return rows


def merge_known_metadata(rows, existing):
    for r in rows:
        prev = existing.get(r[0])
        if prev and len(prev[0]) == len(INVENTORY_COLUMNS) and prev[0][2] != UNKNOWN:
            r[2] = prev[0][2]
    return rows


def render_inventory(rows):
    return INVENTORY_HEADER + "".join("\t".join(r) + "\n" for r in rows)


def check_inventory(root, fail):
    path = Path(root) / INVENTORY
    rows = expected_inventory(root, fail)
    if not path.exists():
        fail("A6", path, "表清单不存在，运行 check.py --write-inventory 生成")
        return
    existing = read_inventory(path)
    for name, entries in existing.items():
        if len(entries) > 1:
            fail("A6", path, f"{name} 重复登记")
        if any(len(e) != len(INVENTORY_COLUMNS) for e in entries):
            fail("A6", path, f"{name} 列数不是 {len(INVENTORY_COLUMNS)}")
    wanted = {r[0]: r for r in rows}
    for name in sorted(set(existing) - set(wanted)):
        fail("A6", path, f"{name} 在清单中但没有建表定义（删表未同步清单，或清单被手改）")
    for name, r in wanted.items():
        if name not in existing:
            fail("A6", path, f"{name} 有建表定义但不在清单中（建表未同步清单）")
            continue
        got = existing[name][0]
        if len(got) != len(INVENTORY_COLUMNS):
            continue
        for i, col in enumerate(INVENTORY_COLUMNS):
            if col != "last_known_metadata" and got[i] != r[i]:
                fail("A6", path, f"{name} 的 {col} 为 {got[i]!r}，建表定义推出 {r[i]!r}")


def write_inventory(root):
    path = Path(root) / INVENTORY
    rows = expected_inventory(root, lambda *a: None)
    existing = read_inventory(path) if path.exists() else {}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_inventory(merge_known_metadata(rows, existing)), encoding="utf-8")


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
    check_inventory(root, fail)
    return failures


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="仓库根目录，只检查其下的 config/")
    ap.add_argument("--write-inventory", action="store_true", help="按建表定义重写表清单后再检查")
    args = ap.parse_args(argv)
    if args.write_inventory:
        write_inventory(args.root)
    failures = run(args.root)
    for rule, where, msg in failures:
        print(f"FAIL {rule} {where}: {msg}")
    print(f"{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
