# API Reference

**Base URL**: `http://localhost:5555/api` (dev) or `/api` (prod)

**Last Updated**: February 7, 2026

---

## 📊 Stocks API

### Get All Stocks
```http
GET /stocks?tag={tag}&search={query}&include_prices={true|false}
```

**Query Parameters**:
- `tag` (optional): Filter by tag name
- `search` (optional): Search in symbol or company name
- `include_prices` (optional): Include current prices (default: false)

**Response**:
```json
{
  "stocks": [
    {
      "id": 1,
      "symbol": "AMZN",
      "company_name": "Amazon.com Inc.",
      "current_price": 210.32,
      "price_change_percent": 2.5,
      "tags": [
        {"id": 1, "name": "tech", "color": "#0d6efd"}
      ],
      "targets": [...],
      "notes_count": 2
    }
  ],
  "total": 3,
  "available_tags": [...]
}
```

---

### Get Single Stock
```http
GET /stocks/{symbol}
```

**Response**:
```json
{
  "id": 1,
  "symbol": "AMZN",
  "company_name": "Amazon.com Inc.",
  "current_price": 210.32,
  "price_change_percent": 2.5,
  "tags": [...],
  "targets": [
    {
      "id": 1,
      "target_type": "Buy",
      "target_price": 180.00,
      "trim_percentage": null,
      "alert_note": "Good entry point",
      "is_active": true,
      "is_triggered": false,
      "difference": 30.32,
      "difference_percent": 16.84
    }
  ],
  "notes": [
    {
      "id": 1,
      "title": "Q4 Earnings",
      "content": "<p><strong>Strong</strong> results...</p>",
      "note_date": "2026-02-07",
      "created_at": "2026-02-07T10:30:00"
    }
  ],
  "alert_history": [...]
}
```

---

### Create Stock
```http
POST /stocks
Content-Type: application/json
```

**Request Body**:
```json
{
  "symbol": "NVDA",
  "company_name": "NVIDIA Corporation",
  "tags": ["tech", "AI"],
  "targets": [
    {
      "target_type": "Buy",
      "target_price": 800.00,
      "alert_note": "Entry point",
      "trim_percentage": null
    }
  ]
}
```

**Response**: Returns created stock with full details (201 Created)

---

### Update Stock
```http
PUT /stocks/{stock_id}
Content-Type: application/json
```

**Request Body**:
```json
{
  "company_name": "Updated Name"
}
```

**Response**:
```json
{
  "success": true
}
```

---

### Delete Stock
```http
DELETE /stocks/{stock_id}
```

**Response**:
```json
{
  "success": true
}
```

---

## 🎯 Targets API

### Get Stock Targets
```http
GET /stocks/{stock_id}/targets
```

**Response**:
```json
{
  "targets": [...]
}
```

---

### Add Target to Stock
```http
POST /stocks/{stock_id}/targets
Content-Type: application/json
```

**Request Body**:
```json
{
  "target_type": "Sell",
  "target_price": 250.00,
  "alert_note": "Take profits",
  "trim_percentage": 25
}
```

**Response**:
```json
{
  "id": 7,
  "success": true
}
```

---

### Update Target
```http
PUT /targets/{target_id}
Content-Type: application/json
```

**Request Body**:
```json
{
  "target_price": 260.00,
  "alert_note": "Updated note",
  "trim_percentage": 30
}
```

**Response**:
```json
{
  "success": true
}
```

---

### Delete Target
```http
DELETE /targets/{target_id}
```

**Response**:
```json
{
  "success": true
}
```

---

### Toggle Target Active Status
```http
PATCH /targets/{target_id}/toggle
```

**Response**:
```json
{
  "is_active": false,
  "success": true
}
```

---

## 📝 Notes API

### Get Stock Notes
```http
GET /stocks/{stock_id}/notes?limit={number}
```

**Query Parameters**:
- `limit` (optional): Max number of notes to return

**Response**:
```json
{
  "notes": [
    {
      "id": 1,
      "title": "Q4 Earnings Analysis",
      "content": "<p>Formatted <strong>HTML</strong> content</p>",
      "note_date": "2026-02-07",
      "created_at": "2026-02-07T10:30:00",
      "updated_at": "2026-02-07T10:30:00"
    }
  ]
}
```

---

### Add Note to Stock
```http
POST /stocks/{stock_id}/notes
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Q4 Earnings",
  "content": "<p><strong>Strong</strong> quarter...</p>",
  "note_date": "2026-02-07"
}
```

