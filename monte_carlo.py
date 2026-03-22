
import numpy as np
import pandas as pd


def simulate_prices_dynamic(S0, returns, days, sims):

    # 🔥 FORCE pandas (handles both numpy + series)
    returns = pd.Series(returns).dropna().reset_index(drop=True)

    if len(returns) == 0:
        raise ValueError("No valid returns data.")

    # Rolling stats
    rolling_mu = returns.rolling(window=20).mean().fillna(0)
    rolling_sigma = returns.rolling(window=20).std().fillna(returns.std())

    # Convert to numpy
    rolling_mu = rolling_mu.values
    rolling_sigma = rolling_sigma.values

    prices = np.zeros((days, sims))
    prices[0] = S0

    for t in range(1, days):
        idx = np.random.randint(0, len(rolling_mu))

        mu = rolling_mu[idx]
        sigma = rolling_sigma[idx]

        Z = np.random.normal(0, 1, sims)

        prices[t] = prices[t - 1] * np.exp((mu - 0.5 * sigma**2) + sigma * Z)

    return prices