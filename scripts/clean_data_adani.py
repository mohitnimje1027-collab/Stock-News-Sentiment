import json
from pathlib import Path

data_path = Path(__file__).resolve().parent.parent / "data" / "adani_headlines.json"
with open(data_path, "r", encoding="utf-8") as f:
    articles = json.load(f)

print(f"Loaded {len(articles)} raw articles")

seen_titles = set()
cleaned = []
for article in articles:
    title = article.get("title")
    if not title or title in seen_titles:
        continue
    seen_titles.add(title)
    published_at = article.get("publishedAt")
    date_only = published_at.split("T")[0] if published_at else None
    cleaned.append({
        "title": title,
        "description": article.get("description"),
        "source": article.get("source", {}).get("name"),
        "date": date_only,
        "url": article.get("url")
    })

print(f"After removing duplicates: {len(cleaned)} articles")

cleaned_path = Path(__file__).resolve().parent.parent / "data" / "adani_headlines_clean.json"
with open(cleaned_path, "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2)
print(f"Saved to {cleaned_path}")