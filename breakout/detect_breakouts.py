"""Flag the days where the real close falls outside its expected range."""

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import load_config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def classify_direction(close: pd.Series, band_lower: pd.Series, band_upper: pd.Series) -> pd.Series:
    """Classify each day as "above", "below", or "within" its expected range."""
    direction = pd.Series("within", index=close.index)
    direction[close > band_upper] = "above"
    direction[close < band_lower] = "below"
    return direction


def compute_deviation(close: pd.Series, band_lower: pd.Series, band_upper: pd.Series) -> pd.Series:
    """Compute how far the close fell outside its band, in price units (0 if within)."""
    above_deviation = (close - band_upper).clip(lower=0)
    below_deviation = (band_lower - close).clip(lower=0)
    return above_deviation + below_deviation


def compute_breakouts(band: pd.DataFrame) -> pd.DataFrame:
    """Flag breakout days and size the deviation relative to that day's band width.

    `relative_deviation` expresses the deviation as a multiple of the band's
    half-width, so a value of 1.0 means the close missed the edge of the band
    by exactly one more half-width — useful later to gauge how anomalous a
    breakout actually was, not just that it happened.
    """
    result = band.copy()
    result["direction"] = classify_direction(result["close"], result["band_lower"], result["band_upper"])
    result["is_breakout"] = result["direction"] != "within"
    result["deviation"] = compute_deviation(result["close"], result["band_lower"], result["band_upper"])
    half_width = (result["band_upper"] - result["band_lower"]) / 2
    result["relative_deviation"] = result["deviation"] / half_width
    return result


def load_band(ticker: str) -> pd.DataFrame:
    """Load the expected-range data produced by the band phase."""
    path = DATA_DIR / f"{ticker.lower()}_band.csv"
    return pd.read_csv(path, index_col="Date", parse_dates=True)


def save_breakouts(flagged: pd.DataFrame, ticker: str) -> Path:
    """Persist the full series with breakout flags to a CSV file."""
    output_path = DATA_DIR / f"{ticker.lower()}_breakouts.csv"
    flagged.to_csv(output_path)
    return output_path


def main() -> None:
    config = load_config()
    ticker = config["ingest"]["ticker"]

    band = load_band(ticker)
    flagged = compute_breakouts(band)
    output_path = save_breakouts(flagged, ticker)

    breakout_count = int(flagged["is_breakout"].sum())
    print(f"Saved {len(flagged)} rows to {output_path} ({breakout_count} breakouts)")


if __name__ == "__main__":
    main()
