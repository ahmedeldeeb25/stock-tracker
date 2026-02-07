# 🎯 Stock Tracker - Complete Architecture Overview

## Executive Summary

Stock Tracker is now a full-stack web application with:
- **Backend**: Python Flask REST API with SQLite database
- **Frontend**: Vue.js 3 Single Page Application
- **Background Services**: Python daemon for continuous monitoring
- **CLI**: Command-line interface for quick operations

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER INTERFACES                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Web Browser │  │  CLI Tool    │  │  Daemon      │         │
│  │  (Vue.js)    │  │  (cli.py)    │  │  (daemon.py) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          │ HTTP/JSON        │ Direct Python    │ Direct Python
          │ REST API         │ Imports          │ Imports
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Flask API Server (web/app.py)                             │ │
│  │  ├─ /api/stocks      → Stock operations                   │ │
│  │  ├─ /api/targets     → Target management                  │ │
│  │  ├─ /api/tags        → Tag operations                     │ │
│  │  ├─ /api/notes       → Note management                    │ │
│  │  ├─ /api/prices      → Real-time prices                   │ │
│  │  └─ /api/alerts      → Alert history                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Business Logic Layer (src/)                               │ │
│  │  ├─ stock_service.py    → High-level stock operations     │ │
│  │  ├─ db_manager.py       → Database operations (CRUD)      │ │
│  │  ├─ stock_fetcher.py    → yfinance price fetching         │ │
│  │  ├─ alert_checker.py    → Alert logic & detection         │ │
│  │  ├─ email_notifier.py   → Email sending (SMTP)            │ │
│  │  └─ models.py           → Data models & schemas           │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                       DATA LAYER                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  stock_tracker.db (SQLite Database)                             │
│  ├─ stocks            → Stock symbols & info                    │
│  ├─ targets           → Price targets (Buy/Sell/DCA/Trim)       │
│  ├─ tags              → Tag definitions                         │
│  ├─ stock_tags        → Many-to-many: stocks ↔ tags            │
│  ├─ notes             → Research notes for stocks              │
│  └─ alert_history     → Log of all triggered alerts            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📦 Complete File Tree

```
stock-tracker/
│
├── 📄 README.md                     # Original project documentation
├── 📄 UPGRADE_GUIDE.md              # What's new guide
├── 📄 WEB_SETUP_GUIDE.md            # Detailed web UI setup
├── 📄 QUICKSTART.md                 # CLI quick reference
├── 📄 ARCHITECTURE.md               # This file
│
├── 📄 requirements.txt              # Python dependencies
├── 📄 .env.example                  # Environment variables template
├── 📄 config.json                   # Configuration file
├── 📄 .gitignore                    # Git ignore rules
│
├── 🗄️ stock_tracker.db              # SQLite database
│
├── 📁 src/                          # Core Python modules
│   ├── __init__.py
│   ├── config.py                    # Configuration management
│   ├── models.py                    # Data models & schemas
│   ├── db_manager.py                # SQLite database operations
│   ├── stock_service.py             # Business logic layer
│   ├── stock_fetcher.py             # Price fetching (yfinance)
│   ├── alert_checker.py             # Alert detection logic
│   └── email_notifier.py            # Email notifications
│
├── 📁 web/                          # 🆕 Web application
│   ├── app.py                       # Flask API server
│   ├── routes/                      # API route handlers
│   │   ├── __init__.py
│   │   ├── stocks.py                # Stock CRUD endpoints
│   │   ├── targets.py               # Target management endpoints
│   │   ├── tags.py                  # Tag management endpoints
│   │   ├── notes.py                 # Note management endpoints
│   │   ├── prices.py                # Price fetching endpoints
│   │   └── alerts.py                # Alert history endpoints
│   │
│   └── frontend/                    # Vue.js Single Page Application
│       ├── package.json             # Node.js dependencies
│       ├── vite.config.js           # Vite build configuration
│       ├── index.html               # HTML entry point
│       │
│       ├── public/                  # Static assets
│       │
│       └── src/
│           ├── main.js              # Vue app entry point
│           ├── App.vue              # Root Vue component
│           ├── router.js            # Vue Router configuration
│           ├── style.css            # Global styles
│           │
│           ├── components/          # Reusable Vue components
│           │   ├── StockCard.vue    # Stock display card
│           │   └── AddStockModal.vue # Add stock modal form
│           │
│           ├── views/               # Page components (routes)
│           │   ├── Dashboard.vue    # Main dashboard view
│           │   ├── StockDetail.vue  # Single stock detail view
│           │   └── AlertHistory.vue # Alert history view
│           │
│           ├── stores/              # Pinia state management
│           │   ├── stocks.js        # Stock state & actions
│           │   ├── tags.js          # Tags state & actions
│           │   └── alerts.js        # Alerts state & actions
│           │
│           ├── api/                 # API client layer
│           │   ├── client.js        # Axios HTTP client
│           │   └── index.js         # API methods (stocks, tags, etc.)
│           │
│           └── utils/
│               └── formatters.js    # Helper functions (price, date formatting)
│
├── 🐍 daemon.py                     # Background monitoring daemon
├── 🐍 cli.py                        # Command-line interface
│
├── 🔧 scripts/start_daemon.sh       # Start daemon script
├── 🔧 scripts/stop_daemon.sh        # Stop daemon script
├── 🔧 scripts/status_daemon.sh      # Check daemon status
│
└── 📄 com.user.stocktracker.plist   # macOS LaunchAgent configuration
```

