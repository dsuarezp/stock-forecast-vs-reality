"""Tests for the conformal-prediction band construction in build_band."""

from math import ceil

import pandas as pd
from build_band import compute_band, conformal_quantile_level, naive_forecast


def test_conformal_quantile_level_applies_finite_sample_correction():
    level = conformal_quantile_level(window=19, coverage=0.9)
    assert level == ceil(20 * 0.9) / 19


def test_conformal_quantile_level_caps_at_one():
    level = conformal_quantile_level(window=5, coverage=0.99)
    assert level == 1.0


def test_naive_forecast_shifts_close_by_one_day():
    close = pd.Series([100, 102, 101])
    forecast = naive_forecast(close)
    assert forecast.isna().iloc[0]
    assert forecast.iloc[1] == 100
    assert forecast.iloc[2] == 102


def test_compute_band_uses_only_past_residuals():
    prices = pd.DataFrame(
        {"close": [100, 102, 101, 105, 95, 100, 110]},
        index=pd.date_range("2026-01-01", periods=7),
    )

    band = compute_band(prices, coverage=0.75, calibration_window_days=3)

    assert list(band["close"]) == [95, 100, 110]
    assert list(band["predicted"]) == [105, 95, 100]
    assert list(band["band_lower"]) == [101, 85, 90]
    assert list(band["band_upper"]) == [109, 105, 110]
