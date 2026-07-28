import json
from pathlib import Path
from collections import defaultdict

data_path = Path(__file__).resolve().parent.parent / "data" / "adani_headlines_scored.json"
with open(data_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

daily_scores = defaultdict(list)
for article in articles:
    date = article.get("date")
    score = article.get("sentiment_score")
    if date and score is not None:
        daily_scores[date].append(score)

daily_avg = []
for date, scores in sorted(daily_scores.items()):
    avg = sum(scores) / len(scores)
    daily_avg.append({"date": date, "avg_sentiment": round(avg, 4), "article_count": len(scores)})

output_path = Path(__file__).resolve().parent.parent / "data" / "adani_daily_sentiment.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(daily_avg, f, indent=2)

print(f"Aggregated sentiment for {len(daily_avg)} days")
print(f"Saved to {output_path}")