**File Count Summary:**
- Python modules: 15+
- Vue.js components: 8
- API routes: 6 blueprints
- Configuration files: 6
- Documentation files: 5

---

## 🔄 Data Flow Examples

### 1. User Adds Stock via Web UI

```
1. User fills form in AddStockModal.vue
   ↓
2. Vue component calls stocksApi.create()
   ↓
3. Axios sends POST /api/stocks
   ↓
4. Flask route (stocks.py) receives request
   ↓
5. Validates data & calls stock_service.create_stock_with_targets()
   ↓
6. stock_service:
   - Calls db_manager.create_stock()
   - Calls db_manager.create_target() for each target
   - Calls db_manager.add_tag_to_stock() for each tag
   ↓
7. db_manager executes SQLite INSERT statements
   ↓
8. Returns created stock data
   ↓
9. Flask sends JSON response
   ↓
10. Vue Pinia store updates state
   ↓
11. Dashboard re-renders with new stock
```

### 2. Daemon Checks Prices & Sends Alert

```
1. daemon.py runs scheduled check (every hour)
   ↓
2. Queries db_manager.get_all_active_targets()
   ↓
3. SQLite returns all active targets with stock info
   ↓
4. stock_fetcher.get_multiple_prices() fetches from yfinance
   ↓
5. alert_checker.check_all_alerts() compares prices vs targets
   ↓
6. If alert triggered:
   - db_manager.create_alert_history() logs to database
   - email_notifier.send_alert() sends email with alert_note
   ↓
7. User receives email:
   "🔔 ALERT: AMZN Buy @ $179.50
    Note: Good entry point for long-term position"
   ↓
8. Alert visible in web UI Alert History page
```

### 3. User Filters Stocks by Tag

```
1. User clicks "tech" tag button
   ↓
2. Vue component calls stocksStore.setFilter('tag', 'tech')
   ↓
3. Pinia getter filteredStocks recomputes
   ↓
4. Vue reactively re-renders stock list
   ↓
5. Only stocks with "tech" tag displayed
```

---

## 🗃️ Database Schema

```sql
-- Core Tables
stocks (id, symbol, company_name, created_at, updated_at)
targets (id, stock_id, target_type, target_price, trim_percentage,
         alert_note, is_active, created_at)
tags (id, name, color, created_at)
notes (id, stock_id, title, content, note_date, created_at, updated_at)

-- Junction Table
stock_tags (stock_id, tag_id, created_at)

-- History
alert_history (id, stock_id, target_id, current_price, target_price,
               target_type, alert_note, email_sent, triggered_at)

-- Relationships
stocks 1:N targets
stocks 1:N notes
stocks M:N tags (via stock_tags)
stocks 1:N alert_history
```

---

## 🔌 API Architecture

### REST Principles
- **Resources**: stocks, targets, tags, notes, alerts
- **HTTP Methods**: GET, POST, PUT, PATCH, DELETE
- **JSON**: Request and response format
- **Status Codes**: 200, 201, 400, 404, 500

### API Organization
```
/api/stocks/*       → Stock operations (CRUD + associations)
/api/targets/*      → Target operations (Update, Delete, Toggle)
/api/tags/*         → Tag operations (CRUD)
/api/notes/*        → Note operations (CRUD)
/api/prices/*       → Real-time price fetching
/api/alerts/*       → Alert history (Read, Delete)
```

### Authentication
- Currently: None (local use)
- Future: JWT tokens, API keys

---

## 🎨 Frontend Architecture

### Vue.js 3 Composition API
- **Reactive State**: `ref()`, `computed()`
- **Lifecycle**: `onMounted()`, `watch()`
- **Composables**: Reusable logic

### State Management (Pinia)
```
stores/stocks.js    → Stock list, current stock, filters
stores/tags.js      → Tag list
stores/alerts.js    → Alert history
```

### Component Hierarchy
```
App.vue
├── router-view
    ├── Dashboard.vue
    │   ├── StockCard.vue (repeated)
    │   └── AddStockModal.vue
    ├── StockDetail.vue
    └── AlertHistory.vue
```

### Styling
- **Bootstrap 5**: UI framework
- **Bootstrap Icons**: Icon library
- **Custom CSS**: `style.css` for app-specific styles

---

## 🔧 Technology Stack

