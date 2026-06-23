"""
Stock Market Analysis Project
Tickers are stock symbols for companies listed on the NSE (National Stock Exchange of India).
This script reads ticker symbols directly from your downloaded NSE file
(columns: SYMBOL, NAME OF COMPANY, SERIES, DATE OF LISTING, PAID UP VALUE,
MARKET LOT, ISIN NUMBER, FACE VALUE).

TEST_MODE = True by default: runs on only the first 20 tickers
verify everything works before committing to the full 2000+ run.
Once verified, set TEST_MODE = False to run the entire file.
"""

import yfinance as yf
import pandas as pd
import os
import time
import json
from datetime import datetime

# Set your file path to the NSE stock list CSV you downloaded from the NSE website
NSE_FILE_PATH = "C:\\Users\\mu pc\\Desktop\\Projects\\Project 3\\Dataset\\EQUITY_L.csv" 
OUTPUT_DIR = "stock_data_full"
CHECKPOINT_FILE = os.path.join(OUTPUT_DIR, "checkpoint.json")
FAILED_LOG = os.path.join(OUTPUT_DIR, "failed_tickers.csv")
BATCH_SIZE = 20
SLEEP_BETWEEN_BATCHES = 5

TEST_MODE = False        # <-- set to False once the 20-ticker test run looks good
TEST_MODE_LIMIT = 20

FILTER_TO_EQ_SERIES = True  # drops rights issues / suspended / non-regular series, keeps plain equity

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "data"), exist_ok=True)


# ---- STEP 1: LOAD TICKERS FROM FILE ----
def load_ticker_list(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"File not found at {path}. Update NSE_FILE_PATH at the top of this "
            f"script to point to wherever you saved your NSE stock list CSV."
        )

    df = pd.read_csv(path)
    df.columns = [c.strip().upper() for c in df.columns]  # normalize headers

    if "SYMBOL" not in df.columns:
        raise ValueError(
            f"Couldn't find a SYMBOL column. Columns found: {list(df.columns)}. "
            f"Edit the script to match your actual column name."
        )

    if FILTER_TO_EQ_SERIES and "SERIES" in df.columns:
        before = len(df)
        df = df[df["SERIES"].str.strip().str.upper() == "EQ"]
        print(f"Filtered to SERIES='EQ': {before} -> {len(df)} rows")

    symbols = df["SYMBOL"].str.strip().tolist()
    tickers = [f"{s}.NS" for s in symbols]
    print(f"Loaded {len(tickers)} tickers total from {path}")

    if TEST_MODE:
        tickers = tickers[:TEST_MODE_LIMIT]
        print(f"TEST_MODE is ON: limiting to first {len(tickers)} tickers")

    return tickers


# ---- STEP 2: CHECKPOINT HANDLING ----
def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    return {"completed": [], "last_batch_index": -1}


def save_checkpoint(state):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(state, f)


# ---- STEP 3: PULL ONE TICKER ----
def pull_ticker(ticker):
    try:
        df = yf.download(ticker, period="max", auto_adjust=True, progress=False)
        if df.empty:
            return False, 0, "empty_dataframe"

        df = df.reset_index()
        df.columns = [c if isinstance(c, str) else c[0] for c in df.columns]
        df = df.dropna()
        df = df[(df["Open"] > 0) & (df["Close"] > 0)]

        if df.empty:
            return False, 0, "all_rows_filtered_out"

        out_path = os.path.join(OUTPUT_DIR, "data", f"{ticker.replace('.NS','')}.csv")
        df.to_csv(out_path, index=False)
        return True, len(df), "ok"

    except Exception as e:
        return False, 0, str(e)[:200]


# ---- STEP 4: MAIN BATCH LOOP ----
def run_pipeline():
    tickers = load_ticker_list(NSE_FILE_PATH)

    state = load_checkpoint()
    completed = set(state["completed"])
    start_batch = state["last_batch_index"] + 1

    batches = [tickers[i:i + BATCH_SIZE] for i in range(0, len(tickers), BATCH_SIZE)]
    print(f"\nTotal batches: {len(batches)} | Resuming from batch {start_batch}\n")

    failed_records = []
    if os.path.exists(FAILED_LOG) and os.path.getsize(FAILED_LOG) > 0:
        try:
            failed_records = pd.read_csv(FAILED_LOG).to_dict("records")
        except pd.errors.EmptyDataError:
            failed_records = []

    for batch_idx in range(start_batch, len(batches)):
        batch = batches[batch_idx]
        print(f"--- Batch {batch_idx + 1}/{len(batches)} ({len(batch)} tickers) ---")

        for ticker in batch:
            if ticker in completed:
                continue

            success, rows, reason = pull_ticker(ticker)

            if success:
                completed.add(ticker)
                print(f"  OK   {ticker}: {rows} rows")
            else:
                failed_records.append({
                    "ticker": ticker,
                    "reason": reason,
                    "timestamp": datetime.now().isoformat()
                })
                print(f"  FAIL {ticker}: {reason}")

        state["completed"] = list(completed)
        state["last_batch_index"] = batch_idx
        save_checkpoint(state)
        pd.DataFrame(failed_records).to_csv(FAILED_LOG, index=False)

        if batch_idx < len(batches) - 1:
            print(f"Batch done. Sleeping {SLEEP_BETWEEN_BATCHES}s...\n")
            time.sleep(SLEEP_BETWEEN_BATCHES)

    print(f"\n=== DONE ===")
    print(f"Successful: {len(completed)} | Failed: {len(failed_records)}")
    print(f"Data saved in: {OUTPUT_DIR}/data/")
    print(f"Failure log: {FAILED_LOG}")
    if TEST_MODE:
        print(f"\nThis was a TEST RUN ({TEST_MODE_LIMIT} tickers only).")
        print(f"If results look good, set TEST_MODE = False and re-run for the full list.")


if __name__ == "__main__":
    run_pipeline()