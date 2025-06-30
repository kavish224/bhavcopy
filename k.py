import json
import requests

# Your required stock/index symbols (case-sensitive for consistency)
required_symbols = {
    # Key Indices
    "NIFTY", "BANKNIFTY", "FINNIFTY", "NIFTY MIDCAP 100",
    "NIFTY NEXT 50", "NIFTY 100", "NIFTY 200", "NIFTY 500",
    "NIFTY MIDCAP 50", "NIFTY SMLCAP 100", "NIFTY IT", "NIFTY FMCG",
    "NIFTY AUTO", "NIFTY PHARMA", "NIFTY ENERGY", "NIFTY INFRA",
    "NIFTY METAL", "NIFTY REALTY", "NIFTY PSU BANK", "INDIA VIX",

    # Nifty 50 stocks
    "ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK",
    "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL",
    "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT", "ETERNAL",
    "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO",
    "HINDALCO", "HINDUNILVR", "ICICIBANK", "ITC", "INDUSINDBK",
    "INFY", "JSWSTEEL", "JIOFIN", "KOTAKBANK", "LT",
    "M&M", "MARUTI", "NTPC", "NESTLEIND", "ONGC",
    "POWERGRID", "RELIANCE", "SBILIFE", "SHRIRAMFIN", "SBIN",
    "SUNPHARMA", "TCS", "TATACONSUM", "TATAMOTORS", "TATASTEEL",
    "TECHM", "TITAN", "TRENT", "ULTRACEMCO", "WIPRO"
}


# Fetch Angel One instruments dump
url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
response = requests.get(url)
data = response.json()

symbol_to_token = {}

for item in data:
    token = item.get("token")
    symbol = item.get("symbol", "")
    name = item.get("name", "").upper()
    exch_seg = item.get("exch_seg", "")
    
    # For stocks: match symbol like "RELIANCE-EQ" → "RELIANCE"
    if symbol.endswith("-EQ") and exch_seg.lower() == "nse":
        stock = symbol.replace("-EQ", "")
        if stock in required_symbols:
            symbol_to_token[stock] = token

    # For indices (e.g., NIFTY, BANKNIFTY) — usually AMXIDX instrument type
    if exch_seg == "NSE" and name in required_symbols:
        symbol_to_token[name] = token

# Save the mapping
with open("symbol_to_token.json", "w") as f:
    json.dump(symbol_to_token, f, indent=2)

print(f"✅ Saved mapping for {len(symbol_to_token)} symbols.")
