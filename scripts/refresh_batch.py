import json, subprocess, sys
from pathlib import Path
from datetime import datetime
from pipeline import run_company

config_path = Path(__file__).resolve().parent.parent / "config" / "companies.json"
BATCH_SIZE = 25  # stays safely under the 50-requests-per-12-hours limit

with open(config_path, "r", encoding="utf-8") as f:
    companies = json.load(f)

# Sort so companies never updated (None) come first, then oldest date first
def sort_key(c):
    return (c["last_updated"] is not None, c["last_updated"] or "")

companies_sorted = sorted(companies, key=sort_key)
batch = companies_sorted[:BATCH_SIZE]

print(f"Refreshing: {[c['name'] for c in batch]}\n")
today = datetime.utcnow().strftime("%Y-%m-%d")

for c in batch:
    result = run_company(c["name"], c["ticker"])
    if result and result.get("num_days", 0) >= 5 and not result.get("had_errors", False):
        c["last_updated"] = today
        print(f"  Refreshed {c['name']} (last_updated = {today})")
    else:
        print(f"  {c['name']} refresh incomplete — will retry next run")

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(companies, f, indent=2)

# Regenerate summary and chart automatically after refreshing
print("\nRegenerating summary and chart...")
subprocess.run([sys.executable, str(Path(__file__).parent / "summary.py")])
subprocess.run([sys.executable, str(Path(__file__).parent / "visualize.py")])
subprocess.run([sys.executable, str(Path(__file__).parent / "generate_report.py")])
print("\nRefresh cycle complete.")