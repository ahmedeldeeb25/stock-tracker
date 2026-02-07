# Stock Tracker - Updated Project

## 🎉 What's New

Your Stock Tracker now has a **complete web UI** built with Flask and Vue.js!

### Major Upgrades

1. ✅ **SQLite Database** - Replaced JSON with proper database
2. ✅ **Flask REST API** - Full-featured backend API
3. ✅ **Vue.js Frontend** - Modern, reactive web interface
4. ✅ **Tags System** - Organize stocks with custom tags
5. ✅ **Notes Feature** - Add research notes to each stock
6. ✅ **Alert Notes** - Custom messages in email alerts
7. ✅ **Alert History** - Track all triggered alerts
8. ✅ **Backward Compatible** - CLI and daemon still work!

---

## 🚀 Quick Start

### 1. Install Everything

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (for web UI)
cd web/frontend
npm install
cd ../..
```

### 2. Migrate Your Data

```bash
# This migrates your existing watchlist.json to SQLite
# and adds sample tags/notes
python -m src.migration --with-samples
```

### 3. Start the Web UI

**Development Mode (3 terminals):**

```bash
# Terminal 1: Flask API
cd web
python app.py

# Terminal 2: Vue.js Dev Server
cd web/frontend
npm run dev

# Terminal 3: Background Daemon
./scripts/start_daemon.sh
```

Then open: **http://localhost:5173**

---

## 📸 What You Get

### Dashboard
- View all stocks with live prices
- Filter by tags (tech, healthcare, etc.)
- Search stocks
- Visual alerts when targets hit
- Real-time updates

### Stock Detail Page
- Full stock information
- All price targets with status
- Add/edit notes and analysis
- Alert history for that stock
- Tag management

### Features
- **Add Stocks**: Modal form with multiple targets
- **Tags**: Organize stocks (e.g., "tech", "growth", "IBKR-similar")
- **Notes**: Add dated analysis for each stock
- **Alerts**: Custom notes sent in email notifications
- **History**: View all past alerts

---

## 📁 Updated Structure

```
stock-tracker/
├── src/                    # Core modules (updated)
│   ├── db_manager.py      # NEW: SQLite operations
│   ├── stock_service.py   # NEW: Business logic
│   ├── models.py          # NEW: Data models
│   ├── migration.py       # NEW: JSON→SQLite migration
│   └── ... (existing modules)
├── web/                    # NEW: Web application
│   ├── app.py             # Flask API server
│   ├── routes/            # API endpoints
│   └── frontend/          # Vue.js app
│       ├── src/
│       │   ├── components/
│       │   ├── views/
│       │   └── stores/
│       └── package.json
├── daemon.py              # Updated for SQLite
├── cli.py                 # Updated for SQLite
├── stock_tracker.db       # NEW: SQLite database
└── requirements.txt       # Updated
```

---

## 🎯 Key Features

### 1. Tags System
Organize stocks with custom tags:
- "tech", "healthcare", "growth"
- "IBKR-similar" for tracking similar stocks
- Filter dashboard by any tag
- Color-coded badges

### 2. Notes & Analysis
Add research notes to each stock:
- Title and date
- Full text content
- Multiple notes per stock
- Timeline view

### 3. Alert Notes
Each price target can have a custom note:
```
When AMZN hits $180:
Email will say: "Good entry point for long-term position"
```

### 4. Alert History
Track all triggered alerts:
- When they triggered
- Current vs target price
- Alert notes included
- Email sent status

---

## 🔄 Migration Details

Running `python -m src.migration --with-samples` will:

1. ✅ Create `stock_tracker.db` SQLite database
2. ✅ Migrate all stocks from `data/watchlist.json`
3. ✅ Migrate all targets (Buy/Sell/DCA/Trim)
4. ✅ Backup your JSON to `watchlist.json.backup.TIMESTAMP`
5. ✅ Add sample tags: tech, healthcare, e-commerce, cloud, growth, retail
6. ✅ Add sample notes to demonstrate feature
7. ✅ Link tags to your stocks:
   - AMZN → tech, e-commerce, cloud, retail
   - HIMS → healthcare, growth
   - ZETA → tech, growth

---

## 🖥️ Using the Web UI

### Add a Stock

1. Click "Add Stock" button
2. Enter symbol (e.g., NVDA)
3. Add company name (optional)
4. Add tags (e.g., tech, AI)
5. Add targets:
   - Buy @ $800 - "Entry point"
   - Sell @ $1000 - "Take profits"
6. Click "Add Stock"

### Filter Stocks

- Click any tag button to filter
- Use search box for symbol/name
- Click "All Stocks" to clear filter

### View Details

- Click stock card
- See all targets with status
- View/add notes
- Check alert history

---

## 📡 REST API

The Flask API provides full programmatic access:

```bash
# Get all stocks
curl http://localhost:5000/api/stocks

