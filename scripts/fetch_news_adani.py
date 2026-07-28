import os
import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_headlines(company="Adani Power", days_back=29):
    url = "https://newsapi.org/v2/everything"
    all_articles = []
    today = datetime.utcnow().date()

    for i in range(days_back):
        day = today - timedelta(days=i+1)
        date_str = day.strftime("%Y-%m-%d")
        params = {
            "q": company, "apiKey": API_KEY, "language": "en",
            "from": date_str, "to": date_str,
            "sortBy": "publishedAt", "pageSize": 20
        }
        response = requests.get(url, params=params)
        data = response.json()
        if data.get("status") != "ok":
            print(f"Error on {date_str}:", data.get("message"))
            continue
        articles = data.get("articles", [])
        print(f"{date_str}: {len(articles)} articles")
        all_articles.extend(articles)

    print(f"\nTotal fetched: {len(all_articles)} articles")
    data_path = Path(__file__).resolve().parent.parent / "data" / "adani_headlines.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, indent=2)
    print(f"Saved to {data_path}")

if __name__ == "__main__":
    fetch_headlines()