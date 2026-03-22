# returns_calculator.py
import numpy as np

def compute_returns(data):
    data["Returns"] = np.log(data["Close"] / data["Close"].shift(1))
    data = data.dropna()

    # 🔥 Dynamic drift (rolling mean)
    mu = data["Returns"].rolling(window=20).mean().iloc[-1] * 252

    return data, mu