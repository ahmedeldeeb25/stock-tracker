# Portfolio Holdings Feature - Engineer Handoff Specification

**Version:** 1.0
**Date:** February 9, 2026
**Status:** Ready for Implementation

---

## 1. Feature Overview

### 1.1 Problem Statement
Users want to track their actual portfolio positions, including number of shares owned and average cost basis, so they can see their unrealized gain/loss compared to current market prices.

### 1.2 Goals
- Allow users to optionally enter number of shares and average buy price per stock
- Display unrealized gain/loss (amount and percentage) when cost basis is provided
- Display total position value when shares are entered
- Maintain clean UX by making this data optional and non-intrusive

### 1.3 User Stories

| ID | As a... | I want to... | So that... |
|----|---------|--------------|------------|
| US-1 | User | Enter the number of shares I own for a stock | I can see my total position value |
| US-2 | User | Enter my average buy price (cost basis) | I can track my unrealized gain/loss |
| US-3 | User | See my gain/loss as both dollar amount and percentage | I understand my investment performance |
| US-4 | User | Update my holdings when I buy or sell | My portfolio stays accurate |
| US-5 | User | See a summary of my total portfolio value | I have an overview of my investments |
| US-6 | User | Leave holdings fields empty | I can still use the app for price alerts only |

### 1.4 Scope

**In Scope:**
- Database schema changes for holdings data
- API endpoints to create/update/delete holdings
- UI for entering and displaying holdings on stock cards
- UI for viewing holdings on stock detail page
- Gain/loss calculation and display
- Position value calculation

**Out of Scope (Future Enhancements):**
- Multiple lots/transactions tracking
- Tax lot accounting (FIFO, LIFO, specific ID)
- Historical performance charts
- Dividend tracking
- Portfolio rebalancing suggestions

---

## 2. Database Schema Changes

### 2.1 New Table: `stock_holdings`

```sql
CREATE TABLE IF NOT EXISTS stock_holdings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL UNIQUE,
    shares DECIMAL(15, 6) NOT NULL,
    average_cost DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_holdings_stock_id ON stock_holdings(stock_id);
```

