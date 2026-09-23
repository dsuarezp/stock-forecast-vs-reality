"""Tests for the breakout classification and sizing logic."""

import pandas as pd
from detect_breakouts import classify_direction, compute_breakouts, compute_deviation


def test_classify_direction_covers_all_three_cases():
    close = pd.Series([100, 120, 80])
    band_lower = pd.Series([90, 90, 90])
    band_upper = pd.Series([110, 110, 110])

    direction = classify_direction(close, band_lower, band_upper)

    assert list(direction) == ["within", "above", "below"]


def test_compute_deviation_is_zero_within_band():
    close = pd.Series([100, 120, 80])
    band_lower = pd.Series([90, 90, 90])
    band_upper = pd.Series([110, 110, 110])

    deviation = compute_deviation(close, band_lower, band_upper)

    assert list(deviation) == [0, 10, 10]


def test_compute_breakouts_flags_and_sizes_relative_to_band_width():
    band = pd.DataFrame(
        {
            "close": [100, 130, 70],
            "band_lower": [90, 90, 90],
            "band_upper": [110, 110, 110],
        }
    )

    flagged = compute_breakouts(band)

    assert list(flagged["is_breakout"]) == [False, True, True]
    assert list(flagged["direction"]) == ["within", "above", "below"]
    # half-width is (110-90)/2 = 10, so a deviation of 20 is 2.0x the half-width
    assert list(flagged["relative_deviation"]) == [0, 2.0, 2.0]
