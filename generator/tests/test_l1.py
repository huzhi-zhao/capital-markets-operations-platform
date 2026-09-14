from pathlib import Path

from cmop_generator import l1, verify_alloc, verify_l1

SEC = Path(__file__).resolve().parents[2] / "data" / "reference" / "sec"


def test_contract_holds():
    table, inst = l1.generate(seed=7, target_rows=200_000, sec_dir=SEC)
    assert table.num_rows >= 200_000
    assert verify_l1.check(table, inst) == []
    assert verify_alloc.check(table, inst) == []


def _hashes(seed):
    t, inst = l1.generate(seed=seed, target_rows=100_000, sec_dir=SEC)
    return [l1.content_hash(x) for x in (t, inst["alloc_messages"], inst["alloc_groups"],
                                          inst["accounts"]["table"], inst["prices"])]


def test_same_seed_same_bytes():
    assert _hashes(11) == _hashes(11)


def test_different_seed_differs():
    a, b = _hashes(11), _hashes(12)
    assert all(x != y for x, y in zip(a, b))


def test_verifier_catches_injections():
    """没有配对注入的断言等于从未验证过（验证规范 §6）。"""
    import numpy as np
    import pyarrow as pa

    table, inst = l1.generate(seed=5, target_rows=100_000, sec_dir=SEC)
    g = inst["alloc_groups"]
    qty = g.column("alloc_qty").to_numpy().copy()
    qty[0] -= 1
    bad = dict(inst, alloc_groups=g.set_column(g.column_names.index("alloc_qty"), "alloc_qty", pa.array(qty)))
    assert "VA-1 总分配数量 = Quantity" in verify_alloc.check(table, bad)

    ctx = dict(inst["alloc_ctx"])
    acct = ctx["account_idx"].copy()
    acc = inst["accounts"]
    other = np.flatnonzero(acc["client"] != acc["client"][acct[0]])[0]
    acct[0] = other
    ctx["account_idx"] = acct
    assert "组内账户同属一个客户" in verify_alloc.check(table, dict(inst, alloc_ctx=ctx))
