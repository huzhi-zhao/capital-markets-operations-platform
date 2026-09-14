"""纽约证券交易所全日休市日历，按规则计算。规范见生成规范 §2A。"""
from datetime import date, timedelta

import numpy as np

SPECIAL_CLOSURES = (date(2018, 12, 5), date(2025, 1, 9))
T2_FROM = date(2017, 9, 5)
T1_FROM = date(2024, 5, 28)


def _easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return date(y, month, day)


def _nth_weekday(y, month, weekday, n):
    d = date(y, month, 1)
    d += timedelta(days=(weekday - d.weekday()) % 7)
    return d + timedelta(weeks=n - 1)


def _last_weekday(y, month, weekday):
    d = date(y + (month == 12), month % 12 + 1, 1) - timedelta(days=1)
    return d - timedelta(days=(d.weekday() - weekday) % 7)


def _observed(d):
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def holidays(year):
    out = set()
    ny = date(year, 1, 1)
    if ny.weekday() == 6:
        out.add(ny + timedelta(days=1))
    elif ny.weekday() != 5:
        out.add(ny)
    out.add(_nth_weekday(year, 1, 0, 3))
    out.add(_nth_weekday(year, 2, 0, 3))
    out.add(_easter(year) - timedelta(days=2))
    out.add(_last_weekday(year, 5, 0))
    if year >= 2022:
        out.add(_observed(date(year, 6, 19)))
    out.add(_observed(date(year, 7, 4)))
    out.add(_nth_weekday(year, 9, 0, 1))
    out.add(_nth_weekday(year, 11, 3, 4))
    out.add(_observed(date(year, 12, 25)))
    out.update(d for d in SPECIAL_CLOSURES if d.year == year)
    return out


def business_days(start, end):
    hol = sorted(h for y in range(start.year, end.year + 1) for h in holidays(y))
    days = np.arange(np.datetime64(start), np.datetime64(end) + np.timedelta64(1, "D"), dtype="datetime64[D]")
    return days[np.is_busday(days, holidays=np.array(hol, dtype="datetime64[D]"))]


def settlement_lag(trade_days):
    """每个交易日对应的结算周期营业日数（生成规范 §2A 末段）。"""
    t = np.asarray(trade_days, dtype="datetime64[D]")
    return np.where(t < np.datetime64(T2_FROM), 3, np.where(t < np.datetime64(T1_FROM), 2, 1))
