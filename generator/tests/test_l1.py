from pathlib import Path

from cmop_generator import l1, verify_l1

SEC = Path(__file__).resolve().parents[2] / "data" / "reference" / "sec"


def test_contract_holds():
    table, inst = l1.generate(seed=7, target_rows=200_000, sec_dir=SEC)
    assert table.num_rows >= 200_000
    assert verify_l1.check(table, inst) == []


def test_same_seed_same_bytes():
    a, _ = l1.generate(seed=11, target_rows=100_000, sec_dir=SEC)
    b, _ = l1.generate(seed=11, target_rows=100_000, sec_dir=SEC)
    assert l1.content_hash(a) == l1.content_hash(b)


def test_different_seed_differs():
    a, _ = l1.generate(seed=11, target_rows=100_000, sec_dir=SEC)
    b, _ = l1.generate(seed=12, target_rows=100_000, sec_dir=SEC)
    assert l1.content_hash(a) != l1.content_hash(b)
