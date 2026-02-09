# Stock Tracker Application - Code Review Report

**Date**: February 8, 2026
**Reviewer**: Senior Software Engineer Agent
**Codebase**: Stock Tracker v1.0
**Last Updated**: February 8, 2026

---

## Status Update

**Issues Resolved**:
- ✅ **[CRITICAL-001]** XSS Vulnerability - Fixed on February 8, 2026
  - Added DOMPurify HTML sanitization to ViewNoteModal.vue
  - All user-generated HTML content is now sanitized before rendering
- ✅ **[HIGH-008]** N+1 Query Problem in Stock List - Fixed on February 8, 2026
  - Implemented batch query methods in DatabaseManager
  - Reduced database queries from 1+5N to just 6 queries
  - 97.6% query reduction for typical workloads

**Remaining Critical Issues**: 2
**Remaining High Priority Issues**: 7

---

## Executive Summary

The Stock Tracker application is a well-structured full-stack application with a Python/Flask backend and Vue.js frontend. The codebase demonstrates good separation of concerns, uses parameterized SQL queries (preventing SQL injection), and follows reasonable coding conventions. However, several security and code quality issues require attention before production deployment.

The most critical findings relate to **XSS vulnerabilities** in the frontend (using `v-html` with unsanitized content) [✅ FIXED], **missing authentication/authorization** on all API endpoints, and **overly permissive CORS configuration**. The application also lacks input validation on several API endpoints and has a large database manager file that should be refactored for maintainability.

**Critical findings**: 3 (1 resolved, 2 remaining)
**High priority findings**: 8 (1 resolved, 7 remaining)
**Medium priority findings**: 9
**Approval status**: **Needs Work** - Critical security issues must be addressed before production use.

---

## Critical Issues (Must Fix Immediately)

### [CRITICAL-001] ✅ RESOLVED - XSS Vulnerability via v-html in Note Content

**File**: `/web/frontend/src/components/ViewNoteModal.vue:28`
**Severity**: Critical
**Status**: ✅ **FIXED** on February 8, 2026
**Issue**: The application was using `v-html` to render note content directly from the database without sanitization. Since notes are created via a rich text editor (Quill), malicious JavaScript could be injected and executed when viewing notes.

**Impact**: An attacker who can create notes (or if note content is ever imported/shared) could execute arbitrary JavaScript in the context of other users' sessions, leading to session hijacking, data theft, or malicious actions.

**Original Code**:
```vue
<div class="note-content" v-html="note?.content" role="article"></div>
```

**Fix Applied**: Installed DOMPurify and implemented HTML sanitization with allowed tags configuration.

**Fixed Code**:
```vue
<script>
import { ref, computed } from 'vue'
import DOMPurify from 'dompurify'

// In setup function
const sanitizedContent = computed(() => {
  if (!props.note?.content) {
    return ''
  }
  return DOMPurify.sanitize(props.note.content, {
    ALLOWED_TAGS: ['h1', 'h2', 'h3', 'p', 'br', 'strong', 'em', 'u', 's', 'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'a'],
    ALLOWED_ATTR: ['href', 'target', 'rel']
  })
})
</script>

<template>
  <div class="note-content" v-html="sanitizedContent" role="article"></div>
</template>
```

**Verification**: Frontend builds successfully with DOMPurify v3.3.1 dependency added.

---

### [CRITICAL-002] No Authentication or Authorization

**Files**: All files in `/web/routes/*.py` and `/web/app.py`
**Severity**: Critical
**Issue**: The entire API is publicly accessible without any authentication. Any user who can reach the server can create, read, update, and delete all stocks, targets, tags, notes, and alerts.

**Impact**:
- Data can be exfiltrated by anyone
- Data can be modified or deleted maliciously
- Sensitive financial tracking information is exposed

**Fix**: Implement authentication using Flask-Login or JWT tokens.

