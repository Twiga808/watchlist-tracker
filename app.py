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

# ── Version tag — bump this each new week to force fresh data on redeploy ─────
CURRENT_VERSION = "2026-W12"   # Week of 3/16/2026

# ── Current week default data ─────────────────────────────────────────────────
DEFAULT_WATCHLIST = {
    "version": CURRENT_VERSION,
    "week_label": "3/16/2026 to 3/20/2026",
    "date": "3/15/2026",
    "tickers": [
        {"ticker": "MU",   "entry": 420.01, "stop": 394.44, "t1": 435,    "t2": 450,    "t3": 465},
        {"ticker": "AVGO", "entry": 315.01, "stop": 294.44, "t1": 325,    "t2": 335,    "t3": 345},
        {"ticker": "NVDA", "entry": 178.01, "stop": 172.98, "t1": 183,    "t2": 188,    "t3": 193},
        {"ticker": "ROST", "entry": 201.01, "stop": 193.44, "t1": 206,    "t2": 211,    "t3": 216},
        {"ticker": "ANAB", "entry":  60.01, "stop":  54.44, "t1":  62.5,  "t2":  65,    "t3":  67.5},
        {"ticker": "NOC",  "entry": 720.01, "stop": 699.44, "t1": 735,    "t2": 750,    "t3": 765},
        {"ticker": "IOVA", "entry":   3.61, "stop":   2.94, "t1":   4.2,  "t2":   4.8,  "t3":   5.4},
        {"ticker": "PUMP", "entry":  12.51, "stop":  10.94, "t1":  13.25, "t2":  14,    "t3":  14.75},
    ]
}

# ── Prior week (seeded into archive on first run) ─────────────────────────────
PRIOR_WEEK_ARCHIVE = {
    "archived_at": "2026-03-15T00:00:00",
    "version": "2026-W11",
    "week_label": "3/9/2026 to 3/13/2026",
    "date": "3/7/2026",
    "tickers": [
        {"ticker": "LC",   "entry": 14.51, "stop": 11.98, "t1": 15.75, "t2": 17.00, "t3": 18.25},
        {"ticker": "MBC",  "entry":  8.51, "stop":  7.44, "t1":  9.50, "t2": 10.50, "t3": 11.50},
        {"ticker": "SFIX", "entry":  3.01, "stop":  2.44, "t1":  3.40, "t2":  3.80, "t3":  4.20},
        {"ticker": "ISRG", "entry":480.01, "stop":459.98, "t1":500.00, "t2":520.00, "t3":540.00},
        {"ticker": "DXST", "entry":  0.21, "stop":  0.09, "t1":  0.35, "t2":  0.50, "t3":  0.65},
        {"ticker": "EOSE", "entry":  5.51, "stop":  3.59, "t1":  6.10, "t2":  6.70, "t3":  7.30},
        {"ticker": "PCT",  "entry":  5.51, "stop":  4.44, "t1":  6.25, "t2":  7.00, "t3":  7.75},
        {"ticker": "SERV", "entry":  8.51, "stop":  7.44, "t1":  9.35, "t2": 10.20, "t3": 11.05},
    ],
    "state": {}
}

STATE_FILE     = os.path.join(os.path.dirname(__file__), "state.json")
WATCHLIST_FILE = os.path.join(os.path.dirname(__file__), "watchlist.json")
ARCHIVE_FILE   = os.path.join(os.path.dirname(__file__), "archive.json")

# ── State helpers ─────────────────────────────────────────────────────────────
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def load_watchlist():
    """
    Load watchlist. If the stored version doesn't match CURRENT_VERSION,
    reset to DEFAULT_WATCHLIST (new week) and clear state.
    """
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE) as f:
                wl = json.load(f)
            # Version mismatch → new week deployed, reset
            if wl.get("version") != CURRENT_VERSION:
                save_watchlist(DEFAULT_WATCHLIST)
                save_state({})
                return DEFAULT_WATCHLIST
            return wl
        except Exception:
            pass
    save_watchlist(DEFAULT_WATCHLIST)
    return DEFAULT_WATCHLIST

def save_watchlist(wl):
    with open(WATCHLIST_FILE, "w") as f:
        json.dump(wl, f, indent=2)

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    # Seed with prior week on first load
    archive = [PRIOR_WEEK_ARCHIVE]
    save_archive(archive)
    return archive

def save_archive(archive):
    with open(ARCHIVE_FILE, "w") as f:
        json.dump(archive, f, indent=2)

# ── Price cache ───────────────────────────────────────────────────────────────
_price_cache = {}
_cache_ts    = {}
CACHE_TTL    = 300

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
    data["version"] = CURRENT_VERSION
    save_watchlist(data)
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

# ── Archive routes ────────────────────────────────────────────────────────────
@app.route("/api/archive", methods=["GET"])
def api_get_archive():
    return jsonify(load_archive())

@app.route("/api/archive", methods=["POST"])
def api_add_to_archive():
    data = request.get_json()
    archive = load_archive()
    entry = {
        "archived_at": datetime.now().isoformat(),
        "week_label": data.get("week_label", ""),
        "date": data.get("date", ""),
        "tickers": data.get("tickers", []),
        "state": data.get("state", {})
    }
    existing_labels = [a.get("week_label") for a in archive]
    if entry["week_label"] not in existing_labels:
        archive.insert(0, entry)
        save_archive(archive)
    return jsonify({"ok": True, "count": len(archive)})

@app.route("/api/archive/<int:idx>", methods=["DELETE"])
def api_delete_archive(idx):
    archive = load_archive()
    if 0 <= idx < len(archive):
        archive.pop(idx)
        save_archive(archive)
    return jsonify({"ok": True})

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  Watchlist Tracker running at http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
