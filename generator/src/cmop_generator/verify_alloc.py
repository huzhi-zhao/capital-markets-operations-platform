"""A-1 与账户维度断言：契约 §3A.6、§3A.7；生成规范 §2A、§3A.2、§3A.5、§3A.7、§6B.2a。"""
import numpy as np

from .calendar import settlement_lag


def check(l1_table, inst):
    failures = []

    def expect(name, ok):
        if not bool(np.all(ok)):
            failures.append(name)

    orders, acc, ctx = inst["orders"], inst["accounts"], inst["alloc_ctx"]
    m = {c: inst["alloc_messages"].column(c).to_numpy(zero_copy_only=False) for c in inst["alloc_messages"].column_names}
    g = {c: inst["alloc_groups"].column(c).to_numpy(zero_copy_only=False) for c in inst["alloc_groups"].column_names}
    n = len(orders["qty"])
    j = m["msg_type"] == "J"
    expect("每单恰好一条 J 两条 P", (j.sum() == n) & ((~j).sum() == 2 * n))
    expect("J 之后依次为 AllocStatus 3 与 0",
           (m["alloc_status"][1::3] == "3") & (m["alloc_status"][2::3] == "0"))
    t = m["transact_time"].astype("datetime64[ms]").astype(np.int64).reshape(n, 3)
    expect("J、P、P 时点严格递增", (t[:, 1] > t[:, 0]) & (t[:, 2] > t[:, 1]))

    l1 = {c: l1_table.column(c).to_numpy(zero_copy_only=False) for c in ("msg_type", "ord_status", "transact_time", "cum_qty", "cl_ord_id")}
    final = l1["ord_status"] == "2"
    expect("J 晚于 L-1 末笔成交", t[:, 0] > l1["transact_time"][final].astype("datetime64[ms]").astype(np.int64))
    expect("Quantity 取 L-1 CumQty（不新编）", m["quantity"][j] == l1["cum_qty"][final])
    expect("ClOrdID 取自 L-1", m["cl_ord_id"][j] == l1["cl_ord_id"][final])

    o = ctx["order_of_group"]
    sum_qty = np.bincount(o, weights=g["alloc_qty"], minlength=n)
    expect("VA-1 总分配数量 = Quantity", sum_qty == m["quantity"][j])
    parts = np.bincount(o, minlength=n)
    expect("NoAllocs 等于组行数", parts == m["no_allocs"][j])
    expect("N 在 2 至 5 之间", (parts >= 2) & (parts <= 5))
    expect("每账户至少一个单位", g["alloc_qty"] >= orders["unit"][o])
    exact = g["alloc_qty"] * g["alloc_avg_px"] * 100
    expect("VA-3 GrossTradeAmt = Σ(AllocQty×AllocAvgPx)，舍入不超过每账户半美分",
           np.abs(np.bincount(o, weights=exact, minlength=n) - m["gross_trade_amt_cents"][j]) <= 0.5 * parts + 1e-6)
    expect("VA-4 NetMoney = ΣAllocNetMoney",
           np.bincount(o, weights=g["alloc_net_money_cents"], minlength=n) == m["net_money_cents"][j])
    sign = np.where(orders["side"][o] == "1", 1, -1)
    expect("VA-5 买入加佣金、卖出减", g["alloc_net_money_cents"] == g["gross_amt_cents"] + sign * g["commission_cents"])
    expect("AllocAvgPx 等于 J 的 AvgPx", g["alloc_avg_px"] == m["avg_px"][j][o])

    a = ctx["account_idx"]
    expect("组内账户同属一个客户", acc["client"][a] == ctx["client"][o])
    key = o * 1_000_000 + a
    expect("组内账户互不重复", len(np.unique(key)) == len(key))
    d = orders["day_idx"][o]
    expect("§3A.7 TradeDate 落在账户存续区间内，并户或关闭当天及之后不分配",
           (acc["open_idx"][a] <= d) & (acc["end_idx"][a] > d))

    days = inst["days"]
    td = m["trade_date"][j]
    expect("TradeDate 是营业日", np.isin(td, days))
    ext = orders["calendar_ext"]
    lag = settlement_lag(td)
    expect("SettlDate = TradeDate + 结算周期营业日", m["settl_date"][j] == ext[np.searchsorted(ext, td) + lag])

    mi = acc["merged_into"]
    src = np.flatnonzero(mi >= 0)
    expect("并户目标同客户", acc["client"][mi[src]] == acc["client"][src])
    expect("并户目标在并户日有效", (acc["open_idx"][mi[src]] <= acc["end_idx"][src]) & (acc["end_idx"][mi[src]] > acc["end_idx"][src]))
    tab = acc["table"]
    ids = tab.column("account_id").to_numpy(zero_copy_only=False)
    vf = tab.column("valid_from").to_numpy(zero_copy_only=False).astype("datetime64[D]")
    vt = tab.column("valid_to").to_numpy(zero_copy_only=False).astype("datetime64[D]")
    same = ids[1:] == ids[:-1]
    expect("版本区间首尾相接、无重叠无空隙", vt[:-1][same] == vf[1:][same])
    expect("版本区间非空", np.isnat(vt) | (vt > vf))
    expect("只有末版本可以不闭合", ~np.isnat(vt[:-1][same]))
    return failures