```python
# Example using Flask-JWT-Extended
from flask_jwt_extended import JWTManager, jwt_required, create_access_token

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Must be set in .env
jwt = JWTManager(app)

# Protect routes
@stocks_bp.route('', methods=['GET'])
@jwt_required()
def get_stocks():
    # ... existing code
```

Add to `.env.example`:
```
JWT_SECRET_KEY=your-secret-key-here-change-in-production
```

---

### [CRITICAL-003] Overly Permissive CORS Configuration

**File**: `/web/app.py:23`
**Severity**: Critical
**Issue**: CORS is enabled with default settings (`CORS(app)`), which allows any origin to make requests to the API. This combined with the lack of authentication creates a significant security risk.

**Impact**: Any malicious website can make API requests on behalf of users who have the Stock Tracker open, potentially stealing or modifying data.

**Current Code**:
```python
CORS(app)  # Enable CORS for Vue.js development
```

**Fix**: Configure CORS to only allow specific origins in production.

```python
from flask_cors import CORS

# Development vs Production CORS
if os.getenv('FLASK_ENV') == 'development':
    CORS(app, origins=['http://localhost:5173', 'http://localhost:5555'])
else:
    # In production, specify your actual domain
    CORS(app, origins=[os.getenv('ALLOWED_ORIGIN', 'https://yourdomain.com')])
```

---

## High Priority Issues (Should Fix Soon)

### [HIGH-001] Missing Input Validation on API Endpoints

**Files**: `/web/routes/stocks.py`, `/web/routes/tags.py`, `/web/routes/targets.py`
**Severity**: High
**Issue**: API endpoints accept user input without proper validation for:
- Stock symbols (no length limit, no format validation)
- Target prices (no range validation, accepts negative numbers)
- Tag colors (no hex color validation)
- Target types (accepts any string, not validated against enum)

**Impact**: Invalid data can corrupt the database or cause unexpected behavior.

**Example** (`/web/routes/stocks.py:101-115`):
```python
# No validation on symbol format, length, or characters
result = current_app.stock_service.create_stock_with_targets(
    symbol=data['symbol'],  # Could be anything
    company_name=data.get('company_name'),
    targets=data['targets'],  # target_type not validated
    tags=data.get('tags', [])
)
```

**Fix**: Add input validation using a library like `marshmallow` or manual validation.

```python
import re

VALID_TARGET_TYPES = {'Buy', 'Sell', 'DCA', 'Trim'}

def validate_stock_data(data):
    errors = []

    symbol = data.get('symbol', '')
    if not symbol or len(symbol) > 10:
        errors.append("Symbol must be 1-10 characters")
    if not re.match(r'^[A-Z0-9.]+$', symbol.upper()):
        errors.append("Symbol contains invalid characters")

    for target in data.get('targets', []):
        if target.get('target_type') not in VALID_TARGET_TYPES:
            errors.append(f"Invalid target type: {target.get('target_type')}")
        if target.get('target_price', 0) <= 0:
            errors.append("Target price must be positive")

    return errors
```

---

### [HIGH-002] Database Manager File Too Large (1107 lines)

**File**: `/src/db_manager.py`
**Severity**: High
**Issue**: The `DatabaseManager` class is 1107 lines long with 40+ methods, making it difficult to maintain, test, and understand. This violates the Single Responsibility Principle.

**Impact**: Increased maintenance burden, higher likelihood of bugs, difficult to unit test.

**Fix**: Refactor into separate repository classes using the Repository pattern.

```python
# stock_repository.py
class StockRepository:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def create(self, symbol: str, company_name: str = None) -> int:
        # Stock creation logic

    def get_by_symbol(self, symbol: str) -> Optional[Stock]:
        # Get stock logic

    # ... other stock operations

# target_repository.py
class TargetRepository:
    # ... target operations

# Then compose in a facade
class DatabaseManager:
    def __init__(self, db_path: str):
        self.stocks = StockRepository(db_path)
        self.targets = TargetRepository(db_path)
        self.tags = TagRepository(db_path)
        # ...
```

---

