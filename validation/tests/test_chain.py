"""VA-11 与 VC-10 的场景与注入，出处见验证规范 §2B.2 与 §6.3、契约 §3A.10 与 §3A.11。"""
import random

from cmop_validation.chain import CYCLE, DANGLING, MISSING_REF, OK, ROOT_NOT_NEW, traverse

NEW, REPLACE, CANCEL = "0", "1", "2"


def run(rows):
    ids, tt, refs = zip(*rows)
    r = traverse(list(ids), list(tt), list(refs))
    return {i: (v, root, d) for i, v, root, d in zip(r.ids, r.verdict, r.root, r.depth)}


def test_a2_one_hop_replace():
    out = run([("A1", NEW, None), ("A2", REPLACE, "A1")])
    assert out["A1"] == (OK, "A1", 0)
    assert out["A2"] == (OK, "A1", 1)


def test_a2b_cancel_then_new_is_not_two_hops():
    """契约 §3A.10 第 2 条更正：重新下达的 New 不回引，自己就是根。"""
    out = run([("A1", NEW, None), ("A2", CANCEL, "A1"), ("A3", NEW, None)])
    assert out["A2"] == (OK, "A1", 1)
    assert out["A3"] == (OK, "A3", 0)


def test_replace_of_replace_long_chain():
    rows = [("K0", NEW, None)] + [(f"K{i}", REPLACE, f"K{i-1}") for i in range(1, 40)]
    out = run(rows)
    assert out["K39"] == (OK, "K0", 39)


def test_injection_two_node_cycle_terminates():
    out = run([("A1", REPLACE, "A2"), ("A2", REPLACE, "A1")])
    assert out["A1"][0] == CYCLE and out["A2"][0] == CYCLE


def test_node_hanging_off_cycle_is_cycle():
    out = run([("A1", REPLACE, "A2"), ("A2", REPLACE, "A1"), ("A3", REPLACE, "A1")])
    assert out["A3"][0] == CYCLE


def test_self_reference_is_cycle():
    assert run([("A1", REPLACE, "A1")])["A1"][0] == CYCLE


def test_dangling_propagates_down_chain():
    out = run([("A2", REPLACE, "GHOST"), ("A3", REPLACE, "A2")])
    assert out["A2"][0] == DANGLING and out["A3"][0] == DANGLING


def test_root_not_new():
    out = run([("A1", REPLACE, None), ("A2", REPLACE, "A1")])
    assert out["A1"][0] == MISSING_REF
    assert out["A2"] == (ROOT_NOT_NEW, "A1", 1)


def test_randomised_against_naive_walk():
    rng = random.Random(20260913)
    for _ in range(200):
        n = rng.randint(1, 30)
        ids = [f"X{i}" for i in range(n)]
        rows = []
        for i in ids:
            t = rng.choice([NEW, REPLACE, CANCEL])
            ref = None if rng.random() < 0.3 else rng.choice(ids + ["GHOST"])
            rows.append((i, t, ref))
        got = run(rows)
        table = {i: (t, r) for i, t, r in rows}
        for i in ids:
            seen, cur, hops = set(), i, 0
            while True:
                if cur in seen:
                    exp = CYCLE
                    break
                seen.add(cur)
                t, r = table[cur]
                if r is None:
                    exp = OK if t == NEW else (MISSING_REF if cur == i else ROOT_NOT_NEW)
                    break
                if r not in table:
                    exp = DANGLING
                    break
                cur, hops = r, hops + 1
            assert got[i][0] == exp, (rows, i)
            if exp in (OK, ROOT_NOT_NEW, MISSING_REF):
                assert got[i][1:] == (cur, hops)
