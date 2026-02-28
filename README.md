# Weekly Stock Watchlist Tracker

A self-contained local web application for tracking your weekly stock watchlist with live delayed prices, position management, and trade logging.

---

## One-Time Setup

**Requirements:** Python 3.8 or later (already installed on most systems).

Open a terminal (Command Prompt on Windows, Terminal on Mac) and run:

```
pip install flask yfinance
```

---

## Running the App

1. Open a terminal and navigate to this folder:
   ```
   cd path/to/watchlist_app
   ```

2. Start the server:
   ```
   python app.py
   ```

3. Open your browser and go to:
   ```
   http://localhost:5000
   ```

Leave the terminal window open while using the app. To stop it, press `Ctrl+C`.

---

## Features

| Feature | How It Works |
|---|---|
| **Live Prices** | Pulls 15-min delayed quotes from Yahoo Finance for all tickers. Auto-refreshes every 5 minutes. |
| **Entry Alert** | Rows highlight yellow with an "ENTRY" badge when current price is within 0.5% of your entry level. |
| **Enter Position** | Click the green **Enter** button to mark yourself in a trade. Records timestamp automatically. |
| **Shares & P&L** | Type your share quantity in the Qty box. Unrealized P&L updates live. |
| **Stop Loss Warning** | Row turns orange when price is within 2% of stop. Turns red if stop is breached. |
| **Target Progress** | Progress bar shows how far price has moved from entry toward T3. Targets auto-check when hit. |
| **Exit Trade** | **Stop** button exits at stop loss price. **Exit** button exits at current market price. Both log to Trade Log. |
| **Trade Log** | Running record of all closed trades with entry/exit price, date/time, P&L $ and %. |
| **Edit Watchlist** | Click **Edit Watchlist** to update tickers and levels for a new week. Saves to `watchlist.json`. |
| **Reset Week** | Click **Reset Week** to clear all open positions and start fresh. Trade log is preserved. |

---

## Row Color Guide

| Color | Meaning |
|---|---|
| Yellow | Entry price has been hit — consider entering |
| Blue border | You are in this position |
| Orange | Price within 2% of stop loss — caution |
| Red (faded) | Stop loss breached |
| Light green | Target 1 hit |
| Medium green | Target 2 hit |
| Dark green | Target 3 hit |

---

## Files

| File | Purpose |
|---|---|
| `app.py` | Flask backend — price fetching, API endpoints |
| `static/index.html` | Frontend dashboard |
| `watchlist.json` | Your saved watchlist (auto-created, editable) |
| `state.json` | Open positions and trade log (auto-created) |

---

## Updating the Watchlist Each Week

Click **Edit Watchlist** in the app header, update all values, then click **Save & Apply**. This resets all open positions for the new week. Your trade log from prior weeks is preserved in `state.json`.