# Get single stock with details
curl http://localhost:5000/api/stocks/AMZN

# Get current price
curl http://localhost:5000/api/prices/AAPL

# Get all tags
curl http://localhost:5000/api/tags

# Get alert history
curl http://localhost:5000/api/alerts
```

Full API documentation in `WEB_SETUP_GUIDE.md`

---

## 🔧 CLI Still Works!

All your existing CLI commands work with SQLite:

```bash
python cli.py price AMZN
python cli.py status
python cli.py list
python cli.py add TSLA Buy 250
python cli.py logs
```

---

## 🤖 Daemon Still Works!

Background monitoring continues:

```bash
./scripts/start_daemon.sh    # Start
./scripts/status_daemon.sh   # Check
./scripts/stop_daemon.sh     # Stop
```

Now with:
- SQLite database reading
- Alert history logging
- Alert notes in emails

---

## 📧 Email Example

When alert triggers, email includes your custom note:

```
🔔 STOCK ALERT: AMZN

Target Type: Buy
Current Price: $179.50
Target Price: $180.00

Alert Note: Good entry point for long-term position.
Consider adding to core holdings.

---

This is an automated message from your Stock Tracker.
```

---

## 🎨 UI Screenshots (Text)

**Dashboard:**
```
┌─────────────────────────────────────────────────────┐
│  Stock Tracker                    [+ Add Stock]     │
├─────────────────────────────────────────────────────┤
│  [Search...]                    [🔄 Refresh Prices] │
│                                                      │
│  [All] [tech (2)] [healthcare (1)] [growth (2)]     │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │ AMZN  $201.45 ↑           [Details] [🗑️]    │  │
│  │ tech • e-commerce • cloud                     │  │
│  │                                                │  │
│  │ 🟢 Buy  @ $180   🔔 -9.64%                   │  │
│  │ 🔴 Sell @ $250   ⏳ +24.17%                  │  │
│  │ 📝 2 notes                                    │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

---

## 🚦 Development vs Production

**Development** (3 terminals, hot reload):
- Flask: http://localhost:5000 (API only)
- Vue: http://localhost:5173 (with proxy to API)
- Daemon: Background

**Production** (1 terminal):
```bash
cd web/frontend && npm run build && cd ..
python app.py
```
- Everything: http://localhost:5000

---

## 📚 Documentation Files

- `WEB_SETUP_GUIDE.md` - Detailed setup instructions
- `QUICKSTART.md` - CLI quick reference (still valid!)
- `README.md` - Original project readme

---

## 🎯 What's Next?

You can now:
1. ✅ Use the beautiful web UI
2. ✅ Organize stocks with tags
3. ✅ Add research notes
4. ✅ Get alerts with custom messages
5. ✅ View alert history
6. ✅ Still use CLI and daemon

Future enhancements:
- Price charts
- Portfolio tracking (shares owned)
- Performance metrics
- Mobile app (using same API)
- WebSocket real-time prices

---

## 🎉 Try It Now!

```bash
# 1. Install
pip install -r requirements.txt
cd web/frontend && npm install && cd ../..

# 2. Migrate
python -m src.migration --with-samples

# 3. Start (development mode)
# Terminal 1:
cd web && python app.py

# Terminal 2:
cd web/frontend && npm run dev

# 4. Open browser
# http://localhost:5173
```

Enjoy your new Stock Tracker UI! 🚀📈
