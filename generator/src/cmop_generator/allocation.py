"""A-1 分配：J、P(3)、P(0)。契约 §3A.1、§3A.6、§3A.7；参数见生成规范 §6B.2a。"""
import numpy as np
import pyarrow as pa

from . import accounts as acc_mod
from .calendar import settlement_lag

N_VALUES = np.array([2, 3, 4, 5])
N_WEIGHTS = np.array([0.4, 0.3, 0.2, 0.1])
COMMISSION_BP = 5
MS_PER_MIN = 60_000


def split(rng, qty, unit, parts):
    """与 l1.split_quantities 同一解法：按剩余量切分，每份至少一个单位，末份取余量。"""
    from .l1 import split_quantities
    return split_quantities(rng, qty, unit, parts)


def generate(r, orders, acc, days, prefix):
    n = len(orders["qty"])
    n_days = len(days)
    day = orders["day_idx"]
    cnt = acc_mod.active_counts(acc, n_days)

    client = np.empty(n, dtype=np.int64)
    order_sorted = np.argsort(day, kind="stable")
    uniq, first = np.unique(day[order_sorted], return_index=True)
    for d, lo, hi in zip(uniq, first, np.r_[first[1:], n]):
        elig = np.flatnonzero(cnt[:, d] >= 2)
        if len(elig) == 0:
            raise ValueError(f"营业日 {days[d]} 没有任何客户拥有两个有效账户")
        client[order_sorted[lo:hi]] = elig[r["alloc_client"].integers(0, len(elig), hi - lo)]

    n_sample = r["alloc_n"].choice(N_VALUES, n, p=N_WEIGHTS)
    unit = orders["unit"]
    chosen = []
    parts = np.empty(n, dtype=np.int64)
    rng_pick = r["alloc_pick"]
    for o in range(n):
        c, d = client[o], day[o]
        peers = np.arange(acc["client_start"][c], acc["client_start"][c + 1])
        live = peers[(acc["open_idx"][peers] <= d) & (acc["end_idx"][peers] > d)]
        k = int(min(n_sample[o], len(live), orders["qty"][o] // unit[o]))
        pick = live[np.argsort(rng_pick.random(len(live)), kind="stable")[:k]]
        chosen.append(pick)
        parts[o] = k

    alloc_qty = split(r["alloc_split"], orders["qty"], unit, parts)
    width = alloc_qty.shape[1]
    live_mask = np.arange(width)[None, :] < parts[:, None]

    notional, cum = orders["notional"], orders["qty"]
    gross = np.where(live_mask, np.rint(alloc_qty * notional[:, None] / cum[:, None]), 0).astype(np.int64)
    commission = np.where(live_mask, np.rint(gross * COMMISSION_BP / 10_000), 0).astype(np.int64)
    sign = np.where(orders["side"] == "1", 1, -1)[:, None]
    net = np.where(live_mask, gross + sign * commission, 0)

    seq = np.arange(n)
    alloc_id = np.char.add(f"A{prefix}-", np.char.zfill(seq.astype(str), 9))
    lag = settlement_lag(days[day])
    settl = orders["calendar_ext"][day + lag]

    t_j = orders["last_fill_ms"] + (MS_PER_MIN * (1 + np.floor(r["alloc_time"].random(n) * 60))).astype(np.int64)
    t_p3 = t_j + np.maximum(np.rint(r["alloc_time"].exponential(1_000, n)), 1).astype(np.int64)
    t_p0 = t_p3 + np.maximum(np.rint(r["alloc_time"].exponential(60_000, n)), 1).astype(np.int64)
    trade_date = days[day]
    base = trade_date.astype("datetime64[ms]")

    rep = lambda a: np.repeat(a, 3)
    step = np.tile([0, 1, 2], n)
    ts = np.stack([t_j, t_p3, t_p0], axis=1).reshape(-1)
    messages = pa.table({
        "msg_seq": pa.array(np.arange(3 * n, dtype=np.int64)),
        "msg_type": pa.array(np.where(step == 0, "J", "P")),
        "alloc_id": pa.array(rep(alloc_id)),
        "alloc_trans_type": pa.array(np.where(step == 0, "0", None).astype(object), pa.string()),
        "alloc_type": pa.array(np.where(step == 0, "1", None).astype(object), pa.string()),
        "alloc_no_orders_type": pa.array(np.where(step == 0, "1", None).astype(object), pa.string()),
        "cl_ord_id": pa.array(np.where(step == 0, rep(orders["cl_ord_id"]), None).astype(object), pa.string()),
        "order_id": pa.array(np.where(step == 0, rep(orders["order_id"]), None).astype(object), pa.string()),
        "side": pa.array(np.where(step == 0, rep(orders["side"]), None).astype(object), pa.string()),
        "symbol": pa.array(np.where(step == 0, rep(orders["symbol"]), None).astype(object), pa.string()),
        "quantity": pa.array(rep(cum), mask=step != 0),
        "avg_px": pa.array(rep(notional / cum / 100.0), mask=step != 0),
        "gross_trade_amt_cents": pa.array(rep(gross.sum(axis=1)), mask=step != 0),
        "net_money_cents": pa.array(rep(net.sum(axis=1)), mask=step != 0),
        "no_allocs": pa.array(rep(parts), mask=step != 0),
        "trade_date": pa.array(rep(trade_date)),
        "settl_date": pa.array(rep(settl), mask=step != 0),
        "alloc_status": pa.array(np.where(step == 1, "3", np.where(step == 2, "0", None)).astype(object), pa.string()),
        "transact_time": pa.array(rep(base) + ts.astype("timedelta64[ms]")),
    })

    o_idx = np.repeat(seq, parts)
    k_idx = np.concatenate([np.arange(p) for p in parts])
    acct = np.concatenate(chosen)
    groups = pa.table({
        "alloc_id": pa.array(alloc_id[o_idx]),
        "group_index": pa.array(k_idx.astype(np.int32)),
        "individual_alloc_id": pa.array(np.char.add(np.char.add(alloc_id[o_idx], "-"), k_idx.astype(str))),
        "alloc_account": pa.array(acc["ids"][acct]),
        "alloc_acct_id_source": pa.array(np.full(len(o_idx), "99")),
        "alloc_account_type": pa.array(np.full(len(o_idx), "1")),
        "alloc_qty": pa.array(alloc_qty[o_idx, k_idx]),
        "alloc_avg_px": pa.array((notional / cum / 100.0)[o_idx]),
        "gross_amt_cents": pa.array(gross[o_idx, k_idx]),
        "commission_cents": pa.array(commission[o_idx, k_idx]),
        "alloc_net_money_cents": pa.array(net[o_idx, k_idx]),
    })
    return messages, groups, {"client": client, "account_idx": acct, "order_of_group": o_idx}
