import sys
print("Python running this app:", sys.executable)
import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
import plotly.graph_objects as go

# Prevent memory leak for sklearn/HMM
os.environ["OMP_NUM_THREADS"] = "1"

# Path fix
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_PATH = os.path.join(BASE_DIR, "src")
sys.path.append(SRC_PATH)

# ---------- IMPORT MODULES ----------
from data_collector import get_stock_data
from returns_calculator import compute_returns
from garch_model import forecast_volatility
from monte_carlo import simulate_prices_dynamic
from markov_model import detect_regimes, get_regime_data, compute_regime_parameters
from black_scholes_merton import black_scholes_price, implied_volatility
from nse_option_chain import fetch_option_chain, get_atm_option_data

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="ANUSH Trading Dashboard", layout="wide")
st.title("📊 ANUSH Trading Dashboard")

# ---------- SIDEBAR INPUTS ----------
st.sidebar.header("⚙️ Controls")
stock = st.sidebar.text_input("Stock / Index", "NIFTY").upper()
days = st.sidebar.number_input("Simulation Days", min_value=1, max_value=365, value=30, step=1)
sims = st.sidebar.number_input("Number of Simulations", min_value=100, max_value=20000, value=1000, step=100)
seed_input = st.sidebar.text_input("Random Seed (optional)")
seed = int(seed_input) if seed_input.isdigit() else None
run_btn = st.sidebar.button("🚀 Run Model")

# ---------- PIPELINE FUNCTION ----------
def run_pipeline(stock, days, sims, seed=None):
    result = {}
    
    # SYMBOL HANDLING
    if stock == "NIFTY":
        yf_symbol = "^NSEI"
    elif stock == "BANKNIFTY":
        yf_symbol = "^NSEBANK"
    elif stock == "FINNIFTY":
        yf_symbol = "^NSEFIN"
    else:
        yf_symbol = stock + ".NS"
    
    # FETCH DATA
    data = get_stock_data(yf_symbol)
    if data is None or data.empty or "Close" not in data.columns:
        return None
    
    # RETURNS
    data, _ = compute_returns(data)
    returns = data["Returns"].dropna().reset_index(drop=True)
    if len(returns) == 0:
        return None
    
    # HMM REGIMES
    returns_array = returns.values.reshape(-1, 1)
    states, model = detect_regimes(returns_array)
    regime_returns, regime = get_regime_data(returns, states)
    mu_hmm, sigma_hmm = compute_regime_parameters(regime_returns)
    
    # GARCH VOL
   try:
    sigma_garch = forecast_volatility(returns)
    sigma_garch_value = sigma_garch.mean()
except Exception as e:
    print("GARCH error:", e)
    sigma_garch = pd.Series(np.zeros_like(returns), index=returns.index)
    sigma_garch_value = 0

# Combine HMM + GARCH volatility
sigma = float(0.6 * sigma_garch_value + 0.4 * sigma_hmm)
    # MONTE CARLO SIMULATION
    S0 = float(data["Close"].iloc[-1])
    sim = simulate_prices_dynamic(S0, regime_returns, days=days, sims=sims, seed=seed)
    final_prices = sim[-1].flatten()
    expected_price = np.mean(final_prices)
    prob_up = np.mean(final_prices > S0)
    
    # BLACK-SCHOLES
    K = S0
    T = days / 252
    r = 0.06
    call_price = black_scholes_price(S0, K, T, r, sigma, "call")
    put_price = black_scholes_price(S0, K, T, r, sigma, "put")
    
    # NSE OPTION CHAIN
    try:
        oc_data = fetch_option_chain(stock)
        atm_data = get_atm_option_data(oc_data, S0)
        market_call = atm_data["call_price"]
        market_put = atm_data["put_price"]
    except:
        oc_data, atm_data = None, None
        market_call, market_put = None, None
    
    # IMPLIED VOL
    iv_call = implied_volatility(S0, K, T, r, market_call, "call") if market_call else None
    iv_put = implied_volatility(S0, K, T, r, market_put, "put") if market_put else None
    
    # MODEL VS MARKET
    diff_call = call_price - market_call if market_call else None
    diff_put = put_price - market_put if market_put else None
    
    # SIGNALS
    threshold = 2
    call_signal = "BUY" if diff_call is not None and diff_call > threshold else \
                  "SELL" if diff_call is not None and diff_call < -threshold else "HOLD"
    put_signal = "BUY" if diff_put is not None and diff_put > threshold else \
                 "SELL" if diff_put is not None and diff_put < -threshold else "HOLD"
    
    # RETURN DICT
    result.update({
        "stock": stock,
        "regime": regime,
        "volatility": sigma,
        "price": data["Close"],
        "vol_series": sigma_garch,
        "expected_price": expected_price,
        "prob_up": prob_up,
        "call_price": call_price,
        "put_price": put_price,
        "market_call": market_call,
        "market_put": market_put,
        "iv_call": iv_call,
        "iv_put": iv_put,
        "diff_call": diff_call,
        "diff_put": diff_put,
        "call_signal": call_signal,
        "put_signal": put_signal,
        "option_chain": oc_data,
        "debug_data": data
    })
    return result

