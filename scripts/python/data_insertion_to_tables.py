"""
This script reads data from CSV files and inserts it into SQL Server tables.

It uses the pyodbc library to connect to the SQL Server database and pandas to read the CSV files. 

The script handles missing values by replacing them with None before inserting into the database.

The script inserts data into two tables: stock_metrics and stock_backtest_result. 
It reads data from stock_summary_metrics.csv and backtest_all_stocks.csv, respectively, 
and inserts the data into the corresponding tables in the StockAnalyis database.
"""

import pyodbc
import pandas as pd
import numpy as np
from sqlalchemy import values

# Connect to the SQL Server database
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=StockAnalyis;"
    "Trusted_Connection=yes;"
)
cursor = conn.cursor()

print("Connected successfully!")

# Read data from CSV files and insert into SQL Server tables
metrics_df = pd.read_csv("C:\\Users\\mu pc\\Desktop\\Projects\\Project 3\\Python\\analysis_output\\stock_summary_metrics.csv")
print(f"Loaded {len(metrics_df)} rows from stock_summary_metrics.csv")

metrics_df = metrics_df.where(pd.notnull(metrics_df), None)

insert_query = """
INSERT INTO stock_metrics 
(stock_ticker, stock_total_trading_days, stock_start_date, stock_end_date, stock_annualized_return_pct, 
 stock_annualized_volatility_pct, stock_sharpe_ratio, stock_latest_close, stock_latest_ma20, stock_latest_ma50, stock_latest_ma200)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

for _, row in metrics_df.iterrows():
    try:
        values = (
            row["Ticker"], row["Total_Trading_Days"], row["Start_Date"], row["End_Date"],
            row["Annualized_Return_Pct"], row["Annualized_Volatility_Pct"], row["Sharpe_Ratio"],
            row["Latest_Close"], row["Latest_MA_20"], row["Latest_MA_50"], row["Latest_MA_200"]
        )
        values = (tuple(None if (isinstance(x, float) and np.isnan(x)) else x for x in values)
        )
        cursor.execute(insert_query, values)
         
    except Exception as e:
        print(f"failed on row index {_}: {row['Ticker']}")
        print(row)
        print(f"Error occurred while inserting row: {e}")
        
        break

print(f"Inserted {len(metrics_df)} rows into stock_metrics")

backtest_df = pd.read_csv("C:\\Users\\mu pc\\Desktop\\Projects\\Project 3\\Python\\analysis_output\\backtest_all_stocks.csv")
print(f"Loaded {len(backtest_df)} rows from backtest_all_stocks.csv")

backtest_df = backtest_df.where(pd.notnull(backtest_df), None)

insert_query = """
INSERT INTO stock_backtest_result
(stock_ticker, stock_num_trades, stock_strategy_return_pct, stock_buy_and_hold_return_pct, stock_strategy_won)
values (?, ?, ?, ?, ?)
"""

for _, row in backtest_df.iterrows():
    try:
        values = (
            row["Ticker"], row["Num_Trades"],
            row["Strategy_Return_Pct"], row["Buy_And_Hold_Return_Pct"], row["Strategy_Won"]
        )
        values = (tuple(None if (isinstance(x, float) and np.isnan(x)) else x for x in values)
        )
        cursor.execute(insert_query, values)
         
    except Exception as e:
        print(f"failed on row index {_}: {row['Ticker']}")
        print(row)
        print(f"Error occurred while inserting row: {e}")
        
        break



conn.commit()
print(f"Inserted {len(backtest_df)} rows into stock_backtest")