### [HIGH-003] Error Messages Expose Internal Details

**Files**: Multiple route files in `/web/routes/*.py`
**Severity**: High
**Issue**: Exception messages are returned directly to clients, potentially exposing sensitive information about the system.

**Example** (`/web/routes/stocks.py:46`):
```python
except Exception as e:
    logger.error(f"Error fetching stocks: {e}", exc_info=True)
    return jsonify({"error": str(e)}), 500  # Exposes full exception
```

**Impact**: Attackers can learn about database structure, file paths, and system internals from error messages.

**Fix**: Return generic error messages to clients while logging details server-side.

```python
except Exception as e:
    logger.error(f"Error fetching stocks: {e}", exc_info=True)
    return jsonify({"error": "An internal error occurred. Please try again later."}), 500
```

For expected errors (validation failures), return specific but safe messages:
```python
except ValueError as e:
    return jsonify({"error": "Invalid input provided"}), 400
```

---

### [HIGH-004] No Rate Limiting on API Endpoints

**File**: `/web/app.py`
**Severity**: High
**Issue**: No rate limiting is implemented, allowing unlimited API requests. The price fetching endpoints are particularly vulnerable as they make external API calls.

**Impact**:
- Denial of Service attacks
- Abuse of yfinance API (could get IP blocked)
- Resource exhaustion

**Fix**: Implement rate limiting using Flask-Limiter.

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Apply stricter limits to price fetching
@prices_bp.route('/<symbol>', methods=['GET'])
@limiter.limit("10 per minute")
def get_price(symbol):
    # ...
```

---

### [HIGH-005] Secrets Could Be Committed via config.json

**File**: `/src/config.py:24-26`
**Severity**: High
**Issue**: The config module supports loading credentials from a `config.json` file. If this file is accidentally committed, secrets would be exposed in version control.

**Current Code**:
```python
if os.path.exists(self.config_path):
    with open(self.config_path, 'r') as f:
        config = json.load(f)
```

**Impact**: Leaked API keys, passwords, and tokens if config.json is committed.

**Fix**:
1. Add `config.json` to `.gitignore` (verify it's there)
2. Add a warning if config.json is being used
3. Prefer environment variables only

```python
if os.path.exists(self.config_path):
    logger.warning("Loading config from file - ensure this file is not committed to version control")
    with open(self.config_path, 'r') as f:
        config = json.load(f)
```

Check `.gitignore`:
```bash
# Ensure these are in .gitignore
config.json
.env
*.db
```

---

### [HIGH-006] Missing CSRF Protection

**File**: `/web/app.py`
**Severity**: High
**Issue**: No CSRF protection is implemented. While the API uses JSON (which provides some CSRF protection), form-based attacks could still be possible.

**Impact**: Cross-site request forgery attacks could modify or delete user data.

**Fix**: Implement CSRF protection using Flask-WTF or custom token validation.

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)

# For JSON API, use custom token header
@app.before_request
def check_csrf_header():
    if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
        if request.content_type == 'application/json':
            csrf_token = request.headers.get('X-CSRF-Token')
            # Validate token
```

---

### [HIGH-007] N+1 Query Problem in Alert History

**File**: `/web/routes/alerts.py:30-45`
**Severity**: High
**Issue**: For each alert in the history, a separate database query is made to fetch the stock symbol, resulting in N+1 queries.

**Current Code**:
```python
for alert in alerts:
    stock = current_app.db_manager.get_stock_by_id(alert.stock_id)  # N queries!
    alert_list.append({
        "symbol": stock.symbol if stock else "Unknown",
        # ...
    })
```

**Impact**: Poor performance with large alert histories, excessive database load.

**Fix**: Use a JOIN query to fetch alerts with stock symbols in a single query.

```python
# In db_manager.py
def get_alert_history_with_symbols(self, stock_id=None, limit=50, offset=0):
    query = """
        SELECT ah.*, s.symbol
        FROM alert_history ah
        JOIN stocks s ON ah.stock_id = s.id
        ORDER BY ah.triggered_at DESC
        LIMIT ? OFFSET ?
    """
    # ...
```

