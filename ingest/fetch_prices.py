"""Fetch and store daily closing prices for the configured stock ticker."""

import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# Running this file directly only puts its own folder on sys.path, so the
# repo root is added explicitly to reach the shared config module.
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import load_config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def compute_date_range(lookback_days: int, today: date | None = None) -> tuple[date, date]:
    """Compute the [start, end] window covering the last `lookback_days` days."""
    end = today or datetime.now(tz=UTC).date()
    start = end - timedelta(days=lookback_days)
    return start, end


def fetch_daily_closes(ticker: str, start: date, end: date) -> pd.DataFrame:
    """Download daily closing prices for `ticker` between start and end.

    Drops days with no close (e.g. the most recent day, if not yet settled
    when this runs).
    """
    data = yf.download(ticker, start=start, end=end, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    prices = data[["Close"]].rename(columns={"Close": "close"})
    return prices.dropna()


def save_prices(prices: pd.DataFrame, ticker: str) -> Path:
    """Persist the price series to a CSV file under data/."""
    DATA_DIR.mkdir(exist_ok=True)
    output_path = DATA_DIR / f"{ticker.lower()}_daily_closes.csv"
    prices.to_csv(output_path)
    return output_path


def main() -> None:
    config = load_config()
    ticker = config["ingest"]["ticker"]
    lookback_days = config["ingest"]["lookback_days"]

    start, end = compute_date_range(lookback_days)
    prices = fetch_daily_closes(ticker, start, end)
    output_path = save_prices(prices, ticker)
    print(f"Saved {len(prices)} rows to {output_path}")


if __name__ == "__main__":
    main()
