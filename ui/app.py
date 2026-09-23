"""FastAPI backend serving price, band, and breakout data to the frontend."""

import sys
from datetime import date as date_type
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import load_config

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Stock Forecast vs Reality")


class PricePoint(BaseModel):
    date: date_type
    close: float
    band_lower: float
    band_upper: float
    direction: str
    is_breakout: bool
    relative_deviation: float


class Explanation(BaseModel):
    date: date_type
    direction: str
    close: float
    band_lower: float
    band_upper: float
    deviation: float
    confidence: str
    text: str


def load_breakouts() -> pd.DataFrame:
    """Load the breakout-flagged price series for the configured ticker."""
    config = load_config()
    ticker = config["ingest"]["ticker"]
    path = DATA_DIR / f"{ticker.lower()}_breakouts.csv"
    return pd.read_csv(path, index_col="Date", parse_dates=True)


def find_row_for_date(df: pd.DataFrame, day: date_type) -> pd.Series | None:
    """Look up the row matching a calendar date, or None if there isn't one."""
    matches = df[df.index.date == day]
    return matches.iloc[0] if not matches.empty else None


@app.get("/api/prices", response_model=list[PricePoint])
def get_prices() -> list[PricePoint]:
    df = load_breakouts()
    return [
        PricePoint(
            date=index.date(),
            close=row["close"],
            band_lower=row["band_lower"],
            band_upper=row["band_upper"],
            direction=row["direction"],
            is_breakout=bool(row["is_breakout"]),
            relative_deviation=row["relative_deviation"],
        )
        for index, row in df.iterrows()
    ]


@app.get("/api/explain/{day}", response_model=Explanation)
def get_explanation(day: date_type) -> Explanation:
    df = load_breakouts()
    row = find_row_for_date(df, day)
    if row is None:
        raise HTTPException(status_code=404, detail="No data for that date")
    if not bool(row["is_breakout"]):
        raise HTTPException(status_code=404, detail="That day was not a breakout")

    return Explanation(
        date=day,
        direction=row["direction"],
        close=row["close"],
        band_lower=row["band_lower"],
        band_upper=row["band_upper"],
        deviation=row["deviation"],
        confidence="n/a",
        text=(
            "Placeholder: the explanation agent (Phase 4) has not been built "
            "yet. This is where its correlation-based, confidence-scored "
            "explanation will appear."
        ),
    )


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
