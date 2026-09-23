"""Tests for the pure date-lookup logic backing the explanation endpoint."""

import pandas as pd
from app import find_row_for_date


def test_find_row_for_date_returns_matching_row():
    df = pd.DataFrame(
        {"close": [100, 101]},
        index=pd.to_datetime(["2026-01-02", "2026-01-03"]),
    )

    row = find_row_for_date(df, pd.Timestamp("2026-01-03").date())

    assert row["close"] == 101


def test_find_row_for_date_returns_none_when_missing():
    df = pd.DataFrame(
        {"close": [100]},
        index=pd.to_datetime(["2026-01-02"]),
    )

    row = find_row_for_date(df, pd.Timestamp("2026-01-05").date())

    assert row is None
