import json
from pathlib import Path
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent / "data"

with open(BASE / "all_companies_summary.json", "r", encoding="utf-8") as f:
    results = json.load(f)

names = [r["name"] for r in results]
same_day = [r["same_day_correlation"] for r in results]
colors = ["#1f77b4" if r["category"] == "top" else "#ff7f0e" for r in results]

fig, ax = plt.subplots(figsize=(10, 12))
ax.barh(names, same_day, color=colors)
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Same-Day Correlation (Sentiment vs Price Change)")
ax.set_title("News Sentiment vs Stock Price Correlation Across 25 Companies")

# Legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor="#1f77b4", label="Top-cap"),
                    Patch(facecolor="#ff7f0e", label="Underdog")]
ax.legend(handles=legend_elements, loc="lower right")

plt.tight_layout()
output_path = BASE / "correlation_chart.png"
plt.savefig(output_path, dpi=150)
print(f"Saved chart to {output_path}")