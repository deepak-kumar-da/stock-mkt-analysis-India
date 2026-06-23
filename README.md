# NSE Stock Market Analysis

End-to-end analytics analyzing 1991 NSE-listed Indian equities: data collection, risk-adjusted return analysis, and backtesting of a moving-average crossover trading strategy against passive buy-and-hold investing.

## Problem Statement

Most retail "stock analysis" projects look at a handful of cherry-picked stocks. This project instead asks a market-wide question: **across the entire investable Indian equity universe, does a popular trend-following strategy (50-day/200-day moving average crossover) actually beat simply buying and holding?**

## Data Source

- **Universe:** 2091 NSE-listed equities (filtered to standard `EQ` series)
- **Provider:** Yahoo Finance via the `yfinance` Python library
- **History:** Maximum available daily OHLCV data per stock (ranging from a few months for recent listings to 25+ years for established companies)
- **Success rate:** 2090–2091 of 2,091 tickers successfully pulled (>99.9%)

## Method

1. **Data Pipeline** — Checkpointed, failure-logged batch pipeline pulls daily OHLCV data for the full ticker universe via `yfinance`, with automatic resume on interruption.
2. **Metrics Calculation** — For each stock: daily returns, 20/50/200-day moving averages, 30-day rolling volatility, and annualized Sharpe Ratio (252 trading days, ~7% risk-free rate).
3. **Strategy Backtest** — Detects Golden Cross (buy) and Death Cross (sell) signals per stock, pairs trades chronologically, and compares cumulative strategy return against simple buy-and-hold return for the same period.
4. **Storage** — Final summary metrics and backtest results loaded into SQL Server across two normalized tables (`stock_metrics`, `stock_backtest_result`), joined on ticker.
5. **Visualization** — Interactive Power BI dashboard: market-wide KPIs, risk-vs-return scatter plot, strategy-vs-buy-and-hold comparison, and a per-stock crossover explorer with buy/sell markers.

## Headline Finding

Across 1,715 stocks with sufficient history and completed trades, the moving-average crossover strategy **beat buy-and-hold in only 34.2% of cases (586 stocks)** — buy-and-hold won in the remaining 65.8%.

This is a real, counter-intuitive insight: simple trend-following rules that work well in theory often **trade investors out of long secular growth runs** to avoid smaller drawdowns, and the cost of missing those runs outweighs the benefit of dodging dips — particularly visible on high-growth compounders like Reliance Industries, where buy-and-hold returned **28,785%** over the available history versus the strategy's **1,039%**.

## Tech Stack

- **Python** — pandas, numpy, yfinance
- **SQL Server** — pyodbc, T-SQL (joins, aggregations)
- **Power BI** — DAX measures, interactive slicers, multi-page dashboard

## Dashboard Preview

<img width="808" height="456" alt="gif" src="https://github.com/user-attachments/assets/d67b0004-90a6-4a92-b4be-0dd6e861b9e9" />

## How to Run

```bash
pip install yfinance pandas numpy pyodbc

# 1. Pull data (resumable, checkpointed)
python scripts/data_fetch.py

# 2. Calculate metrics (returns, volatility, Sharpe ratio)
python scripts/analysis.py

# 3. Run market-wide backtest
python scripts/backtesting_all.py

# 4. Load results into SQL Server
python scripts/data_insertion_to_tables.py
```

Power BI dashboard (`.pbix`) connects directly to the SQL Server `stock_analysis` database.

## Project Structure

```
nifty-stock-market-analysis/
├── README.md
├── scripts/
│   ├── data_fetch.py
│   ├── analysis.py
│   ├── backtesting.py
│   ├── backtesting_all.py
│   └── data_insertion_to_table.py
├── sql/
│   └── create_tables.sql
├── outputs/
│   ├── stock_summary_metrics_sample.csv
│   └── backtest_all_stocks_sample.csv
│   └── all_chart_data.csv
└── dashboard/
    └── screenshots/
```

## Limitations & Future Work

- Backtest assumes no transaction costs, slippage, or taxes
- Risk-free rate held constant (~7%) rather than time-varying
- Strategy tested in isolation; no portfolio-level position sizing or risk management
- Future direction: extend to options/futures data via a brokerage API (e.g., Kite Connect), add sector-level aggregation, test alternative signal combinations (RSI, MACD)
