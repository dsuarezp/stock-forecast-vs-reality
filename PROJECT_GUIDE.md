# Project Guide

Internal working plan for Stock Forecast vs Reality. This is the detailed,
evolving counterpart to `README.md`: goals, design decisions, milestones, and
current progress. Updated as work advances.

## Goal

Build a complete local ML/LLM pipeline, end to end, as a hands-on path toward
MLOps/MLEng and LLMOps/LLMEng: data ingestion, a probabilistic model,
evaluation against reality, and an LLM agent gated by that evaluation — all
running locally before any deployment concerns are introduced.

## What the tool does

1. Ingest daily closing prices for a single stock (starting with AAPL) over a
   recent period.
2. Generate, for each day, an **expected range** (a band), not a single
   predicted price. The specific method for building this band is an open
   decision (see below).
3. Compare the real close against the band for each day. Most days fall
   inside the band (normal noise). Some days break above or below it
   (breakouts) — those are the interesting events.
4. On a breakout day only, run an agent that:
   * Reports the expected range vs. the actual close and the size of the
     deviation.
   * Searches same-day news about the company.
   * Lists findings as correlated signals, never as proven causes, always
     with a correlation-is-not-causation disclaimer.
   * Assigns a confidence level based on how clean the signal is (one clear
     event vs. several mixed/conflicting news items).
5. Visualize the result: the band, the real price line, breakout points
   highlighted, and a click-to-explain interaction that surfaces the agent's
   explanation for a given breakout.

## Design principles

* **Range, not point.** A forecast is either "within expectation" or "outside
  expectation." This matches how markets actually behave and avoids the false
  precision of a single predicted number.
* **Agent gated by evaluation, not always-on.** The LLM only runs when the
  statistical model says a day is actually unusual. This is the core
  guardrail against the narrative fallacy — inventing a tidy story for what
  was really just noise.
* **Honesty over narrative.** Every explanation states its confidence level
  and explicitly separates correlation from causation.
* **Local first.** The full pipeline runs locally before any cloud,
  deployment, or orchestration concerns are introduced, so each MLOps concept
  (versioning, config management, evaluation, testing) is learned in
  isolation first.

## Phases / milestones

- [x] **Phase 0 — Repo scaffolding.** Conventions (`claude.md`), `README.md`,
      `PROJECT_GUIDE.md`, `.gitignore`, and local Python environment.
- [ ] **Phase 1 — Data ingestion.** Fetch and store daily closing prices for
      AAPL over a configurable period.
- [ ] **Phase 2 — Expected-range model.** Produce a daily band of expected
      movement from historical data. Methodology is an open decision.
- [ ] **Phase 3 — Breakout detection.** Compare real closes against the band
      and flag breakout days.
- [ ] **Phase 4 — Explanation agent.** On breakout days, retrieve same-day
      news and generate a confidence-scored, correlation-only explanation.
- [ ] **Phase 5 — Visualization.** Timeline chart with the band, the real
      price, highlighted breakouts, and click-to-explain.

## Open decisions (to resolve before implementing, not by default)

* **Band methodology** (Phase 2): historical volatility bands (e.g.
  Bollinger-style), GARCH-based conditional volatility, quantile regression,
  conformal prediction, or another approach. Each has different statistical
  guarantees and implementation complexity.
* **News source** (Phase 4): which API/provider for same-day company news,
  and how to handle its cost/rate limits as a secret-backed config value.
* **Agent orchestration** (Phase 4): direct LLM API calls vs. an
  agent/orchestration framework — to be decided based on actual need, not by
  default.
* **Visualization approach** (Phase 5): local plotting library vs. a small
  web UI — to be decided once Phases 1-4 produce real data to visualize.

## Progress log

* 2026-09-23 — Repo initialized. Conventions defined in `claude.md`. Overall
  project scope and phased plan agreed upon. `README.md` and this guide
  created. Local Python virtual environment set up next.
