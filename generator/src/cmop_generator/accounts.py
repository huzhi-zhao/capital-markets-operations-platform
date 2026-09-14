"""客户与账户维度：开立、关闭、改名、并户。规范见生成规范 §3A。"""
import numpy as np
import pyarrow as pa

N_CLIENTS = 2000
ACCOUNTS_MEAN, ACCOUNTS_CAP = 6, 200
OPEN_AT_START_SHARE = 0.40
CLOSE_RATE, RENAME_RATE, MERGE_RATE = 0.05, 0.02, 0.01
DAYS_PER_YEAR = 252


def build(rng, days, prefix):
    n_days = len(days)
    counts = np.minimum(rng.geometric(1 / ACCOUNTS_MEAN, N_CLIENTS), ACCOUNTS_CAP)
    client = np.repeat(np.arange(N_CLIENTS), counts)
    n = len(client)
    client_start = np.r_[0, np.cumsum(counts)]

    open_idx = np.where(rng.random(n) < OPEN_AT_START_SHARE, 0, rng.integers(0, n_days, n))
    close_idx = open_idx + np.ceil(rng.exponential(DAYS_PER_YEAR / CLOSE_RATE, n)).astype(np.int64) + 1
    merge_idx = open_idx + np.ceil(rng.exponential(DAYS_PER_YEAR / MERGE_RATE, n)).astype(np.int64) + 1
    end_idx = np.where(close_idx < n_days, close_idx, n_days)
    end_reason = np.where(close_idx < n_days, "closed", None).astype(object)
    merged_into = np.full(n, -1, dtype=np.int64)

    # 按并户日升序处理：目标必须同客户、并户日当天有效。先并走的账户已终止，不会被后来者选中，
    # 因此并户链不可能成环（生成规范 §3A.5 允许成链）。
    for a in np.argsort(merge_idx, kind="stable"):
        m = merge_idx[a]
        if m >= min(close_idx[a], n_days):
            continue
        peers = np.arange(client_start[client[a]], client_start[client[a] + 1])
        ok = peers[(peers != a) & (open_idx[peers] <= m) & (end_idx[peers] > m)]
        if len(ok) == 0:
            continue
        merged_into[a] = ok[rng.integers(0, len(ok))]
        end_idx[a], end_reason[a] = m, "merged"

    ids = np.char.add(f"ACC{prefix}-", np.char.zfill(np.arange(n).astype(str), 6))
    client_ids = np.char.add(f"CLI{prefix}-", np.char.zfill(np.arange(N_CLIENTS).astype(str), 5))

    rows = {k: [] for k in ("account_id", "client_id", "version", "account_name", "valid_from",
                            "valid_to", "end_reason", "merged_into")}
    for a in range(n):
        life = end_idx[a] - open_idx[a]
        k = rng.poisson(RENAME_RATE * life / DAYS_PER_YEAR) if life > 1 else 0
        cuts = np.unique(rng.integers(open_idx[a] + 1, end_idx[a], k)) if k else np.array([], dtype=np.int64)
        bounds = np.r_[open_idx[a], cuts, end_idx[a]]
        for v in range(len(bounds) - 1):
            last = v == len(bounds) - 2
            rows["account_id"].append(ids[a])
            rows["client_id"].append(client_ids[client[a]])
            rows["version"].append(v + 1)
            rows["account_name"].append(f"Synthetic Account {a:06d} v{v + 1}")
            rows["valid_from"].append(days[bounds[v]])
            rows["valid_to"].append(days[bounds[v + 1]] if bounds[v + 1] < n_days else np.datetime64("NaT", "D"))
            rows["end_reason"].append(end_reason[a] if last else None)
            rows["merged_into"].append(ids[merged_into[a]] if last and merged_into[a] >= 0 else None)
    table = pa.table({
        "account_id": pa.array(rows["account_id"]),
        "client_id": pa.array(rows["client_id"]),
        "version": pa.array(rows["version"], pa.int32()),
        "account_name": pa.array(rows["account_name"]),
        "valid_from": pa.array(np.array(rows["valid_from"], dtype="datetime64[D]")),
        "valid_to": pa.array(np.array(rows["valid_to"], dtype="datetime64[D]"),
                             mask=np.isnat(np.array(rows["valid_to"], dtype="datetime64[D]"))),
        "end_reason": pa.array(rows["end_reason"], pa.string()),
        "merged_into": pa.array(rows["merged_into"], pa.string()),
    })
    return {"client": client, "client_start": client_start, "open_idx": open_idx, "end_idx": end_idx,
            "merged_into": merged_into, "ids": ids, "client_ids": client_ids, "table": table}


def active_counts(acc, n_days):
    """客户 × 营业日的有效账户数；有效区间为 [open, end)。"""
    diff = np.zeros((N_CLIENTS, n_days + 1), dtype=np.int32)
    np.add.at(diff, (acc["client"], acc["open_idx"]), 1)
    np.add.at(diff, (acc["client"], acc["end_idx"]), -1)
    return np.cumsum(diff, axis=1)[:, :n_days]
