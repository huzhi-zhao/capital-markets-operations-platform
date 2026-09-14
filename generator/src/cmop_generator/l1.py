"""L-1 订单生命周期生成器原型：新建 → 接受 → 至少两笔部分成交 → 全部成交。

契约：监管数据契约 §3.3 至 §3.6；生成规范 §2、§3、§6.1 至 §6.6。
可复现性：同一根种子、同一代码提交、同一参考数据版本产出逐行相同的结果。
"""
import argparse
import hashlib
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from . import accounts, allocation, reference
from .calendar import business_days

WINDOW_START = date(2016, 1, 4)
WINDOW_END = date(2025, 12, 31)
SESSION_OPEN_MS = (9 * 60 + 30) * 60_000
SESSION_CLOSE_MS = 16 * 60 * 60_000
ZIPF_EXPONENT = 1.0
ZERO_FACT_SHARE = 0.05
FILL_P = 2 / 3
FILL_CAP = 12
QTY_MEDIAN, QTY_SIGMA, QTY_CAP, LOT, ODD_LOT_SHARE = 500, 1.5, 100_000, 100, 0.05
PX_STEP_BP = 10
FILL_GAP_MEAN_MS = 45_000
ACK_GAP_MEAN_MS = 500
PRICE_MEDIAN_CENTS, PRICE_SIGMA, PRICE_DAILY_VOL = 5_000, 1.0, 0.02
REPO_ROOT = Path(__file__).resolve().parents[3]

# 子生成器顺序即派生顺序。只能在末尾追加，否则同种子下既有子流会整体改变（生成规范 §2）。
STREAMS = ("rank", "zero", "fills", "alloc", "day", "qty", "split", "price_series",
           "px_walk", "time", "side", "accounts", "alloc_client", "alloc_n", "alloc_pick",
           "alloc_split", "alloc_time")


def rngs(seed):
    children = np.random.SeedSequence(seed).spawn(len(STREAMS))
    out = {name: np.random.Generator(np.random.PCG64(ss)) for name, ss in zip(STREAMS, children)}
    out["price_series_seq"] = children[STREAMS.index("price_series")]
    return out


def id_prefix(seed):
    return hashlib.sha256(f"cmop-l1-{seed}".encode()).hexdigest()[:8].upper()


def sample_fill_counts(rng, n):
    return np.minimum(3 + rng.geometric(FILL_P, n) - 1, FILL_CAP)


def build_instruments(sec_dir, r):
    ciks = reference.load_universe(sec_dir)
    delist = reference.load_delistings(sec_dir)
    days = business_days(WINDOW_START, WINDOW_END)
    n = len(ciks)
    last_idx = np.full(n, len(days) - 1)
    for i, c in enumerate(ciks):
        d = delist.get(c)
        if d is not None:
            # 退市日当天及之后不得有成交（生成规范 §3）
            last_idx[i] = np.searchsorted(days, np.datetime64(d)) - 1
    rank = r["rank"].permutation(n) + 1
    zero = np.zeros(n, dtype=bool)
    zero[r["zero"].choice(n, int(round(n * ZERO_FACT_SHARE)), replace=False)] = True
    zero |= last_idx < 0
    return {"cik": np.array(ciks), "rank": rank, "zero": zero, "last_idx": last_idx, "days": days}


def allocate_orders(inst, n_orders, rng):
    active = np.flatnonzero(~inst["zero"])
    if n_orders < len(active):
        raise ValueError(f"订单数 {n_orders} 少于有事实标的数 {len(active)}，无法满足每标的下限")
    weights = 1.0 / inst["rank"][active].astype(float) ** ZIPF_EXPONENT
    extra = rng.multinomial(n_orders - len(active), weights / weights.sum())
    counts = 1 + extra
    order_inst = np.repeat(active, counts)
    return order_inst


