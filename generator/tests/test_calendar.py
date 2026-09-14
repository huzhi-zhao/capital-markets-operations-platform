from datetime import date

from cmop_generator.calendar import business_days, holidays


def test_known_holidays():
    assert holidays(2016) == {date(2016, 1, 1), date(2016, 1, 18), date(2016, 2, 15), date(2016, 3, 25),
                              date(2016, 5, 30), date(2016, 7, 4), date(2016, 9, 5), date(2016, 11, 24),
                              date(2016, 12, 26)}
    h22 = holidays(2022)
    assert date(2022, 6, 20) in h22 and date(2022, 12, 26) in h22
    assert date(2021, 12, 31) not in holidays(2021)          # 元旦逢周六不补休
    assert date(2018, 12, 5) in holidays(2018) and date(2025, 1, 9) in holidays(2025)
    assert date(2021, 6, 18) not in holidays(2021)           # 六月节 2022 年起


def test_trading_day_counts():
    for y, n in [(2016, 252), (2022, 251), (2023, 250), (2024, 252), (2025, 250)]:
        assert len(business_days(date(y, 1, 1), date(y, 12, 31))) == n, y
