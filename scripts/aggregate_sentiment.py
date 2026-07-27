import json
from pathlib import Path
from collections import defaultdict

# Load scored headlines
data_path = Path(__file__).resolve().parent.parent / "data" / "tesla_headlines_scored.json"
with open(data_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

# Group scores by date
daily_scores = defaultdict(list)
for article in articles:
    date = article.get("date")
    score = article.get("sentiment_score")
    if date and score is not None:
        daily_scores[date].append(score)

# Compute daily average
daily_avg = []
for date, scores in sorted(daily_scores.items()):
    avg = sum(scores) / len(scores)
    daily_avg.append({
        "date": date,
        "avg_sentiment": round(avg, 4),
        "article_count": len(scores)
    })

# Save
output_path = Path(__file__).resolve().parent.parent / "data" / "tesla_daily_sentiment.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(daily_avg, f, indent=2)

print(f"Aggregated sentiment for {len(daily_avg)} days")
print(f"Saved to {output_path}")

print("\nPreview:")
for d in daily_avg[:5]:
    print(d)