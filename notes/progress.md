# 📅 Project Development Progress & Milestones

This log documents the iterative development journey of the **Stock News Sentiment vs Price Movement** project across its development cycle.

---

### Milestone 1: Foundation & Single-Stock Pipeline (Days 1–7)
- **Data Acquisition**: Integrated NewsAPI to pull daily news headlines for Tesla (`TSLA`).
- **Data Cleaning**: Implemented normalization and title deduplication pipelines (`clean_data.py`).
- **Sentiment Scoring**: Integrated VADER (`SentimentIntensityAnalyzer`) to extract headline polarity compound scores (`score_sentiment.py`).
- **Market Data Alignment**: Integrated `yfinance` to fetch historical Open, Close, and calculate percentage price fluctuations (`fetch_price.py`).
- **Data Merging**: Synchronized sentiment timestamps with active market trading days (`merge_data.py`).
- **Statistical Correlation**: Built first correlation model measuring same-day and 1-day lagged Pearson correlation ($r$).

---

### Milestone 2: Multi-Company Expansion (Days 8–19)
- Scaled pipeline across a diverse basket of equities:
  - **Large-Cap / Tech Giants**: Apple, Microsoft, Amazon, Alphabet, Nvidia, Reliance, TCS, Infosys, HDFC Bank, ITC, Adani Enterprises.
  - **Mid-Cap / Emerging Underdogs**: Adani Power, Zomato (Eternal), Paytm, IRCTC, Delhivery, Happiest Minds, Latent View, Angel One, Tejas Networks, CarTrade, Route Mobile, IEX, Yatra Online.
- Built individual JSON storage architecture under `data/<TICKER>/`.

---

### Milestone 3: Comparative Analysis & Visualization (Days 20–22)
- Built `summary.py` to aggregate statistics across all monitored equities.
- Developed `visualize.py` using Matplotlib to generate horizontal comparative correlation charts.
- Overcame API quota barriers by transitioning from NewsAPI to Google News RSS feeds with automated URI query encoding (`feedparser`), unlocking unlimited headline retrieval without API keys.
- Established automated batch refresh mechanism (`refresh_batch.py`).

---

### Milestone 4: Interactive Web Application & UX (Days 23–25)
- Developed Flask web application (`app.py`) serving live dynamic dashboards (`generate_report.py`).
- Implemented human-readable plain-English narrative interpretations for each stock based on correlation thresholds and sample sizes.
- Converted compound sentiment scores into an intuitive **0–10 Positivity Index**.
- Refactored frontend to a sleek, modern **Dark Mode** design.
- Added live on-demand custom stock search enabling analysis of any Yahoo Finance ticker.

---

### Milestone 5: Production Hardening & Cloud Deployment (Days 26–28+)
- Added client-side persistence using HTML5 `localStorage` so custom stock additions persist across browser sessions without cluttering shared server state.
- Resolved serverless / free-tier HTTP request timeouts (e.g. Render 30s limit) by re-architecting custom stock analysis into an asynchronous background worker (`threading` + UUID task queue) with frontend polling (`/analyze_custom` and `/job_status/<job_id>`).
- Configured production WSGI deployment via `Gunicorn` and created `Procfile` and pinned `requirements.txt`.
- Finalized repository documentation, environment templates, and licensing.