**Response**:
```json
{
  "id": 4,
  "success": true
}
```

---

### Update Note
```http
PUT /notes/{note_id}
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Updated Title",
  "content": "<p>Updated content</p>",
  "note_date": "2026-02-08"
}
```

**Response**:
```json
{
  "success": true
}
```

---

### Delete Note
```http
DELETE /notes/{note_id}
```

**Response**:
```json
{
  "success": true
}
```

---

## 🏷️ Tags API

### Get All Tags
```http
GET /tags
```

**Response**:
```json
{
  "tags": [
    {
      "id": 1,
      "name": "tech",
      "color": "#0d6efd",
      "stock_count": 2
    }
  ]
}
```

---

### Create Tag
```http
POST /tags
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "AI",
  "color": "#ff6b6b"
}
```

**Response**:
```json
{
  "id": 7,
  "success": true
}
```

---

### Update Tag
```http
PUT /tags/{tag_id}
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "artificial-intelligence",
  "color": "#ff0000"
}
```

**Response**:
```json
{
  "success": true
}
```

---

### Delete Tag
```http
DELETE /tags/{tag_id}
```

**Response**:
```json
{
  "success": true
}
```

---

### Add Tag to Stock
```http
POST /stocks/{stock_id}/tags
Content-Type: application/json
```

**Request Body**:
```json
{
  "tag_id": 3
}
```

**Response**:
```json
{
  "success": true
}
```

---

### Remove Tag from Stock
```http
DELETE /stocks/{stock_id}/tags/{tag_id}
```

**Response**:
```json
{
  "success": true
}
```

---

## 💰 Prices API

### Get Single Price
```http
GET /prices/{symbol}
```

**Response**:
```json
{
  "symbol": "AMZN",
  "price": 210.32,
  "currency": "USD",
  "timestamp": "2026-02-07T15:30:00"
}
```

---

### Get Batch Prices
```http
POST /prices/batch
Content-Type: application/json
```

**Request Body**:
```json
{
  "symbols": ["AMZN", "HIMS", "ZETA"]
}
```

**Response**:
```json
{
  "prices": {
    "AMZN": 210.32,
    "HIMS": 28.45,
    "ZETA": 22.10
  }
}
```

---

## 🔔 Alerts API

### Get Alert History
```http
GET /alerts?stock_id={id}&limit={number}&offset={number}
```

**Query Parameters**:
- `stock_id` (optional): Filter by stock
- `limit` (optional): Number of results
- `offset` (optional): Pagination offset

**Response**:
```json
{
  "alerts": [
    {
      "id": 1,
      "stock_symbol": "AMZN",
      "target_type": "Buy",
      "current_price": 179.50,
      "target_price": 180.00,
      "alert_note": "Good entry point",
      "email_sent": true,
      "triggered_at": "2026-02-07T09:30:00"
    }
  ],
  "total": 10
}
```

---

### Delete Alert
```http
DELETE /alerts/{alert_id}
```

**Response**:
```json
{
  "success": true
}
```

---

## 🏥 Health Check

### Check API Health
```http
GET /health
```

**Response**:
```json
{
  "status": "ok",
  "message": "Stock Tracker API is running",
  "timestamp": "2026-02-07T15:30:00"
}
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request body",
  "success": false
}
```

### 404 Not Found
```json
{
  "error": "Stock not found",
  "success": false
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error message",
  "success": false
}
```

---

## 🔑 Target Types

| Type | Alert Condition | Use Case |
|------|----------------|----------|
| `Buy` | Price ≤ target | Entry point |
| `DCA` | Price ≤ target | Dollar-cost averaging |
| `Sell` | Price ≥ target | Take profits |
| `Trim` | Price ≥ target | Partial sell (with percentage) |

---

## 📋 Notes

- All timestamps are in ISO 8601 format
- Prices are in USD
- Note content is HTML formatted (from Quill editor)
- Alert notes are plain text
- All DELETE operations cascade (delete related records)

---

**Testing the API**:
```bash
# Health check
curl http://localhost:5555/health

# Get all stocks
curl http://localhost:5555/api/stocks

# Get specific stock
curl http://localhost:5555/api/stocks/AMZN

# Create stock
curl -X POST http://localhost:5555/api/stocks \
  -H "Content-Type: application/json" \
  -d '{"symbol":"NVDA","company_name":"NVIDIA","targets":[{"target_type":"Buy","target_price":800}]}'
```
