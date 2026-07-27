import json
from pathlib import Path
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load cleaned headlines
data_path = Path(__file__).resolve().parent.parent / "data" / "tesla_headlines_clean.json"
with open(data_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

analyzer = SentimentIntensityAnalyzer()

for article in articles:
    text = article.get("title") or ""
    scores = analyzer.polarity_scores(text)
    article["sentiment_score"] = scores["compound"]  # ranges from -1 (very negative) to +1 (very positive)

# Save with sentiment scores added
output_path = Path(__file__).resolve().parent.parent / "data" / "tesla_headlines_scored.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(articles, f, indent=2)

print(f"Scored {len(articles)} headlines")
print(f"Saved to {output_path}")

# Quick preview of first 5
print("\nSample scores:")
for a in articles[:5]:
    print(f"{a['sentiment_score']:.2f} | {a['title']}")