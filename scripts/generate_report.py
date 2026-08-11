import json
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent.parent / "data"

def strength_label(val):
    v = abs(val)
    if v < 0.2:
        return "very weak"
    elif v < 0.4:
        return "weak"
    elif v < 0.6:
        return "moderate"
    else:
        return "strong"

def describe_company(r):
    same_day = r.get("same_day_correlation")
    num_days = r.get("num_days", 0)

    if same_day is None:
        return f"Not enough data was available for {r['name']} to draw a conclusion."

    if same_day > 0.05:
        direction = "tended to rise"
    elif same_day < -0.05:
        direction = "tended to fall"
    else:
        direction = "showed no clear pattern"

    strength = strength_label(same_day)

    sentence = (
        f"On days with more positive news about {r['name']}, its stock price {direction}. "
        f"This pattern was {strength}"
    )

    if num_days < 12:
        sentence += f", and it's based on a small sample (only {num_days} trading days), so treat it as a rough signal, not a rule."
    else:
        sentence += f" (based on {num_days} trading days)."

    return sentence

def build_report_data():
    with open(BASE / "all_companies_summary.json", "r", encoding="utf-8") as f:
        results = json.load(f)

    companies = []
    for r in sorted(results, key=lambda x: x.get("same_day_correlation") or 0):
        companies.append({
            "name": r["name"],
            "category": r["category"],
            "num_days": r["num_days"],
            "same_day": r.get("same_day_correlation"),
            "lagged": r.get("lagged_correlation"),
            "description": describe_company(r)
        })

    return companies

def generate_html():
    companies = build_report_data()

    company_blocks = ""
    for c in companies:
        badge_color = "#1f77b4" if c["category"] == "top" else "#ff7f0e"
        company_blocks += f"""
        <div class="company-card">
          <div class="company-header">
            <span class="company-name">{c['name']}</span>
            <span class="badge" style="background:{badge_color}">{c['category']}</span>
          </div>
          <p>{c['description']}</p>
        </div>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Stock News Sentiment vs Price Movement — Report</title>
<style>
  body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; color: #222; }}
  h1 {{ color: #1f3864; }}
  .updated {{ color: #666; font-size: 0.9em; margin-bottom: 10px; }}
  button {{ background: #1f3864; color: white; border: none; padding: 12px 24px; font-size: 1em;
            border-radius: 6px; cursor: pointer; margin-bottom: 25px; }}
  button:hover {{ background: #16294d; }}
  button:disabled {{ background: #999; cursor: not-allowed; }}
  img {{ max-width: 100%; margin: 20px 0; border: 1px solid #ddd; border-radius: 4px; }}
  .company-card {{ background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 6px;
                    padding: 14px 18px; margin-bottom: 12px; }}
  .company-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .company-name {{ font-weight: bold; font-size: 1.1em; }}
  .badge {{ color: white; font-size: 0.75em; padding: 3px 10px; border-radius: 12px; text-transform: uppercase; }}
  #status {{ color: #1f3864; font-style: italic; }}
</style>
</head>
<body>
  <h1>Stock News Sentiment vs Price Movement</h1>
  <p class="updated">Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</p>

  <button id="fetchBtn" onclick="fetchNews()">Fetch Latest News & Refresh</button>
  <p id="status"></p>

  <h2>Chart</h2>
  <img src="/data/correlation_chart.png" alt="Correlation chart across 25 companies">

  <h2>What Each Stock Shows</h2>
  <div id="companies">
    {company_blocks}
  </div>

  <script>
    function fetchNews() {{
      const btn = document.getElementById('fetchBtn');
      const status = document.getElementById('status');
      btn.disabled = true;
      status.innerText = "Fetching fresh news and recalculating... this can take up to a minute.";
      fetch('/refresh', {{ method: 'POST' }})
        .then(r => r.json())
        .then(data => {{
          status.innerText = "Done! Reloading...";
          location.reload();
        }})
        .catch(err => {{
          status.innerText = "Something went wrong: " + err;
          btn.disabled = false;
        }});
    }}
  </script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    output_path = BASE / "report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generate_html())
    print(f"Report saved to {output_path}")