# stock-and-optionpricing-repo
i have made a stock probablity predivtor and option pricing simulator...it is very staright foward


ANUSH Model

ANUSH is an advanced algorithmic trading model designed for analyzing financial markets using a combination of statistical and machine learning techniques. It integrates GARCH volatility modeling, Hidden Markov Models (HMM) for market regime detection, and real-time NSE option chain data to provide actionable insights for trading strategies.


---

Features

Volatility Forecasting: Implements GARCH models to predict market volatility accurately.

Regime Detection: Uses HMM to identify market regimes (bull, bear, or sideways).

Option Chain Analysis: Fetches live NSE option chain data to inform trading decisions.

Integrated Pipeline: All modules are combined into a streamlined pipeline for automated execution.

Modular Design: Each module is separate for easy modification and experimentation.



---

Installation

1. Clone the repository:



git clone <your-repo-link>
cd anush-model

2. Set up a virtual environment (recommended):



python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

3. Install required dependencies:



pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

Key libraries: numpy, pandas, scipy, statsmodels, hmmlearn, scikit-learn, arch, scipy, requests.


---

Usage

1. Running the main pipeline:



python main_pipeline.py

2. Module Overview:



Module	Description

garch_model.py	Handles volatility forecasting using GARCH models
markov_model.py	Performs market regime detection using HMM
data_collector.py	Collects NSE option chain data for analysis


3. Configuration:



Update config.py to set your preferred stocks, indices, or data parameters.


---

Notes & Best Practices

Data Blocking: NSE may block frequent requests. Use throttling or caching to avoid IP bans.(quarter of code dosent work if this happens pls make sure it dosent happen)

Historical Data: HMM requires sufficient historical data for reliable regime detection.

GARCH Model: Ensure enough historical volatility data for accurate predictions.

Modular Pipeline: You can run individual modules independently to test or tweak components before full integration.

Logging: All modules have basic logging enabled for debugging and performance monitoring.

If hmmlearn library doesnt work on vscode try installing anaconda or miniconda and try running the prompt on the anaconda prompt

this version is still in alpha so dont expect best of the best result

use python 3.11 and vscode and anaconda for best result

run the main pipeline only for the results and enter the output in the terminal

it only runs nifty 50 stocks and indices
 
also there is a dormant file app.py which orginally meant to create ui dashboard for the anush model....i had to scrape it due to a problem of integrating the markov_model.py file into streamlit which ran me into a barrage of problems...if you want to try to fix it...install streamlit libraries and try to integrate it

also i should update the requirement txt file......(even though i named most of the libraries)

also a huge thanks to veritasium for the inspiration on the option pricing video...be sure to check it out

Contributing

Contributions are welcome:

Fork the repository

Create a feature branch

Submit a pull request with detailed explanation(even though the project is public....rules pa thambi RULES)



---

License

© 2026 ANUSH Project. All rights reserved. No license granted. Unauthorized use, reproduction, or distribution of this software is prohibited.
