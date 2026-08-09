import json
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "data"

# Tesla
with open(BASE / "correlation_results.json", "r", encoding="utf-8") as f:
    tesla = json.load(f)
tesla_result = {
    "name": "Tesla", "ticker": "TSLA", "num_days": tesla["num_days"],
    "same_day_correlation": tesla["same_day_correlation"],
    "lagged_correlation": tesla["lagged_correlation"], "had_errors": False
}
with open(BASE / "TSLA" / "correlation.json", "w", encoding="utf-8") as f:
    json.dump(tesla_result, f, indent=2)

# Adani Power
with open(BASE / "adani_correlation_results.json", "r", encoding="utf-8") as f:
    adani = json.load(f)
adani_result = {
    "name": "Adani Power", "ticker": "ADANIPOWER.NS", "num_days": adani["num_days"],
    "same_day_correlation": adani["same_day_correlation"],
    "lagged_correlation": adani["lagged_correlation"], "had_errors": False
}
with open(BASE / "ADANIPOWER_NS" / "correlation.json", "w", encoding="utf-8") as f:
    json.dump(adani_result, f, indent=2)

print("Migrated Tesla and Adani Power to new format")