def sample_quantities(rng, n_fills):
    n = len(n_fills)
    raw = np.exp(np.log(QTY_MEDIAN) + QTY_SIGMA * rng.standard_normal(n))
    raw = np.minimum(raw, QTY_CAP)
    odd = rng.random(n) < ODD_LOT_SHARE
    unit = np.where(odd, 1, LOT)
    qty = np.where(odd, np.maximum(np.rint(raw), 1), np.maximum(np.rint(raw / LOT), 1) * LOT).astype(np.int64)
    # 每笔至少一个单位，L-1 至少三笔，因此数量下限是笔数乘单位
    qty = np.maximum(qty, n_fills * unit)
    return qty, unit


def split_quantities(rng, qty, unit, n_fills):
    """按剩余量逐笔切分，每笔至少一个单位，末笔取精确余量（生成规范 §6.2）。"""
    n = len(qty)
    width = int(n_fills.max())
    out = np.zeros((n, width), dtype=np.int64)
    remaining = qty.copy()
    for k in range(width):
        left = n_fills - k
        live = left > 0
        last = left == 1
        slack_units = (remaining - left * unit) // unit
        draw = np.floor(rng.random(n) * (2 * slack_units / np.maximum(left, 1) + 1)).astype(np.int64)
        q = unit * (1 + np.minimum(draw, slack_units))
        q = np.where(last, remaining, q)
        q = np.where(live, q, 0)
        out[:, k] = q
        remaining -= q
    assert (remaining == 0).all()
    return out


def arrival_prices(inst, seed_seq, order_inst, day_idx):
    """每个标的一条日度对数随机游走，以美分计，逐标的按需计算。

    成交价与估值取自同一序列（生成规范 §6.2）。每个标的的子流由其下标派生，
    所以一条序列不受其他标的是否被计算影响；峰值内存是一条序列而不是整张矩阵。
    返回每单的到达价，以及用到的 (标的, 营业日) 价格点。
    """
    out = np.empty(len(order_inst), dtype=np.int64)
    by_inst = np.argsort(order_inst, kind="stable")
    uniq, first = np.unique(order_inst[by_inst], return_index=True)
    pts_i, pts_d, pts_p = [], [], []
    children = seed_seq.spawn(len(inst["cik"]))
    for i, lo, hi in zip(uniq, first, np.r_[first[1:], len(by_inst)]):
        g = np.random.Generator(np.random.PCG64(children[i]))
        orders = by_inst[lo:hi]
        last = int(day_idx[orders].max())
        base = np.log(PRICE_MEDIAN_CENTS) + PRICE_SIGMA * g.standard_normal()
        steps = g.standard_normal(last + 1) * PRICE_DAILY_VOL
        steps[0] = 0
        series = np.maximum(np.rint(np.exp(base + np.cumsum(steps))), 1).astype(np.int64)
        out[orders] = series[day_idx[orders]]
        used = np.unique(day_idx[orders])
        pts_i.append(np.full(len(used), i, dtype=np.int32))
        pts_d.append(used)
        pts_p.append(series[used])
    return out, (np.concatenate(pts_i), np.concatenate(pts_d), np.concatenate(pts_p))


