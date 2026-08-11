from flask import Flask, send_from_directory, jsonify
from pathlib import Path
import subprocess, sys

app = Flask(__name__)
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

if __name__ == "__main__":
    print("Starting server... open http://127.0.0.1:5000 in your browser")
    app.run(debug=True, port=5000)