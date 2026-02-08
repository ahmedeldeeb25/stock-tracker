# Investment Timeframes Feature

## Overview
Added an investment timeframe categorization system that allows stocks to be tagged with multiple investment strategies (Long-Term, Short-Term, Swing Trade, etc.). This helps users organize their portfolio by investment horizon and trading strategy.

## Key Features
- ✅ Multiple timeframes per stock (e.g., a stock can be both "Long Term" and "Swing Trade")
- ✅ No duplicate timeframes on same stock (enforced by database constraint)
- ✅ Pre-populated with 5 default timeframes
- ✅ Fully customizable (create, edit, delete timeframes)
- ✅ Color-coded badges for visual identification
- ✅ Description field for each timeframe
- ✅ Stock count tracking for each timeframe

## Default Timeframes
1. **Long Term** 🟢 (#10B981) - Hold for 1+ years
2. **Medium Term** 🔵 (#3B82F6) - Hold for 3-12 months
3. **Short Term** 🟠 (#F59E0B) - Hold for weeks to 3 months
4. **Swing Trade** 🟣 (#8B5CF6) - Hold for days to weeks
5. **Day Trade** 🔴 (#EF4444) - Intraday positions

## Implementation Details

### 1. Database Schema

#### New Tables:
```sql
-- Investment timeframes table
CREATE TABLE investment_timeframes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL UNIQUE,
    color VARCHAR(7),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Stock-timeframe junction table (many-to-many)
CREATE TABLE stock_timeframes (
    stock_id INTEGER NOT NULL,
    timeframe_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (stock_id, timeframe_id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    FOREIGN KEY (timeframe_id) REFERENCES investment_timeframes(id) ON DELETE CASCADE
);
```

#### Indexes:
- `idx_timeframes_name` on `investment_timeframes(name)`
- Primary key constraint ensures no duplicate timeframe assignments

### 2. Backend Implementation

#### New Model: `src/models.py`
```python
@dataclass
class Timeframe:
    """Investment timeframe model."""
    id: Optional[int] = None
    name: str = ""
    color: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
```

#### Database Manager Methods: `src/db_manager.py`
- `get_all_timeframes()` - Get all timeframes with stock counts
- `get_timeframe_by_id(timeframe_id)` - Get single timeframe
- `get_timeframes_for_stock(stock_id)` - Get stock's timeframes
- `add_timeframe_to_stock(stock_id, timeframe_id)` - Assign timeframe to stock
- `remove_timeframe_from_stock(stock_id, timeframe_id)` - Remove assignment
- `create_timeframe(name, color, description)` - Create new timeframe
- `update_timeframe(timeframe_id, name, color, description)` - Update timeframe
- `delete_timeframe(timeframe_id)` - Delete timeframe

#### Stock Service Updates: `src/stock_service.py`
Updated both `get_stock_with_details()` and `get_all_stocks_with_details()` to include timeframes in the response:
```python
timeframes = self.db.get_timeframes_for_stock(stock.id)
result["timeframes"] = [
    {"id": tf.id, "name": tf.name, "color": tf.color, "description": tf.description}
    for tf in timeframes
]
```

#### New API Routes: `web/routes/timeframes.py`
```
GET    /api/timeframes              - Get all timeframes with stock counts
GET    /api/timeframes/:id          - Get single timeframe
POST   /api/timeframes              - Create new timeframe
PUT    /api/timeframes/:id          - Update timeframe
DELETE /api/timeframes/:id          - Delete timeframe
```

#### Stock Routes Updates: `web/routes/stocks.py`
```
POST   /api/stocks/:id/timeframes            - Add timeframe to stock
DELETE /api/stocks/:id/timeframes/:id        - Remove timeframe from stock
```

#### App Registration: `web/app.py`
Registered timeframes blueprint:
```python
from routes.timeframes import timeframes_bp
app.register_blueprint(timeframes_bp, url_prefix='/api/timeframes')
```

### 3. Frontend Implementation

#### API Client: `web/frontend/src/api/index.js`
```javascript
// Added to stocksApi
addTimeframe(id, timeframeId)
removeTimeframe(id, timeframeId)

// New timeframesApi
export const timeframesApi = {
  getAll()
  get(id)
  create(data)
  update(id, data)
  delete(id)
}
```

#### New Component: `ManageTimeframesModal.vue` (420 lines)
A comprehensive modal for managing investment timeframes, featuring:

**Sections:**
1. **Current Timeframes** - Shows assigned timeframes with remove button
2. **Add Existing** - Dropdown to add from available timeframes (with stock count)
3. **Create New** - Form to create custom timeframes (name, description, color)
4. **Manage All** - List of all timeframes with edit/delete actions

**Features:**
- Real-time description preview when selecting timeframe
- Inline editing with save/cancel buttons
- Confirm dialogs for delete operations
- Toast notifications for all actions
- Auto-refresh on changes
- Accessible (ARIA labels, keyboard navigation)

#### StockDetail.vue Updates
**Display Section:**
```vue
<!-- Investment Timeframes -->
<div class="mb-4">
  <label class="form-label small text-muted mb-1">Investment Timeframe</label>
  <div v-if="stock.timeframes && stock.timeframes.length">
    <button
      v-for="timeframe in stock.timeframes"
      :key="timeframe.id"
      class="badge timeframe-badge clickable-tag"
      :style="{ backgroundColor: timeframe.color }"
      @click="showManageTimeframesModal"
      :title="timeframe.description"
    >
      <i class="bi bi-clock me-1"></i>
      {{ timeframe.name }}
    </button>
  </div>
  <button v-else @click="showManageTimeframesModal">
    <i class="bi bi-plus me-1"></i>
    Add Timeframe
  </button>
</div>
```

**Modal Integration:**
- Imported `ManageTimeframesModal` component
- Added `showManageTimeframesModal()` function
- Added `handleTimeframesUpdated()` callback
- Included modal in template

#### StockCard.vue Updates
Added timeframes display after tags:
```vue
<!-- Investment Timeframes -->
<div class="mb-2" v-if="stock.timeframes && stock.timeframes.length">
  <span
    v-for="timeframe in stock.timeframes"
    :key="timeframe.id"
    class="badge timeframe-badge me-1"
    :style="{ backgroundColor: timeframe.color }"
    :title="timeframe.description"
  >
    <i class="bi bi-clock me-1"></i>
    {{ timeframe.name }}
  </span>
</div>
```

## Usage Examples

### 1. Assign Timeframe to Stock
1. Navigate to stock detail page
2. Click on "Add Timeframe" button (or existing timeframe badge)
3. Select timeframe from dropdown and click "Add"
4. Or create new timeframe with custom name/color/description

### 2. Remove Timeframe from Stock
1. Open timeframes modal
2. Click X button on timeframe badge in "Current Timeframes" section
3. Confirm removal

### 3. Create Custom Timeframe
1. Open timeframes modal
2. In "Create New Timeframe" section:
   - Enter name (e.g., "Scalping")
   - Enter description (e.g., "Very short-term trades")
   - Choose color
3. Click "Create"

### 4. Edit Existing Timeframe
1. Open timeframes modal
2. In "All Timeframes" section, click pencil icon
3. Edit name, description, and/or color
4. Click checkmark to save

### 5. Delete Timeframe
1. Open timeframes modal
2. In "All Timeframes" section, click trash icon
3. Confirm deletion (removes from all stocks)

## UI/UX Features

### Visual Design:
- **Clock Icon** 🕐 - Distinguishes timeframes from tags
- **Color Coding** - Each timeframe has unique color
- **Badges** - Consistent badge style with tags
- **Tooltips** - Hover to see description
- **Labels** - "Investment Timeframe" label above section

### Interactions:
- **Clickable** - Click any badge to open management modal
- **Add Button** - Shows when no timeframes assigned
- **Inline Editing** - Edit directly in list without separate modal
- **Confirmation** - Confirms destructive actions (remove/delete)
- **Toast Feedback** - Success/error messages for all actions

### Accessibility:
- ✅ ARIA labels on all interactive elements
- ✅ Semantic HTML (buttons, labels, forms)
- ✅ Keyboard navigation
- ✅ Screen reader support
- ✅ Focus management
- ✅ Color independence (icon + text)

## Data Flow

```
User Action
    ↓
Frontend Component (ManageTimeframesModal)
    ↓
API Client (timeframesApi / stocksApi)
    ↓
Backend Routes (timeframes_bp / stocks_bp)
    ↓
Database Manager (db_manager)
    ↓
SQLite Database
    ↓
Response back through chain
    ↓
UI Updates + Toast Notification
```

## Business Logic

### Timeframe Assignment Rules:
1. ✅ A stock can have multiple timeframes
2. ✅ No duplicate timeframes on same stock (enforced by primary key)
3. ✅ Same stock CAN have both "Long Term" and "Swing Trade"
4. ❌ Same stock CANNOT have "Long Term" twice

### Deletion Behavior:
- **Delete Stock** → Automatically removes all timeframe assignments (CASCADE)
- **Delete Timeframe** → Removes from all stocks, then deletes timeframe

### Default Behavior:
- New database automatically creates 5 default timeframes
- Existing databases get defaults on next initialization
- Users can delete/modify defaults if desired

## Testing Scenarios

### Manual Testing:
1. ✅ Create new stock and assign multiple timeframes
2. ✅ Remove timeframe from stock
3. ✅ Create custom timeframe
4. ✅ Edit timeframe (name, color, description)
5. ✅ Delete timeframe (check removal from all stocks)
6. ✅ Try to add same timeframe twice (should fail gracefully)
7. ✅ Check timeframes display on Dashboard (StockCard)
8. ✅ Check timeframes display on Stock Detail page
9. ✅ Verify color coding and icons
10. ✅ Test with no timeframes assigned

### Edge Cases:
- ✅ Stock with no timeframes (shows "Add Timeframe" button)
- ✅ All timeframes already assigned (dropdown empty)
- ✅ Delete last timeframe from system
- ✅ Long timeframe names/descriptions
- ✅ Special characters in names

## Files Created/Modified

### Created:
1. `/web/routes/timeframes.py` (150 lines) - Timeframes API routes
2. `/web/frontend/src/components/ManageTimeframesModal.vue` (420 lines) - Management UI

### Modified:
3. `/src/db_manager.py` - Added timeframe schema and CRUD methods (~200 lines added)
4. `/src/models.py` - Added Timeframe model (8 lines)
5. `/src/stock_service.py` - Include timeframes in stock details (4 lines)
6. `/web/app.py` - Register timeframes blueprint (3 lines)
7. `/web/routes/stocks.py` - Add/remove timeframe routes (50 lines)
8. `/web/frontend/src/api/index.js` - Timeframes API client (35 lines)
9. `/web/frontend/src/views/StockDetail.vue` - Display and manage timeframes (60 lines)
10. `/web/frontend/src/components/StockCard.vue` - Display timeframes on cards (15 lines)

## Future Enhancements

### Potential Features:
1. **Timeframe Filtering** - Filter dashboard by timeframe
2. **Timeframe Statistics** - Performance metrics by timeframe
3. **Timeframe Presets** - Quick assign common combinations
4. **Bulk Assignment** - Assign timeframe to multiple stocks
5. **Timeframe Calendar** - View holdings by expiration/holding period
6. **Smart Suggestions** - Recommend timeframes based on targets/notes
7. **Timeframe Alerts** - Notify when holding period reached
8. **Historical Tracking** - Track timeframe changes over time

### Advanced Features:
- **Auto-Assignment** - Assign based on target prices/dates
- **Timeframe-based Portfolio View** - Separate views for each strategy
- **Performance Comparison** - Compare returns across timeframes
- **Risk Analysis** - Risk metrics per timeframe category

## Benefits

### For Users:
- 📊 **Better Organization** - Categorize stocks by investment strategy
- 🎯 **Clear Strategy** - Visualize investment approach at a glance
- 🔍 **Quick Filtering** - (Future) Filter by timeframe
- 📈 **Performance Tracking** - (Future) Track strategy effectiveness

### For Portfolio Management:
- **Diversification** - See balance across timeframes
- **Tax Planning** - Identify long-term vs short-term holdings
- **Risk Management** - Adjust exposure by timeframe
- **Strategic Planning** - Align holdings with investment goals

---

**Date:** February 7, 2026
**Version:** 1.0
**Author:** Claude Code
**Status:** ✅ Complete and Ready for Use
