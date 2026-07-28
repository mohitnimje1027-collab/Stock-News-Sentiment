import json
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

data_path = Path(__file__).resolve().parent.parent / "data" / "adani_headlines_clean.json"
with open(data_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

analyzer = SentimentIntensityAnalyzer()
for article in articles:
    text = article.get("title") or ""
    scores = analyzer.polarity_scores(text)
    article["sentiment_score"] = scores["compound"]

output_path = Path(__file__).resolve().parent.parent / "data" / "adani_headlines_scored.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2)

print(f"Scored {len(articles)} headlines")
print(f"Saved to {output_path}")