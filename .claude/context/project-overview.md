# Project Overview - Stock Tracker

**Last Updated**: February 7, 2026

---

## 📊 What is Stock Tracker?

A full-stack web application for monitoring stock prices, setting price targets, and tracking investment analysis notes. It combines real-time price monitoring with a modern web interface for portfolio management.

---

## 🎯 Core Features

### Price Monitoring
- Real-time stock prices via yfinance API
- Background daemon for automated price checking
- Email notifications when targets are hit

### Price Targets
- Multiple target types: Buy, Sell, DCA, Trim
- Alert logic: Buy/DCA (alert below), Sell/Trim (alert above)
- Active/inactive target toggling
- Add targets during stock creation or afterward

### Analysis Notes
- Rich text notes with Quill editor
- Formatting: Bold, italic, headers, lists, colors
- Date-based organization
- Per-stock note history

### Tagging System
- Categorize stocks by tags (tech, healthcare, etc.)
- Filter dashboard by tags
- Color-coded tag badges
- Tag-based organization

### Web Interface
- Modern Vue 3 + Bootstrap UI
- Dashboard with stock cards
- Detailed stock view
- Alert history
- Responsive design

---

## 🏗️ Architecture

### Two-Part System

**1. Backend (Flask + Python)**
- RESTful JSON API (port 5555)
- SQLite database
- Price fetching daemon
- Email notifications

**2. Frontend (Vue 3 + Vite)**
- Modern SPA (port 5173)
- Pinia state management
- Bootstrap 5 UI
- Real-time data updates

---

## 📁 Project Structure

```
stock-tracker/
├── .claude/                    # AI assistant context
├── scripts/                    # Shell scripts
├── src/                        # Python source (daemon, CLI)
├── web/                        # Web application
│   ├── routes/                # Flask API routes
│   ├── frontend/              # Vue.js application
│   └── app.py                 # Flask server
├── data/                       # Database
│   └── stock_tracker.db       # SQLite database
├── venv/                       # Python virtual environment
└── [config files]
```

---

## 🔄 How It Works

### Price Monitoring Flow
1. Daemon runs every hour (9 AM - 5 PM)
2. Fetches current prices from yfinance
3. Compares against active targets
4. Sends email if target is hit
5. Records alert in database

### Web Interface Flow
1. User opens dashboard (http://localhost:5173)
2. Frontend fetches stocks from API
3. Displays cards with current prices
4. User can add stocks, targets, notes
5. Changes update database via API
6. UI refreshes with new data

---

## 👥 User Workflows

### Adding a New Stock
1. Click "Add Stock" button
2. Enter symbol, company name
3. Add tags (optional)
4. Add at least one price target
5. Submit to create stock

### Managing Existing Stock
1. Click stock card to view details
2. Click "+" in Price Targets to add target
3. Click "+" in Analysis Notes to add note
4. View alert history for this stock
5. See real-time price updates

### Filtering and Searching
1. Click tag badge to filter by tag
2. Use search box to find stocks
3. Dashboard updates dynamically
4. Clear filters to see all stocks

---

## 🎨 Design Philosophy

### Modularity
- Clear separation: daemon, CLI, web
- Each component can run independently
- Easy to extend or replace parts

### User Experience
- One-command start (`./scripts/start_all.sh`)
- Intuitive interface
- Minimal configuration needed
- Professional design

### Maintainability
- Clean code structure
- Comprehensive documentation
- Session handovers for continuity
- Established patterns

---

## 🔧 Technology Choices

### Why Flask?
- Lightweight for this use case
- Easy to understand and extend
- Good Python integration
- RESTful API simplicity

### Why Vue 3?
- Modern reactive framework
- Composition API for cleaner code
- Good ecosystem (Pinia, Router)
- Excellent DX with Vite

### Why SQLite?
- No server needed
- Perfect for single-user
- Easy backup (single file)
- Good enough performance

### Why yfinance?
- Free stock data
- No API key needed
- Reliable and maintained
- Easy to use

---

## 📊 Current State

### Database Content
- **3 stocks**: AMZN, HIMS, ZETA
- **6 targets**: Mix of Buy/Sell/DCA/Trim
- **6 tags**: tech, e-commerce, cloud, healthcare, etc.
- **3 notes**: Sample analysis notes

### Features Status
- ✅ Core monitoring working
- ✅ Web interface complete
- ✅ All CRUD operations functional
- ✅ Rich text notes implemented
- ✅ Target management working
- ✅ Tag filtering working

---

## 🚀 Running the Application

### Quick Start
```bash
./scripts/start_all.sh
# Opens http://localhost:5173
```

### Components
- **Backend**: http://localhost:5555/api
- **Frontend**: http://localhost:5173
- **Daemon**: Background process (optional)

---

## 🎯 Key Success Metrics

### For Users
- Can track multiple stocks easily
- Gets notified of price targets
- Can organize with tags
- Can write analysis notes

### For Developers
- Easy to add new features
- Clear code structure
- Good documentation
- Context preservation for AI

---

## 🔮 Future Possibilities

### Near Term
- Edit/delete notes
- Edit targets
- More chart views
- Export data

### Long Term
- Multi-user support
- Mobile app
- Advanced analytics
- Portfolio tracking
- Dividend tracking

---

## 🎓 What Makes This Project Special

1. **Complete Full-Stack**: Real backend + frontend + daemon
2. **Professional UI**: Not just functional, but beautiful
3. **AI-Friendly**: Excellent documentation and context preservation
4. **Modular**: Each part can be understood independently
5. **Production-Ready**: Could be deployed with minimal changes

---

**Note**: This is a living document. Update when architecture changes significantly.