# ---------- MAIN ----------
if run_btn:
    st.subheader(f"📍 Results for {stock}")
    data = run_pipeline(stock, days, sims, seed)

    if data is None:
        st.warning("❌ Failed to fetch data or run model")
    else:
        # METRICS
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Current Price", f"{data['price'].iloc[-1]:.2f}")
        col2.metric("Expected Price", f"{data['expected_price']:.2f}")
        col3.metric("Market Regime", data["regime"])
        col4.metric("Volatility (σ)", f"{data['volatility']:.4f}")
        col5.metric("Prob UP", f"{data['prob_up']*100:.2f}%")
        
        # TABS
        tab1, tab2, tab3 = st.tabs(["Charts", "Option Chain", "Signals & Debug"])
        
        # ---------- CHARTS ----------
        with tab1:
            st.subheader("📈 Price Chart")
            fig_price = go.Figure()
            fig_price.add_trace(go.Scatter(x=data["price"].index, y=data["price"].values, mode='lines', name="Price"))
            fig_price.update_layout(title=f"{stock} Price", xaxis_title="Time", yaxis_title="Price")
            st.plotly_chart(fig_price, use_container_width=True)
            
            st.subheader("📊 Volatility Trend")
            fig_vol = go.Figure()
            vol_series = data["vol_series"]
            if isinstance(vol_series, (pd.Series, pd.DataFrame)):
                fig_vol.add_trace(go.Scatter(x=vol_series.index, y=vol_series.values, mode='lines', name="Volatility"))
            fig_vol.update_layout(title=f"{stock} Volatility", xaxis_title="Time", yaxis_title="Volatility")
            st.plotly_chart(fig_vol, use_container_width=True)
        
        # ---------- OPTION CHAIN ----------
        with tab2:
            st.subheader("📉 Option Chain Snapshot")
            if data["option_chain"] is not None:
                st.dataframe(data["option_chain"].style.format("{:.2f}"), use_container_width=True)
            else:
                st.info("No option chain data available")
        
        # ---------- SIGNALS & DEBUG ----------
        with tab3:
            st.subheader("💹 Model vs Market Option Prices")
            st.write({
                "Call Price (Model)": data["call_price"],
                "Put Price (Model)": data["put_price"],
                "Market Call": data["market_call"],
                "Market Put": data["market_put"],
                "Call IV": data["iv_call"],
                "Put IV": data["iv_put"],
                "Call Mispricing": data["diff_call"],
                "Put Mispricing": data["diff_put"]
            })
            
            st.subheader("📊 Trading Signals")
            st.markdown(f"**CALL:** <span style='color:{'green' if data['call_signal']=='BUY' else 'red' if data['call_signal']=='SELL' else 'orange'}'>{data['call_signal']}</span>", unsafe_allow_html=True)
            st.markdown(f"**PUT:** <span style='color:{'green' if data['put_signal']=='BUY' else 'red' if data['put_signal']=='SELL' else 'orange'}'>{data['put_signal']}</span>", unsafe_allow_html=True)
            
            st.subheader("🔍 Debug Data (last 10 rows)")
            st.dataframe(data["debug_data"].tail(10))
