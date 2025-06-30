import csv
import requests
from bs4 import BeautifulSoup
import time

symbols = [
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
]

def get_market_cap(symbol):
    url = f"https://www.screener.in/company/{symbol}/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all("li", class_="flex flex-space-between")

            for item in items:
                if "Market Cap" in item.text:
                    market_cap_text = item.find_all("span")[1].text.strip()
                    market_cap_cleaned = market_cap_text.replace(",", "").replace("₹", "").replace("Cr.", "").strip()
                    print(f"{symbol} → ₹{market_cap_text}")
                    return float(market_cap_cleaned)
    except Exception as e:
        print(f"❌ Error fetching market cap for {symbol}: {e}")
    return 0.0

def write_csv():
    with open("market_caps.csv", "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["symbol", "market_cap"])
        for symbol in symbols:
            cap = get_market_cap(symbol)
            writer.writerow([symbol, cap])
            time.sleep(1)  # To prevent blocking by Screener

if __name__ == "__main__":
    print(f"ka{len(symbols)}")
    write_csv()