def generate(seed, target_rows, sec_dir):
    r = rngs(seed)
    inst = build_instruments(sec_dir, r)

    est = int(target_rows / 5.5 * 1.05) + 1
    fills_pool = sample_fill_counts(r["fills"], est)
    rows_per_order = fills_pool + 2
    cut = int(np.searchsorted(np.cumsum(rows_per_order), target_rows)) + 1
    n_fills = fills_pool[:cut]
    n_orders = len(n_fills)

    order_inst = allocate_orders(inst, n_orders, r["alloc"])
    r["alloc"].shuffle(order_inst)
    day_idx = np.floor(r["day"].random(n_orders) * (inst["last_idx"][order_inst] + 1)).astype(np.int64)

    qty, unit = sample_quantities(r["qty"], n_fills)
    fill_qty = split_quantities(r["split"], qty, unit, n_fills)
    width = fill_qty.shape[1]

    arrival, price_points = arrival_prices(inst, r["price_series_seq"], order_inst, day_idx)
    walk = r["px_walk"].integers(-PX_STEP_BP, PX_STEP_BP + 1, (n_orders, width))
    fill_px = np.maximum(np.rint(arrival[:, None] * (1 + np.cumsum(walk, axis=1) / 10_000)), 1).astype(np.int64)
    live = np.arange(width)[None, :] < n_fills[:, None]
    fill_px = np.where(live, fill_px, 0)

    gaps = np.maximum(np.rint(r["time"].exponential(FILL_GAP_MEAN_MS, (n_orders, width))), 1).astype(np.int64)
    gaps = np.where(live, gaps, 0)
    ack = np.maximum(np.rint(r["time"].exponential(ACK_GAP_MEAN_MS, n_orders)), 1).astype(np.int64)
    span = ack + gaps.sum(axis=1)
    latest_start = np.maximum(SESSION_CLOSE_MS - 1 - span, SESSION_OPEN_MS)
    start = SESSION_OPEN_MS + np.floor(r["time"].random(n_orders) * (latest_start - SESSION_OPEN_MS + 1)).astype(np.int64)
    side = np.where(r["side"].random(n_orders) < 0.5, "1", "2")

    table, inst = assemble(seed, inst, order_inst, day_idx, n_fills, qty, fill_qty, fill_px, start, ack, gaps, side)
    notional = (fill_qty * fill_px).sum(axis=1)
    last_fill_ms = start + ack + gaps.sum(axis=1)
    prefix = id_prefix(seed)
    seq = np.arange(n_orders).astype(str)
    days = inst["days"]
    calendar_ext = business_days(WINDOW_START, date(WINDOW_END.year + 1, 1, 31))
    orders = {"qty": qty, "unit": unit, "day_idx": day_idx, "notional": notional, "side": side,
              "last_fill_ms": last_fill_ms, "calendar_ext": calendar_ext,
              "cl_ord_id": np.char.add(f"C{prefix}-", np.char.zfill(seq, 9)),
              "order_id": np.char.add(f"O{prefix}-", np.char.zfill(seq, 9)),
              "symbol": np.char.add("SYN", np.char.zfill(order_inst.astype(str), 5))}
    acc = accounts.build(r["accounts"], days, prefix)
    alloc_msgs, alloc_groups, alloc_ctx = allocation.generate(r, orders, acc, days, prefix)
    pi, pd_, pp = price_points
    prices = pa.table({"instrument_index": pa.array(pi), "trade_date": pa.array(days[pd_]),
                       "close_px_cents": pa.array(pp)})
    inst.update(orders=orders, accounts=acc, alloc_ctx=alloc_ctx, alloc_messages=alloc_msgs,
                alloc_groups=alloc_groups, prices=prices)
    return table, inst


