"""对生成结果断言 L-1 契约：§3.5 步骤序列、§3.6 三条不变量、生成规范 §3 生命周期与 §6.6 分配。"""
import numpy as np
import pyarrow.compute as pc


def check(table, inst):
    t = {c: table.column(c).to_numpy(zero_copy_only=False) for c in table.column_names}
    failures = []

    def expect(name, ok):
        if not bool(np.all(ok)):
            failures.append(name)

    msg = t["msg_type"]
    is_d = msg == "D"
    order_no = np.cumsum(is_d) - 1
    counts = np.bincount(order_no)
    expect("每单至少五条报文", counts >= 5)
    starts = np.flatnonzero(is_d)
    pos = np.arange(len(msg)) - starts[order_no]
    expect("第二条是接受回报", (t["exec_type"][pos == 1] == "0") & (t["ord_status"][pos == 1] == "0"))
    fills = pos >= 2
    expect("成交回报 ExecType=F", t["exec_type"][fills] == "F")
    last = np.r_[starts[1:] - 1, len(msg) - 1]
    expect("末条 OrdStatus=2", t["ord_status"][last] == "2")
    mid = fills & ~np.isin(np.arange(len(msg)), last)
    expect("中间成交 OrdStatus=1", t["ord_status"][mid] == "1")

    er = ~is_d
    expect("CumQty + LeavesQty = OrderQty", t["cum_qty"][er] + t["leaves_qty"][er] == t["order_qty"][er])
    expect("每笔 LastQty > 0", t["last_qty"][fills] > 0)
    cum_from_fills = np.cumsum(np.where(fills, t["last_qty"], 0))
    base = np.r_[0, cum_from_fills][starts][order_no]
    expect("CumQty = ΣLastQty", (cum_from_fills - base)[er] == t["cum_qty"][er])
    expect("末笔 CumQty = OrderQty", t["cum_qty"][last] == t["order_qty"][last])
    notional = np.where(fills, t["last_qty"] * t["last_px_cents"], 0).cumsum()
    nbase = np.r_[0, notional][starts][order_no]
    expect("AvgPx 与逐笔成交自洽",
           np.abs(t["avg_px"][fills] * t["cum_qty"][fills] * 100 - (notional - nbase)[fills])
           <= 1e-6 * np.maximum((notional - nbase)[fills], 1))
    expect("接受回报 AvgPx=0 且 CumQty=0", (t["avg_px"][pos == 1] == 0) & (t["cum_qty"][pos == 1] == 0))

    ts = t["transact_time"].astype("datetime64[ms]").astype(np.int64)
    same = np.r_[False, order_no[1:] == order_no[:-1]]
    expect("链内时点严格递增", ts[1:][same[1:]] > ts[:-1][same[1:]])
    expect("整单落在同一交易日", t["trade_date"][1:][same[1:]] == t["trade_date"][:-1][same[1:]])

    idx = t["instrument_index"]
    days = inst["days"]
    last_day = days[np.maximum(inst["last_idx"], 0)]
    expect("不早于窗口起点", t["trade_date"] >= days[0])
    expect("退市日及之后无成交", t["trade_date"] <= last_day[idx])
    expect("零事实标的无事实", ~inst["zero"][idx])
    active = int((~inst["zero"]).sum())
    expect("每个有事实标的至少一单", len(np.unique(idx[is_d])) == active)
    expect("ExecID 全局唯一", len(pc.unique(table.column("exec_id")).drop_null()) == int(er.sum()))
    return failures