### Backend
| Component | Technology | Version |
|-----------|-----------|---------|
| Language | Python | 3.8+ |
| Web Framework | Flask | 3.0+ |
| Database | SQLite | 3 |
| HTTP Client | yfinance | 0.2+ |
| Email | smtplib | Built-in |
| Scheduler | schedule | 1.2+ |
| CLI | Click | 8.1+ |

### Frontend
| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Vue.js | 3.4+ |
| Router | Vue Router | 4.2+ |
| State | Pinia | 2.1+ |
| HTTP | Axios | 1.6+ |
| Build Tool | Vite | 5.0+ |
| CSS | Bootstrap | 5.3+ |
| Icons | Bootstrap Icons | 1.11+ |

---

## 🚀 Deployment Options

### Local Development
```bash
# Backend: http://localhost:5000
cd web && python app.py

# Frontend: http://localhost:5173 (with hot reload)
cd web/frontend && npm run dev
```

### Local Production
```bash
# Build frontend
cd web/frontend && npm run build

# Serve everything on :5000
cd .. && python app.py
```

### Server Deployment
- **Flask**: Gunicorn + Nginx
- **Frontend**: Pre-built static files
- **Database**: Keep SQLite or migrate to PostgreSQL
- **Daemon**: systemd service

### Cloud Options
- **Heroku**: Python + Node buildpacks
- **Railway**: Auto-detect and deploy
- **AWS**: EC2 + RDS
- **Docker**: Containerize app + daemon

---

## 🔐 Security Considerations

### Current State (Local Use)
- ✅ No authentication needed
- ✅ CORS enabled for development
- ✅ Environment variables for secrets

### Production Recommendations
- [ ] Add authentication (JWT, OAuth)
- [ ] Rate limiting on API
- [ ] Input validation & sanitization
- [ ] SQL injection prevention (using parameterized queries ✅)
- [ ] HTTPS/SSL certificates
- [ ] Secure email credentials (vault, secrets manager)

---

## 📊 Performance Considerations

### Current Optimizations
- ✅ SQLite indexes on frequently queried columns
- ✅ Batch price fetching
- ✅ Efficient SQL queries with JOINs
- ✅ Vue.js reactivity for minimal re-renders

### Future Optimizations
- [ ] Redis caching for prices
- [ ] WebSocket for real-time updates
- [ ] Database connection pooling
- [ ] Frontend code splitting
- [ ] CDN for static assets
- [ ] Background job queue (Celery)

---

## 🧪 Testing Strategy

### Backend Testing
```python
# Unit tests
tests/test_db_manager.py
tests/test_stock_service.py
tests/test_alert_checker.py

# API tests
tests/test_api_stocks.py
tests/test_api_tags.py
```

### Frontend Testing
```javascript
// Unit tests (Vitest)
tests/components/StockCard.spec.js

// E2E tests (Playwright/Cypress)
e2e/dashboard.spec.js
```

---

## 📈 Metrics & Monitoring

### Logging
- **Backend**: Python logging to `stock_tracker.log`
- **Daemon**: Background operations logged
- **Frontend**: Console errors in development

### Future Monitoring
- [ ] Application Performance Monitoring (APM)
- [ ] Error tracking (Sentry)
- [ ] Analytics (stock views, alert frequencies)
- [ ] Database query performance

---

## 🎯 Future Enhancements

### Phase 1 (Easy)
- [ ] Add note editing/deletion in UI
- [ ] Target editing in UI
- [ ] Stock company name auto-lookup
- [ ] Dark mode toggle

### Phase 2 (Medium)
- [ ] Price charts (Chart.js)
- [ ] Historical price data
- [ ] Portfolio tracking (shares owned)
- [ ] P&L calculations

### Phase 3 (Advanced)
- [ ] Mobile app (React Native + same API)
- [ ] WebSocket real-time prices
- [ ] News integration (Finnhub API)
- [ ] Technical indicators
- [ ] Multi-user support

---

## 🤝 Contributing

To add features:

1. **Backend**: Add route in `web/routes/*.py`
2. **Database**: Update `db_manager.py` schema
3. **Frontend**: Add API method in `api/index.js`
4. **UI**: Create/update Vue component
5. **State**: Update Pinia store if needed

---

## 📞 Support & Resources

- **Flask Docs**: https://flask.palletsprojects.com/
- **Vue.js Docs**: https://vuejs.org/
- **Pinia Docs**: https://pinia.vuejs.org/
- **Bootstrap Docs**: https://getbootstrap.com/
- **yfinance Docs**: https://github.com/ranaroussi/yfinance

---

## 🎉 Summary

You now have a **production-ready** stock tracking application with:

✅ Modern web interface (Vue.js)
✅ RESTful API (Flask)
✅ Reliable database (SQLite)
✅ Background monitoring (Daemon)
✅ CLI for quick operations
✅ Email notifications
✅ Tags & filtering
✅ Research notes
✅ Alert history
✅ Fully modular & extensible

**Happy tracking! 📈🚀**
