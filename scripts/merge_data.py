import json
from pathlib import Path

base = Path(__file__).resolve().parent.parent / "data"

with open(base / "tesla_daily_sentiment.json", "r", encoding="utf-8") as f:
    sentiment = json.load(f)

with open(base / "tesla_prices.json", "r", encoding="utf-8") as f:
    prices = json.load(f)

# Index price data by date for easy lookup
price_by_date = {p["date"]: p for p in prices}

merged = []
for s in sentiment:
    date = s["date"]
    price = price_by_date.get(date)
    if price:
        merged.append({
            "date": date,
            "avg_sentiment": s["avg_sentiment"],
            "article_count": s["article_count"],
            "open": price["open"],
            "close": price["close"],
            "pct_change": price["pct_change"]
        })

print(f"Merged {len(merged)} days where both sentiment and price data exist")

output_path = base / "tesla_merged.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(merged, f, indent=2)

print(f"Saved to {output_path}")

print("\nPreview:")
for m in merged[:5]:
    print(m)