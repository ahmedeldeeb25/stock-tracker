# 📚 Documentation Index

Quick reference to all documentation in the Stock Tracker project.

---

## 🎯 Quick Reference (Start Here)

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **SESSION_HANDOVER.md** | Latest session changes and handover notes | Start of each new session |
| **CURRENT_STATUS.md** | Current project status and quick start | When you need to run the app |
| **QUICKSTART.md** | Quick command reference | When you need specific commands |

---

## 📖 Comprehensive Documentation

| Document | Purpose | Contents |
|----------|---------|----------|
| **README.md** | Main project documentation | Installation, usage, features, architecture |
| **ARCHITECTURE.md** | System architecture | Technical design, database schema, API structure |
| **WEB_SETUP_GUIDE.md** | Web interface setup | Complete web UI setup instructions |
| **UPGRADE_GUIDE.md** | Migration guide | Upgrading from CLI to web version |
| **IMPLEMENTATION_SUMMARY.md** | Implementation details | Technical implementation notes |

---

## 🔄 Session History

| Date | Document | Changes |
|------|----------|---------|
| 2026-02-07 | SESSION_HANDOVER.md | Added target/note modals, rich text editor, filtered cards, scripts organization |

---

## 🗂️ File Locations Quick Map

### Frontend Components
```
web/frontend/src/components/
├── AddStockModal.vue         # Add new stock with targets
├── AddTargetModal.vue         # Add price target to existing stock
├── AddNoteModal.vue           # Add analysis note with rich text
└── StockCard.vue              # Stock card (dashboard view)
```

### Frontend Views
```
web/frontend/src/views/
├── Dashboard.vue              # Home page with all stocks
├── StockDetail.vue            # Individual stock details
└── AlertHistory.vue           # Alert history page
```

### Backend Routes
```
web/routes/
├── stocks.py                  # Stock CRUD, targets, notes
├── targets.py                 # Target updates, delete, toggle
├── tags.py                    # Tag management
├── notes.py                   # Note updates, delete
├── prices.py                  # Price fetching
└── alerts.py                  # Alert history
```

### Scripts
```
scripts/
├── start_all.sh               # Start everything
├── start_daemon.sh            # Start price monitor daemon
├── start_web.sh               # Start Flask backend
├── start_frontend.sh          # Start Vue frontend
├── stop_daemon.sh             # Stop daemon
├── status_daemon.sh           # Check daemon status
├── fresh_start.sh             # Fresh start
└── test_flask.sh              # Test Flask server
```

### Configuration
```
Root directory:
├── .env                       # Environment variables (email config)
├── requirements.txt           # Python dependencies
└── data/
    └── stock_tracker.db       # SQLite database
```

---

## 🔍 Quick Find

### Need to...

**Run the application:**
- Read: `CURRENT_STATUS.md` → Quick Start section
- Run: `./scripts/start_all.sh`

**Find a specific command:**
- Read: `QUICKSTART.md`

**Understand the architecture:**
- Read: `ARCHITECTURE.md`

**Set up web interface for first time:**
- Read: `WEB_SETUP_GUIDE.md`

**Know what was done in last session:**
- Read: `SESSION_HANDOVER.md`

**Add a new feature:**
1. Read `SESSION_HANDOVER.md` → Technical Stack section
2. Check existing components in file map above
3. Follow patterns from existing modals/components

---

## 🚀 Common Tasks Reference

### Adding a New Modal
1. Create component in `/web/frontend/src/components/YourModal.vue`
2. Import in parent view: `import YourModal from '@/components/YourModal.vue'`
3. Add to components: `components: { YourModal }`
4. Add to template: `<YourModal :prop="value" @event="handler" />`
5. Show modal: `new window.bootstrap.Modal(document.getElementById('yourModalId')).show()`

### Adding a New API Endpoint
1. Add route in `/web/routes/your_route.py`
2. Register blueprint in `/web/app.py`
3. Add to API client: `/web/frontend/src/api/index.js`
4. Use in component: `import { yourApi } from '@/api'`

### Adding a New Script
1. Create in `/scripts/your_script.sh`
2. Make executable: `chmod +x scripts/your_script.sh`
3. Document in README.md if it's for users

---

## 📝 Documentation Standards

### When to Update
- **SESSION_HANDOVER.md**: After each coding session
- **CURRENT_STATUS.md**: When project status changes
- **README.md**: When features/usage changes
- **ARCHITECTURE.md**: When architecture changes
- **QUICKSTART.md**: When commands change

### File Naming
- Use UPPERCASE for root documentation: `README.md`, `ARCHITECTURE.md`
- Use snake_case for scripts: `start_daemon.sh`
- Use PascalCase for Vue components: `AddStockModal.vue`
- Use snake_case for Python: `stock_fetcher.py`

---

**Last Updated**: February 7, 2026
