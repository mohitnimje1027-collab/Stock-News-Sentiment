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

    # 1. Fetch news via Google News RSS (unlimited, no API key)
    import feedparser
    from urllib.parse import quote

    today = datetime.utcnow().date()
    query = quote(f"{name} stock")
    rss_url = f"https://news.google.com/rss/search?q={query}+when:30d&hl=en-IN&gl=IN&ceid=IN:en"
    feed = feedparser.parse(rss_url)

    all_articles = []
    for entry in feed.entries:
        title = entry.get("title", "")
        published = entry.get("published_parsed")
        if published:
            date_str = datetime(*published[:6]).strftime("%Y-%m-%d")
        else:
            date_str = None
        all_articles.append({
            "title": title,
            "publishedAt": date_str + "T00:00:00Z" if date_str else None,
            "source": {"name": entry.get("source", {}).get("title", "Google News") if hasattr(entry, "source") else "Google News"}
        })

    error_count = 0  # RSS doesn't hit quota errors
    print(f"  Fetched {len(all_articles)} raw articles (via RSS)")

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
    if daily_avg:
        overall_avg_sentiment = sum(d["avg_sentiment"] for d in daily_avg) / len(daily_avg)
    else:
        overall_avg_sentiment = 0

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
        positivity_index = round((overall_avg_sentiment + 1) * 5, 1)  # converts -1..+1 scale to 0..10
        result = {"name": name, "ticker": ticker, "num_days": len(merged),
                    "same_day_correlation": None, "lagged_correlation": None,
                    "positivity_index": positivity_index}
    else:
        merged_sorted = sorted(merged, key=lambda x: x["date"])
        # Filter out any rows with NaN/missing values before correlating
        clean_rows = [m for m in merged_sorted
                      if m.get("avg_sentiment") is not None and m.get("pct_change") is not None
                      and not (isinstance(m["avg_sentiment"], float) and np.isnan(m["avg_sentiment"]))
                      and not (isinstance(m["pct_change"], float) and np.isnan(m["pct_change"]))]

        if len(clean_rows) < len(merged_sorted):
            print(f"  Filtered out {len(merged_sorted) - len(clean_rows)} row(s) with missing values")

        sentiments = [m["avg_sentiment"] for m in clean_rows]
        changes = [m["pct_change"] for m in clean_rows]

        if len(clean_rows) < 3:
            print("  Not enough clean data after filtering — skipping correlation")
            result = {"name": name, "ticker": ticker, "num_days": len(clean_rows),
                       "same_day_correlation": None, "lagged_correlation": None}
        else:
            same_day = float(np.corrcoef(sentiments, changes)[0, 1])
            lagged = float(np.corrcoef(sentiments[:-1], changes[1:])[0, 1])
            positivity_index = round((overall_avg_sentiment + 1) * 5, 1)  # converts -1..+1 scale to 0..10
            result = {"name": name, "ticker": ticker, "num_days": len(clean_rows),
                       "same_day_correlation": round(same_day, 4), "lagged_correlation": round(lagged, 4),
                       "positivity_index": positivity_index}
            print(f"  Same-day corr: {same_day:.4f} | Lagged corr: {lagged:.4f}")
        

    # Save everything for this company
    with open(folder / "merged.json", "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    with open(folder / "correlation.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    result["had_errors"] = error_count > 0
    return result