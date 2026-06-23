"""
Reads every stock CSV produced by the Data fetch pipeline and calculates:
  - Daily returns
  - 30-day rolling volatility (annualized)
  - 20/50/200-day moving averages
  - Annualized Sharpe ratio per stock
  - A correlation matrix across all stocks (closing price returns)

Output: all chart data in a single CSV, and a correlation matrix CSV.
"""

import pandas as pd
import numpy as np
import os

# Set your data directory here (where the stock CSVs are located)
DATA_DIR = "C:\\Users\\mu pc\\Desktop\\Projects\\Project 3\\Python\\stock_data_full2\\data"
OUTPUT_DIR = "analysis_output"
TRADING_DAYS_PER_YEAR = 252
RISK_FREE_RATE = 0.07   # Theoretical rate of return for the risk-free asset
ROLLING_WINDOW = 30     # days, for rolling volatility

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---- STEP 1: LOAD ALL STOCK DATA ----
def load_all_stocks(data_dir):
    stock_data = {}
    files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
    print(f"Found {len(files)} stock files to load...")

    for f in files:
        ticker = f.replace(".csv", "")
        path = os.path.join(data_dir, f)
        try:
            df = pd.read_csv(path, parse_dates=["Date"])
            df = df.sort_values("Date").reset_index(drop=True)
            if len(df) < 60:  # need at least ~60 days for meaningful 30-day rolling stats
                print(f"  Skipping {ticker}: only {len(df)} rows, too short for analysis")
                continue
            stock_data[ticker] = df
        except Exception as e:
            print(f"  Error loading {ticker}: {e}")

    print(f"Successfully loaded {len(stock_data)} stocks for analysis\n")
    return stock_data

# ---- STEP 2: CALCULATE METRICS PER STOCK ----
def calculate_metrics(ticker, df):
    """Calculates returns, volatility, moving averages, Sharpe ratio for one stock."""
    df = df.copy()

    # Daily returns
    df["Daily_Return"] = df["Close"].pct_change()

    # Moving averages
    df["MA_20"] = df["Close"].rolling(20).mean()
    df["MA_50"] = df["Close"].rolling(50).mean()
    df["MA_200"] = df["Close"].rolling(200).mean()

    # Rolling volatility (annualized)
    df["Rolling_Volatility_Annualized"] = (
        df["Daily_Return"].rolling(ROLLING_WINDOW).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    )

    # Summary stats for this stock
    mean_daily_return = df["Daily_Return"].mean()
    annualized_return = mean_daily_return * TRADING_DAYS_PER_YEAR
    annualized_volatility = df["Daily_Return"].std() * np.sqrt(TRADING_DAYS_PER_YEAR)

    sharpe_ratio = (
        (annualized_return - RISK_FREE_RATE) / annualized_volatility
        if annualized_volatility > 0 else np.nan
    )

    summary_row = {
        "Ticker": ticker,
        "Total_Trading_Days": len(df),
        "Start_Date": df["Date"].min().date(),
        "End_Date": df["Date"].max().date(),
        "Annualized_Return_Pct": round(annualized_return * 100, 2),
        "Annualized_Volatility_Pct": round(annualized_volatility * 100, 2),
        "Sharpe_Ratio": round(sharpe_ratio, 3) if not np.isnan(sharpe_ratio) else None,
        "Latest_Close": round(df["Close"].iloc[-1], 2),
        "Latest_MA_20": round(df["MA_20"].iloc[-1], 2) if not pd.isna(df["MA_20"].iloc[-1]) else None,
        "Latest_MA_50": round(df["MA_50"].iloc[-1], 2) if not pd.isna(df["MA_50"].iloc[-1]) else None,
        "Latest_MA_200": round(df["MA_200"].iloc[-1], 2) if not pd.isna(df["MA_200"].iloc[-1]) else None,
    }

    return summary_row, df

#---- STEP 3: BUILD CORRELATION MATRIX ----
def build_correlation_matrix(stock_data):
    """Builds a correlation matrix of daily returns across all stocks."""
    returns_dict = {}
    for ticker, df in stock_data.items():
        returns_dict[ticker] = df.set_index("Date")["Close"].pct_change()

    returns_df = pd.DataFrame(returns_dict)
    corr_matrix = returns_df.corr()
    return corr_matrix

#---- MAIN EXECUTION ----
def main():
    stock_data = load_all_stocks(DATA_DIR)

    summary_rows = []
    print("Calculating metrics per stock...")
    for ticker, df in stock_data.items():
        summary_row, _ = calculate_metrics(ticker, df)
        summary_rows.append(summary_row)

    summary_df = pd.DataFrame(summary_rows)
    summary_df = summary_df.sort_values("Sharpe_Ratio", ascending=False)

    summary_path = os.path.join(OUTPUT_DIR, "stock_summary_metrics.csv")
    summary_df.to_csv(summary_path, index=False)
    print(f"\nSaved summary metrics for {len(summary_df)} stocks -> {summary_path}")

    print("\nBuilding correlation matrix (this can take a moment for large universes)...")
    corr_matrix = build_correlation_matrix(stock_data)
    corr_path = os.path.join(OUTPUT_DIR, "correlation_matrix.csv")
    corr_matrix.to_csv(corr_path)
    print(f"Saved correlation matrix -> {corr_path}")

    # Quick preview
    print("\n--- Top 5 stocks by Sharpe Ratio ---")
    print(summary_df[["Ticker", "Annualized_Return_Pct", "Annualized_Volatility_Pct", "Sharpe_Ratio"]].head(5).to_string(index=False))

    print("\n--- Bottom 5 stocks by Sharpe Ratio ---")
    print(summary_df[["Ticker", "Annualized_Return_Pct", "Annualized_Volatility_Pct", "Sharpe_Ratio"]].tail(5).to_string(index=False))


if __name__ == "__main__":
    main()