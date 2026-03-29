from arch import arch_model
import numpy as np

def forecast_volatility(returns):
    """
    GARCH(1,1) volatility forecast
    """

    returns = returns.dropna()

    if len(returns) < 50:
        raise ValueError("Not enough data for GARCH")

    # Scale for numerical stability
    scaled_returns = returns * 100

    model = arch_model(scaled_returns, vol='Garch', p=1, q=1)
    result = model.fit(disp="off")

    # Conditional volatility series
    cond_vol = result.conditional_volatility / 100

    return cond_vol