---

### [HIGH-008] ✅ RESOLVED - N+1 Query Problem in Stock List

**File**: `/src/stock_service.py:181-186`
**Severity**: High
**Status**: ✅ **FIXED** on February 8, 2026
**Issue**: When fetching all stocks with details, multiple queries were made per stock (targets, tags, timeframes, notes_count, latest_alert). With N stocks, this resulted in 1+5N database queries.

**Impact**: With 50 stocks, this resulted in 251 database queries instead of 6 optimized queries. Poor performance and excessive database load.

**Original Code**:
```python
for stock in stocks:
    targets = self.db.get_targets_for_stock(stock.id)  # N queries
    tags = self.db.get_tags_for_stock(stock.id)        # N queries
    timeframes = self.db.get_timeframes_for_stock(stock.id)  # N queries
    notes_count = self.db.get_notes_count_for_stock(stock.id)  # N queries
    latest_alert = self.db.get_latest_alert_for_stock(stock.id)  # N queries
```

**Fix Applied**: Implemented 5 new batch query methods in DatabaseManager:
1. `get_targets_for_stocks_batch(stock_ids)` - Fetch all targets in one query
2. `get_tags_for_stocks_batch(stock_ids)` - Fetch all tags with JOIN in one query
3. `get_timeframes_for_stocks_batch(stock_ids)` - Fetch all timeframes with JOIN
4. `get_notes_count_for_stocks_batch(stock_ids)` - Count notes with GROUP BY
5. `get_latest_alert_for_stocks_batch(stock_ids)` - Fetch latest alerts with subquery

**Fixed Code** (`/src/stock_service.py`):
```python
# Batch fetch all related data to avoid N+1 queries (HIGH-008 fix)
stock_ids = [s.id for s in stocks]
targets_batch = self.db.get_targets_for_stocks_batch(stock_ids)
tags_batch = self.db.get_tags_for_stocks_batch(stock_ids)
timeframes_batch = self.db.get_timeframes_for_stocks_batch(stock_ids)
notes_counts = self.db.get_notes_count_for_stocks_batch(stock_ids)
latest_alerts = self.db.get_latest_alert_for_stocks_batch(stock_ids)

for stock in stocks:
    # Retrieve pre-fetched data from batch results
    targets = targets_batch.get(stock.id, [])
    tags = tags_batch.get(stock.id, [])
    timeframes = timeframes_batch.get(stock.id, [])
    notes_count = notes_counts.get(stock.id, 0)
    latest_alert = latest_alerts.get(stock.id)
```

**Performance Improvement**:
- Before: 1 + 5×N queries (e.g., 251 queries for 50 stocks)
- After: 1 + 5 = 6 queries (regardless of N)
- **97.6% reduction in database queries for typical workloads**

**Verification**: Python syntax validated successfully.

---

## Medium Priority Issues (Consider Fixing)

### [MEDIUM-001] Console.log in Production Code

**File**: `/web/frontend/src/api/client.js:27`
**Severity**: Medium
**Issue**: API errors are logged to console, which can expose sensitive information to users with browser dev tools.

**Current Code**:
```javascript
console.error('API Error:', error.response?.data || error.message)
```

**Fix**: Use a proper logging service or remove in production.

```javascript
if (import.meta.env.DEV) {
  console.error('API Error:', error.response?.data || error.message)
}
```

---

### [MEDIUM-002] TODO Without Issue Tracking

**File**: `/web/routes/prices.py:20`
**Severity**: Medium
**Issue**: TODO comment without a linked issue or clear timeline.

**Current Code**:
```python
# TODO: Calculate change and change_percent (requires historical data)
```

**Fix**: Create an issue in the project tracker and reference it.

```python
# TODO(issue-#42): Calculate change and change_percent
```

---

### [MEDIUM-003] Missing Database Connection Pooling

