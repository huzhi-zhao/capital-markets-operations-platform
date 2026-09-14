"""SQL 版回溯与参考实现在同一组用例上逐行对照（validation/README.md：结论必须相同）。"""
import random

import pytest

duckdb = pytest.importorskip("duckdb")

from cmop_validation import chain, chain_sql  # noqa: E402

NEW, REPLACE, CANCEL = "0", "1", "2"


def both(rows):
    con = duckdb.connect()
    con.execute("CREATE TABLE msgs (id VARCHAR, trans_type VARCHAR, ref_id VARCHAR)")
    if rows:
        con.executemany("INSERT INTO msgs VALUES (?, ?, ?)", rows)
    got = {i: (v, root, d) for i, v, root, d in chain_sql.traverse(con, "msgs")}
    ids, tt, refs = zip(*rows)
    r = chain.traverse(list(ids), list(tt), list(refs))
    exp = {i: (v, root, int(d)) for i, v, root, d in zip(r.ids, r.verdict, r.root, r.depth)}
    return got, exp


CASES = {
    "a2_replace": [("A1", NEW, None), ("A2", REPLACE, "A1")],
    "a2b_cancel_then_new": [("A1", NEW, None), ("A2", CANCEL, "A1"), ("A3", NEW, None)],
    "long_replace_chain": [("K0", NEW, None)] + [(f"K{i}", REPLACE, f"K{i-1}") for i in range(1, 40)],
    "two_node_cycle": [("A1", REPLACE, "A2"), ("A2", REPLACE, "A1")],
    "hanging_off_cycle": [("A1", REPLACE, "A2"), ("A2", REPLACE, "A1"), ("A3", REPLACE, "A1")],
    "self_reference": [("A1", REPLACE, "A1")],
    "dangling": [("A2", REPLACE, "GHOST"), ("A3", REPLACE, "A2")],
    "root_not_new": [("A1", REPLACE, None), ("A2", REPLACE, "A1")],
}


@pytest.mark.parametrize("name", CASES)
def test_named_cases_match_reference(name):
    got, exp = both(CASES[name])
    assert got == exp


def test_a2b_values_explicitly():
    got, _ = both(CASES["a2b_cancel_then_new"])
    assert got["A2"] == ("ok", "A1", 1)
    assert got["A3"] == ("ok", "A3", 0)


def test_duplicate_ids_rejected():
    con = duckdb.connect()
    con.execute("CREATE TABLE msgs AS SELECT * FROM (VALUES ('A1','0',NULL), ('A1','1','A1')) t(id, trans_type, ref_id)")
    with pytest.raises(ValueError):
        chain_sql.traverse(con, "msgs")


def test_randomised_against_reference():
    rng = random.Random(20260913)
    for _ in range(200):
        n = rng.randint(1, 60)
        ids = [f"X{i}" for i in range(n)]
        rows = [(i, rng.choice([NEW, REPLACE, CANCEL]),
                 None if rng.random() < 0.3 else rng.choice(ids + ["GHOST"])) for i in ids]
        got, exp = both(rows)
        assert got == exp, rows
