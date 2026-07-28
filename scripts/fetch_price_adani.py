import yfinance as yf
import json
from pathlib import Path
from datetime import datetime, timedelta

def fetch_prices(ticker="ADANIPOWER.NS", days_back=35):
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)

    data = yf.download(ticker, start=start_date.strftime("%Y-%m-%d"),
                        end=end_date.strftime("%Y-%m-%d"), progress=False)

    if data.empty:
        print("No price data returned — check ticker or date range.")
        return

    records = []
    for date, row in data.iterrows():
        records.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "close": round(float(row["Close"]), 2),
            "pct_change": round(((float(row["Close"]) - float(row["Open"])) / float(row["Open"])) * 100, 4)
        })

    print(f"Fetched {len(records)} trading days for {ticker}")
    output_path = Path(__file__).resolve().parent.parent / "data" / "adani_prices.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Saved to {output_path}")
    print("\nPreview:")
    for r in records[:5]:
        print(r)

if __name__ == "__main__":
    fetch_prices()