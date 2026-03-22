
import yfinance as yf
import pandas as pd
import time


def get_stock_data(symbol, period="2y", retries=3):
    """
    Fetch stock/index data safely from Yahoo Finance
    """

    for attempt in range(retries):
        try:
            data = yf.download(symbol, period=period, progress=False)

            # ❌ If empty → retry
            if data is None or data.empty:
                raise ValueError(f"No data returned for {symbol}")

            # 🔥 FIX: Flatten multi-index columns
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # 🔥 Ensure required columns exist
            required_cols = ["Open", "High", "Low", "Close", "Volume"]
            for col in required_cols:
                if col not in data.columns:
                    raise ValueError(f"Missing column: {col}")

            # 🔥 Drop rows with NaN in Close
            data = data.dropna(subset=["Close"])

            if data.empty:
                raise ValueError("All data is NaN after cleaning")

            return data

        except Exception as e:
            print(f"⚠️ Attempt {attempt+1} failed for {symbol}: {e}")
            time.sleep(1)

    # ❌ Final failure
    print(f"❌ Data fetch completely failed for {symbol}")
    return pd.DataFrame()