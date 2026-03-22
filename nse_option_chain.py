
import requests
import time


def fetch_option_chain(symbol="NIFTY", retries=3):

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.nseindia.com/"
    }

    for attempt in range(retries):
        try:
            # Step 1: get cookies
            session.get("https://www.nseindia.com", headers=headers)
            time.sleep(1)

            # Step 2: endpoint
            if symbol in ["NIFTY", "BANKNIFTY", "FINNIFTY"]:
                url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
            else:
                url = f"https://www.nseindia.com/api/option-chain-equities?symbol={symbol}"

            response = session.get(url, headers=headers)

            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")

            data = response.json()

            # 🔥 Validate response
            if "records" not in data or "data" not in data["records"]:
                raise Exception("Blocked or invalid response")

            return data

        except Exception as e:
            print(f"⚠️ NSE attempt {attempt+1} failed: {e}")
            time.sleep(2)

    # ❌ After retries
    print("❌ NSE completely failed — continuing without it")
    return None


def get_atm_option_data(data, S0):

    if data is None:
        return {
            "strike": None,
            "call_price": None,
            "put_price": None,
            "call_iv": None,
            "put_iv": None,
        }

    try:
        records = data["records"]["data"]

        valid = [x for x in records if "strikePrice" in x]

        if not valid:
            raise Exception("No valid strikes")

        closest = min(valid, key=lambda x: abs(x["strikePrice"] - S0))

        ce = closest.get("CE", {})
        pe = closest.get("PE", {})

        return {
            "strike": closest["strikePrice"],
            "call_price": ce.get("lastPrice"),
            "put_price": pe.get("lastPrice"),
            "call_iv": ce.get("impliedVolatility"),
            "put_iv": pe.get("impliedVolatility"),
        }

    except Exception as e:
        print(f"⚠️ NSE parsing failed: {e}")

        return {
            "strike": None,
            "call_price": None,
            "put_price": None,
            "call_iv": None,
            "put_iv": None,
        }