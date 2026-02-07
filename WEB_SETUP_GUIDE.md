# Stock Tracker Web UI - Setup Guide

## 🚀 Complete Setup Instructions

### Phase 1: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for frontend
cd web/frontend
npm install
cd ../..
```

### Phase 2: Database Migration

```bash
# Migrate existing JSON data to SQLite (with sample tags and notes)
python -m src.migration --with-samples

# Or migrate without samples
python -m src.migration
```

This will:
- Create `stock_tracker.db` SQLite database
- Migrate all stocks and targets from `data/watchlist.json`
- Backup your JSON file
- Add sample tags and notes (if --with-samples flag used)

### Phase 3: Start the Application

#### Option A: Development Mode (Recommended for testing)

**Terminal 1 - Start Flask API:**
```bash
cd web
python app.py
```
API will run on: http://localhost:5000

**Terminal 2 - Start Vue.js Dev Server:**
```bash
cd web/frontend
npm run dev
```
Frontend will run on: http://localhost:5173

**Terminal 3 - Start Background Daemon:**
```bash
./scripts/start_daemon.sh
```

#### Option B: Production Mode

```bash
# Build Vue.js frontend
cd web/frontend
npm run build
cd ..

# Start Flask (serves both API and frontend)
python app.py
```

Access the app at: http://localhost:5000

### Phase 4: Configure Email (for alerts)

Edit your `.env` file or `config.json` with email credentials:

```bash
# .env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
```

---

## 📁 Project Structure

```
stock-tracker/
├── src/                          # Core Python modules
│   ├── db_manager.py            # SQLite database operations
│   ├── stock_service.py         # Business logic layer
│   ├── stock_fetcher.py         # Price fetching (yfinance)
│   ├── alert_checker.py         # Alert detection logic
│   ├── email_notifier.py        # Email notifications
│   ├── models.py                # Data models
│   └── migration.py             # JSON to SQLite migration
├── web/                          # Web application
│   ├── app.py                   # Flask API server
│   ├── routes/                  # API endpoints
│   │   ├── stocks.py
│   │   ├── targets.py
│   │   ├── tags.py
│   │   ├── notes.py
│   │   ├── prices.py
│   │   └── alerts.py
│   └── frontend/                # Vue.js application
│       ├── src/
│       │   ├── components/      # Reusable Vue components
│       │   ├── views/           # Page components
│       │   ├── stores/          # Pinia state management
│       │   ├── api/             # API client
│       │   └── utils/           # Helper functions
│       ├── package.json
│       └── vite.config.js
├── daemon.py                     # Background monitoring (updated for SQLite)
├── cli.py                        # Command-line interface (updated for SQLite)
├── stock_tracker.db             # SQLite database (created after migration)
└── requirements.txt
```

---

## 🎨 Features

### ✅ Implemented Features

1. **Dashboard View**
   - View all stocks with current prices
   - Filter by tags
   - Search by symbol or company name
   - Real-time price updates
   - Visual indicators for triggered alerts

2. **Stock Management**
   - Add new stocks with multiple targets
   - Edit stock information
   - Delete stocks
   - View detailed stock information

3. **Price Targets**
   - Multiple targets per stock (Buy, Sell, DCA, Trim)
   - Alert notes for email notifications
   - Active/inactive toggle
   - Visual status indicators

4. **Tags System**
   - Create custom tags with colors
   - Assign multiple tags to stocks
   - Filter stocks by tag
   - Tag-based organization

5. **Notes & Analysis**
   - Add research notes to stocks
   - Date-based notes
   - Timeline view
   - Rich text support

6. **Alert History**
   - View all triggered alerts
   - Email sent status
   - Alert details and notes
   - Historical tracking

7. **Background Monitoring**
   - Continuous price checking
   - Email notifications
   - Alert logging
   - Daemon mode

---

## 🔧 API Endpoints Reference

### Stocks
- `GET /api/stocks` - Get all stocks
- `GET /api/stocks/:symbol` - Get stock details
- `POST /api/stocks` - Create new stock
- `PUT /api/stocks/:id` - Update stock
- `DELETE /api/stocks/:id` - Delete stock
- `GET /api/stocks/:id/status` - Get stock with price status

### Targets
- `GET /api/stocks/:id/targets` - Get all targets for stock
- `POST /api/stocks/:id/targets` - Add target to stock
- `PUT /api/targets/:id` - Update target
- `DELETE /api/targets/:id` - Delete target
- `PATCH /api/targets/:id/toggle` - Toggle active status

### Tags
- `GET /api/tags` - Get all tags
- `POST /api/tags` - Create tag
- `PUT /api/tags/:id` - Update tag
- `DELETE /api/tags/:id` - Delete tag
- `POST /api/stocks/:id/tags` - Add tag to stock
- `DELETE /api/stocks/:id/tags/:tagId` - Remove tag from stock

### Notes
- `GET /api/stocks/:id/notes` - Get notes for stock
- `POST /api/stocks/:id/notes` - Add note to stock
- `GET /api/notes/:id` - Get single note
- `PUT /api/notes/:id` - Update note
- `DELETE /api/notes/:id` - Delete note

### Prices
- `GET /api/prices/:symbol` - Get current price
- `POST /api/prices/batch` - Get multiple prices

### Alerts
- `GET /api/alerts` - Get alert history
- `DELETE /api/alerts/:id` - Delete alert

---

## 🖥️ Using the Web UI

### Adding a Stock

1. Click "Add Stock" button on dashboard
2. Fill in the form:
   - **Symbol**: Stock ticker (e.g., AAPL)
   - **Company Name**: Optional company name
   - **Tags**: Add tags for organization
   - **Targets**: Add one or more price targets
     - Select type (Buy/Sell/DCA/Trim)
     - Enter target price
     - Add alert note (optional)
     - For Trim: specify percentage

3. Click "Add Stock"

### Managing Stocks

- **View Details**: Click on stock card or "Details" button
- **Delete Stock**: Click trash icon on stock card
- **Filter by Tag**: Click tag buttons above stock list
- **Search**: Use search box to find stocks by symbol/name

### Working with Notes

1. Open stock detail page
2. Click "+" button in Notes section
3. Add title, date, and content
4. Save note

### Alert History

- View all triggered alerts from "Alert History" page
- See which alerts sent emails
- Delete old alerts

---

## 🔄 Backward Compatibility

The existing CLI and daemon still work!

### CLI Commands (Updated for SQLite)

```bash
# All existing commands work with SQLite now
python cli.py price AMZN
python cli.py status
python cli.py list
python cli.py add NVDA Buy 800
python cli.py logs
```

### Daemon (Updated for SQLite)

```bash
# Start background monitoring
./scripts/start_daemon.sh