**File**: `/src/db_manager.py:26-39`
**Severity**: Medium
**Issue**: Each database operation creates a new connection. While SQLite handles this reasonably well, it's inefficient for high-traffic scenarios.

**Current Code**:
```python
@contextmanager
def get_connection(self):
    conn = sqlite3.connect(self.db_path)  # New connection each time
    # ...
```

**Fix**: Consider using connection pooling or a persistent connection for read operations.

---

### [MEDIUM-004] Hardcoded Port Numbers

**Files**: `/web/app.py:114`, `/web/frontend/src/api/client.js:4`
**Severity**: Medium
**Issue**: Port 5555 is hardcoded in multiple places.

**Current Code**:
```python
port = int(os.getenv('PORT', 5555))
```

```javascript
baseURL: import.meta.env.DEV ? 'http://localhost:5555/api' : '/api',
```

**Fix**: Make port configurable via environment variable on frontend too, or document the dependency.

---

### [MEDIUM-005] Missing Request Timeout Configuration

**File**: `/web/frontend/src/api/client.js:5`
**Severity**: Medium
**Issue**: 10-second timeout may be too short for some yfinance operations but too long for simple operations.

**Current Code**:
```javascript
timeout: 10000,
```

**Fix**: Make timeout configurable per request type.

```javascript
const client = axios.create({
  baseURL: import.meta.env.DEV ? 'http://localhost:5555/api' : '/api',
  timeout: 30000, // Default longer timeout
})

// Override for quick operations
stocksApi.getAll = (params = {}) => {
  return client.get('/stocks', { params, timeout: 10000 })
}
```

---

### [MEDIUM-006] No Database Backup Mechanism

**Files**: All database-related files
**Severity**: Medium
**Issue**: No mechanism exists to backup the SQLite database, risking data loss.

**Fix**: Add a backup endpoint or CLI command.

```python
@cli.command()
def backup():
    """Backup the database."""
    import shutil
    from datetime import datetime

    db_path = "stock_tracker.db"
    backup_path = f"backups/stock_tracker_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    os.makedirs("backups", exist_ok=True)
    shutil.copy2(db_path, backup_path)
    click.echo(f"Backup created: {backup_path}")
```

---

### [MEDIUM-007] Missing Pagination Limits

**File**: `/web/routes/alerts.py:22-23`
**Severity**: Medium
**Issue**: No maximum limit on pagination, allowing requests for millions of records.

**Current Code**:
```python
limit = request.args.get('limit', default=50, type=int)
offset = request.args.get('offset', default=0, type=int)
```

**Fix**: Enforce maximum limits.

```python
MAX_LIMIT = 100
limit = min(request.args.get('limit', default=50, type=int), MAX_LIMIT)
offset = request.args.get('offset', default=0, type=int)
```

---

### [MEDIUM-008] TradingView Widget Security

**File**: `/web/frontend/src/views/StockDetail.vue:467-475`
**Severity**: Medium
**Issue**: Dynamically loading external scripts from TradingView. While TradingView is reputable, dynamically loading scripts introduces potential supply chain risks.

**Current Code**:
```javascript
const script = document.createElement('script')
script.src = 'https://s3.tradingview.com/tv.js'
```

**Fix**: Use Subresource Integrity (SRI) to verify the script.

```javascript
script.integrity = 'sha384-<hash-of-script>'
script.crossOrigin = 'anonymous'
```

---

### [MEDIUM-009] Missing Health Check Authentication Status

**File**: `/web/app.py:73-76`
**Severity**: Medium
**Issue**: Health check doesn't indicate whether authentication is enabled/disabled.

**Current Code**:
```python
@app.route('/health')
def health_check():
    return {"status": "ok", "message": "Stock Tracker API is running"}
```

**Fix**: Add more useful health information.

```python
@app.route('/health')
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "auth_enabled": bool(app.config.get('JWT_SECRET_KEY')),
        "database": "connected" if check_db_connection() else "error"
    }
```

