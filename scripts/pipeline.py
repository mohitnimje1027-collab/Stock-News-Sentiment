import os, json, requests
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yfinance as yf
import numpy as np

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")
API_KEY = os.getenv("NEWSAPI_KEY")
BASE = Path(__file__).resolve().parent.parent / "data"

def safe_name(ticker):
    return ticker.replace(".", "_")

def run_company(name, ticker, days_back=29, price_days_back=35):
    folder = BASE / safe_name(ticker)
    folder.mkdir(parents=True, exist_ok=True)
    print(f"\n=== {name} ({ticker}) ===")

    # 1. Fetch news
    all_articles = []
    error_count = 0
    today = datetime.utcnow().date()
    for i in range(days_back):
        day = today - timedelta(days=i+1)
        date_str = day.strftime("%Y-%m-%d")
        params = {"q": name, "apiKey": API_KEY, "language": "en",
                  "from": date_str, "to": date_str, "sortBy": "publishedAt", "pageSize": 20}
        r = requests.get("https://newsapi.org/v2/everything", params=params)
        d = r.json()
        if d.get("status") != "ok":
            print(f"  {date_str}: error - {d.get('message')}")
            error_count += 1
            continue
        arts = d.get("articles", [])
        all_articles.extend(arts)

    if error_count > 0:
        print(f"  WARNING: {error_count} day(s) hit API errors — data is incomplete")
    print(f"  Fetched {len(all_articles)} raw articles")

    # 2. Clean + dedupe
    seen, cleaned = set(), []
    for a in all_articles:
        title = a.get("title")
        if not title or title in seen:
            continue
        seen.add(title)
        pub = a.get("publishedAt")
        cleaned.append({"title": title, "date": pub.split("T")[0] if pub else None,
                         "source": a.get("source", {}).get("name")})
    print(f"  Cleaned to {len(cleaned)} unique articles")

    # 3. Score sentiment
    analyzer = SentimentIntensityAnalyzer()
    for a in cleaned:
        a["sentiment_score"] = analyzer.polarity_scores(a["title"])["compound"]

    # 4. Aggregate daily
    daily = defaultdict(list)
    for a in cleaned:
        if a["date"]:
            daily[a["date"]].append(a["sentiment_score"])
    daily_avg = [{"date": d, "avg_sentiment": round(sum(s)/len(s), 4), "article_count": len(s)}
                 for d, s in sorted(daily.items())]

    # 5. Fetch price
    start = (today - timedelta(days=price_days_back)).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    price_data = yf.download(ticker, start=start, end=end, progress=False)
    if price_data.empty:
        print(f"  No price data for {ticker} — skipping")
        return None
    prices = [{"date": idx.strftime("%Y-%m-%d"), "open": round(float(row["Open"]), 2),
               "close": round(float(row["Close"]), 2),
               "pct_change": round(((float(row["Close"]) - float(row["Open"])) / float(row["Open"])) * 100, 4)}
              for idx, row in price_data.iterrows()]

    # 6. Merge
    price_by_date = {p["date"]: p for p in prices}
    merged = []
    for s in daily_avg:
        p = price_by_date.get(s["date"])
        if p:
            merged.append({**s, **p})
    print(f"  Merged {len(merged)} trading days")

    if len(merged) < 3:
        print("  Not enough merged data to correlate — skipping correlation")
        result = {"name": name, "ticker": ticker, "category": None, "num_days": len(merged),
                   "same_day_correlation": None, "lagged_correlation": None}
    else:
        merged_sorted = sorted(merged, key=lambda x: x["date"])
        sentiments = [m["avg_sentiment"] for m in merged_sorted]
        changes = [m["pct_change"] for m in merged_sorted]
        same_day = float(np.corrcoef(sentiments, changes)[0, 1])
        lagged = float(np.corrcoef(sentiments[:-1], changes[1:])[0, 1])
        result = {"name": name, "ticker": ticker, "num_days": len(merged),
                   "same_day_correlation": round(same_day, 4), "lagged_correlation": round(lagged, 4)}
        print(f"  Same-day corr: {same_day:.4f} | Lagged corr: {lagged:.4f}")

    # Save everything for this company
    with open(folder / "merged.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    with open(folder / "correlation.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    result["had_errors"] = error_count > 0
    return result