"""Fetch BNB/USDT historical OHLCV data from Binance API."""

import os
import pandas as pd
from binance.client import Client
from datetime import datetime


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")


def fetch_bnb_daily(start_date: str = "2020-01-01", end_date: str = None, symbol: str = "BNBUSDT") -> pd.DataFrame:
    """Fetch daily OHLCV from Binance API (no API key needed)."""
    client = Client()

    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Fetching {symbol} daily data: {start_date} -> {end_date}")
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1DAY, start_date, end_date)

    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "num_trades",
        "taker_buy_base", "taker_buy_quote", "ignore"
    ])

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    for col in ["open", "high", "low", "close", "volume", "quote_volume"]:
        df[col] = df[col].astype(float)
    df["num_trades"] = df["num_trades"].astype(int)

    df = df[["timestamp", "open", "high", "low", "close", "volume", "quote_volume", "num_trades"]]
    df = df.set_index("timestamp")
    df = df.sort_index()

    # Remove duplicate dates
    df = df[~df.index.duplicated(keep="last")]

    return df


def save_data(df: pd.DataFrame, filename: str = "bnb_usdt_daily.csv"):
    """Cache data to CSV."""
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    filepath = os.path.join(PROCESSED_DIR, filename)
    df.to_csv(filepath)
    print(f"Saved {len(df)} rows -> {filepath}")
    return filepath


def load_data(filename: str = "bnb_usdt_daily.csv") -> pd.DataFrame:
    """Load cached data."""
    filepath = os.path.join(PROCESSED_DIR, filename)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Data not found: {filepath}. Run fetch first.")
    df = pd.read_csv(filepath, index_col="timestamp", parse_dates=True)
    return df


def fetch_fear_greed_index() -> pd.DataFrame:
    """Fetch Crypto Fear & Greed Index historical data."""
    import requests
    url = "https://api.alternative.me/fng/?limit=0&format=json"
    resp = requests.get(url, timeout=30)
    data = resp.json()["data"]

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["timestamp"].astype(int), unit="s")
    df["value"] = df["value"].astype(int)
    df = df[["timestamp", "value", "value_classification"]]
    df = df.set_index("timestamp").sort_index()
    df = df.rename(columns={"value": "fear_greed", "value_classification": "fg_label"})
    return df


if __name__ == "__main__":
    # Fetch and cache BNB data
    df = fetch_bnb_daily("2020-01-01")
    save_data(df)

    print(f"\nData shape: {df.shape}")
    print(f"Date range: {df.index.min()} -> {df.index.max()}")
    print(f"Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"\nFirst 5 rows:\n{df.head()}")
    print(f"\nLast 5 rows:\n{df.tail()}")

    # Check for gaps
    date_range = pd.date_range(df.index.min(), df.index.max(), freq="D")
    missing = date_range.difference(df.index)
    print(f"\nMissing dates: {len(missing)}")

    # Fetch Fear & Greed
    try:
        fg = fetch_fear_greed_index()
        save_data(fg, "fear_greed_index.csv")
        print(f"\nFear & Greed data: {fg.shape[0]} days")
    except Exception as e:
        print(f"\nFear & Greed fetch failed (optional): {e}")
