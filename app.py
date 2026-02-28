"""
Weekly Stock Watchlist Tracker
Self-contained Flask app — run with: python3 app.py
Then open http://localhost:5000 in your browser.
"""

from flask import Flask, jsonify, request, send_from_directory
import yfinance as yf
import json
import os
import time
from datetime import datetime

app = Flask(__name__, static_folder="static")

# ── Default watchlist (editable via UI) ──────────────────────────────────────
DEFAULT_WATCHLIST = {
    "week_label": "3/2/2026 to 3/6/2026",
    "date": "2/28/2026",
    "tickers": [
        {"ticker": "SOFI",  "entry": 17.51, "stop": 15.98, "t1": 19.00, "t2": 20.50, "t3": 22.00},
        {"ticker": "CAVA",  "entry": 77.51, "stop": 71.44, "t1": 80.50, "t2": 83.50, "t3": 86.50},
        {"ticker": "WD",    "entry": 42.51, "stop": 39.44, "t1": 46.50, "t2": 50.50, "t3": 54.50},
        {"ticker": "APLD",  "entry": 26.51, "stop": 24.44, "t1": 28.50, "t2": 30.50, "t3": 32.50},
        {"ticker": "BLDR",  "entry":103.01, "stop": 99.44, "t1":106.00, "t2":109.00, "t3":112.00},
        {"ticker": "AMC",   "entry":  1.11, "stop":  0.94, "t1":  1.20, "t2":  1.30, "t3":  1.40},
        {"ticker": "BBAI",  "entry":  3.71, "stop":  3.24, "t1":  4.10, "t2":  4.50, "t3":  4.90},
        {"ticker": "CLSK",  "entry":  9.51, "stop":  8.24, "t1": 10.50, "t2": 11.50, "t3": 12.50},
    ]
}

STATE_FILE    = os.path.join(os.path.dirname(__file__), "state.json")
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")

# ── State helpers ─────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_watchlist():
    if os.path.exists(WATCHLIST_FILE):
        with open(WATCHLIST_FILE) as f:
            return json.load(f)
    return DEFAULT_WATCHLIST

def save_watchlist(wl):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(wl, f, indent=2)

# ── Price cache (avoid hammering Yahoo) ──────────────────────────────────────
_price_cache = {}
_cache_ts    = {}
CACHE_TTL    = 300  # 5 minutes

def get_price(ticker):
    now = time.time()
    if ticker in _price_cache and (now - _cache_ts.get(ticker, 0)) < CACHE_TTL:
        return _price_cache[ticker]
    try:
        t = yf.Ticker(ticker)
        info = t.fast_info
        price = round(float(info.last_price), 4)
        _price_cache[ticker] = price
        _cache_ts[ticker] = now
        return price
    except Exception:
        return _price_cache.get(ticker, None)

# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/api/watchlist", methods=["GET"])
def api_watchlist():
    return jsonify(load_watchlist())

@app.route("/api/watchlist", methods=["POST"])
def api_save_watchlist():
    data = request.get_json()
    save_watchlist(data)
    # Reset state when watchlist changes
    save_state({})
    return jsonify({"ok": True})

@app.route("/api/prices", methods=["GET"])
def api_prices():
    wl = load_watchlist()
    result = {}
    for row in wl["tickers"]:
        sym = row["ticker"]
        result[sym] = get_price(sym)
    return jsonify(result)

@app.route("/api/state", methods=["GET"])
def api_state():
    return jsonify(load_state())

@app.route("/api/state", methods=["POST"])
def api_save_state():
    data = request.get_json()
    save_state(data)
    return jsonify({"ok": True})

@app.route("/api/state/<ticker>", methods=["POST"])
def api_update_ticker_state(ticker):
    state = load_state()
    payload = request.get_json()
    state[ticker] = payload
    save_state(state)
    return jsonify({"ok": True})

@app.route("/api/state/<ticker>", methods=["DELETE"])
def api_clear_ticker_state(ticker):
    state = load_state()
    state.pop(ticker, None)
    save_state(state)
    return jsonify({"ok": True})

@app.route("/api/reset", methods=["POST"])
def api_reset():
    save_state({})
    return jsonify({"ok": True})

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Watchlist Tracker running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
