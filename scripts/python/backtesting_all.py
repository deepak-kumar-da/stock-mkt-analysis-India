"""
This script backtests a simple moving average crossover strategy (Golden Cross and Death Cross) on multiple stock data files.

It reads stock data from CSV files in the specified DATA_DIR, calculates moving averages, identifies buy/sell signals, 
and compares the strategy's performance against a buy-and-hold approach.

The results are saved to CSV files in the OUTPUT_DIR, including a summary of each stock's performance and detailed chart data for visualization.
"""

import pandas as pd
import os

DATA_DIR = r"C:\Users\mu pc\Desktop\Projects\Project 3\Python\stock_data_full2\data"
OUTPUT_DIR = r"C:\Users\mu pc\Desktop\Projects\Project 3\Python\analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---Step 1: Backtest all stock ---
def backtest_one_stock(ticker, df):
    df = df.sort_values("Date").reset_index(drop=True)

    df["MA_50"] = df["Close"].rolling(50).mean()
    df["MA_50_yesterday"] = df["MA_50"].shift(1)
    df["MA_200"] = df["Close"].rolling(200).mean()
    df["MA_200_yesterday"] = df["MA_200"].shift(1)

    df["Golden_Cross"] = (df["MA_50_yesterday"] < df["MA_200_yesterday"]) & (df["MA_50"] > df["MA_200"])
    df["Death_Cross"] = (df["MA_50_yesterday"] > df["MA_200_yesterday"]) & (df["MA_50"] < df["MA_200"])
    df["Ticker"] = ticker

    signals = []
    for idx, row in df.iterrows():
        if row["Golden_Cross"]:
            signals.append(("BUY", row["Close"]))
        elif row["Death_Cross"]:
            signals.append(("SELL", row["Close"]))

    trades = []
    buy_price = None
    for action, price in signals:
        if action == "BUY" and buy_price is None:
            buy_price = price
        elif action == "SELL" and buy_price is not None:
            trades.append((price - buy_price) / buy_price)
            buy_price = None

    if len(df) < 200 or len(trades) == 0:
        return None,None  # not enough data or no completed trades

    strategy_return = sum(trades) * 100
    buy_and_hold_return = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100

    summary = {
        "Ticker": ticker,
        "Num_Trades": len(trades),
        "Strategy_Return_Pct": round(strategy_return, 2),
        "Buy_And_Hold_Return_Pct": round(buy_and_hold_return, 2),
        "Strategy_Won": strategy_return > buy_and_hold_return
    }

    chart_data = df[["Date","Ticker","Close","MA_50","MA_200","Golden_Cross","Death_Cross"]].copy()
    chart_data = chart_data.dropna(subset=["MA_50", "MA_200"])  # drop rows where moving averages are NaN
    chart_data["Signal_Price"] = None
    chart_data["Signal_Type"] = None
    chart_data.loc[chart_data["Golden_Cross"], "Signal_Price"] = chart_data["Close"]
    chart_data.loc[chart_data["Golden_Cross"], "Signal_Type"] = "BUY"

    chart_data.loc[chart_data["Death_Cross"], "Signal_Price"] = chart_data["Close"]
    chart_data.loc[chart_data["Death_Cross"], "Signal_Type"] = "SELL"

    return summary, chart_data

# ---Step 2: Backtest all stocks in the data directory ---
def main():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    print(f"Found {len(files)} files to backtest...")

    results = []
    all_chart_data = []
    for f in files:
        ticker = f.replace(".csv", "")
        try:
            df = pd.read_csv(os.path.join(DATA_DIR, f), parse_dates=["Date"])
            result = backtest_one_stock(ticker, df)
            if result[0] is not None:
                results.append(result[0])
                all_chart_data.append(result[1])
        except Exception as e:
            print(f"  Error on {ticker}: {e}")

    results_df = pd.DataFrame(results)
    out_path = os.path.join(OUTPUT_DIR, "backtest_all_stocks.csv")
    results_df.to_csv(out_path, index=False)

    combined_chart_data = pd.concat(all_chart_data, ignore_index=True)
    combined_chart_data.to_csv(os.path.join(OUTPUT_DIR, "all_chart_data.csv"), index=False)

    print(f"\nBacktested {len(results_df)} stocks -> {out_path}")
    print(f"\nStrategy beat buy-and-hold in {results_df['Strategy_Won'].sum()} out of {len(results_df)} stocks")
    print(f"That's {results_df['Strategy_Won'].mean()*100:.1f}% of stocks")

    print(f"\nAverage Strategy Return: {results_df['Strategy_Return_Pct'].mean():.2f}%")
    print(f"Average Buy-and-Hold Return: {results_df['Buy_And_Hold_Return_Pct'].mean():.2f}%")
    print(f"\nMedian Strategy Return: {results_df['Strategy_Return_Pct'].median():.2f}%")
    print(f"Median Buy-and-Hold Return: {results_df['Buy_And_Hold_Return_Pct'].median():.2f}%")

if __name__ == "__main__":
    main()
