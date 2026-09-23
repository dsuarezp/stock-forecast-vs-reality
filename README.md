# Stock Forecast vs Reality

A tool that takes a single stock (starting with AAPL) and shows, on a shared
timeline, three things at once: what actually happened to the price, what a
model expected to happen, and the moments where reality broke away from that
expectation. When a break happens, an agent looks for same-day news and
explains what may have driven it — always as a correlation, never as a proven
cause.

## What it is

* An **expected range**, not a point forecast. Each day gets a band of
  "normal" movement instead of a single predicted price. A price is either
  inside or outside that range — it is never "right" or "wrong."
* A **breakout detector** that flags the days where the real close falls
  outside the expected band. Most days are noise; breakouts are the
  interesting ones.
* An **explanation agent** that activates only on breakout days, pulls
  same-day news, and reports it with an explicit confidence level and a
  correlation-is-not-causation disclaimer.

## What it is not

* Not a price predictor meant to inform buy/sell decisions.
* Not a tool that claims certainty about why the market moved.
* It is a tool for understanding the past, not forecasting the future for
  profit.

## Project status

Early development. The pipeline is being built end to end, one phase at a
time: data ingestion, the expected-range model, breakout detection, the news
agent, and finally the visualization layer. See
[PROJECT_GUIDE.md](PROJECT_GUIDE.md) for the detailed plan, design decisions,
and current progress.

## Setup

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/) for dependency
management.

```bash
uv sync
```

This creates a local `.venv` and installs all dependencies pinned in
`uv.lock`. Run any script with `uv run`, e.g.:

```bash
uv run python ingest/fetch_prices.py
```

Run instructions for later phases will be added here as they land.
