
import numpy as np
from hmmlearn.hmm import GaussianHMM
from sklearn.preprocessing import StandardScaler


# -----------------------------
# STEP 1: Detect Regimes (HMM)
# -----------------------------
def detect_regimes(returns, n_states=3):
    """
    Detect hidden market regimes using Gaussian HMM
    """

    scaler = StandardScaler()

    # ✅ Ensure correct shape
    returns = np.array(returns).reshape(-1, 1)

    # ✅ Scale data (IMPORTANT for convergence)
    returns_scaled = scaler.fit_transform(returns)

    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=2000,
        random_state=42
    )

    model.fit(returns_scaled)

    states = model.predict(returns_scaled)

    return states, model


# -----------------------------
# STEP 2: Extract Regime Data
# -----------------------------
def get_regime_data(returns, states):
    """
    Get returns corresponding to the current regime
    """

    returns = np.array(returns)
    states = np.array(states)

    if len(returns) != len(states):
        raise ValueError("Returns and states length mismatch.")

    # ✅ Current regime = last state
    current_state = states[-1]

    # ✅ Filter returns for that regime
    regime_returns = returns[states == current_state]

    if len(regime_returns) == 0:
        raise ValueError("No data points found for detected regime.")

    return regime_returns, current_state


# -----------------------------
# STEP 3: Compute Parameters
# -----------------------------
def compute_regime_parameters(regime_returns):
    """
    Compute drift (mu) and volatility (sigma)
    """

    regime_returns = np.array(regime_returns)

    mu = np.mean(regime_returns)
    sigma = np.std(regime_returns)

    # ✅ Safety fallback
    if np.isnan(mu) or np.isnan(sigma):
        raise ValueError("Invalid regime statistics.")

    return float(mu), float(sigma)