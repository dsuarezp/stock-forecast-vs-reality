"""Build a rolling conformal-prediction expected range around a naive forecast."""

import sys
from math import ceil
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import load_config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def naive_forecast(close: pd.Series) -> pd.Series:
    """Predict each day's close as the previous day's close (random-walk baseline)."""
    return close.shift(1)


def conformal_quantile_level(window: int, coverage: float) -> float:
    """Finite-sample-corrected quantile level used by split conformal prediction."""
    return min(ceil((window + 1) * coverage) / window, 1.0)


def compute_band(prices: pd.DataFrame, coverage: float, calibration_window_days: int) -> pd.DataFrame:
    """Wrap the naive forecast in a rolling conformal expected range.

    Each day's half-width is the conformal quantile of absolute forecast
    errors from the `calibration_window_days` prior days only, so the band
    adapts to recent volatility without leaking the current day's error.
    """
    predicted = naive_forecast(prices["close"])
    abs_residual = (prices["close"] - predicted).abs()

    level = conformal_quantile_level(calibration_window_days, coverage)
    half_width = (
        abs_residual.rolling(calibration_window_days)
        .quantile(level, interpolation="higher")
        .shift(1)
    )

    result = prices.copy()
    result["predicted"] = predicted
    result["band_lower"] = predicted - half_width
    result["band_upper"] = predicted + half_width
    return result.dropna(subset=["band_lower", "band_upper"])


def load_prices(ticker: str) -> pd.DataFrame:
    """Load the daily closes produced by the ingest phase."""
    path = DATA_DIR / f"{ticker.lower()}_daily_closes.csv"
    return pd.read_csv(path, index_col="Date", parse_dates=True)


def save_band(band: pd.DataFrame, ticker: str) -> Path:
    """Persist the price series with its expected range to a CSV file."""
    output_path = DATA_DIR / f"{ticker.lower()}_band.csv"
    band.to_csv(output_path)
    return output_path


def main() -> None:
    config = load_config()
    ticker = config["ingest"]["ticker"]
    coverage = config["band"]["coverage"]
    calibration_window_days = config["band"]["calibration_window_days"]

    prices = load_prices(ticker)
    band = compute_band(prices, coverage, calibration_window_days)
    output_path = save_band(band, ticker)
    print(f"Saved {len(band)} rows with expected-range bands to {output_path}")


if __name__ == "__main__":
    main()
