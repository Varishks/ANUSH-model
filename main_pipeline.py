import os

# 🔥 Prevent memory leak
os.environ["OMP_NUM_THREADS"] = "1"

import sys
import numpy as np

# 🔥 Path fix
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_PATH)

from data_collector import get_stock_data
from returns_calculator import compute_returns
from garch_model import forecast_volatility
from monte_carlo import simulate_prices_dynamic
from markov_model import (
    detect_regimes,
    get_regime_data,
    compute_regime_parameters
)
from black_scholes_merton import black_scholes_price, implied_volatility
from nse_option_chain import fetch_option_chain, get_atm_option_data


def main():

    print("\n========== ANUSH QUANT ENGINE (LIVE OPTIONS) ==========")

    stock = input("Enter stock/index (e.g. NIFTY, KOTAKBANK): ").upper()

    # 🔥 Handle Yahoo Finance symbols
    if stock in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
        if stock == "NIFTY":
            yf_symbol = "^NSEI"
        elif stock == "BANKNIFTY":
            yf_symbol = "^NSEBANK"
        else:
            yf_symbol = "^NSEFIN"
    else:
        yf_symbol = stock + ".NS"

    try:
        days = int(input("Enter simulation days: "))
        sims = int(input("Enter number of simulations: "))
    except ValueError:
        print("❌ Invalid input.")
        return

    # ===== DATA =====
    print("\nFetching data...")
    data = get_stock_data(yf_symbol)

    if data.empty:
        print("❌ No data found.")
        return

    # ===== RETURNS =====
    print("Calculating returns...")
    data, _ = compute_returns(data)

    returns = data["Returns"].dropna().reset_index(drop=True)

    if len(returns) == 0:
        print("❌ No valid returns.")
        return

    # ===== HMM =====
    print("Detecting regimes...")
    returns_array = returns.values.reshape(-1, 1)

    states, model = detect_regimes(returns_array)
    regime_returns, regime = get_regime_data(returns, states)

    mu_hmm, sigma_hmm = compute_regime_parameters(regime_returns)

    # ===== GARCH =====
    print("Estimating volatility...")
    try:
        sigma_garch = forecast_volatility(returns)
    except Exception as e:
        print(f"❌ GARCH failed: {e}")
        return

    sigma = float((sigma_hmm + sigma_garch) / 2)

    # ===== MONTE CARLO =====
    print("Running simulation...")

    S0 = float(data["Close"].iloc[-1].item())

    sim = simulate_prices_dynamic(S0, regime_returns, days, sims)
    final_prices = sim[-1].flatten()

    expected_price = np.mean(final_prices)
    prob_up = np.mean(final_prices > S0)

    print("\n========== MODEL RESULTS ==========")
    print(f"Current Price: {S0:.2f}")
    print(f"Expected Price: {expected_price:.2f}")
    print(f"Regime: {regime}")
    print(f"Volatility (σ): {sigma:.4f}")
    print(f"Probability UP: {prob_up:.2%}")

    # ===== BLACK-SCHOLES =====
    print("\nCalculating model option prices...")

    K = S0
    T = days / 252
    r = 0.06

    call_price = black_scholes_price(S0, K, T, r, sigma, "call")
    put_price = black_scholes_price(S0, K, T, r, sigma, "put")

    print("\n========== MODEL OPTION PRICES ==========")
    print(f"Call Price (Model): {call_price}")
    print(f"Put Price (Model): {put_price}")

    # ===== NSE OPTION DATA =====
    print("\nFetching NSE option chain...")

    try:
        oc_data = fetch_option_chain(stock)
        atm_data = get_atm_option_data(oc_data, S0)

        market_call = atm_data["call_price"]
        market_put = atm_data["put_price"]

        print("\n========== NSE OPTION DATA ==========")
        print(f"Strike: {atm_data['strike']}")
        print(f"Market Call Price: {market_call}")
        print(f"Market Put Price: {market_put}")
        print(f"Market Call IV: {atm_data['call_iv']}")
        print(f"Market Put IV: {atm_data['put_iv']}")

    except Exception as e:
        print(f"❌ NSE fetch failed: {e}")
        market_call, market_put = None, None

    # ===== IMPLIED VOL =====
    print("\n========== IMPLIED VOLATILITY ==========")

    iv_call = implied_volatility(S0, K, T, r, market_call, "call")
    iv_put = implied_volatility(S0, K, T, r, market_put, "put")

    if iv_call is not None:
        print(f"Call IV: {iv_call:.4f} ({iv_call*100:.2f}%)")
    else:
        print("Call IV: Not available")

    if iv_put is not None:
        print(f"Put IV: {iv_put:.4f} ({iv_put*100:.2f}%)")
    else:
        print("Put IV: Not available")

    # ===== COMPARISON =====
    print("\n========== MODEL vs MARKET ==========")

    if call_price is not None and market_call is not None:
        diff_call = call_price - market_call
        print(f"Call Mispricing: {diff_call:.2f}")
    else:
        diff_call = None
        print("Call comparison not available")

    if put_price is not None and market_put is not None:
        diff_put = put_price - market_put
        print(f"Put Mispricing: {diff_put:.2f}")
    else:
        diff_put = None
        print("Put comparison not available")

    # ===== SIGNALS =====
    print("\n========== TRADING SIGNALS ==========")

    threshold = 2

    if diff_call is not None:
        if diff_call > threshold:
            print("📈 CALL: BUY")
        elif diff_call < -threshold:
            print("📉 CALL: SELL")
        else:
            print("⚖️ CALL: HOLD")

    if diff_put is not None:
        if diff_put > threshold:
            print("📈 PUT: BUY")
        elif diff_put < -threshold:
            print("📉 PUT: SELL")
        else:
            print("⚖️ PUT: HOLD")


if __name__ == "__main__":
    main()