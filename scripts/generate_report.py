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
    positivity = r.get("positivity_index")

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

    if positivity is not None:
        sentence += f" Overall, the news coverage for {r['name']} had a positivity score of {positivity}/10."

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
            "positivity_index": r.get("positivity_index"),
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
  body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px;
          background: #121212; color: #e0e0e0; }}
  h1 {{ color: #7fb3ff; }}
  h2 {{ color: #7fb3ff; }}
  .updated {{ color: #999; font-size: 0.9em; margin-bottom: 10px; }}
  button {{ background: #2d5fa3; color: white; border: none; padding: 12px 24px; font-size: 1em;
            border-radius: 6px; cursor: pointer; margin-bottom: 25px; }}
  button:hover {{ background: #3a72c4; }}
  button:disabled {{ background: #555; cursor: not-allowed; }}
  img {{ max-width: 100%; margin: 20px 0; border: 1px solid #333; border-radius: 4px;
         background: #fff; padding: 8px; }}
  .company-card {{ background: #1e1e1e; border: 1px solid #333; border-radius: 6px;
                    padding: 14px 18px; margin-bottom: 12px; }}
  .company-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }}
  .company-name {{ font-weight: bold; font-size: 1.1em; color: #fff; }}
  .badge {{ color: white; font-size: 0.75em; padding: 3px 10px; border-radius: 12px; text-transform: uppercase; }}
  #status {{ color: #7fb3ff; font-style: italic; }}
  .search-box {{ background: #1a2634; border: 1px solid #2d5fa3; border-radius: 6px;
                  padding: 16px 20px; margin: 25px 0; }}
  .search-box input {{ padding: 8px 12px; margin-right: 10px; border: 1px solid #444;
                        border-radius: 4px; width: 200px; background: #2a2a2a; color: #e0e0e0; }}
  .search-box input::placeholder {{ color: #888; }}
</style>
</head>
<body>
  <h1>Stock News Sentiment vs Price Movement</h1>
  <p class="updated">Last updated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}</p>

  <button id="fetchBtn" onclick="fetchNews()">Fetch Latest News & Refresh</button>
  <p id="status"></p>

  <div class="search-box">
    <h2>Check a Different Stock</h2>
    <p style="color:#999; font-size:0.9em;">You'll need the company name and its Yahoo Finance ticker symbol (e.g. "Netflix" and "NFLX", or "Wipro" and "WIPRO.NS").</p>
    <input type="text" id="companyName" placeholder="Company name (e.g. Netflix)">
    <input type="text" id="companyTicker" placeholder="Ticker (e.g. NFLX or WIPRO.NS)">
    <label style="color:#ccc; font-size:0.9em;">News window:
      <select id="companyDays" style="padding:8px; border-radius:4px; background:#2a2a2a; color:#e0e0e0; border:1px solid #444;">
        <option value="7">Last 7 days</option>
        <option value="14">Last 14 days</option>
        <option value="30" selected>Last 30 days</option>
        <option value="60">Last 60 days</option>
        <option value="90">Last 90 days</option>
      </select>
    </label>
    <button onclick="addCompany()">Add & Analyze</button>
    <p id="addStatus"></p>
  </div>

  <h2>Your Stocks</h2>
  <div id="myCompanies"></div>

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
    function addCompany() {{
      const name = document.getElementById('companyName').value.trim();
      const ticker = document.getElementById('companyTicker').value.trim();
      const days = document.getElementById('companyDays').value;
      const status = document.getElementById('addStatus');

      if (!name || !ticker) {{
        status.innerText = "Please enter both a company name and ticker.";
        return;
      }}

      status.innerText = "Fetching and analyzing " + name + " (last " + days + " days)... this can take up to a minute.";
      fetch('/analyze_custom', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{ name: name, ticker: ticker, days: parseInt(days) }})
      }})
        .then(r => r.json())
        .then(data => {{
          if (data.error) {{
            status.innerText = "Error: " + data.error;
          }} else {{
            status.innerText = "Added!";
            saveToLocalStorage(data.company);
            renderCustomCompany(data.company);
            document.getElementById('companyName').value = '';
            document.getElementById('companyTicker').value = '';
          }}
        }})
        .catch(err => {{
          status.innerText = "Something went wrong: " + err;
        }});
    }}

    function saveToLocalStorage(company) {{
      let myStocks = JSON.parse(localStorage.getItem('myStocks') || '[]');
      myStocks = myStocks.filter(c => c.ticker !== company.ticker);  // avoid duplicates
      myStocks.push(company);
      localStorage.setItem('myStocks', JSON.stringify(myStocks));
    }}

    function renderCustomCompany(c) {{
      const container = document.getElementById('myCompanies');
      const card = document.createElement('div');
      card.className = 'company-card';
      card.innerHTML = `
        <div class="company-header">
          <span class="company-name">${{c.name}}</span>
          <span class="badge" style="background:#8e44ad">my stock</span>
        </div>
        <p>${{c.description}}</p>
      `;
      container.appendChild(card);
    }}

    function loadMyStocks() {{
      const myStocks = JSON.parse(localStorage.getItem('myStocks') || '[]');
      myStocks.forEach(c => renderCustomCompany(c));
    }}

    window.onload = loadMyStocks;
  </script>
</body>
</html>"""
    return html

if __name__ == "__main__":
    output_path = BASE / "report.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generate_html())
    print(f"Report saved to {output_path}")