"""设计文 Acceptance criteria 第 3 至 7 条，外加仓库真实配置必须通过。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import check  # noqa: E402

REPO = Path(__file__).resolve().parents[3]

GOOD_SPARK = """spark.sql.extensions org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions
spark.sql.catalog.cmop org.apache.iceberg.spark.SparkCatalog
spark.sql.catalog.cmop.type rest
"""
MOR = "TBLPROPERTIES ('write.delete.mode'='merge-on-read', 'write.update.mode'='merge-on-read', 'write.merge.mode'='merge-on-read');"


def build(tmp, spark=GOOD_SPARK, trino="connector.name=iceberg\niceberg.catalog.type=rest\n",
          listing="", tables=None):
    c = tmp / "config"
    (c / "spark").mkdir(parents=True)
    (c / "trino" / "catalog").mkdir(parents=True)
    (c / "iceberg" / "tables").mkdir(parents=True)
    (c / "spark" / "cmop.conf").write_text(spark)
    (c / "trino" / "catalog" / "cmop.properties").write_text(trino)
    (c / "iceberg" / "dual-write-tables.toml").write_text(listing)
    for name, ddl in (tables or {}).items():
        (c / "iceberg" / "tables" / f"{name}.sql").write_text(ddl)
    check.write_inventory(tmp)
    return tmp


def loc(name):
    return f"LOCATION 's3://cmop-warehouse/{name.replace('.', '/')}' "


def rules(tmp):
    return {r for r, _, _ in check.run(tmp)}


def test_repo_config_passes():
    assert check.run(REPO) == []


def test_case3_filesystem_catalog_fails(tmp_path):
    spark = GOOD_SPARK.replace("type rest", "type hadoop")
    assert "A2" in rules(build(tmp_path, spark=spark))


def test_case3_hadoop_catalog_impl_fails(tmp_path):
    spark = GOOD_SPARK + "spark.sql.catalog.cmop.catalog-impl org.apache.iceberg.hadoop.HadoopCatalog\n"
    assert "A2" in rules(build(tmp_path, spark=spark))


def test_missing_type_fails(tmp_path):
    spark = GOOD_SPARK.replace("spark.sql.catalog.cmop.type rest\n", "")
    assert "A1" in rules(build(tmp_path, spark=spark))


def test_trino_non_rest_fails(tmp_path):
    assert "A3" in rules(build(tmp_path, trino="connector.name=iceberg\niceberg.catalog.type=hive_metastore\n"))


def test_missing_extensions_fails(tmp_path):
    spark = GOOD_SPARK.split("\n", 1)[1]
    assert "A4" in rules(build(tmp_path, spark=spark))


def test_case4_listed_table_missing_delete_mode_fails(tmp_path):
    ddl = "CREATE TABLE silver.x (id BIGINT) USING iceberg TBLPROPERTIES ('write.update.mode'='merge-on-read', 'write.merge.mode'='merge-on-read');"
    listing = '[[table]]\nname = "silver.x"\nmaintenance_period = "P1D"\n'
    assert "L2" in rules(build(tmp_path, listing=listing, tables={"silver.x": ddl}))


def test_case5_empty_maintenance_fails(tmp_path):
    ddl = "CREATE TABLE silver.x (id BIGINT) USING iceberg " + MOR
    listing = '[[table]]\nname = "silver.x"\nmaintenance_period = ""\n'
    assert "L2" in rules(build(tmp_path, listing=listing, tables={"silver.x": ddl}))


def test_listed_table_without_ddl_fails(tmp_path):
    listing = '[[table]]\nname = "silver.missing"\nmaintenance_period = "P1D"\n'
    assert "A5" in rules(build(tmp_path, listing=listing))


def test_unparseable_listing_fails(tmp_path):
    assert "A5" in rules(build(tmp_path, listing="[[table]\n"))


def test_case6_unlisted_table_with_defaults_passes(tmp_path):
    ddl = "CREATE TABLE gold.y (id BIGINT) USING iceberg " + loc("gold.y") + ";"
    assert check.run(build(tmp_path, tables={"gold.y": ddl})) == []


def test_listed_table_complete_passes(tmp_path):
    ddl = "CREATE TABLE silver.x (id BIGINT) USING iceberg " + loc("silver.x") + MOR
    listing = '[[table]]\nname = "silver.x"\nmaintenance_period = "P1D"\n'
    assert check.run(build(tmp_path, listing=listing, tables={"silver.x": ddl})) == []


def test_case7_hive_metastore_outside_scope_passes(tmp_path):
    root = build(tmp_path)
    outside = root / "reference" / "uoip"
    outside.mkdir(parents=True)
    (outside / "iceberg.properties").write_text("connector.name=iceberg\niceberg.catalog.type=hive_metastore\n")
    assert check.run(root) == []


def test_non_iceberg_trino_catalog_ignored(tmp_path):
    assert check.run(build(tmp_path, trino="connector.name=postgresql\n")) == []


# ---- 表清单（A6、A7），技术选型评估 §2.6.1 ----

def test_inventory_generated_rows(tmp_path):
    ddl = "CREATE TABLE silver.x (id BIGINT) USING iceberg " + loc("silver.x") + MOR
    listing = '[[table]]\nname = "silver.x"\nmaintenance_period = "P1D"\n'
    gold = "CREATE TABLE gold.y (id BIGINT) USING iceberg " + loc("gold.y") + ";"
    root = build(tmp_path, listing=listing, tables={"silver.x": ddl, "gold.y": gold})
    rows = check.read_inventory(root / check.INVENTORY)
    assert rows["silver.x"][0] == ["silver.x", "s3://cmop-warehouse/silver/x", "-", "dual", "P1D"]
    assert rows["gold.y"][0] == ["gold.y", "s3://cmop-warehouse/gold/y", "-", "spark", "-"]
    assert check.run(root) == []


def test_inventory_missing_fails(tmp_path):
    root = build(tmp_path)
    (root / check.INVENTORY).unlink()
    assert "A6" in rules(root)


def test_table_created_without_inventory_update_fails(tmp_path):
    root = build(tmp_path)
    (root / "config" / "iceberg" / "tables" / "gold.z.sql").write_text(
        "CREATE TABLE gold.z (id BIGINT) USING iceberg " + loc("gold.z") + ";")
    assert "A6" in rules(root)


def test_table_dropped_without_inventory_update_fails(tmp_path):
    gold = "CREATE TABLE gold.y (id BIGINT) USING iceberg " + loc("gold.y") + ";"
    root = build(tmp_path, tables={"gold.y": gold})
    (root / "config" / "iceberg" / "tables" / "gold.y.sql").unlink()
    assert "A6" in rules(root)


def test_location_changed_without_inventory_update_fails(tmp_path):
    root = build(tmp_path, tables={"gold.y": "CREATE TABLE gold.y (id BIGINT) USING iceberg " + loc("gold.y") + ";"})
    (root / "config" / "iceberg" / "tables" / "gold.y.sql").write_text(
        "CREATE TABLE gold.y (id BIGINT) USING iceberg LOCATION 's3://elsewhere/gold/y';")
    assert "A6" in rules(root)


def test_ddl_without_location_fails(tmp_path):
    assert "A7" in rules(build(tmp_path, tables={"gold.y": "CREATE TABLE gold.y (id BIGINT) USING iceberg;"}))


def test_ddl_name_mismatch_fails(tmp_path):
    ddl = "CREATE TABLE gold.other (id BIGINT) USING iceberg " + loc("gold.y") + ";"
    assert "A7" in rules(build(tmp_path, tables={"gold.y": ddl}))


def test_known_metadata_preserved_on_regenerate(tmp_path):
    root = build(tmp_path, tables={"gold.y": "CREATE TABLE gold.y (id BIGINT) USING iceberg " + loc("gold.y") + ";"})
    inv = root / check.INVENTORY
    meta = "s3://cmop-warehouse/gold/y/metadata/00007-abc.metadata.json"
    inv.write_text(inv.read_text().replace("gold/y\t-\t", f"gold/y\t{meta}\t"))
    assert check.run(root) == []
    check.write_inventory(root)
    assert check.read_inventory(inv)["gold.y"][0][2] == meta
