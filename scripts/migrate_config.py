import json
from pathlib import Path
from datetime import datetime

config_path = Path(__file__).resolve().parent.parent / "config" / "companies.json"
with open(config_path, "r", encoding="utf-8") as f:
    companies = json.load(f)

today = datetime.utcnow().strftime("%Y-%m-%d")
for c in companies:
    if c.get("done"):
        c["last_updated"] = today
    else:
        c["last_updated"] = None
    if "done" in c:
        del c["done"]

with open(config_path, "w", encoding="utf-8") as f:
    json.dump(companies, f, indent=2)

print("Migrated config to last_updated format")