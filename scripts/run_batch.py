import json
from pathlib import Path
from pipeline import run_company

config_path = Path(__file__).resolve().parent.parent / "config" / "companies.json"

with open(config_path, "r", encoding="utf-8") as f:
    companies = json.load(f)

BATCH_SIZE = 1  # one company per run, to safely fit the 50-requests-per-12-hours limit

todo = [c for c in companies if not c["done"]]
batch = todo[:BATCH_SIZE]

if not batch:
    print("All companies already processed!")
else:
    print(f"Processing: {[c['name'] for c in batch]}\n")
    for c in batch:
        result = run_company(c["name"], c["ticker"])
        # Only mark done if we actually got enough real data
        if result and result.get("num_days", 0) >= 5:
            c["done"] = True
            print(f"  ✅ Marked {c['name']} as done ({result['num_days']} days)")
        else:
            print(f"  ⚠️ {c['name']} did not get enough data — will retry next run")

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(companies, f, indent=2)

    remaining = len([c for c in companies if not c["done"]])
    print(f"\n{remaining} companies remaining.")