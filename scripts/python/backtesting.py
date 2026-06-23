"""
This script is a test implementation of a simple backtesting strategy based on the Golden Cross and Death Cross signals.

The strategy buys when the 50-day moving average crosses above the 200-day moving average (Golden Cross) 
and sells when the 50-day moving average crosses below the 200-day moving average (Death Cross).

The script reads stock data from a CSV file, calculates the moving averages, identifies the signals, 
and evaluates the performance of the strategy compared to a buy-and-hold approach.
"""

import pandas as pd

# Read stock data from CSV file
df = pd.read_csv("C:\\Users\\mu pc\\Desktop\\Projects\\Project 3\\Python\\stock_data_full2\\data\\RELIANCE.csv", parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

df["MA_50"] = df["Close"].rolling(50).mean()
df["MA_50_yesterday"] = df["MA_50"].shift(1)

df["MA_200"] = df["Close"].rolling(200).mean()
df["MA_200_yesterday"] = df["MA_200"].shift(1)

df["Golden_Cross"] = (df["MA_50_yesterday"] < df["MA_200_yesterday"]) & (df["MA_50"] > df["MA_200"])
df["Death_Cross"] = (df["MA_50_yesterday"] > df["MA_200_yesterday"]) & (df["MA_50"] < df["MA_200"])

print(df[df["Golden_Cross"] == True][["Date", "MA_50", "MA_200"]])
print(df[df["Death_Cross"] == True][["Date", "MA_50", "MA_200"]])

# Combine signals into one list, sorted by date
signals = []
for idx, row in df.iterrows():
    if row["Golden_Cross"]:
        signals.append((row["Date"], "BUY", row["Close"]))
    elif row["Death_Cross"]:
        signals.append((row["Date"], "SELL", row["Close"]))

# Walk through signals, pairing each BUY with the next SELL
trades = []
buy_price = None
buy_date = None

for date, action, price in signals:
    if action == "BUY" and buy_price is None:
        buy_price = price
        buy_date = date
    elif action == "SELL" and buy_price is not None:
        trade_return = (price - buy_price) / buy_price
        trades.append({
            "Buy_Date": buy_date,
            "Sell_Date": date,
            "Buy_Price": buy_price,
            "Sell_Price": price,
            "Return_Pct": round(trade_return * 100, 2)
        })
        buy_price = None
        buy_date = None

trades_df = pd.DataFrame(trades)
print(trades_df)

total_strategy_return = trades_df["Return_Pct"].sum()
print(f"\nTotal strategy return (sum of all trades): {total_strategy_return:.2f}%")

# Compare to buy-and-hold
buy_and_hold_return = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
print(f"Buy-and-hold return over same period: {buy_and_hold_return:.2f}%")