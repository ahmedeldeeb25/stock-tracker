# Technology Stack Reference

**Last Updated**: February 7, 2026

---

## 🐍 Backend Stack

### Core Framework
```
Flask 3.0.0          - Web framework
Python 3.9+          - Programming language
```

### Database
```
SQLite 3             - Database engine
SQLAlchemy           - ORM (future consideration)
```

### Data & APIs
```
yfinance             - Stock price data
schedule             - Task scheduling for daemon
smtplib              - Email notifications (built-in)
```

### Python Dependencies
```python
# Core
flask==3.0.0
flask-cors==4.0.0

# Stock data
yfinance==0.2.33

# Scheduling
schedule==1.2.0

# Environment
python-dotenv==1.0.0
```

---

## 🎨 Frontend Stack

### Core Framework
```
Vue 3.4.0            - UI framework (Composition API)
Vite 6.4.1           - Build tool & dev server
```

### State & Routing
```
Pinia 2.1.7          - State management (Vuex successor)
Vue Router 4.2.5     - Client-side routing
```

### HTTP & UI
```
Axios 1.6.5          - HTTP client
Bootstrap 5          - CSS framework (via CDN)
Bootstrap Icons      - Icon library (via CDN)
```

### Rich Text Editor
```
@vueup/vue-quill     - Quill editor for Vue 3
Quill.js             - Rich text editing
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "axios": "^1.6.5",
    "@vueup/vue-quill": "latest"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^6.4.1"
  }
}
```

---

## 🗄️ Database Schema

### Tables

#### `stocks`
```sql
CREATE TABLE stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT UNIQUE NOT NULL,
    company_name TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### `targets`
```sql
CREATE TABLE targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    target_type TEXT NOT NULL,  -- 'Buy', 'Sell', 'DCA', 'Trim'
    target_price REAL NOT NULL,
    trim_percentage INTEGER,    -- For 'Trim' type only
    alert_note TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
)
```

#### `tags`
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    color TEXT,                 -- Hex color code
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

#### `stock_tags` (Junction Table)
```sql
CREATE TABLE stock_tags (
    stock_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (stock_id, tag_id),
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
)
```

#### `notes`
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,      -- HTML formatted content
    note_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
)
```

#### `alert_history`
```sql
CREATE TABLE alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    target_type TEXT NOT NULL,
    current_price REAL NOT NULL,
    target_price REAL NOT NULL,
    alert_note TEXT,
    email_sent BOOLEAN DEFAULT 0,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
)
```

---

## 🔌 API Architecture

### RESTful API Design
```
Base URL (Dev):  http://localhost:5555/api
Base URL (Prod): /api
Format:          JSON
CORS:            Enabled for localhost:5173
```

### Response Format
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### Error Format
```json
{
  "error": "Error message",
  "success": false
}
```

---

## 🎨 Frontend Architecture

### Vue 3 Composition API Pattern
```vue
<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { someApi } from '@/api'

export default {
  name: 'ComponentName',
  props: { ... },
  emits: ['event-name'],
  setup(props, { emit }) {
    const data = ref(null)
    const computed = computed(() => ...)

    const method = async () => { ... }

    onMounted(() => { ... })

    return { data, computed, method }
  }
}
</script>
```

### Pinia Store Pattern
```javascript
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useStoreNameStore = defineStore('storeName', () => {
  // State
  const data = ref([])

  // Getters
  const processedData = computed(() => ...)

  // Actions
  const fetchData = async () => { ... }

  return { data, processedData, fetchData }
})
```

### API Client Pattern
```javascript
// api/client.js
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.DEV
    ? 'http://localhost:5555/api'
    : '/api'
})

export default client

// api/index.js
import client from './client'

export const resourceApi = {
  getAll: () => client.get('/resource'),
  create: (data) => client.post('/resource', data),
  update: (id, data) => client.put(`/resource/${id}`, data),
  delete: (id) => client.delete(`/resource/${id}`)
}
```

---

## 🎭 Bootstrap Modal Pattern

```javascript
// Show modal (Bootstrap loaded via CDN)
const showModal = () => {
  const modal = new window.bootstrap.Modal(
    document.getElementById('modalId')
  )
  modal.show()
}

// Hide modal
const modalInstance = window.bootstrap.Modal.getInstance(
  document.getElementById('modalId')
)
modalInstance.hide()
```

---

## 🎨 CSS Architecture

### Bootstrap 5 Classes
```html
<!-- Layout -->
<div class="container">
  <div class="row">
    <div class="col-md-6">...</div>
  </div>
</div>

<!-- Components -->
<button class="btn btn-primary">Button</button>
<span class="badge bg-success">Badge</span>
<div class="card">...</div>

<!-- Utilities -->
<div class="mt-3 mb-4 p-2">...</div>
<div class="d-flex justify-content-between">...</div>
```

### Custom Styles (Scoped)
```vue
<style scoped>
.custom-class {
  /* Component-specific styles */
}

/* Style child components */
:deep(.child-class) {
  /* Styles that penetrate child components */
}
</style>
```

---

## 🔧 Development Tools

### Commands
```bash
# Backend
python app.py              # Start Flask server
python cli.py [command]    # CLI tool

# Frontend
npm run dev                # Start Vite dev server
npm run build              # Build for production
npm run preview            # Preview production build

# Scripts
./scripts/start_all.sh     # Start everything
./scripts/start_daemon.sh  # Start price monitoring
```

### Environment Variables
```bash
# .env file
SENDER_EMAIL=your@email.com
SENDER_PASSWORD=app-password
RECIPIENT_EMAIL=recipient@email.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

---

## 📦 Build & Deployment

### Frontend Build
```bash
cd web/frontend
npm run build
# Output: dist/ folder
```

### Production Serving
- Static files → Nginx/Apache
- API → Flask with gunicorn/uwsgi
- Database → SQLite (same file)

---

## 🔐 Security Considerations

### Current Implementation
- ✅ CORS configured for specific origins
- ✅ .env for sensitive data
- ✅ .gitignore for secrets
- ⚠️ No authentication (single user)
- ⚠️ No input sanitization (trust internal)

### For Production
- Add authentication (JWT)
- Add input validation
- Add SQL injection protection (use parameterized queries)
- Add rate limiting
- Use HTTPS
- Sanitize HTML in notes

---

## 🧪 Testing Approach

### Manual Testing
- Test API endpoints with curl
- Test UI workflows manually
- Check logs for errors

### Future Testing
- Backend: pytest
- Frontend: Vitest + Vue Test Utils
- E2E: Playwright/Cypress

---

## 📊 Performance Considerations

### Current State
- SQLite: Good for single user (<1000 stocks)
- yfinance: Rate limited (be respectful)
- No caching: Every request fetches fresh data

### Optimization Opportunities
- Add Redis for caching prices
- Use PostgreSQL for multi-user
- Implement pagination for large datasets
- Add service worker for offline support

---

## 🎓 Key Patterns to Follow

### ✅ DO
- Use Composition API in Vue 3
- Use Pinia for state (not Vuex)
- Access Bootstrap via `window.bootstrap`
- Store HTML content in notes (not plain text)
- Use parameterized SQL queries
- Follow RESTful conventions

### ❌ DON'T
- Import Bootstrap as npm package (it's CDN)
- Use Options API for new components
- Store sensitive data in code
- Make breaking changes without documenting
- Skip error handling

---

**Note**: Update this file when adding new technologies or changing patterns.
