import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data"
config_path = Path(__file__).resolve().parent.parent / "config" / "companies.json"

with open(config_path, "r", encoding="utf-8") as f:
    companies = json.load(f)

results = []
for c in companies:
    ticker_safe = c["ticker"].replace(".", "_")
    corr_path = BASE / ticker_safe / "correlation.json"
    if corr_path.exists():
        with open(corr_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            data["category"] = c["category"]
            results.append(data)

# Sort by same-day correlation strength (most negative to most positive)
results_sorted = sorted(
    [r for r in results if r.get("same_day_correlation") is not None],
    key=lambda x: x["same_day_correlation"]
)

print(f"{'Company':<25} {'Category':<10} {'Days':<6} {'Same-Day':<10} {'Lagged':<10}")
print("-" * 65)
for r in results_sorted:
    print(f"{r['name']:<25} {r['category']:<10} {r['num_days']:<6} "
          f"{r['same_day_correlation']:<10.4f} {r.get('lagged_correlation', 0):<10.4f}")

# Basic stats
same_day_vals = [r["same_day_correlation"] for r in results_sorted]
lagged_vals = [r["lagged_correlation"] for r in results_sorted if r.get("lagged_correlation") is not None]

avg_same_day = sum(same_day_vals) / len(same_day_vals)
avg_lagged = sum(lagged_vals) / len(lagged_vals)

print(f"\nAverage same-day correlation across {len(same_day_vals)} companies: {avg_same_day:.4f}")
print(f"Average lagged correlation across {len(lagged_vals)} companies: {avg_lagged:.4f}")

# By category
top_vals = [r["same_day_correlation"] for r in results_sorted if r["category"] == "top"]
underdog_vals = [r["same_day_correlation"] for r in results_sorted if r["category"] == "underdog"]

if top_vals:
    print(f"\nTop-cap avg same-day correlation: {sum(top_vals)/len(top_vals):.4f} (n={len(top_vals)})")
if underdog_vals:
    print(f"Underdog avg same-day correlation: {sum(underdog_vals)/len(underdog_vals):.4f} (n={len(underdog_vals)})")

# Save full summary
output_path = BASE / "all_companies_summary.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results_sorted, f, indent=2)
print(f"\nSaved full summary to {output_path}")