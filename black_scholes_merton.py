
#this my beloved anush models main mathematical engine which it uses to calculate the prices of option chain deriavatives
#fun fact: i have named this model as black scholes and merton in the py file because robert c merton also derived this model using stochastic calculus stochastic calculus and won nobel prize along with black and scholes in 1973



import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq


# -----------------------------
# BLACK-SCHOLES PRICING
# -----------------------------
def black_scholes_price(S, K, T, r, sigma, option_type="call"):
    """
    Black-Scholes option pricing
    """

    # ✅ Safety checks (important for real data)
    if S <= 0 or K <= 0:
        return None
    if T <= 0 or sigma <= 0:
        return None

    try:
        d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        if option_type == "call":
            price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

        elif option_type == "put":
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        else:
            return None

        return float(price)

    except:
        return None


# -----------------------------
# IMPLIED VOLATILITY
# -----------------------------
def implied_volatility(S, K, T, r, market_price, option_type="call"):
    """
    Compute implied volatility from market price
    """

    # ✅ Safety checks
    if market_price is None or market_price <= 0:
        return None
    if S <= 0 or K <= 0 or T <= 0:
        return None

    def objective(sigma):
        price = black_scholes_price(S, K, T, r, sigma, option_type)
        if price is None:
            return 1e6
        return price - market_price

    try:
        # 🔥 Wider bounds for real market conditions
        iv = brentq(objective, 1e-6, 5.0)
        return float(iv)

    except:
        return None