---

## Positive Observations

- **SQL Injection Prevention**: All database queries use parameterized queries with `?` placeholders, preventing SQL injection attacks.

- **Good Separation of Concerns**: The codebase follows a clean architecture with separate layers (routes, services, database manager, fetchers).

- **Proper Context Manager Usage**: Database connections use context managers ensuring proper cleanup.

- **Environment Variable Configuration**: Sensitive configuration uses environment variables with fallbacks.

- **Good Accessibility**: Vue.js components include ARIA labels, roles, and keyboard navigation support.

- **Proper Error Logging**: Server-side errors are logged with full stack traces for debugging.

- **Type Hints**: Python code includes type hints improving code readability and IDE support.

- **Dataclasses for Models**: Clean model definitions using Python dataclasses.

- **Component-Based Frontend**: Vue.js frontend is well-organized with reusable components.

- **Toast Notification System**: User-friendly feedback system for actions.

---

## Recommendations

### Architecture

1. **Add Authentication Layer**: Implement JWT-based authentication before any production deployment.

2. **Implement API Versioning**: Add `/api/v1/` prefix to prepare for future API changes.

3. **Consider PostgreSQL**: For production use with multiple users, consider migrating from SQLite to PostgreSQL.

4. **Add Caching Layer**: Implement Redis caching for frequently accessed data like stock prices.

### Refactoring Opportunities

1. **Split DatabaseManager**: Break into separate repository classes (StockRepository, TargetRepository, etc.).

2. **Create Validation Module**: Centralize input validation logic in a dedicated module.

3. **Extract Price Service**: Move price-related logic from routes to a dedicated service.

4. **Create Error Handler Middleware**: Centralize error handling for consistent responses.

### Testing Strategy

1. **Unit Tests**: Add pytest tests for:
   - Database operations
   - Alert logic
   - Price calculations
   - Input validation

2. **Integration Tests**: Test API endpoints with various inputs.

3. **Security Tests**: Add tests for:
   - SQL injection attempts
   - XSS payloads
   - Invalid input handling

4. **Performance Tests**: Load test the price fetching endpoints.

### Documentation

1. **API Documentation**: Add OpenAPI/Swagger documentation.

2. **Security Documentation**: Document authentication flow once implemented.

3. **Deployment Guide**: Add production deployment instructions.

4. **Environment Variables**: Document all required and optional environment variables.

---

## Statistics

- **Total files reviewed**: 28
- **Lines of code reviewed**: ~6,000
- **Python files**: 16
- **Vue.js files**: 12
- **Critical issues**: 3
- **High priority issues**: 8
- **Medium priority issues**: 9

### Issues by Category

| Category | Critical | High | Medium |
|----------|----------|------|--------|
| Security | 3 | 4 | 2 |
| Code Quality | 0 | 2 | 3 |
| Performance | 0 | 2 | 1 |
| Best Practices | 0 | 0 | 3 |

---

## Conclusion

The Stock Tracker application has a solid foundation with good code organization and proper SQL injection prevention. However, **the application is not ready for production deployment** due to critical security vulnerabilities:

1. **XSS vulnerability** in note content rendering
2. **Complete lack of authentication** on all API endpoints
3. **Overly permissive CORS** configuration

### Recommended Priority Order

1. **Immediate** (Before any deployment):
   - Fix XSS vulnerability with DOMPurify
   - Implement authentication
   - Configure CORS properly

2. **Short-term** (Before production):
   - Add input validation
   - Implement rate limiting
   - Add CSRF protection
   - Fix N+1 query problems

3. **Medium-term** (For maintainability):
   - Refactor DatabaseManager
   - Add comprehensive tests
   - Implement caching
   - Add API documentation

For a personal/local-only application, the security issues may be acceptable risks. For any shared or internet-facing deployment, the critical issues must be addressed first.

---

**Report Generated**: February 8, 2026
**Review Tool**: Claude Code (Opus 4.5)
