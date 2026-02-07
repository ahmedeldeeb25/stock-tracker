# Component Map

**Last Updated**: February 7, 2026

Quick reference for finding and understanding components in the Stock Tracker project.

---

## 📁 Frontend Components

### Location: `/web/frontend/src/components/`

| Component | File | Purpose | Props | Events | Used By |
|-----------|------|---------|-------|--------|---------|
| **StockCard** | `StockCard.vue` | Stock display on dashboard | `stock: Object` | `delete: (id)` | Dashboard.vue |
| **AddStockModal** | `AddStockModal.vue` | Create new stock with targets | - | `stock-added: ()` | Dashboard.vue |
| **AddTargetModal** | `AddTargetModal.vue` | Add target to existing stock | `stockId: Number` | `target-added: ()` | StockDetail.vue |
| **AddNoteModal** | `AddNoteModal.vue` | Add note with rich text | `stockId: Number` | `note-added: ()` | StockDetail.vue |

---

### StockCard.vue
**Location**: `/web/frontend/src/components/StockCard.vue`

**Purpose**: Display stock information in a card on the dashboard

**Features**:
- Shows symbol, company name, current price
- Displays tags with colors
- Shows **only Buy/Sell targets** (filters out DCA/Trim)
- Shows notes count
- Links to stock detail page
- Delete button

**Props**:
```javascript
{
  stock: {
    type: Object,
    required: true
    // Expected shape: { id, symbol, company_name, current_price, targets: [], tags: [], notes_count }
  }
}
```

**Emits**:
- `delete: (stockId)` - When delete button clicked

**Usage**:
```vue
<StockCard
  :stock="stock"
  @delete="handleDelete"
/>
```

---

### AddStockModal.vue
**Location**: `/web/frontend/src/components/AddStockModal.vue`

**Purpose**: Modal form for creating new stocks

**Features**:
- Symbol and company name inputs
- Tag management (add/remove tags)
- Multiple price targets
- Dynamic target type selection
- Trim percentage for Trim targets
- Alert notes for each target

**Props**: None (modal triggered via Bootstrap)

**Emits**:
- `stock-added: ()` - After successful creation

**Usage**:
```vue
<AddStockModal @stock-added="handleStockAdded" />

<!-- Trigger -->
<button data-bs-toggle="modal" data-bs-target="#addStockModal">
  Add Stock
</button>
```

---

### AddTargetModal.vue
**Location**: `/web/frontend/src/components/AddTargetModal.vue`

**Purpose**: Modal form for adding price targets to existing stocks

**Features**:
- Target type selection (Buy/Sell/DCA/Trim)
- Price input
- Trim percentage (conditional, only for Trim)
- Optional alert note
- Validation

**Props**:
```javascript
{
  stockId: {
    type: Number,
    required: true
  }
}
```

**Emits**:
- `target-added: ()` - After successful creation

**Usage**:
```vue
<AddTargetModal
  :stock-id="stock.id"
  @target-added="handleTargetAdded"
/>

<!-- Trigger -->
<button @click="showAddTargetModal">Add Target</button>

<script>
const showAddTargetModal = () => {
  const modal = new window.bootstrap.Modal(
    document.getElementById('addTargetModal')
  )
  modal.show()
}
</script>
```

---

### AddNoteModal.vue
**Location**: `/web/frontend/src/components/AddNoteModal.vue`

**Purpose**: Modal form for adding analysis notes with rich text formatting

**Features**:
- Title input
- Date picker (defaults to today)
- Quill rich text editor with full toolbar
- HTML content storage
- Content validation

**Dependencies**:
- `@vueup/vue-quill` - Rich text editor
- `@vueup/vue-quill/dist/vue-quill.snow.css` - Editor styles

**Props**:
```javascript
{
  stockId: {
    type: Number,
    required: true
  }
}
```

**Emits**:
- `note-added: ()` - After successful creation

**Usage**:
```vue
<AddNoteModal
  :stock-id="stock.id"
  @note-added="handleNoteAdded"
/>

<!-- Trigger -->
<button @click="showAddNoteModal">Add Note</button>

<script>
const showAddNoteModal = () => {
  const modal = new window.bootstrap.Modal(
    document.getElementById('addNoteModal')
  )
  modal.show()
}
</script>
```

---

## 📄 Frontend Views

### Location: `/web/frontend/src/views/`

| View | File | Route | Purpose |
|------|------|-------|---------|
| **Dashboard** | `Dashboard.vue` | `/` | Main page, stock grid |
| **StockDetail** | `StockDetail.vue` | `/stock/:symbol` | Individual stock details |
| **AlertHistory** | `AlertHistory.vue` | `/alerts` | Alert history page |

---

### Dashboard.vue
**Location**: `/web/frontend/src/views/Dashboard.vue`

**Purpose**: Main dashboard with all stocks

**Features**:
- Grid of StockCard components
- Tag filtering
- Search functionality
- Add stock button
- Loading state
- Empty state

**Components Used**:
- `StockCard`
- `AddStockModal`

**Store Used**:
- `useStocksStore()`

---

### StockDetail.vue
**Location**: `/web/frontend/src/views/StockDetail.vue`

**Purpose**: Detailed view of a single stock

**Features**:
- Stock header with current price
- Price targets list with add button
- Analysis notes with add button
- Alert history
- Refresh button
- Tags display

**Components Used**:
- `AddTargetModal`
- `AddNoteModal`

**Store Used**:
- `useStocksStore()`

**Route Params**:
- `symbol: string` - Stock symbol (from URL)

---

