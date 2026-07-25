import os
import requests
import json
from dotenv import load_dotenv

# Load API key from .env file
from pathlib import Path
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("NEWSAPI_KEY")

def fetch_headlines(company="Tesla", page_size=50):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": company,
        "apiKey": API_KEY,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": page_size
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "ok":
        print("Error:", data)
        return

    articles = data["articles"]
    print(f"Fetched {len(articles)} articles for '{company}'")

    # Save to a JSON file in the data folder
    data_path = Path(__file__).resolve().parent.parent / "data" / "tesla_headlines.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2)

    print(f"Saved to {data_path}")

if __name__ == "__main__":
    fetch_headlines()