def assemble(seed, inst, order_inst, day_idx, n_fills, qty, fill_qty, fill_px, start, ack, gaps, side):
    n_orders = len(n_fills)
    prefix = id_prefix(seed)
    rows_per = n_fills + 2
    total = int(rows_per.sum())
    order_of_row = np.repeat(np.arange(n_orders), rows_per)
    offsets = np.cumsum(rows_per) - rows_per
    step = np.arange(total) - offsets[order_of_row]          # 0=D, 1=接受, 2..=成交
    fill_k = np.maximum(step - 2, 0)

    cum_q = np.cumsum(fill_qty, axis=1)
    cum_notional = np.cumsum(fill_qty * fill_px, axis=1)
    cum_t = start[:, None] + ack[:, None] + np.cumsum(gaps, axis=1)

    is_fill = step >= 2
    o = order_of_row
    last_qty = np.where(is_fill, fill_qty[o, fill_k], 0)
    last_px = np.where(is_fill, fill_px[o, fill_k], 0)
    cum = np.where(is_fill, cum_q[o, fill_k], 0)
    notional = np.where(is_fill, cum_notional[o, fill_k], 0)
    t_ms = np.select([step == 0, step == 1], [start[o], start[o] + ack[o]], cum_t[o, fill_k])
    final = is_fill & (fill_k == n_fills[o] - 1)

    days = inst["days"]
    trade_date = days[day_idx[o]]
    ts = trade_date.astype("datetime64[ms]") + t_ms.astype("timedelta64[ms]")
    seq = np.arange(n_orders)
    cl = np.char.add(f"C{prefix}-", np.char.zfill(seq.astype(str), 9))
    oid = np.char.add(f"O{prefix}-", np.char.zfill(seq.astype(str), 9))
    symbol = np.char.add("SYN", np.char.zfill(order_inst.astype(str), 5))
    exec_id = np.char.add(np.char.add(f"E{prefix}-", np.char.zfill(o.astype(str), 9)),
                          np.char.add("-", np.char.zfill(step.astype(str), 2)))

    null_if = lambda mask, arr: pa.array(arr, mask=mask)
    table = pa.table({
        "msg_seq": pa.array(np.arange(total, dtype=np.int64)),
        "msg_type": pa.array(np.where(step == 0, "D", "8")),
        "cl_ord_id": pa.array(cl[o]),
        "order_id": null_if(step == 0, oid[o]),
        "exec_id": null_if(step == 0, exec_id),
        "exec_type": null_if(step == 0, np.where(step == 1, "0", "F")),
        "ord_status": null_if(step == 0, np.select([step == 1, final], ["0", "2"], "1")),
        "symbol": pa.array(symbol[o]),
        "side": pa.array(side[o]),
        "order_qty": pa.array(qty[o]),
        "ord_type": pa.array(np.full(total, "1")),
        "last_qty": null_if(~is_fill, last_qty),
        "last_px_cents": null_if(~is_fill, last_px),
        "cum_qty": null_if(step == 0, cum),
        "leaves_qty": null_if(step == 0, qty[o] - cum),
        "avg_px": null_if(step == 0, np.where(cum > 0, notional / np.maximum(cum, 1) / 100.0, 0.0)),
        "cum_notional_cents": null_if(step == 0, notional),
        "transact_time": pa.array(ts),
        "trade_date": pa.array(trade_date),
        "instrument_index": pa.array(order_inst[o].astype(np.int32)),
    })
    return table, inst


def content_hash(table):
    h = hashlib.sha256()
    for col in table.column_names:
        h.update(col.encode())
        for chunk in table.column(col).chunks:
            for buf in chunk.buffers():
                if buf is not None:
                    h.update(buf)
    return h.hexdigest()


def git_commit():
    try:
        return subprocess.run(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main(argv=None):
    ap = argparse.ArgumentParser(description="生成 L-1 订单生命周期原型数据")
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--rows", type=int, default=1_000_000)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sec-dir", type=Path, default=REPO_ROOT / "data" / "reference" / "sec")
    args = ap.parse_args(argv)

    table, inst = generate(args.seed, args.rows, args.sec_dir)
    args.out.mkdir(parents=True, exist_ok=True)
    outputs = {"fix_l1_messages": table, "fix_alloc_messages": inst["alloc_messages"],
               "fix_alloc_groups": inst["alloc_groups"], "dim_account": inst["accounts"]["table"],
               "instrument_daily_price": inst["prices"]}
    for name, t in outputs.items():
        pq.write_table(t, args.out / f"{name}.parquet")
    manifest = {
        "seed": args.seed,
        "generator_commit": git_commit(),
        "reference_extracted_on": reference.manifest_extracted_on(args.sec_dir),
        "rows": table.num_rows,
        "orders": int((np.asarray(table.column("msg_type")) == "D").sum()),
        "instruments": int(len(inst["cik"])),
        "zero_fact_instruments": int(inst["zero"].sum()),
        "content_sha256": {name: content_hash(t) for name, t in outputs.items()},
    }
    (args.out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