**Field Descriptions:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | INTEGER | Auto | Primary key |
| `stock_id` | INTEGER | Yes | Foreign key to stocks table (unique - one holding per stock) |
| `shares` | DECIMAL(15,6) | Yes | Number of shares owned (supports fractional shares) |
| `average_cost` | DECIMAL(10,2) | No | Average cost per share in USD (null = don't show gain/loss) |
| `created_at` | TIMESTAMP | Auto | Record creation timestamp |
| `updated_at` | TIMESTAMP | Auto | Last update timestamp |

### 2.2 Migration Strategy

Add migration to `init_database()` method in `src/db_manager.py`:

```python
# Stock holdings table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_id INTEGER NOT NULL UNIQUE,
        shares DECIMAL(15, 6) NOT NULL,
        average_cost DECIMAL(10, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
    )
""")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_holdings_stock_id ON stock_holdings(stock_id)")
```

---

## 3. Data Model Changes

### 3.1 New Model: `Holding`

**File:** `src/models.py`

```python
@dataclass
class Holding:
    """Stock holding/position model."""
    id: Optional[int] = None
    stock_id: Optional[int] = None
    shares: float = 0.0
    average_cost: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
```

### 3.2 Updated Model: `StockWithDetails`

Add holding field to existing dataclass:

```python
@dataclass
class StockWithDetails:
    """Stock with all related data."""
    stock: Stock
    tags: List[Tag]
    targets: List[Target]
    notes: List[Note]
    holding: Optional[Holding] = None  # NEW
    notes_count: int = 0
    current_price: Optional[float] = None
    price_change: Optional[float] = None
    price_change_percent: Optional[float] = None
```

---

## 4. Repository Layer

### 4.1 New Repository: `HoldingRepository`

**File:** `src/repositories/holding_repository.py`

```python
"""Holding repository for stock holding CRUD operations."""

from typing import Optional, Dict, List
from datetime import datetime

from src.repositories.base_repository import BaseRepository
from src.models import Holding


class HoldingRepository(BaseRepository):
    """Repository for stock holding database operations."""

    def create_or_update_holding(
        self,
        stock_id: int,
        shares: float,
        average_cost: Optional[float] = None
    ) -> int:
        """Create or update a stock holding (upsert).

        Args:
            stock_id: Stock ID
            shares: Number of shares
            average_cost: Average cost per share (optional)

        Returns:
            ID of created/updated holding
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stock_holdings (stock_id, shares, average_cost)
                VALUES (?, ?, ?)
                ON CONFLICT(stock_id) DO UPDATE SET
                    shares = excluded.shares,
                    average_cost = excluded.average_cost,
                    updated_at = CURRENT_TIMESTAMP
            """, (stock_id, shares, average_cost))

            # Get the ID (either new or existing)
            cursor.execute(
                "SELECT id FROM stock_holdings WHERE stock_id = ?",
                (stock_id,)
            )
            return cursor.fetchone()[0]

    def get_holding_for_stock(self, stock_id: int) -> Optional[Holding]:
        """Get holding for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            Holding object or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM stock_holdings WHERE stock_id = ?",
                (stock_id,)
            )
            row = cursor.fetchone()

            if row:
                return Holding(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    shares=float(row['shares']),
                    average_cost=float(row['average_cost']) if row['average_cost'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
            return None

    def get_holdings_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, Holding]:
        """Get holdings for multiple stocks in a single query.

        Args:
            stock_ids: List of stock IDs

        Returns:
            Dictionary mapping stock_id to Holding
        """
        if not stock_ids:
            return {}

        with self.get_connection() as conn:
            cursor = conn.cursor()
            placeholders = ','.join('?' * len(stock_ids))
            cursor.execute(
                f"SELECT * FROM stock_holdings WHERE stock_id IN ({placeholders})",
                stock_ids
            )

            holdings = {}
            for row in cursor.fetchall():
                holding = Holding(
                    id=row['id'],
                    stock_id=row['stock_id'],
                    shares=float(row['shares']),
                    average_cost=float(row['average_cost']) if row['average_cost'] else None,
                    created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                    updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                )
                holdings[row['stock_id']] = holding

            return holdings

    def delete_holding(self, stock_id: int) -> bool:
        """Delete a holding for a stock.

        Args:
            stock_id: Stock ID

        Returns:
            True if deleted, False if not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM stock_holdings WHERE stock_id = ?",
                (stock_id,)
            )
            return cursor.rowcount > 0

    def get_portfolio_summary(self) -> Dict[str, float]:
        """Get total portfolio summary (all stocks with holdings).

        Returns:
            Dictionary with total_shares, total_cost_basis
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    COUNT(*) as positions,
                    SUM(shares * COALESCE(average_cost, 0)) as total_cost_basis
                FROM stock_holdings
            """)
            row = cursor.fetchone()

            return {
                "positions": row['positions'] or 0,
                "total_cost_basis": float(row['total_cost_basis']) if row['total_cost_basis'] else 0.0
            }
```

### 4.2 Update `src/repositories/__init__.py`

```python
from src.repositories.holding_repository import HoldingRepository
```

### 4.3 Update `DatabaseManager`

Add to `src/db_manager.py`:

```python
# In __init__:
self.holdings = HoldingRepository(db_path)

# Add facade methods:
def create_or_update_holding(self, stock_id: int, shares: float,
                             average_cost: Optional[float] = None) -> int:
    """Create or update a stock holding."""
    return self.holdings.create_or_update_holding(stock_id, shares, average_cost)

def get_holding_for_stock(self, stock_id: int) -> Optional[Holding]:
    """Get holding for a stock."""
    return self.holdings.get_holding_for_stock(stock_id)

def get_holdings_for_stocks_batch(self, stock_ids: List[int]) -> Dict[int, Holding]:
    """Get holdings for multiple stocks."""
    return self.holdings.get_holdings_for_stocks_batch(stock_ids)

def delete_holding(self, stock_id: int) -> bool:
    """Delete a holding."""
    return self.holdings.delete_holding(stock_id)

def get_portfolio_summary(self) -> Dict[str, float]:
    """Get portfolio summary."""
    return self.holdings.get_portfolio_summary()
```

---

## 5. API Endpoints

### 5.1 New Endpoints

**File:** `web/routes/stocks.py` (add to existing file)

#### 5.1.1 GET `/api/stocks/<stock_id>/holding`

Get holding for a specific stock.

**Response (200):**
```json
{
    "holding": {
        "id": 1,
        "stock_id": 5,
        "shares": 100.5,
        "average_cost": 150.25,
        "created_at": "2026-02-09T10:30:00",
        "updated_at": "2026-02-09T10:30:00"
    }
}
```

**Response (404) - No holding:**
```json
{
    "holding": null
}
```

#### 5.1.2 PUT `/api/stocks/<stock_id>/holding`

Create or update holding for a stock.

**Request Body:**
```json
{
    "shares": 100.5,
    "average_cost": 150.25
}
```

**Validation Rules:**
- `shares`: Required, must be > 0
- `average_cost`: Optional, if provided must be > 0

**Response (200/201):**
```json
{
    "success": true,
    "holding": {
        "id": 1,
        "stock_id": 5,
        "shares": 100.5,
        "average_cost": 150.25,
        "created_at": "2026-02-09T10:30:00",
        "updated_at": "2026-02-09T10:30:00"
    }
}
```

**Response (400):**
```json
{
    "error": "shares is required and must be greater than 0"
}
```

#### 5.1.3 DELETE `/api/stocks/<stock_id>/holding`

Delete holding for a stock.

**Response (200):**
```json
{
    "success": true
}
```

**Response (404):**
```json
{
    "error": "No holding found for this stock"
}
```

#### 5.1.4 GET `/api/portfolio/summary`

Get portfolio-wide summary with current values.

**Response (200):**
```json
{
    "positions_count": 15,
    "total_cost_basis": 25000.50,
    "total_current_value": 28500.75,
    "total_gain_loss": 3500.25,
    "total_gain_loss_percent": 14.0
}
```

### 5.2 Updated Endpoints

#### 5.2.1 Update GET `/api/stocks` Response

Add holding data to each stock when present:

```json
{
    "stocks": [
        {
            "id": 1,
            "symbol": "AAPL",
            "company_name": "Apple Inc.",
            "current_price": 185.50,
            "holding": {
                "shares": 100,
                "average_cost": 150.00,
                "position_value": 18550.00,
                "gain_loss": 3550.00,
                "gain_loss_percent": 23.67
            },
            // ... other fields
        }
    ]
}
```

#### 5.2.2 Update GET `/api/stocks/<symbol>` Response

Add holding data with calculated values:

```json
{
    "id": 1,
    "symbol": "AAPL",
    "current_price": 185.50,
    "holding": {
        "id": 1,
        "shares": 100,
        "average_cost": 150.00,
        "position_value": 18550.00,
        "cost_basis_total": 15000.00,
        "gain_loss": 3550.00,
        "gain_loss_percent": 23.67
    },
    // ... other fields
}
```

### 5.3 Implementation Code

**Add to `web/routes/stocks.py`:**

```python
@stocks_bp.route('/<int:stock_id>/holding', methods=['GET'])
def get_stock_holding(stock_id):
    """Get holding for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        holding = current_app.db_manager.get_holding_for_stock(stock_id)

        if holding:
            return jsonify({
                "holding": {
                    "id": holding.id,
                    "stock_id": holding.stock_id,
                    "shares": holding.shares,
                    "average_cost": holding.average_cost,
                    "created_at": holding.created_at.isoformat() if holding.created_at else None,
                    "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
                }
            })
        else:
            return jsonify({"holding": None})

    except Exception as e:
        logger.error(f"Error fetching holding for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/holding', methods=['PUT'])
def update_stock_holding(stock_id):
    """Create or update holding for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        data = request.get_json()

        # Validate shares
        shares = data.get('shares')
        if shares is None or shares <= 0:
            return jsonify({"error": "shares is required and must be greater than 0"}), 400

        # Validate average_cost if provided
        average_cost = data.get('average_cost')
        if average_cost is not None and average_cost <= 0:
            return jsonify({"error": "average_cost must be greater than 0"}), 400

        holding_id = current_app.db_manager.create_or_update_holding(
            stock_id=stock_id,
            shares=shares,
            average_cost=average_cost
        )

        holding = current_app.db_manager.get_holding_for_stock(stock_id)

        return jsonify({
            "success": True,
            "holding": {
                "id": holding.id,
                "stock_id": holding.stock_id,
                "shares": holding.shares,
                "average_cost": holding.average_cost,
                "created_at": holding.created_at.isoformat() if holding.created_at else None,
                "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
            }
        }), 200

    except Exception as e:
        logger.error(f"Error updating holding for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@stocks_bp.route('/<int:stock_id>/holding', methods=['DELETE'])
def delete_stock_holding(stock_id):
    """Delete holding for a stock."""
    try:
        stock = current_app.db_manager.get_stock_by_id(stock_id)
        if not stock:
            return jsonify({"error": "Stock not found"}), 404

        success = current_app.db_manager.delete_holding(stock_id)

        if success:
            return jsonify({"success": True})
        else:
            return jsonify({"error": "No holding found for this stock"}), 404

    except Exception as e:
        logger.error(f"Error deleting holding for stock {stock_id}: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
```

**Add new route file `web/routes/portfolio.py`:**

```python
"""Portfolio API routes."""

from flask import Blueprint, jsonify, current_app
import logging

logger = logging.getLogger(__name__)

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """Get portfolio summary with total values."""
    try:
        # Get all stocks with holdings
        stocks = current_app.db_manager.get_all_stocks()
        stock_ids = [s.id for s in stocks]

        holdings_batch = current_app.db_manager.get_holdings_for_stocks_batch(stock_ids)

        if not holdings_batch:
            return jsonify({
                "positions_count": 0,
                "total_cost_basis": 0,
                "total_current_value": 0,
                "total_gain_loss": 0,
                "total_gain_loss_percent": 0
            })

        # Fetch current prices for stocks with holdings
        symbols_with_holdings = []
        stock_id_to_symbol = {}
        for stock in stocks:
            if stock.id in holdings_batch:
                symbols_with_holdings.append(stock.symbol)
                stock_id_to_symbol[stock.id] = stock.symbol

        prices = current_app.stock_fetcher.get_multiple_prices(symbols_with_holdings)

        # Calculate totals
        total_cost_basis = 0
        total_current_value = 0
        positions_count = 0

        for stock_id, holding in holdings_batch.items():
            symbol = stock_id_to_symbol.get(stock_id)
            current_price = prices.get(symbol) if symbol else None

            positions_count += 1

            if holding.average_cost:
                total_cost_basis += holding.shares * holding.average_cost

            if current_price:
                total_current_value += holding.shares * current_price

        total_gain_loss = total_current_value - total_cost_basis if total_cost_basis else 0
        total_gain_loss_percent = (total_gain_loss / total_cost_basis * 100) if total_cost_basis else 0

        return jsonify({
            "positions_count": positions_count,
            "total_cost_basis": round(total_cost_basis, 2),
            "total_current_value": round(total_current_value, 2),
            "total_gain_loss": round(total_gain_loss, 2),
            "total_gain_loss_percent": round(total_gain_loss_percent, 2)
        })

    except Exception as e:
        logger.error(f"Error fetching portfolio summary: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
```

---

## 6. Frontend API Layer

### 6.1 Update `web/frontend/src/api/index.js`

Add to `stocksApi` object:

```javascript
export const stocksApi = {
  // ... existing methods ...

  // Get holding for a stock
  getHolding(stockId) {
    return client.get(`/stocks/${stockId}/holding`)
  },

  // Create or update holding
  updateHolding(stockId, data) {
    return client.put(`/stocks/${stockId}/holding`, data)
  },

  // Delete holding
  deleteHolding(stockId) {
    return client.delete(`/stocks/${stockId}/holding`)
  }
}

// Add new portfolio API
export const portfolioApi = {
  // Get portfolio summary
  getSummary() {
    return client.get('/portfolio/summary')
  }
}
```

---

## 7. Frontend UI Components

### 7.1 Updated StockCard Component

**File:** `web/frontend/src/components/StockCard.vue`

#### 7.1.1 Wireframe (Text-Based)

```
+--------------------------------------------------+
| AAPL                           $185.50  +2.35%   |
| Apple Inc.                                       |
|                                                  |
| [tech] [growth]                                  |
| [clock] Long Term                                |
|                                                  |
| +----------------------------------------------+ |
| | HOLDINGS                                     | |
| | 100 shares @ $150.00 avg                     | |
| | Value: $18,550.00                            | |
| | Gain: +$3,550.00 (+23.67%)                   | |
| +----------------------------------------------+ |
|                                                  |
| Buy @ $140.00 ..................... -24.59%     |
| Sell @ $200.00 .................... +7.82%      |
|                                                  |
| [journal icon] 3 notes                           |
|--------------------------------------------------|
| [eye] Details          [pencil] Holdings  [trash]|
+--------------------------------------------------+
```

#### 7.1.2 Holdings Section Specifications

**Container:**
- Background: `#f8f9fa` (Bootstrap's `bg-light`)
- Border: 1px solid `#dee2e6` (Bootstrap's border color)
- Border-radius: 0.375rem (6px)
- Padding: 0.75rem (12px)
- Margin-bottom: 0.75rem

**Typography:**
- Label "HOLDINGS": `text-muted`, `text-uppercase`, `small`, font-weight 600, letter-spacing 0.5px
- Shares line: Regular weight, "100 shares @ $150.00 avg"
- Value line: Font-weight 500, "Value: $18,550.00"
- Gain/Loss line:
  - Positive: `text-success` (green), "+$3,550.00 (+23.67%)"
  - Negative: `text-danger` (red), "-$500.00 (-3.23%)"
  - Zero/None: `text-muted` (gray)

**Conditional Display:**
- Show holdings section only if `stock.holding` exists
- Show "Gain/Loss" line only if `holding.average_cost` is not null
- If no average_cost, show only shares and position value

#### 7.1.3 Updated Template Section

```vue
<!-- Holdings Section (insert after timeframes, before targets) -->
<div v-if="stock.holding" class="holdings-section mb-3">
  <div class="holdings-label text-muted text-uppercase small fw-semibold mb-1">
    Holdings
  </div>
  <div class="holdings-content">
    <div class="shares-line">
      {{ formatNumber(stock.holding.shares) }} shares
      <span v-if="stock.holding.average_cost" class="text-muted">
        @ {{ formatPrice(stock.holding.average_cost) }} avg
      </span>
    </div>
    <div class="value-line fw-medium" v-if="stock.holding.position_value">
      Value: {{ formatPrice(stock.holding.position_value) }}
    </div>
    <div
      v-if="stock.holding.gain_loss !== undefined && stock.holding.gain_loss !== null"
      class="gain-loss-line"
      :class="getGainLossClass(stock.holding.gain_loss)"
    >
      {{ stock.holding.gain_loss >= 0 ? 'Gain' : 'Loss' }}:
      {{ formatGainLoss(stock.holding.gain_loss) }}
      ({{ formatPercent(stock.holding.gain_loss_percent) }})
    </div>
  </div>
</div>
```

#### 7.1.4 New Formatter Functions

Add to `web/frontend/src/utils/formatters.js`:

```javascript
// Format number with commas (for shares)
export function formatNumber(num) {
  if (num === null || num === undefined) return 'N/A'
  return parseFloat(num).toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 6
  })
}

// Format gain/loss with + or - sign
export function formatGainLoss(value) {
  if (value === null || value === undefined) return 'N/A'
  const formatted = Math.abs(value).toLocaleString('en-US', {
    style: 'currency',
    currency: 'USD'
  })
  return value >= 0 ? `+${formatted}` : `-${formatted}`
}

// Get CSS class for gain/loss display
export function getGainLossClass(value) {
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-danger'
  return 'text-muted'
}
```

### 7.2 New EditHoldingModal Component

**File:** `web/frontend/src/components/EditHoldingModal.vue`

#### 7.2.1 Wireframe

```
+--------------------------------------------------+
|                Edit Holdings            [X Close]|
|--------------------------------------------------|
|                                                  |
|  Shares Owned *                                  |
|  +--------------------------------------------+  |
|  | 100                                        |  |
|  +--------------------------------------------+  |
|  Number of shares you currently own              |
|                                                  |
|  Average Cost Per Share                          |
|  +--------------------------------------------+  |
|  | 150.00                                     |  |
|  +--------------------------------------------+  |
|  Leave empty to hide gain/loss calculations      |
|                                                  |
|  +--------------------------------------------+  |
|  | Preview:                                   |  |
|  | Position Value: $15,000.00                 |  |
|  | Cost Basis: $15,000.00                     |  |
|  +--------------------------------------------+  |
|                                                  |
|  [!] Warning: This is for tracking only.         |
|      It does not execute any trades.             |
|                                                  |
|--------------------------------------------------|
|  [Delete Holdings]              [Cancel] [Save]  |
+--------------------------------------------------+
```

#### 7.2.2 Component Specifications

**Modal:**
- ID: `editHoldingModal`
- Size: Default (no `modal-lg`)
- Scrollable: No (content fits)

**Form Fields:**

| Field | Type | Required | Validation | Help Text |
|-------|------|----------|------------|-----------|
| Shares | number (step=0.000001) | Yes | > 0 | "Number of shares you currently own" |
| Average Cost | number (step=0.01) | No | If provided, > 0 | "Leave empty to hide gain/loss calculations" |

**Buttons:**
- Delete Holdings: `btn-outline-danger`, left-aligned, only shown if holding exists
- Cancel: `btn-outline-secondary`, dismisses modal
- Save: `btn-primary`, submits form

**Accessibility:**
- All inputs have associated labels
- Required fields marked with asterisk and `aria-required="true"`
- Delete button has confirmation tooltip

#### 7.2.3 Component Code

```vue
<template>
  <div
    class="modal fade"
    id="editHoldingModal"
    tabindex="-1"
    aria-labelledby="editHoldingModalLabel"
    aria-modal="true"
    role="dialog"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="editHoldingModalLabel">
            {{ hasExistingHolding ? 'Edit Holdings' : 'Add Holdings' }}
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Shares -->
            <div class="mb-3">
              <label for="holdingShares" class="form-label">
                Shares Owned <span class="text-danger">*</span>
              </label>
              <input
                id="holdingShares"
                type="number"
                step="0.000001"
                min="0.000001"
                class="form-control"
                v-model.number="formData.shares"
                required
                aria-required="true"
                aria-describedby="sharesHelp"
              >
              <small id="sharesHelp" class="form-text text-muted">
                Number of shares you currently own
              </small>
            </div>

            <!-- Average Cost -->
            <div class="mb-3">
              <label for="holdingCost" class="form-label">
                Average Cost Per Share
              </label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input
                  id="holdingCost"
                  type="number"
                  step="0.01"
                  min="0.01"
                  class="form-control"
                  v-model.number="formData.average_cost"
                  aria-describedby="costHelp"
                >
              </div>
              <small id="costHelp" class="form-text text-muted">
                Leave empty to hide gain/loss calculations
              </small>
            </div>

            <!-- Preview -->
            <div v-if="preview.positionValue" class="alert alert-light mb-3">
              <strong>Preview:</strong>
              <div>Position Value: {{ formatPrice(preview.positionValue) }}</div>
              <div v-if="preview.costBasis">
                Cost Basis: {{ formatPrice(preview.costBasis) }}
              </div>
            </div>

            <!-- Info Notice -->
            <div class="alert alert-info small mb-0">
              <i class="bi bi-info-circle me-1" aria-hidden="true"></i>
              This is for tracking purposes only. It does not execute any trades.
            </div>
          </form>
        </div>
        <div class="modal-footer justify-content-between">
          <button
            v-if="hasExistingHolding"
            type="button"
            class="btn btn-outline-danger"
            @click="handleDelete"
            :disabled="submitting"
          >
            <i class="bi bi-trash me-1" aria-hidden="true"></i>
            Delete
          </button>
          <div v-else></div>
          <div>
            <button
              type="button"
              class="btn btn-outline-secondary me-2"
              data-bs-dismiss="modal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="handleSubmit"
              :disabled="submitting || !isValid"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                aria-hidden="true"
              ></span>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { stocksApi } from '@/api'
import { formatPrice } from '@/utils/formatters'
import { useToastStore } from '@/stores/toast'

export default {
  name: 'EditHoldingModal',
  props: {
    stockId: {
      type: Number,
      required: true
    },
    currentPrice: {
      type: Number,
      default: null
    },
    existingHolding: {
      type: Object,
      default: null
    }
  },
  emits: ['holding-updated', 'holding-deleted'],
  setup(props, { emit }) {
    const toast = useToastStore()

    const formData = ref({
      shares: null,
      average_cost: null
    })

    const submitting = ref(false)

    const hasExistingHolding = computed(() => !!props.existingHolding)

    const isValid = computed(() => {
      return formData.value.shares && formData.value.shares > 0
    })

    const preview = computed(() => {
      if (!formData.value.shares || !props.currentPrice) {
        return {}
      }

      return {
        positionValue: formData.value.shares * props.currentPrice,
        costBasis: formData.value.average_cost
          ? formData.value.shares * formData.value.average_cost
          : null
      }
    })

    // Initialize form when existingHolding changes
    watch(() => props.existingHolding, (newHolding) => {
      if (newHolding) {
        formData.value = {
          shares: newHolding.shares,
          average_cost: newHolding.average_cost
        }
      } else {
        formData.value = {
          shares: null,
          average_cost: null
        }
      }
    }, { immediate: true })

    const handleSubmit = async () => {
      if (!isValid.value) return

      submitting.value = true

      try {
        await stocksApi.updateHolding(props.stockId, {
          shares: formData.value.shares,
          average_cost: formData.value.average_cost || null
        })

        // Close modal
        const modal = document.getElementById('editHoldingModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('holding-updated')
        toast.success('Holdings updated successfully')
      } catch (error) {
        toast.error('Failed to update holdings: ' + (error.response?.data?.error || error.message))
      } finally {
        submitting.value = false
      }
    }

    const handleDelete = async () => {
      if (!confirm('Are you sure you want to delete this holding?')) return

      submitting.value = true

      try {
        await stocksApi.deleteHolding(props.stockId)

        // Close modal
        const modal = document.getElementById('editHoldingModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('holding-deleted')
        toast.success('Holdings deleted successfully')
      } catch (error) {
        toast.error('Failed to delete holdings: ' + (error.response?.data?.error || error.message))
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      submitting,
      hasExistingHolding,
      isValid,
      preview,
      formatPrice,
      handleSubmit,
      handleDelete
    }
  }
}
</script>
```

### 7.3 StockDetail View Updates

**File:** `web/frontend/src/views/StockDetail.vue`

#### 7.3.1 Updated Wireframe (Header Section)

```
+------------------------------------------------------------------+
| <- Back to Dashboard                                              |
|                                                                   |
| AAPL [chart icon]                    $185.50                      |
| Apple Inc.                           After Hours: $186.20 +0.38%  |
|                                      RSI: 52.34                   |
|                                      [Refresh]                    |
|                                                                   |
| [tech] [growth]                                                   |
| [clock] Long Term                                                 |
|                                                                   |
| +---------------------------------------------------------------+ |
| | YOUR POSITION                                      [Edit]     | |
| +---------------------------------------------------------------+ |
| | 100 shares @ $150.00 avg                                      | |
| |                                                               | |
| | Position Value    Cost Basis      Gain/Loss                   | |
| | $18,550.00        $15,000.00      +$3,550.00 (+23.67%)        | |
| +---------------------------------------------------------------+ |
|                                                                   |
+------------------------------------------------------------------+
```

#### 7.3.2 Holdings Panel Specifications

**Container:**
- Use `CollapsibleCard` component for consistency
- Default open: true
- Storage key: `position-holdings`
- Icon: `bi bi-wallet2`

**Layout (when holding exists):**
- Top row: Shares count and average cost (if set)
- Bottom row: Three-column grid
  - Column 1: Position Value (label + value)
  - Column 2: Cost Basis (label + value, only if average_cost set)
  - Column 3: Gain/Loss (label + value with color, only if average_cost set)

**Edit Button:**
- Position: In card header actions slot
- Style: `btn btn-sm btn-outline-primary`
- Icon: `bi bi-pencil`

**Empty State (no holding):**
- Centered text: "No position tracked"
- Button: "Add Holdings"

#### 7.3.3 Component Template Addition

Add after Investment Timeframes section, before the main row:

```vue
<!-- Position Holdings -->
<CollapsibleCard
  title="Your Position"
  icon="bi bi-wallet2"
  :default-open="true"
  storage-key="position-holdings"
  class="mb-4"
>
  <template #actions>
    <button
      class="btn btn-sm btn-outline-primary"
      @click.stop="showEditHoldingModal"
      :aria-label="stock.holding ? 'Edit holdings' : 'Add holdings'"
    >
      <i :class="stock.holding ? 'bi bi-pencil' : 'bi bi-plus'" aria-hidden="true"></i>
    </button>
  </template>

  <div v-if="stock.holding" class="holding-details">
    <div class="shares-info mb-3">
      <span class="h5 mb-0">{{ formatNumber(stock.holding.shares) }} shares</span>
      <span v-if="stock.holding.average_cost" class="text-muted ms-2">
        @ {{ formatPrice(stock.holding.average_cost) }} avg
      </span>
    </div>

    <div class="row text-center">
      <div class="col">
        <div class="text-muted small text-uppercase">Position Value</div>
        <div class="h5 mb-0">{{ formatPrice(stock.holding.position_value) }}</div>
      </div>
      <div class="col" v-if="stock.holding.average_cost">
        <div class="text-muted small text-uppercase">Cost Basis</div>
        <div class="h5 mb-0">{{ formatPrice(stock.holding.cost_basis_total) }}</div>
      </div>
      <div class="col" v-if="stock.holding.gain_loss !== undefined">
        <div class="text-muted small text-uppercase">Gain/Loss</div>
        <div class="h5 mb-0" :class="getGainLossClass(stock.holding.gain_loss)">
          {{ formatGainLoss(stock.holding.gain_loss) }}
          <small>({{ formatPercent(stock.holding.gain_loss_percent) }})</small>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="text-center py-4">
    <i class="bi bi-wallet2 display-6 text-muted" aria-hidden="true"></i>
    <p class="text-muted mt-2 mb-3">No position tracked</p>
    <button class="btn btn-primary btn-sm" @click="showEditHoldingModal">
      <i class="bi bi-plus me-1" aria-hidden="true"></i>
      Add Holdings
    </button>
  </div>
</CollapsibleCard>
```

---

## 8. Service Layer Updates

### 8.1 StockService Updates

**File:** `src/stock_service.py`

Add holding calculation to `get_stock_with_details()` and `get_all_stocks_with_details()`:

```python
def _calculate_holding_values(
    self,
    holding: Holding,
    current_price: Optional[float]
) -> Dict[str, Any]:
    """Calculate holding values including gain/loss.

    Args:
        holding: Holding object
        current_price: Current stock price

    Returns:
        Dictionary with calculated values
    """
    result = {
        "id": holding.id,
        "shares": holding.shares,
        "average_cost": holding.average_cost,
        "created_at": holding.created_at.isoformat() if holding.created_at else None,
        "updated_at": holding.updated_at.isoformat() if holding.updated_at else None
    }

    # Calculate position value
    if current_price:
        result["position_value"] = round(holding.shares * current_price, 2)

    # Calculate gain/loss if average_cost is set
    if holding.average_cost and current_price:
        cost_basis_total = holding.shares * holding.average_cost
        position_value = holding.shares * current_price
        gain_loss = position_value - cost_basis_total
        gain_loss_percent = (gain_loss / cost_basis_total) * 100

        result["cost_basis_total"] = round(cost_basis_total, 2)
        result["gain_loss"] = round(gain_loss, 2)
        result["gain_loss_percent"] = round(gain_loss_percent, 2)

    return result
```

Update `get_stock_with_details()`:

```python
# After fetching other data, add:
holding = self.db.get_holding_for_stock(stock.id)

# In the result dict, add:
if holding:
    result["holding"] = self._calculate_holding_values(holding, result.get("current_price"))
```

Update `get_all_stocks_with_details()`:

```python
# In batch fetching section:
holdings_batch = self.db.get_holdings_for_stocks_batch(stock_ids)

# In the per-stock loop:
holding = holdings_batch.get(stock.id)
if holding:
    stock_dict["holding"] = self._calculate_holding_values(
        holding,
        prices.get(stock.symbol)
    )
```

---

## 9. Edge Cases and Validation

### 9.1 Input Validation Rules

| Field | Rule | Error Message |
|-------|------|---------------|
| shares | Required | "Shares is required" |
| shares | > 0 | "Shares must be greater than 0" |
| shares | Max 15 digits, 6 decimal places | "Invalid shares value" |
| average_cost | If provided, > 0 | "Average cost must be greater than 0" |
| average_cost | Max 10 digits, 2 decimal places | "Invalid average cost value" |

### 9.2 Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Current price unavailable | Show position value as "N/A", hide gain/loss |
| Average cost is null | Show shares and position value, hide gain/loss section |
| Average cost is 0 | Reject with validation error |
| Very small shares (0.000001) | Accept and display correctly |
| Very large position value | Format with commas, no scientific notation |
| Stock deleted | Holding cascade-deletes via foreign key |
| Negative gain (loss) | Display in red with minus sign |
| Zero gain/loss | Display in gray as "$0.00 (0.00%)" |

### 9.3 Accessibility Considerations

| Element | Requirement |
|---------|-------------|
| Gain/Loss colors | Use icons in addition to color (up/down arrows) |
| Form inputs | All have associated labels and help text |
| Modal | Proper ARIA attributes, focus trapping |
| Holdings section | Screen reader announces values with context |
| Delete action | Requires confirmation before executing |

---

## 10. Acceptance Criteria

### 10.1 Functional Requirements

- [ ] **AC-1:** User can add shares owned for any tracked stock
- [ ] **AC-2:** User can add average cost (optional) for any tracked stock
- [ ] **AC-3:** Position value displays when shares are entered and price is available
- [ ] **AC-4:** Gain/loss displays only when both average cost and current price are available
- [ ] **AC-5:** User can update existing holdings
- [ ] **AC-6:** User can delete holdings (removes both shares and average cost)
- [ ] **AC-7:** Holdings persist across page refreshes
- [ ] **AC-8:** Holdings display on both Dashboard (StockCard) and StockDetail views
- [ ] **AC-9:** Fractional shares (up to 6 decimal places) are supported

### 10.2 UI Requirements

- [ ] **AC-10:** Holdings section is visually distinct but consistent with existing design
- [ ] **AC-11:** Gain displayed in green, loss displayed in red
- [ ] **AC-12:** Modal provides real-time preview of position value
- [ ] **AC-13:** Empty state encourages user to add holdings
- [ ] **AC-14:** Loading states shown during save operations
- [ ] **AC-15:** Success/error toasts displayed after operations

### 10.3 Technical Requirements

- [ ] **AC-16:** Database migration runs without data loss
- [ ] **AC-17:** API validates all inputs server-side
- [ ] **AC-18:** Batch queries used to prevent N+1 problems
- [ ] **AC-19:** Holdings cascade-delete when stock is deleted
- [ ] **AC-20:** All new code follows existing patterns and conventions

---

## 11. Testing Checklist

### 11.1 Unit Tests

- [ ] `HoldingRepository.create_or_update_holding()` - create new
- [ ] `HoldingRepository.create_or_update_holding()` - update existing
- [ ] `HoldingRepository.get_holding_for_stock()` - exists
- [ ] `HoldingRepository.get_holding_for_stock()` - not exists
- [ ] `HoldingRepository.get_holdings_for_stocks_batch()` - multiple stocks
- [ ] `HoldingRepository.delete_holding()` - success
- [ ] `StockService._calculate_holding_values()` - with average cost
- [ ] `StockService._calculate_holding_values()` - without average cost
- [ ] Input validation - shares required
- [ ] Input validation - shares > 0
- [ ] Input validation - average_cost > 0 when provided

### 11.2 Integration Tests

- [ ] Create holding via API
- [ ] Update holding via API
- [ ] Delete holding via API
- [ ] Get stock with holding data
- [ ] Get all stocks with holdings batch
- [ ] Portfolio summary calculation

### 11.3 E2E Tests

- [ ] Add holdings from StockDetail page
- [ ] Edit holdings from StockDetail page
- [ ] Delete holdings with confirmation
- [ ] Holdings display on Dashboard StockCard
- [ ] Holdings persist after refresh
- [ ] Gain/loss displays correctly (positive, negative, zero)

---

## 12. Files to Create/Modify

### 12.1 New Files

| File | Description |
|------|-------------|
| `src/repositories/holding_repository.py` | Holding database operations |
| `web/routes/portfolio.py` | Portfolio summary endpoint |
| `web/frontend/src/components/EditHoldingModal.vue` | Holdings edit modal |

### 12.2 Modified Files

| File | Changes |
|------|---------|
| `src/models.py` | Add `Holding` dataclass |
| `src/db_manager.py` | Add schema migration, facade methods |
| `src/repositories/__init__.py` | Export `HoldingRepository` |
| `src/stock_service.py` | Add holding calculations to stock details |
| `web/routes/stocks.py` | Add holding CRUD endpoints |
| `web/routes/__init__.py` | Register portfolio blueprint |
| `web/frontend/src/api/index.js` | Add holding and portfolio API methods |
| `web/frontend/src/utils/formatters.js` | Add `formatNumber`, `formatGainLoss`, `getGainLossClass` |
| `web/frontend/src/components/StockCard.vue` | Add holdings section |
| `web/frontend/src/views/StockDetail.vue` | Add holdings panel, modal integration |

---

## 13. Implementation Order

### Phase 1: Backend Foundation
1. Create database migration and Holding model
2. Create HoldingRepository
3. Update DatabaseManager with facade methods
4. Update StockService with holding calculations

### Phase 2: API Layer
5. Add holding CRUD endpoints to stocks routes
6. Create portfolio routes with summary endpoint
7. Test all endpoints manually

### Phase 3: Frontend Foundation
8. Add API methods to frontend
9. Add formatter functions
10. Create EditHoldingModal component

### Phase 4: Frontend Integration
11. Update StockCard with holdings display
12. Update StockDetail with holdings panel
13. Wire up modal triggers and event handlers

### Phase 5: Testing and Polish
14. Write unit tests
15. Write integration tests
16. Manual QA testing
17. Fix edge cases and polish

---

## 14. Future Enhancements (Out of Scope)

- **Multiple Lots:** Track individual purchase transactions with dates and prices
- **Tax Lot Accounting:** Support FIFO, LIFO, specific identification for tax reporting
- **Performance History:** Chart showing portfolio value over time
- **Dividend Tracking:** Record and track dividend payments
- **Portfolio Allocation:** Pie chart showing portfolio composition
- **Rebalancing:** Suggestions based on target allocation percentages
- **Import/Export:** CSV import of holdings from brokerages
- **Cost Basis Updates:** Automatic adjustment for stock splits

---

**Document End**

*This specification is ready for engineering review and implementation.*
