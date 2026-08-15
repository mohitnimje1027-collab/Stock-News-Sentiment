from flask import Flask, send_from_directory, jsonify
from pathlib import Path
import subprocess, sys
import threading
import uuid

app = Flask(__name__)
jobs = {}
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"

@app.route("/")
def home():
    from generate_report import generate_html
    return generate_html()

@app.route("/data/<path:filename>")
def serve_data(filename):
    return send_from_directory(DATA_DIR, filename)

@app.route("/refresh", methods=["POST"])
def refresh():
    result = subprocess.run(
        [sys.executable, str(BASE / "scripts" / "refresh_batch.py")],
        capture_output=True, text=True
    )
    return jsonify({"status": "done", "log": result.stdout[-2000:]})

@app.route("/add_company", methods=["POST"])
def add_company():
    from flask import request
    import json as json_lib

    data = request.get_json()
    name = data.get("name", "").strip()
    ticker = data.get("ticker", "").strip()
    days_back = int(data.get("days", 29))

    if not name or not ticker:
        return jsonify({"error": "Missing name or ticker"}), 400

    config_path = BASE / "config" / "companies.json"
    with open(config_path, "r", encoding="utf-8") as f:
        companies = json_lib.load(f)

    # Check if this ticker already exists
    existing = next((c for c in companies if c["ticker"].upper() == ticker.upper()), None)

    if not existing:
        companies.append({
            "name": name, "ticker": ticker,
            "category": "custom", "last_updated": None
        })
        with open(config_path, "w", encoding="utf-8") as f:
            json_lib.dump(companies, f, indent=2)

    # Run the pipeline for just this one company
    from pipeline import run_company
    result = run_company(name, ticker, days_back=days_back, price_days_back=days_back + 10)

    if not result or result.get("num_days", 0) < 3:
        return jsonify({"error": f"Not enough data found for {name} ({ticker}). Try a different ticker."}), 400

    # Mark it as updated in config
    from datetime import datetime
    today = datetime.utcnow().strftime("%Y-%m-%d")
    with open(config_path, "r", encoding="utf-8") as f:
        companies = json_lib.load(f)
    for c in companies:
        if c["ticker"].upper() == ticker.upper():
            c["last_updated"] = today
    with open(config_path, "w", encoding="utf-8") as f:
        json_lib.dump(companies, f, indent=2)

    # Regenerate summary and chart to include the new company
    subprocess.run([sys.executable, str(BASE / "scripts" / "summary.py")])
    subprocess.run([sys.executable, str(BASE / "scripts" / "visualize.py")])

    return jsonify({"status": "done", "company": name})

@app.route("/analyze_custom", methods=["POST"])
def analyze_custom():
    from flask import request
    data = request.get_json()
    name = data.get("name", "").strip()
    ticker = data.get("ticker", "").strip()
    days_back = int(data.get("days", 29))

    if not name or not ticker:
        return jsonify({"error": "Missing name or ticker"}), 400

    job_id = str(uuid.uuid4())
    jobs[job_id] = {"status": "running", "result": None, "error": None}

    def run_job():
        from pipeline import run_company
        from generate_report import describe_company
        try:
            result = run_company(name, ticker, days_back=days_back, price_days_back=days_back + 10)
            if not result or result.get("num_days", 0) < 3:
                jobs[job_id]["status"] = "error"
                jobs[job_id]["error"] = f"Not enough data found for {name} ({ticker}). Try a different ticker."
                return
            result["category"] = "custom"
            result["description"] = describe_company(result)
            jobs[job_id]["status"] = "done"
            jobs[job_id]["result"] = result
        except Exception as e:
            jobs[job_id]["status"] = "error"
            jobs[job_id]["error"] = str(e)

    thread = threading.Thread(target=run_job)
    thread.start()

    return jsonify({"job_id": job_id})

@app.route("/job_status/<job_id>")
def job_status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({"error": "Unknown job"}), 404
    return jsonify(job)

if __name__ == "__main__":
    print("Starting server... open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)