# Check status
./scripts/status_daemon.sh

# Stop daemon
./scripts/stop_daemon.sh
```

The daemon now:
- Reads from SQLite database
- Logs alerts to `alert_history` table
- Includes alert notes in emails

---

## 🚦 Development Tips

### Hot Reload During Development

- Vue.js hot reloads automatically when you edit `.vue` files
- Flask auto-reloads when you edit Python files (if debug=True)
- Edit code and see changes instantly!

### Adding New Features

**Add a new API endpoint:**
1. Create function in appropriate `web/routes/*.py`
2. Update frontend API client in `web/frontend/src/api/index.js`
3. Use in Vue component

**Add a new Vue component:**
1. Create `.vue` file in `web/frontend/src/components/`
2. Import in view or other component
3. Use in template

### Database Changes

If you need to modify the database schema:
1. Edit `src/db_manager.py` - update `init_database()`
2. Delete `stock_tracker.db`
3. Re-run migration: `python -m src.migration --with-samples`

---

## 🐛 Troubleshooting

### Port Already in Use

**Flask (5000):**
```bash
lsof -ti:5000 | xargs kill -9
```

**Vite (5173):**
```bash
lsof -ti:5173 | xargs kill -9
```

### Database Locked Error

```bash
# Stop daemon first
./scripts/stop_daemon.sh

# Then start web app
cd web && python app.py
```

### Frontend Not Loading

```bash
# Rebuild frontend
cd web/frontend
npm run build
```

### API CORS Errors

Make sure Flask app has CORS enabled (already configured in `web/app.py`)

---

## 📊 Example Workflow

1. **Initial Setup**
   ```bash
   pip install -r requirements.txt
   cd web/frontend && npm install && cd ../..
   python -m src.migration --with-samples
   ```

2. **Development**
   ```bash
   # Terminal 1
   cd web && python app.py

   # Terminal 2
   cd web/frontend && npm run dev

   # Terminal 3
   ./scripts/start_daemon.sh
   ```

3. **Open Browser**
   - Go to http://localhost:5173
   - Add stocks, set targets, add notes
   - Filter by tags, search stocks

4. **Production Build**
   ```bash
   cd web/frontend && npm run build && cd ..
   python app.py
   ```
   - Access at http://localhost:5000

---

## 🎯 Next Steps

Potential enhancements:
- [ ] Add price charts (integrate Chart.js)
- [ ] Export data (CSV, PDF reports)
- [ ] Mobile app (using same API)
- [ ] WebSocket for real-time prices
- [ ] Portfolio tracking (shares owned)
- [ ] Performance metrics (gains/losses)
- [ ] News integration
- [ ] Technical indicators

---

## 📧 Support

For issues or questions:
- Check logs: `python cli.py logs`
- Check daemon status: `./scripts/status_daemon.sh`
- View API health: http://localhost:5000/health
- Database location: `stock_tracker.db`

---

## 🎉 You're All Set!

The Stock Tracker web UI is now ready to use. Enjoy monitoring your stocks with a beautiful interface!
