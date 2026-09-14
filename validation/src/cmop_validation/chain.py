"""引用链回溯检查：VA-11（`RefAllocID`）与 VC-10（`ConfirmRefID`）。

判据：沿引用回溯必须终止于一条 TransType=New 的报文，且链上无环。

实现是指针倍增。根与断链点指向自身；每轮 dist ← dist + dist[nxt]，nxt ← nxt[nxt]。
ceil(log2 n) + 1 轮后，无环节点的 nxt 必为终点、dist 为精确跳数；仍未停在自指点上的节点
在环上或挂在环上。每一轮是一次按父键的自连接，因此可照搬成 Spark 3.5 SQL 的有限轮自连接，
不需要递归 CTE，也不会在环上死循环。
"""
from dataclasses import dataclass

import numpy as np

NEW = "0"

OK = "ok"
DANGLING = "dangling_reference"   # 链上某处的引用指向不存在的报文
CYCLE = "cycle"                   # 在环上或挂在环上
ROOT_NOT_NEW = "root_not_new"     # 回溯终点不是 New
MISSING_REF = "missing_reference" # 非 New 却不带引用（VA-7 的同一缺陷，在此处暴露为终点）


@dataclass(frozen=True)
class ChainResult:
    ids: np.ndarray
    root: np.ndarray      # 回溯终点的报文标识；判不出时为 None
    depth: np.ndarray     # 到终点的跳数；判不出时为 -1
    verdict: np.ndarray


def traverse(ids, trans_types, ref_ids):
    """三个序列等长；ref_ids 中缺席用 None。"""
    ids = np.asarray(ids, dtype=object)
    trans = np.asarray(trans_types, dtype=object)
    n = len(ids)
    index = {v: i for i, v in enumerate(ids.tolist())}
    if len(index) != n:
        raise ValueError("报文标识不唯一，回溯前提不成立（契约 §3A.10：每条报文各带新号）")

    nxt = np.arange(n, dtype=np.int64)
    dist = np.zeros(n, dtype=np.int64)
    dangling_self = np.zeros(n, dtype=bool)
    for i, r in enumerate(ref_ids):
        if r is None:
            continue
        j = index.get(r)
        if j is None:
            dangling_self[i] = True
        else:
            nxt[i], dist[i] = j, 1

    for _ in range(int(np.ceil(np.log2(max(n, 2)))) + 1):
        dist = dist + dist[nxt]
        nxt = nxt[nxt]

    has_parent = np.array([r is not None and not dangling_self[i] for i, r in enumerate(ref_ids)])
    stopped = ~has_parent[nxt]            # 终点没有可走的父指针，才算真正停下

    verdict = np.full(n, OK, dtype=object)
    verdict[~stopped] = CYCLE
    end = nxt
    verdict[stopped & dangling_self[end]] = DANGLING
    no_ref_non_new = np.array([ref_ids[i] is None and trans[i] != NEW for i in range(n)])
    resolved = verdict == OK
    verdict[resolved & no_ref_non_new[end]] = np.where(
        (np.arange(n) == end)[resolved & no_ref_non_new[end]], MISSING_REF, ROOT_NOT_NEW)
    resolved = np.isin(verdict, [OK, ROOT_NOT_NEW, MISSING_REF])
    root = np.array([ids[end[i]] if resolved[i] else None for i in range(n)], dtype=object)
    depth = np.where(resolved, dist, -1)
    return ChainResult(ids=ids, root=root, depth=depth, verdict=verdict)
