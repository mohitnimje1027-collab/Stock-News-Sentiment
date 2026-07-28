import json
from pathlib import Path
import numpy as np

base = Path(__file__).resolve().parent.parent / "data"
with open(base / "adani_merged.json", "r", encoding="utf-8") as f:
    data = json.load(f)

data = sorted(data, key=lambda x: x["date"])
sentiments = [d["avg_sentiment"] for d in data]
pct_changes = [d["pct_change"] for d in data]

print(f"Analyzing {len(data)} days of data\n")

same_day_corr = np.corrcoef(sentiments, pct_changes)[0, 1]
print(f"Same-day correlation: {same_day_corr:.4f}")

lagged_sentiment = sentiments[:-1]
next_day_change = pct_changes[1:]
lagged_corr = np.corrcoef(lagged_sentiment, next_day_change)[0, 1]
print(f"Lagged correlation (next day): {lagged_corr:.4f}")

print("\nDate       | Sentiment | Price % Change")
print("-" * 45)
for d in data:
    print(f"{d['date']} |  {d['avg_sentiment']:+.4f}  |  {d['pct_change']:+.2f}%")

results = {
    "num_days": len(data),
    "same_day_correlation": round(float(same_day_corr), 4),
    "lagged_correlation": round(float(lagged_corr), 4)
}
output_path = base / "adani_correlation_results.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print(f"\nSaved to {output_path}")