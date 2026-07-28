import json
from pathlib import Path
import numpy as np

base = Path(__file__).resolve().parent.parent / "data"

with open(base / "tesla_merged.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Sort by date to make lagging correct
data = sorted(data, key=lambda x: x["date"])

sentiments = [d["avg_sentiment"] for d in data]
pct_changes = [d["pct_change"] for d in data]
dates = [d["date"] for d in data]

print(f"Analyzing {len(data)} days of data\n")

# --- Same-day correlation ---
same_day_corr = np.corrcoef(sentiments, pct_changes)[0, 1]
print(f"Same-day correlation (sentiment vs price change same day): {same_day_corr:.4f}")

# --- Lagged correlation: today's sentiment vs TOMORROW's price change ---
if len(data) > 1:
    lagged_sentiment = sentiments[:-1]       # sentiment on day t
    next_day_change = pct_changes[1:]        # price change on day t+1
    lagged_corr = np.corrcoef(lagged_sentiment, next_day_change)[0, 1]
    print(f"Lagged correlation (sentiment vs NEXT day's price change): {lagged_corr:.4f}")

# --- Print the raw data so it's easy to eyeball ---
print("\nDate       | Sentiment | Price % Change")
print("-" * 45)
for d in data:
    print(f"{d['date']} |  {d['avg_sentiment']:+.4f}  |  {d['pct_change']:+.2f}%")

# Save results summary
results = {
    "num_days": len(data),
    "same_day_correlation": round(float(same_day_corr), 4),
    "lagged_correlation": round(float(lagged_corr), 4) if len(data) > 1 else None
}

output_path = base / "correlation_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved summary to {output_path}")