### AlertHistory.vue
**Location**: `/web/frontend/src/views/AlertHistory.vue`

**Purpose**: View all triggered alerts

**Features**:
- List of all alerts
- Filter by stock
- Pagination
- Alert details
- Email sent indicator

---

## 🗂️ State Management

### Location: `/web/frontend/src/stores/`

| Store | File | Purpose |
|-------|------|---------|
| **Stocks** | `stocks.js` | Manage stocks, targets, notes |

---

### stocks.js
**Location**: `/web/frontend/src/stores/stocks.js`

**Purpose**: Centralized stock data management

**State**:
```javascript
{
  stocks: [],           // All stocks
  currentStock: null,   // Currently viewed stock (detail page)
  loading: false,       // Loading indicator
  error: null          // Error message
}
```

**Actions**:
- `fetchStocks()` - Get all stocks
- `fetchStockDetails(symbol)` - Get single stock with full details
- `createStock(data)` - Create new stock
- `deleteStock(id)` - Delete stock

---

## 🔌 API Client

### Location: `/web/frontend/src/api/`

| File | Purpose |
|------|---------|
| `client.js` | Axios instance with base config |
| `index.js` | API method exports |

---

### API Exports

**From** `/web/frontend/src/api/index.js`:

```javascript
// Stocks
stocksApi.getAll(params)
stocksApi.getBySymbol(symbol)
stocksApi.create(data)
stocksApi.update(id, data)
stocksApi.delete(id)
stocksApi.addTarget(id, data)      // ← Use this for AddTargetModal
stocksApi.addNote(id, data)        // ← Use this for AddNoteModal

// Targets
targetsApi.update(id, data)
targetsApi.delete(id)
targetsApi.toggle(id)

// Tags
tagsApi.getAll()
tagsApi.create(data)
tagsApi.update(id, data)
tagsApi.delete(id)

// Notes
notesApi.get(id)
notesApi.update(id, data)
notesApi.delete(id)

// Prices
pricesApi.get(symbol)
pricesApi.getBatch(symbols)

// Alerts
alertsApi.getAll(params)
alertsApi.delete(id)
```

---

## 🎨 Utilities

### Location: `/web/frontend/src/utils/`

| File | Purpose |
|------|---------|
| `formatters.js` | Formatting functions |

---

### formatters.js
**Location**: `/web/frontend/src/utils/formatters.js`

**Exports**:
```javascript
formatPrice(price)              // → "$210.32"
formatPercent(percent)          // → "+2.5%" or "-2.5%"
formatDate(dateString)          // → "Feb 7, 2026"
formatDateTime(dateString)      // → "Feb 7, 2026 3:30 PM"
getPriceChangeClass(value)      // → "text-success" or "text-danger"
getTargetBadgeClass(type)       // → "bg-success" (for target type)
```

---

## 🐍 Backend Routes

### Location: `/web/routes/`

| File | Blueprint | Prefix | Purpose |
|------|-----------|--------|---------|
| `stocks.py` | `stocks_bp` | `/stocks` | Stock CRUD, targets, notes |
| `targets.py` | `targets_bp` | `/targets` | Target operations |
| `tags.py` | `tags_bp` | `/tags` | Tag management |
| `notes.py` | `notes_bp` | `/notes` | Note operations |
| `prices.py` | `prices_bp` | `/prices` | Price fetching |
| `alerts.py` | `alerts_bp` | `/alerts` | Alert history |

---

## 📜 Python Source

### Location: `/src/`

| File | Purpose |
|------|---------|
| `config.py` | Configuration management |
| `db_manager.py` | Database operations (DatabaseManager class) |
| `models.py` | Data models (Stock, Target, Tag, Note, etc.) |
| `stock_fetcher.py` | Fetch prices from yfinance |
| `stock_service.py` | Business logic layer |
| `alert_checker.py` | Check prices vs targets |
| `email_notifier.py` | Send email alerts |

---

## 🛠️ Scripts

### Location: `/scripts/`

| Script | Purpose |
|--------|---------|
| `start_all.sh` | Start everything |
| `start_daemon.sh` | Start price monitoring daemon |
| `start_web.sh` | Start Flask backend |
| `start_frontend.sh` | Start Vue dev server |
| `stop_daemon.sh` | Stop daemon |
| `status_daemon.sh` | Check daemon status |
| `fresh_start.sh` | Clean start |
| `test_flask.sh` | Test Flask server |

---

## 🎯 When Adding New Components

### Component Checklist
- [ ] Create in `/web/frontend/src/components/`
- [ ] Use PascalCase naming: `MyComponent.vue`
- [ ] Use Composition API (not Options API)
- [ ] Define props with types and required
- [ ] Define emits explicitly
- [ ] Export default with name
- [ ] Add to this map

### View Checklist
- [ ] Create in `/web/frontend/src/views/`
- [ ] Add route in `/web/frontend/src/router/index.js`
- [ ] Add to navbar if needed
- [ ] Use Pinia store for data
- [ ] Add to this map

### API Endpoint Checklist
- [ ] Create route in `/web/routes/` (or add to existing)
- [ ] Register blueprint in `/web/app.py`
- [ ] Add to `/web/frontend/src/api/index.js`
- [ ] Document in `.claude/context/api-reference.md`
- [ ] Add to this map

---

**Quick Find Commands**:
```bash
# Find component usage
grep -r "AddTargetModal" web/frontend/src/

# Find API usage
grep -r "stocksApi.addTarget" web/frontend/src/

# Find route definitions
grep -r "@.*_bp.route" web/routes/

# Find store usage
grep -r "useStocksStore" web/frontend/src/
```
