"""Tests for the pure date-range and transformation logic in fetch_prices."""

from datetime import date

import pandas as pd
from fetch_prices import compute_date_range, fetch_daily_closes


def test_compute_date_range_subtracts_lookback_days():
    today = date(2026, 9, 23)
    start, end = compute_date_range(lookback_days=180, today=today)
    assert end == today
    assert start == date(2026, 3, 27)


def test_compute_date_range_zero_lookback_returns_same_day():
    today = date(2026, 9, 23)
    start, end = compute_date_range(lookback_days=0, today=today)
    assert start == end == today


def test_fetch_daily_closes_flattens_multiindex_and_drops_unsettled_days(monkeypatch):
    columns = pd.MultiIndex.from_product([["Close", "Volume"], ["AAPL"]], names=["Price", "Ticker"])
    raw = pd.DataFrame(
        [[190.0, 1000], [191.5, 1200], [float("nan"), 900]],
        index=pd.to_datetime(["2026-01-02", "2026-01-03", "2026-01-04"]),
        columns=columns,
    )
    monkeypatch.setattr("fetch_prices.yf.download", lambda *args, **kwargs: raw)

    result = fetch_daily_closes("AAPL", date(2026, 1, 1), date(2026, 1, 5))

    assert list(result.columns) == ["close"]
    assert result["close"].tolist() == [190.0, 191.5]
