# Stock Tracker - Product Roadmap
**Version:** 1.0
**Date:** February 2026
**Author:** Product Design (Fintech Specialist)

---

## Executive Summary

Stock Tracker has established a solid foundation as a personal portfolio tracking application with Phase 1 (accessibility, mobile responsiveness) and Phase 2 (UX patterns, skeleton loaders, custom modals) successfully implemented. However, to compete with industry leaders like **Robinhood**, **TradingView**, **Bloomberg Terminal**, and **Interactive Brokers**, the application requires strategic enhancements in three critical areas:

1. **Real-Time Data Infrastructure**: Transition from hourly polling to WebSocket-based live pricing
2. **Portfolio Intelligence**: Add comprehensive P&L tracking, allocation analysis, and risk metrics
3. **Trading Research Tools**: Implement technical indicators, charting capabilities, and market sentiment analysis

This roadmap outlines a **26-week implementation plan** across three phases, prioritizing features that deliver the highest impact on "time-to-insight" and "decision confidence" for traders and investors.

---

## Current State Assessment

### ✅ Strengths
- **Solid Technical Foundation**: Vue 3 Composition API, Pinia state management, Bootstrap 5
- **WCAG 2.1 AA Compliance**: Semantic HTML, ARIA labels, keyboard navigation
- **Responsive Design**: Mobile-first layout with proper breakpoints
- **Core Features**: Price targets, analysis notes, tags, alert system
- **Professional UX Patterns**: Custom confirm modals, toast notifications, skeleton loaders

### ⚠️ Critical Gaps
1. **No Real-Time Data**: Prices update hourly via yfinance polling (vs. WebSocket streaming)
2. **Limited Portfolio Analytics**: No P&L tracking, allocation breakdown, or performance metrics
3. **Missing Technical Analysis**: No indicators (RSI, MACD, Bollinger Bands), single timeframe only
4. **No Risk Management**: No position sizing tools, stop-loss calculators, or volatility metrics
5. **Single Data Source**: Dependent on yfinance; no redundancy or data quality checks
6. **No News Integration**: Missing market sentiment, earnings calendars, SEC filings
7. **Basic Alerting**: Price-based only; no technical/volume/news-based triggers

---

## Phase 3: Real-Time Foundation (8 Weeks)

### 🎯 Objectives
- Establish WebSocket infrastructure for live price streaming
- Build comprehensive portfolio analytics dashboard
- Implement intelligent alert system with multiple trigger types

### Feature Breakdown

#### 3.1 Real-Time Price Streaming (3 weeks)
**Priority:** 🔴 Critical
**Complexity:** High

**Implementation:**
```javascript
// WebSocket client integration
// File: web/frontend/src/services/websocket.js

import { reactive } from 'vue'

class StockWebSocket {
  constructor() {
    this.socket = null
    this.subscriptions = new Map()
    this.prices = reactive({})
  }

  connect() {
    this.socket = new WebSocket('ws://localhost:5001/ws/prices')

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      // Flash animation trigger
      this.prices[data.symbol] = {
        ...data,
        flash: data.change >= 0 ? 'up' : 'down',
        timestamp: Date.now()
      }

      setTimeout(() => {
        if (this.prices[data.symbol]) {
          this.prices[data.symbol].flash = null
        }
      }, 800)
    }

    this.socket.onerror = () => {
      // Graceful degradation to polling
      this.fallbackToPolling()
    }
  }

  subscribe(symbols) {
    this.socket.send(JSON.stringify({
      action: 'subscribe',
      symbols: symbols
    }))
  }

  fallbackToPolling() {
    console.warn('WebSocket failed, falling back to polling')
    // Implement 30-second polling as backup
  }
}

export const stockWS = new StockWebSocket()
```

**Backend Architecture:**
```python
# File: src/services/websocket_server.py

from flask_socketio import SocketIO, emit
from threading import Thread
import yfinance as yf
import time

socketio = SocketIO(app, cors_allowed_origins="*")

class PriceStreamer:
    def __init__(self):
        self.active_symbols = set()
        self.running = False

    def start(self):
        self.running = True
        thread = Thread(target=self._stream_loop)
        thread.daemon = True
        thread.start()

    def _stream_loop(self):
        while self.running:
            if not self.active_symbols:
                time.sleep(1)
                continue

            # Fetch batch prices
            tickers = yf.Tickers(' '.join(self.active_symbols))

            for symbol in self.active_symbols:
                try:
                    ticker = tickers.tickers[symbol]
                    info = ticker.info

                    socketio.emit('price_update', {
                        'symbol': symbol,
                        'price': info.get('currentPrice'),
                        'change': info.get('regularMarketChangePercent'),
                        'volume': info.get('volume'),
                        'timestamp': time.time()
                    }, broadcast=True)
                except Exception as e:
                    print(f"Error fetching {symbol}: {e}")

            time.sleep(5)  # 5-second refresh rate

streamer = PriceStreamer()

@socketio.on('subscribe')
def handle_subscribe(data):
    streamer.active_symbols.update(data['symbols'])
    if not streamer.running:
        streamer.start()

@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    streamer.active_symbols.difference_update(data['symbols'])
```

**UI Components:**
```vue
<!-- File: web/frontend/src/components/LivePriceTicker.vue -->
<template>
  <div class="live-price" :class="`flash-${flash}`">
    <span class="price-value" style="font-family: 'Roboto Mono', monospace;">
      ${{ formattedPrice }}
    </span>
    <span class="price-change" :class="changeClass">
      <i class="bi" :class="changeIcon" aria-hidden="true"></i>
      {{ formattedChange }}%
    </span>
    <span class="live-indicator" v-if="isLive">
      <span class="pulse-dot"></span> LIVE
    </span>
  </div>
</template>

<script setup>
import { computed, watch, ref } from 'vue'
import { stockWS } from '@/services/websocket'

const props = defineProps(['symbol'])
const flash = ref(null)

const priceData = computed(() => stockWS.prices[props.symbol])

watch(() => priceData.value?.flash, (newFlash) => {
  flash.value = newFlash
  if (newFlash) {
    setTimeout(() => { flash.value = null }, 800)
  }
})

const formattedPrice = computed(() => {
  return priceData.value?.price?.toFixed(2) || '0.00'
})

const changeClass = computed(() => {
  return priceData.value?.change >= 0 ? 'text-success' : 'text-danger'
})
</script>

<style scoped>
.live-price {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  transition: background-color 0.8s ease;
}

.flash-up {
  background-color: rgba(5, 150, 105, 0.15);
}

.flash-down {
  background-color: rgba(220, 38, 38, 0.15);
}

.price-value {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.02em;
}

.pulse-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  background-color: var(--color-success);
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}
</style>
```

**Database Schema Updates:**
```sql
-- File: migrations/003_websocket_tracking.sql

CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    price REAL NOT NULL,
    volume INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    source TEXT DEFAULT 'websocket',
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);

CREATE INDEX idx_price_history_stock ON price_history(stock_id, timestamp DESC);
CREATE INDEX idx_price_history_timestamp ON price_history(timestamp);

-- Store intraday data for 7 days, aggregate to daily after that
```

#### 3.2 Portfolio Analytics Dashboard (3 weeks)
**Priority:** 🟠 High
**Complexity:** Medium

**Features:**
- **Total Portfolio Value**: Real-time aggregation with 24h change
- **Unrealized P&L**: Gains/losses vs. purchase price (when available)
- **Allocation Breakdown**: Pie chart by sector, asset type, or custom tags
- **Top Performers**: Best/worst stocks by percentage change
- **Diversification Score**: Basic Herfindahl index calculation

**UI Design:**
```vue
<!-- File: web/frontend/src/views/PortfolioAnalytics.vue -->
<template>
  <div class="portfolio-dashboard">
    <h1 class="h2">Portfolio Analytics</h1>

    <!-- Summary Cards -->
    <div class="row g-3 mb-4">
      <div class="col-6 col-md-3">
        <div class="stat-card">
          <div class="stat-label">Total Value</div>
          <div class="stat-value" style="font-family: 'Roboto Mono', monospace;">
            ${{ totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 }) }}
          </div>
          <div class="stat-change" :class="totalChangeClass">
            {{ totalChange >= 0 ? '+' : '' }}${{ Math.abs(totalChange).toFixed(2) }}
            ({{ totalChangePercent.toFixed(2) }}%)
          </div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="stat-card">
          <div class="stat-label">Unrealized P&L</div>
          <div class="stat-value" :class="plClass">
            {{ unrealizedPL >= 0 ? '+' : '' }}${{ unrealizedPL.toLocaleString() }}
          </div>
          <div class="stat-sublabel">
            {{ (unrealizedPL / totalCost * 100).toFixed(2) }}% return
          </div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="stat-card">
          <div class="stat-label">Day's Change</div>
          <div class="stat-value" :class="dayChangeClass">
            {{ dayChange >= 0 ? '+' : '' }}${{ Math.abs(dayChange).toFixed(2) }}
          </div>
        </div>
      </div>

      <div class="col-6 col-md-3">
        <div class="stat-card">
          <div class="stat-label">Diversity Score</div>
          <div class="stat-value">{{ diversityScore }}/100</div>
          <div class="diversity-bar">
            <div class="diversity-fill" :style="{ width: diversityScore + '%' }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Allocation Chart -->
    <div class="row g-3">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="h5">Allocation by Tag</h3>
          </div>
          <div class="card-body">
            <canvas ref="allocationChart"></canvas>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="h5">Top Performers (24h)</h3>
          </div>
          <div class="card-body">
            <div class="performer-list">
              <div v-for="stock in topPerformers" :key="stock.id" class="performer-item">
                <span class="performer-symbol">{{ stock.symbol }}</span>
                <span class="performer-change" :class="stock.change >= 0 ? 'text-success' : 'text-danger'">
                  {{ stock.change >= 0 ? '+' : '' }}{{ stock.change.toFixed(2) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Chart from 'chart.js/auto'
import { stocksApi } from '@/api'

const stocks = ref([])
const allocationChart = ref(null)

const totalValue = computed(() => {
  return stocks.value.reduce((sum, s) => sum + (s.currentPrice * s.shares || s.currentPrice), 0)
})

const unrealizedPL = computed(() => {
  return stocks.value.reduce((sum, s) => {
    if (!s.purchasePrice || !s.shares) return sum
    return sum + ((s.currentPrice - s.purchasePrice) * s.shares)
  }, 0)
})

const diversityScore = computed(() => {
  if (stocks.value.length === 0) return 0

  // Herfindahl index (1 - H) * 100
  const total = totalValue.value
  const sumOfSquares = stocks.value.reduce((sum, s) => {
    const weight = (s.currentPrice * (s.shares || 1)) / total
    return sum + (weight * weight)
  }, 0)

  return Math.round((1 - sumOfSquares) * 100)
})

onMounted(async () => {
  const response = await stocksApi.getAll()
  stocks.value = response.data.stocks

  // Render allocation chart
  const ctx = allocationChart.value.getContext('2d')
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: getTagLabels(),
      datasets: [{
        data: getTagValues(),
        backgroundColor: getTagColors()
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom' }
      }
    }
  })
})
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 8px;
  padding: var(--space-3);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.stat-label {
  font-size: var(--font-size-small);
  color: var(--color-text-muted);
  margin-bottom: var(--space-1);
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.2;
}

.diversity-bar {
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
  margin-top: var(--space-1);
}

.diversity-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--color-danger), var(--color-warning), var(--color-success));
  transition: width 0.5s ease;
}
</style>
```

**Backend API Endpoints:**
```python
# File: src/routes/analytics.py

from flask import Blueprint, jsonify
from src.database import get_db
from src.services.yahoo_finance import fetch_current_prices

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/analytics/portfolio', methods=['GET'])
def get_portfolio_analytics():
    """Calculate comprehensive portfolio metrics"""
    db = get_db()
    stocks = db.execute('''
        SELECT s.*,
               GROUP_CONCAT(t.name) as tags,
               ps.shares, ps.purchase_price, ps.purchase_date
        FROM stocks s
        LEFT JOIN stock_tags st ON s.id = st.stock_id
        LEFT JOIN tags t ON st.tag_id = t.id
        LEFT JOIN positions ps ON s.id = ps.stock_id
        GROUP BY s.id
    ''').fetchall()

    # Fetch current prices
    symbols = [s['symbol'] for s in stocks]
    prices = fetch_current_prices(symbols)

    total_value = 0
    total_cost = 0
    day_change = 0

    enriched_stocks = []
    for stock in stocks:
        current_price = prices.get(stock['symbol'], {}).get('price', 0)
        shares = stock['shares'] or 1

        position_value = current_price * shares
        total_value += position_value

        if stock['purchase_price']:
            cost_basis = stock['purchase_price'] * shares
            total_cost += cost_basis

        day_change += prices.get(stock['symbol'], {}).get('change', 0) * shares

        enriched_stocks.append({
            **dict(stock),
            'current_price': current_price,
            'position_value': position_value
        })

    unrealized_pl = total_value - total_cost if total_cost > 0 else 0

    return jsonify({
        'total_value': total_value,
        'total_cost': total_cost,
        'unrealized_pl': unrealized_pl,
        'day_change': day_change,
        'day_change_percent': (day_change / total_value * 100) if total_value > 0 else 0,
        'stocks': enriched_stocks,
        'diversity_score': calculate_diversity_score(enriched_stocks, total_value)
    })

def calculate_diversity_score(stocks, total_value):
    """Calculate Herfindahl index"""
    if total_value == 0:
        return 0

    sum_of_squares = sum((s['position_value'] / total_value) ** 2 for s in stocks)
    return round((1 - sum_of_squares) * 100)
```

**Database Schema:**
```sql
-- File: migrations/004_portfolio_tracking.sql

CREATE TABLE IF NOT EXISTS positions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    shares REAL NOT NULL,
    purchase_price REAL,
    purchase_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE
);

CREATE INDEX idx_positions_stock ON positions(stock_id);
```

#### 3.3 Smart Alert System (2 weeks)
**Priority:** 🟡 Medium
**Complexity:** Medium

**Enhanced Alert Types:**
1. **Price Threshold**: Existing functionality (when price crosses X)
2. **Percentage Move**: Alert when stock moves ±Y% in timeframe
3. **Volume Spike**: Alert when volume > N× average
4. **Technical Indicator**: Alert when RSI > 70 or < 30
5. **Time-Based**: Recurring alerts (daily open/close summary)

**Implementation:**
```python
# File: src/services/alert_engine.py

from datetime import datetime, timedelta
from src.database import get_db
from src.services.notifications import send_email_alert

class AlertEngine:
    def __init__(self):
        self.active_alerts = []

    def check_alerts(self, symbol, current_data):
        """Check all alert conditions for a symbol"""
        db = get_db()
        alerts = db.execute('''
            SELECT * FROM alerts
            WHERE stock_id IN (SELECT id FROM stocks WHERE symbol = ?)
            AND is_active = 1
        ''', (symbol,)).fetchall()

        for alert in alerts:
            if self._should_trigger(alert, current_data):
                self._trigger_alert(alert, current_data)

    def _should_trigger(self, alert, data):
        alert_type = alert['alert_type']

        if alert_type == 'price_above':
            return data['price'] >= alert['threshold']

        elif alert_type == 'price_below':
            return data['price'] <= alert['threshold']

        elif alert_type == 'percent_change':
            # Check if price moved ±threshold% in last N minutes
            historical = self._get_historical_price(alert['stock_id'], minutes=alert['timeframe'])
            if historical:
                change_pct = ((data['price'] - historical) / historical) * 100
                return abs(change_pct) >= alert['threshold']

        elif alert_type == 'volume_spike':
            avg_volume = self._get_average_volume(alert['stock_id'], days=20)
            return data['volume'] >= (avg_volume * alert['threshold'])

        elif alert_type == 'rsi':
            rsi = self._calculate_rsi(alert['stock_id'], period=14)
            if alert['condition'] == 'overbought':
                return rsi >= alert['threshold']
            elif alert['condition'] == 'oversold':
                return rsi <= alert['threshold']

        return False

    def _trigger_alert(self, alert, data):
        """Send notification and update alert status"""
        db = get_db()

        # Log the trigger
        db.execute('''
            INSERT INTO alert_history (alert_id, triggered_at, price, message)
            VALUES (?, ?, ?, ?)
        ''', (alert['id'], datetime.now(), data['price'], self._format_message(alert, data)))

        # Send notification
        if alert['notification_method'] == 'email':
            send_email_alert(alert, data)

        # Disable one-time alerts
        if not alert['is_recurring']:
            db.execute('UPDATE alerts SET is_active = 0 WHERE id = ?', (alert['id'],))

        db.commit()

engine = AlertEngine()
```

**Database Schema:**
```sql
-- File: migrations/005_enhanced_alerts.sql

ALTER TABLE alerts ADD COLUMN alert_type TEXT DEFAULT 'price_above';
ALTER TABLE alerts ADD COLUMN condition TEXT; -- 'overbought', 'oversold', etc.
ALTER TABLE alerts ADD COLUMN timeframe INTEGER; -- minutes for percent_change alerts
ALTER TABLE alerts ADD COLUMN is_recurring BOOLEAN DEFAULT 0;
ALTER TABLE alerts ADD COLUMN notification_method TEXT DEFAULT 'email';

CREATE TABLE IF NOT EXISTS alert_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_id INTEGER NOT NULL,
    triggered_at DATETIME NOT NULL,
    price REAL,
    message TEXT,
    FOREIGN KEY (alert_id) REFERENCES alerts(id) ON DELETE CASCADE
);

CREATE INDEX idx_alert_history_alert ON alert_history(alert_id);
CREATE INDEX idx_alert_history_time ON alert_history(triggered_at DESC);
```

---

## Phase 4: Advanced Analytics (8 Weeks)

### 🎯 Objectives
- Implement comprehensive technical analysis indicators
- Add risk management and position sizing tools
- Enable multi-stock comparison and correlation analysis

### Feature Breakdown

#### 4.1 Technical Indicators (4 weeks)
**Priority:** 🟠 High
**Complexity:** High

**Indicators to Implement:**
1. **Trend Indicators**: SMA, EMA (20/50/200 day), MACD, ADX
2. **Momentum Indicators**: RSI, Stochastic Oscillator, Williams %R
3. **Volatility Indicators**: Bollinger Bands, ATR, Standard Deviation
4. **Volume Indicators**: OBV (On-Balance Volume), Volume SMA

**Implementation Example (RSI):**
```python
# File: src/services/technical_indicators.py

import numpy as np
from src.database import get_db

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(symbol, period=14):
        """Calculate Relative Strength Index"""
        db = get_db()
        prices = db.execute('''
            SELECT price FROM price_history
            WHERE stock_id = (SELECT id FROM stocks WHERE symbol = ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, period + 1)).fetchall()

        if len(prices) < period + 1:
            return None

        prices = [p['price'] for p in reversed(prices)]
        deltas = np.diff(prices)

        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return round(rsi, 2)

    @staticmethod
    def calculate_bollinger_bands(symbol, period=20, std_dev=2):
        """Calculate Bollinger Bands"""
        db = get_db()
        prices = db.execute('''
            SELECT price FROM price_history
            WHERE stock_id = (SELECT id FROM stocks WHERE symbol = ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, period)).fetchall()

        if len(prices) < period:
            return None

        prices = [p['price'] for p in prices]
        sma = np.mean(prices)
        std = np.std(prices)

        return {
            'middle': round(sma, 2),
            'upper': round(sma + (std_dev * std), 2),
            'lower': round(sma - (std_dev * std), 2)
        }

    @staticmethod
    def calculate_macd(symbol, fast=12, slow=26, signal=9):
        """Calculate MACD (Moving Average Convergence Divergence)"""
        db = get_db()
        prices = db.execute('''
            SELECT price FROM price_history
            WHERE stock_id = (SELECT id FROM stocks WHERE symbol = ?)
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (symbol, slow + signal)).fetchall()

        if len(prices) < slow + signal:
            return None

        prices = np.array([p['price'] for p in reversed(prices)])

        # Calculate EMAs
        ema_fast = TechnicalIndicators._calculate_ema(prices, fast)
        ema_slow = TechnicalIndicators._calculate_ema(prices, slow)

        macd_line = ema_fast - ema_slow
        signal_line = TechnicalIndicators._calculate_ema(macd_line, signal)
        histogram = macd_line - signal_line

        return {
            'macd': round(macd_line[-1], 4),
            'signal': round(signal_line[-1], 4),
            'histogram': round(histogram[-1], 4)
        }

    @staticmethod
    def _calculate_ema(prices, period):
        """Calculate Exponential Moving Average"""
        multiplier = 2 / (period + 1)
        ema = np.zeros(len(prices))
        ema[0] = prices[0]

        for i in range(1, len(prices)):
            ema[i] = (prices[i] * multiplier) + (ema[i-1] * (1 - multiplier))

        return ema

indicators = TechnicalIndicators()
```

**API Endpoint:**
```python
# File: src/routes/indicators.py

from flask import Blueprint, jsonify, request
from src.services.technical_indicators import indicators

indicators_bp = Blueprint('indicators', __name__)

@indicators_bp.route('/api/stocks/<symbol>/indicators', methods=['GET'])
def get_indicators(symbol):
    """Get all technical indicators for a stock"""
    indicator_type = request.args.get('type', 'all')

    result = {}

    if indicator_type in ['all', 'momentum']:
        result['rsi'] = indicators.calculate_rsi(symbol, period=14)

    if indicator_type in ['all', 'volatility']:
        result['bollinger_bands'] = indicators.calculate_bollinger_bands(symbol)
        result['atr'] = indicators.calculate_atr(symbol, period=14)

    if indicator_type in ['all', 'trend']:
        result['macd'] = indicators.calculate_macd(symbol)
        result['sma_20'] = indicators.calculate_sma(symbol, period=20)
        result['sma_50'] = indicators.calculate_sma(symbol, period=50)
        result['sma_200'] = indicators.calculate_sma(symbol, period=200)

    return jsonify(result)
```

**UI Component:**
```vue
<!-- File: web/frontend/src/components/TechnicalIndicatorsPanel.vue -->
<template>
  <div class="indicators-panel">
    <h3 class="h5 mb-3">Technical Indicators</h3>

    <div class="indicator-grid">
      <!-- RSI Card -->
      <div class="indicator-card">
        <div class="indicator-label">RSI (14)</div>
        <div class="indicator-value" :class="rsiClass">
          {{ indicators.rsi || '--' }}
        </div>
        <div class="indicator-bar">
          <div class="rsi-zones">
            <span class="zone oversold">0</span>
            <span class="zone neutral">50</span>
            <span class="zone overbought">100</span>
          </div>
          <div class="rsi-marker" :style="{ left: indicators.rsi + '%' }"></div>
        </div>
        <div class="indicator-signal">
          {{ rsiSignal }}
        </div>
      </div>

      <!-- Bollinger Bands Card -->
      <div class="indicator-card">
        <div class="indicator-label">Bollinger Bands</div>
        <div class="bb-values">
          <div class="bb-line">
            <span class="bb-label">Upper:</span>
            <span class="bb-price">${{ indicators.bollinger_bands?.upper || '--' }}</span>
          </div>
          <div class="bb-line middle">
            <span class="bb-label">Middle:</span>
            <span class="bb-price">${{ indicators.bollinger_bands?.middle || '--' }}</span>
          </div>
          <div class="bb-line">
            <span class="bb-label">Lower:</span>
            <span class="bb-price">${{ indicators.bollinger_bands?.lower || '--' }}</span>
          </div>
        </div>
        <div class="indicator-signal">
          {{ bollingerSignal }}
        </div>
      </div>

      <!-- MACD Card -->
      <div class="indicator-card">
        <div class="indicator-label">MACD (12, 26, 9)</div>
        <div class="macd-values">
          <div class="macd-line">
            <span>MACD:</span>
            <span class="macd-value">{{ indicators.macd?.macd || '--' }}</span>
          </div>
          <div class="macd-line">
            <span>Signal:</span>
            <span class="macd-value">{{ indicators.macd?.signal || '--' }}</span>
          </div>
          <div class="macd-line histogram">
            <span>Histogram:</span>
            <span class="macd-value" :class="macdHistogramClass">
              {{ indicators.macd?.histogram || '--' }}
            </span>
          </div>
        </div>
        <div class="indicator-signal">
          {{ macdSignal }}
        </div>
      </div>

      <!-- Moving Averages Card -->
      <div class="indicator-card">
        <div class="indicator-label">Moving Averages</div>
        <div class="ma-values">
          <div class="ma-line">
            <span class="ma-label">SMA 20:</span>
            <span class="ma-price">${{ indicators.sma_20 || '--' }}</span>
          </div>
          <div class="ma-line">
            <span class="ma-label">SMA 50:</span>
            <span class="ma-price">${{ indicators.sma_50 || '--' }}</span>
          </div>
          <div class="ma-line">
            <span class="ma-label">SMA 200:</span>
            <span class="ma-price">${{ indicators.sma_200 || '--' }}</span>
          </div>
        </div>
        <div class="indicator-signal">
          {{ maSignal }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { stocksApi } from '@/api'

const props = defineProps(['symbol'])
const indicators = ref({})

const rsiClass = computed(() => {
  const rsi = indicators.value.rsi
  if (!rsi) return ''
  if (rsi >= 70) return 'text-danger'
  if (rsi <= 30) return 'text-success'
  return 'text-muted'
})

const rsiSignal = computed(() => {
  const rsi = indicators.value.rsi
  if (!rsi) return 'Loading...'
  if (rsi >= 70) return '⚠️ Overbought - Consider selling'
  if (rsi <= 30) return '✅ Oversold - Potential buying opportunity'
  return 'Neutral'
})

const bollingerSignal = computed(() => {
  const bb = indicators.value.bollinger_bands
  const price = indicators.value.current_price
  if (!bb || !price) return 'Loading...'

  if (price >= bb.upper) return '⚠️ Price at upper band - potential reversal'
  if (price <= bb.lower) return '✅ Price at lower band - potential bounce'
  return 'Price within bands'
})

const macdSignal = computed(() => {
  const macd = indicators.value.macd
  if (!macd) return 'Loading...'

  if (macd.histogram > 0 && macd.macd > macd.signal) return '📈 Bullish momentum'
  if (macd.histogram < 0 && macd.macd < macd.signal) return '📉 Bearish momentum'
  return 'Neutral momentum'
})

onMounted(async () => {
  const response = await stocksApi.getIndicators(props.symbol)
  indicators.value = response.data
})
</script>

<style scoped>
.indicator-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--space-3);
}

.indicator-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-3);
}

.indicator-label {
  font-size: var(--font-size-small);
  color: var(--color-text-muted);
  margin-bottom: var(--space-2);
  font-weight: 600;
}

.indicator-value {
  font-size: 2rem;
  font-weight: 700;
  font-family: 'Roboto Mono', monospace;
  margin-bottom: var(--space-2);
}

.rsi-zones {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.rsi-marker {
  position: absolute;
  top: 0;
  width: 3px;
  height: 100%;
  background: var(--color-primary);
  transform: translateX(-50%);
}

.indicator-signal {
  margin-top: var(--space-2);
  padding: var(--space-1) var(--space-2);
  background: var(--color-background);
  border-radius: 4px;
  font-size: var(--font-size-small);
}
</style>
```

#### 4.2 Risk Management Tools (2 weeks)
**Priority:** 🟠 High
**Complexity:** Medium

**Features:**
1. **Position Sizing Calculator**: Based on portfolio %, max loss tolerance
2. **Stop-Loss Calculator**: Based on ATR, support levels, percentage
3. **Risk/Reward Ratio**: Visualize potential outcomes
4. **Portfolio Heat Map**: Show concentration risk by position size
5. **Volatility Metrics**: Beta, Standard Deviation, Sharpe Ratio

#### 4.3 Stock Comparison Tool (2 weeks)
**Priority:** 🟡 Medium
**Complexity:** Medium

**Features:**
- Side-by-side comparison of up to 4 stocks
- Overlay price charts with normalized scales
- Compare P/E ratios, market caps, volumes
- Correlation matrix visualization

---

## Phase 5: Market Intelligence & Optimization (10 Weeks)

### 🎯 Objectives
- Integrate news and sentiment analysis
- Add comprehensive export and reporting
- Implement advanced mobile features
- Optimize performance for scale

### Feature Breakdown

#### 5.1 News & Sentiment Integration (4 weeks)
**Priority:** 🟡 Medium
**Complexity:** High

**Data Sources:**
1. **News Aggregation**: NewsAPI, Yahoo Finance RSS, Alpha Vantage
2. **Earnings Calendar**: Quarterly reports, analyst estimates
3. **SEC Filings**: 10-K, 10-Q, 8-K alerts
4. **Social Sentiment**: Twitter/X mentions (optional, rate-limited)

**Implementation:**
```python
# File: src/services/news_aggregator.py

import requests
from datetime import datetime, timedelta
from src.config import NEWS_API_KEY

class NewsAggregator:
    def __init__(self):
        self.base_url = 'https://newsapi.org/v2'

    def get_stock_news(self, symbol, days=7):
        """Fetch recent news for a stock"""
        company_name = self._get_company_name(symbol)

        params = {
            'q': f'{symbol} OR {company_name}',
            'from': (datetime.now() - timedelta(days=days)).isoformat(),
            'sortBy': 'relevancy',
            'language': 'en',
            'apiKey': NEWS_API_KEY
        }

        response = requests.get(f'{self.base_url}/everything', params=params)
        articles = response.json().get('articles', [])

        # Simple sentiment scoring
        for article in articles:
            article['sentiment'] = self._analyze_sentiment(article['title'] + ' ' + article['description'])

        return articles

    def _analyze_sentiment(self, text):
        """Basic sentiment analysis (consider using TextBlob or VADER)"""
        positive_words = ['surge', 'gain', 'profit', 'growth', 'beat', 'soar', 'rise']
        negative_words = ['plunge', 'loss', 'decline', 'fall', 'miss', 'concern', 'risk']

        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)

        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        return 'neutral'

news_aggregator = NewsAggregator()
```

#### 5.2 Export & Reporting (3 weeks)
**Priority:** 🟡 Medium
**Complexity:** Medium

**Export Formats:**
1. **CSV**: Portfolio holdings, transaction history
2. **PDF Reports**: Monthly performance summaries with charts
3. **Tax Reports**: Capital gains/losses by tax lot
4. **API Export**: JSON endpoint for programmatic access

#### 5.3 Performance Optimization (3 weeks)
**Priority:** 🟠 High
**Complexity:** Medium

**Optimizations:**
1. **Database Migration**: SQLite → PostgreSQL for production scale
2. **Caching Layer**: Redis for price data, computed metrics
3. **API Rate Limiting**: Respect yfinance limits, implement backoff
4. **Lazy Loading**: Virtual scrolling for large watchlists
5. **Service Worker**: Offline support, background sync

---

## UX Improvements & Code Examples

### 1. Real-Time Price Display with Flash Animation

**Design Specification:**
- Use monospace font (Roboto Mono) for all price data to prevent layout shift
- Implement subtle green/red background flash when price updates (800ms fade)
- Show "LIVE" indicator with pulsing green dot
- Ensure 4.5:1 contrast ratio on flash background colors

**Current Price Display (Before):**
```vue
<div class="price">
  ${{ stock.currentPrice }}
</div>
```

**Enhanced Price Display (After):**
```vue
<div class="live-price-ticker" :class="`flash-${priceFlash}`">
  <div class="price-main">
    <span class="price-value" style="font-family: 'Roboto Mono', monospace;">
      ${{ formatPrice(currentPrice) }}
    </span>
    <span class="price-change" :class="changeClass">
      <i class="bi" :class="changeIcon" aria-hidden="true"></i>
      {{ formatChange(priceChange) }}%
    </span>
  </div>
  <span class="live-badge" v-if="isLive">
    <span class="pulse-dot"></span> LIVE
  </span>
</div>
```

**CSS:**
```css
.live-price-ticker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2);
  border-radius: 8px;
  transition: background-color 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}

.flash-up {
  background-color: rgba(5, 150, 105, 0.12); /* WCAG compliant */
  box-shadow: 0 0 0 1px rgba(5, 150, 105, 0.2);
}

.flash-down {
  background-color: rgba(220, 38, 38, 0.12);
  box-shadow: 0 0 0 1px rgba(220, 38, 38, 0.2);
}

.price-value {
  font-size: 1.75rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  /* Monospace prevents layout shift during updates */
  font-variant-numeric: tabular-nums;
}

.live-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-success);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  background-color: var(--color-success);
  border-radius: 50%;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.95);
  }
}
```

### 2. Target Progress Visualization

**Design Specification:**
- Use circular progress rings to show proximity to price targets
- Color-code: Green (target met), Blue (in progress), Gray (far from target)
- Display percentage to target with 2 decimal precision
- Animate progress changes smoothly over 600ms

**Implementation:**
```vue
<!-- File: web/frontend/src/components/TargetProgressRing.vue -->
<template>
  <div class="target-progress-ring">
    <svg :width="size" :height="size" viewBox="0 0 120 120">
      <!-- Background circle -->
      <circle
        cx="60"
        cy="60"
        :r="radius"
        fill="none"
        stroke="#E5E7EB"
        :stroke-width="strokeWidth"
      />
      <!-- Progress circle -->
      <circle
        cx="60"
        cy="60"
        :r="radius"
        fill="none"
        :stroke="progressColor"
        :stroke-width="strokeWidth"
        :stroke-dasharray="circumference"
        :stroke-dashoffset="dashOffset"
        stroke-linecap="round"
        transform="rotate(-90 60 60)"
        class="progress-circle"
      />
    </svg>
    <div class="ring-content">
      <div class="ring-percentage">{{ progressPercent }}%</div>
      <div class="ring-label">{{ label }}</div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  currentPrice: { type: Number, required: true },
  targetPrice: { type: Number, required: true },
  direction: { type: String, default: 'sell' }, // 'sell' or 'buy'
  size: { type: Number, default: 120 },
  strokeWidth: { type: Number, default: 8 }
})

const radius = computed(() => 60 - props.strokeWidth / 2)
const circumference = computed(() => 2 * Math.PI * radius.value)

const progressPercent = computed(() => {
  let progress
  if (props.direction === 'sell') {
    // For sell targets, progress = (current - initial) / (target - initial)
    // Simplified: assume we're measuring from current to target
    progress = (props.currentPrice / props.targetPrice) * 100
  } else {
    // For buy targets (below current price)
    progress = ((props.targetPrice - props.currentPrice) / props.targetPrice) * 100
  }
  return Math.min(Math.max(progress, 0), 100).toFixed(1)
})

const dashOffset = computed(() => {
  const progress = parseFloat(progressPercent.value)
  return circumference.value * (1 - progress / 100)
})

const progressColor = computed(() => {
  const progress = parseFloat(progressPercent.value)
  if (progress >= 100) return '#059669' // Success green
  if (progress >= 75) return '#2563EB' // Primary blue
  if (progress >= 50) return '#8B5CF6' // Purple
  return '#6B7280' // Gray
})

const label = computed(() => {
  return `$${props.targetPrice.toFixed(2)}`
})
</script>

<style scoped>
.target-progress-ring {
  position: relative;
  display: inline-block;
}

.progress-circle {
  transition: stroke-dashoffset 0.6s cubic-bezier(0.4, 0, 0.2, 1),
              stroke 0.3s ease;
}

.ring-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.ring-percentage {
  font-size: 1.25rem;
  font-weight: 700;
  font-family: 'Roboto Mono', monospace;
  line-height: 1;
}

.ring-label {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  margin-top: 4px;
}
</style>
```

### 3. Market Status Bar

**Design Specification:**
- Top-of-page status bar showing market open/closed state
- Display: "Market Open" (green) | "Pre-Market" (blue) | "After Hours" (orange) | "Market Closed" (red)
- Show next market event: "Opens in 2h 34m" or "Closes in 5h 12m"
- Auto-hide after 10 seconds unless hovered

**Implementation:**
```vue
<!-- File: web/frontend/src/components/MarketStatusBar.vue -->
<template>
  <Transition name="slide-down">
    <div v-if="isVisible" class="market-status-bar" :class="`status-${marketStatus}`" @mouseenter="pauseAutoHide" @mouseleave="resumeAutoHide">
      <div class="container-fluid d-flex align-items-center justify-content-between">
        <div class="status-content">
          <span class="status-indicator"></span>
          <span class="status-text">{{ statusText }}</span>
          <span class="status-time">{{ timeUntilNext }}</span>
        </div>
        <button class="btn-close btn-close-white" @click="isVisible = false" aria-label="Close market status"></button>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const isVisible = ref(true)
const currentTime = ref(new Date())
let intervalId = null
let hideTimeoutId = null

const marketStatus = computed(() => {
  const hour = currentTime.value.getHours()
  const day = currentTime.value.getDay()

  // Weekend
  if (day === 0 || day === 6) return 'closed'

  // Pre-market: 4am - 9:30am ET
  if (hour >= 4 && hour < 9 || (hour === 9 && currentTime.value.getMinutes() < 30)) {
    return 'pre-market'
  }

  // Market hours: 9:30am - 4pm ET
  if (hour >= 9 && hour < 16 || (hour === 9 && currentTime.value.getMinutes() >= 30)) {
    return 'open'
  }

  // After hours: 4pm - 8pm ET
  if (hour >= 16 && hour < 20) {
    return 'after-hours'
  }

  return 'closed'
})

const statusText = computed(() => {
  switch (marketStatus.value) {
    case 'open': return 'Market Open'
    case 'pre-market': return 'Pre-Market Trading'
    case 'after-hours': return 'After Hours Trading'
    case 'closed': return 'Market Closed'
    default: return 'Unknown'
  }
})

const timeUntilNext = computed(() => {
  // Calculate time until next market event
  // This is simplified - production should use market calendar API
  const hour = currentTime.value.getHours()

  if (marketStatus.value === 'open') {
    const closeTime = new Date(currentTime.value)
    closeTime.setHours(16, 0, 0)
    const diff = closeTime - currentTime.value
    return `Closes in ${formatTimeDiff(diff)}`
  }

  if (marketStatus.value === 'closed') {
    const openTime = new Date(currentTime.value)
    openTime.setDate(openTime.getDate() + 1)
    openTime.setHours(9, 30, 0)
    const diff = openTime - currentTime.value
    return `Opens in ${formatTimeDiff(diff)}`
  }

  return ''
})

function formatTimeDiff(ms) {
  const hours = Math.floor(ms / (1000 * 60 * 60))
  const minutes = Math.floor((ms % (1000 * 60 * 60)) / (1000 * 60))
  return `${hours}h ${minutes}m`
}

function pauseAutoHide() {
  if (hideTimeoutId) {
    clearTimeout(hideTimeoutId)
    hideTimeoutId = null
  }
}

function resumeAutoHide() {
  hideTimeoutId = setTimeout(() => {
    isVisible.value = false
  }, 10000)
}

onMounted(() => {
  intervalId = setInterval(() => {
    currentTime.value = new Date()
  }, 30000) // Update every 30 seconds

  resumeAutoHide()
})

onUnmounted(() => {
  if (intervalId) clearInterval(intervalId)
  if (hideTimeoutId) clearTimeout(hideTimeoutId)
})
</script>

<style scoped>
.market-status-bar {
  padding: var(--space-2) 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  text-align: center;
  position: relative;
  z-index: 1000;
}

.status-open {
  background: linear-gradient(90deg, #059669, #10B981);
}

.status-pre-market,
.status-after-hours {
  background: linear-gradient(90deg, #2563EB, #3B82F6);
}

.status-closed {
  background: linear-gradient(90deg, #6B7280, #9CA3AF);
}

.status-content {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.status-indicator {
  width: 10px;
  height: 10px;
  background: white;
  border-radius: 50%;
  animation: pulse-glow 2s infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 1; box-shadow: 0 0 8px rgba(255,255,255,0.6); }
  50% { opacity: 0.7; box-shadow: 0 0 4px rgba(255,255,255,0.3); }
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  transform: translateY(-100%);
  opacity: 0;
}

.slide-down-leave-to {
  opacity: 0;
}
</style>
```

---

## Technical Architecture

### Backend Stack Recommendations

**Current:** Flask, SQLite, yfinance, APScheduler
**Phase 3+ Recommended:**

1. **Database Migration Path:**
   ```bash
   # Development: SQLite (current)
   # Staging/Production: PostgreSQL 15+

   # Benefits:
   - Concurrent writes for WebSocket price updates
   - Better indexing for time-series queries
   - JSONB support for flexible metadata
   - Replication for high availability
   ```

2. **WebSocket Server:**
   ```python
   # Flask-SocketIO with Redis message broker

   pip install flask-socketio redis python-socketio[client]

   # Configuration:
   socketio = SocketIO(
       app,
       cors_allowed_origins="*",
       message_queue='redis://localhost:6379',
       async_mode='threading'
   )
   ```

3. **Caching Layer:**
   ```python
   # Redis for frequently accessed data

   import redis
   from functools import wraps

   redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

   def cache_price(ttl=60):
       def decorator(func):
           @wraps(func)
           def wrapper(symbol):
               cache_key = f'price:{symbol}'
               cached = redis_client.get(cache_key)
               if cached:
                   return json.loads(cached)

               result = func(symbol)
               redis_client.setex(cache_key, ttl, json.dumps(result))
               return result
           return wrapper
       return decorator
   ```

### Database Schema Extensions

**Phase 3 Tables:**
```sql
-- Price history for charting and technical analysis
CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    price DECIMAL(12, 4) NOT NULL,
    volume BIGINT,
    open DECIMAL(12, 4),
    high DECIMAL(12, 4),
    low DECIMAL(12, 4),
    close DECIMAL(12, 4),
    timestamp TIMESTAMPTZ NOT NULL,
    source VARCHAR(20) DEFAULT 'yfinance',
    CONSTRAINT unique_stock_timestamp UNIQUE(stock_id, timestamp)
);

CREATE INDEX idx_price_history_stock_time ON price_history(stock_id, timestamp DESC);
CREATE INDEX idx_price_history_timestamp ON price_history(timestamp);

-- Portfolio positions for P&L tracking
CREATE TABLE positions (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    shares DECIMAL(12, 6) NOT NULL,
    purchase_price DECIMAL(12, 4),
    purchase_date DATE,
    cost_basis DECIMAL(14, 2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enhanced alerts with multiple trigger types
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    alert_type VARCHAR(30) NOT NULL, -- 'price_above', 'price_below', 'percent_change', 'volume_spike', 'rsi', etc.
    threshold DECIMAL(12, 4) NOT NULL,
    condition VARCHAR(20), -- 'overbought', 'oversold', etc.
    timeframe INTEGER, -- minutes for percent_change alerts
    is_active BOOLEAN DEFAULT true,
    is_recurring BOOLEAN DEFAULT false,
    notification_method VARCHAR(20) DEFAULT 'email',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_active ON alerts(is_active, stock_id);

-- Alert trigger history
CREATE TABLE alert_history (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES alerts(id) ON DELETE CASCADE,
    triggered_at TIMESTAMPTZ NOT NULL,
    price DECIMAL(12, 4),
    message TEXT,
    notification_sent BOOLEAN DEFAULT false
);

CREATE INDEX idx_alert_history_alert ON alert_history(alert_id, triggered_at DESC);

-- Technical indicator cache
CREATE TABLE indicator_cache (
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    indicator_type VARCHAR(30) NOT NULL, -- 'rsi', 'macd', 'bollinger', etc.
    value JSONB NOT NULL,
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (stock_id, indicator_type)
);

CREATE INDEX idx_indicator_cache_time ON indicator_cache(calculated_at);

-- News articles
CREATE TABLE news_articles (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT UNIQUE NOT NULL,
    source VARCHAR(100),
    published_at TIMESTAMPTZ,
    sentiment VARCHAR(20), -- 'positive', 'negative', 'neutral'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_news_stock_published ON news_articles(stock_id, published_at DESC);
CREATE INDEX idx_news_published ON news_articles(published_at DESC);
```

### API Endpoints (New)

**Phase 3 Endpoints:**
```
WebSocket:
  WS  /ws/prices                          # Real-time price streaming

REST:
  GET  /api/analytics/portfolio           # Portfolio metrics (P&L, allocation, etc.)
  GET  /api/analytics/performance         # Historical performance data
  POST /api/positions                     # Add/update position
  GET  /api/positions/:id                 # Get position details
  DELETE /api/positions/:id               # Remove position

  GET  /api/stocks/:symbol/history        # Price history (OHLCV)
  GET  /api/stocks/:symbol/indicators     # Technical indicators

  POST /api/alerts                        # Create advanced alert
  PUT  /api/alerts/:id                    # Update alert
  GET  /api/alerts/history                # Alert trigger history
```

**Phase 4 Endpoints:**
```
  GET  /api/stocks/:symbol/indicators/:type  # Specific indicator (rsi, macd, etc.)
  GET  /api/risk/position-size               # Position sizing calculator
  GET  /api/risk/stop-loss                   # Stop-loss calculator
  POST /api/comparison                       # Multi-stock comparison
  GET  /api/correlation                      # Correlation matrix
```

**Phase 5 Endpoints:**
```
  GET  /api/news                          # Aggregated market news
  GET  /api/news/:symbol                  # Stock-specific news
  GET  /api/earnings/:symbol              # Earnings calendar

  GET  /api/export/portfolio/csv          # Export to CSV
  GET  /api/export/portfolio/pdf          # Generate PDF report
  GET  /api/export/tax-report             # Capital gains/losses
```

---

## Success Metrics & KPIs

### Technical Performance
- **Price Update Latency**: < 1 second from market data to UI (WebSocket)
- **API Response Time**: P95 < 200ms for GET requests
- **Uptime**: 99.5% availability
- **Database Query Performance**: All queries < 100ms (with proper indexing)

### User Experience
- **WCAG Compliance**: 100% WCAG 2.1 AA (maintain from Phase 1-2)
- **Core Web Vitals**:
  - LCP (Largest Contentful Paint): < 2.5s
  - FID (First Input Delay): < 100ms
  - CLS (Cumulative Layout Shift): < 0.1
- **Mobile Performance**: Lighthouse score > 90

### Feature Adoption (After 3 months)
- **Real-Time Prices**: > 80% of active users enable WebSocket
- **Portfolio Analytics**: > 60% visit analytics dashboard weekly
- **Technical Indicators**: > 40% use at least one indicator
- **Smart Alerts**: > 50% create advanced alerts (beyond simple price)

---

## Resource Requirements & Timeline

### Team Composition (Recommended)
- **1× Backend Engineer**: Flask, WebSocket, PostgreSQL expertise
- **1× Frontend Engineer**: Vue 3, real-time UI, data visualization
- **1× DevOps Engineer**: Docker, Redis, monitoring, CI/CD (0.5 FTE)
- **1× Product Designer**: Fintech UX, data visualization (0.5 FTE for Phases 4-5)
- **1× QA Engineer**: Automated testing, accessibility audits (0.5 FTE)

### Timeline Summary
| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 3 | 8 weeks | WebSocket prices, portfolio analytics, smart alerts |
| Phase 4 | 8 weeks | Technical indicators, risk tools, comparison |
| Phase 5 | 10 weeks | News, export, mobile optimization, performance |
| **Total** | **26 weeks** | **~6 months** |

### Infrastructure Costs (Monthly Estimates)
- **Phase 1-2 (Current)**: $0 (Local development, free tiers)
- **Phase 3+**:
  - VPS/Cloud (4GB RAM, 2 vCPU): $20-40/month
  - PostgreSQL managed instance: $15-25/month
  - Redis managed instance: $10-20/month
  - News API subscription: $50-100/month
  - Domain + SSL: $15/month
  - **Total**: ~$110-200/month

---

## Competitive Positioning

### Feature Comparison Matrix

| Feature | Stock Tracker (Phase 2) | After Phase 5 | Robinhood | TradingView | Yahoo Finance |
|---------|-------------------------|---------------|-----------|-------------|---------------|
| **Real-Time Prices** | ❌ Hourly | ✅ WebSocket | ✅ | ✅ | ✅ (Delayed) |
| **Portfolio Analytics** | ❌ | ✅ P&L, allocation | ✅ | ⚠️ Basic | ⚠️ Basic |
| **Technical Indicators** | ❌ | ✅ 12+ indicators | ❌ | ✅ 100+ | ⚠️ 5-6 |
| **Custom Alerts** | ⚠️ Price only | ✅ Multi-trigger | ⚠️ Price only | ✅ | ⚠️ Price only |
| **News Integration** | ❌ | ✅ Aggregated | ⚠️ Basic | ✅ | ✅ |
| **Risk Management** | ❌ | ✅ Tools | ❌ | ✅ | ❌ |
| **Mobile App** | ⚠️ Responsive web | ⚠️ PWA | ✅ Native | ✅ Native | ✅ Native |
| **Privacy** | ✅ Self-hosted | ✅ Self-hosted | ❌ Account required | ❌ Account required | ❌ Tracking |
| **Cost** | ✅ Free | ✅ Free/OSS | ✅ Free (+ paid) | ⚠️ $15-60/mo | ✅ Free |
| **Customization** | ✅ Open source | ✅ Open source | ❌ | ❌ | ❌ |

### Unique Value Propositions

**After Phase 5 completion, Stock Tracker will offer:**

1. **Privacy-First Trading Research**: No account required, self-hosted, zero tracking
2. **Professional-Grade Tools**: Bloomberg-caliber analytics without the $24k/year cost
3. **Fully Customizable**: Open-source codebase, extensible with custom indicators/alerts
4. **Unified Experience**: Portfolio tracking + research + alerts in one lightweight app
5. **Learning-Friendly**: Clean codebase for students/developers learning fintech development

---

## Risk Mitigation

### Technical Risks

**1. yfinance API Reliability**
- **Risk**: yfinance is unofficial and may break without notice
- **Mitigation**:
  - Implement adapter pattern for easy data source swapping
  - Add fallback to Alpha Vantage or IEX Cloud
  - Cache aggressively to reduce API calls
  - Monitor API health with alerts

**2. WebSocket Connection Stability**
- **Risk**: Users on poor networks may experience disconnections
- **Mitigation**:
  - Implement exponential backoff reconnection (1s, 2s, 4s, 8s, max 30s)
  - Graceful degradation to 30-second polling if WebSocket fails
  - Show clear connection status indicator in UI

**3. Database Performance at Scale**
- **Risk**: SQLite may become bottleneck with 1000+ stocks, historical data
- **Mitigation**:
  - Document clear migration path to PostgreSQL in Phase 3
  - Implement data retention policies (7 days intraday, aggregate to daily)
  - Use database indexes aggressively (see schema section)

### Business/Product Risks

**1. Feature Creep**
- **Risk**: Attempting to match TradingView's 500+ features
- **Mitigation**:
  - Stick to roadmap priorities
  - Use feature flagging for experimental features
  - Validate each feature with user feedback before building next

**2. Regulatory Compliance**
- **Risk**: Providing financial advice without proper disclaimers
- **Mitigation**:
  - Add clear disclaimer: "Not financial advice, for informational purposes only"
  - Avoid language like "buy signals" or "guaranteed returns"
  - Consult legal counsel before adding trading execution features

---

## Next Steps & Recommendations

### Immediate Actions (This Week)
1. **User Validation**: Survey 10-15 target users to validate Phase 3 priorities
   - Question: "What's the #1 feature missing from your stock tracking workflow?"
2. **Technical Spike**: Prototype WebSocket price streaming (2-3 hours)
   - Validate performance with 50+ simultaneous stock subscriptions
3. **Database Planning**: Design full schema for Phases 3-5 (see above)

### Phase 3 Kickoff (Week 1-2)
1. **Backend**: Set up Flask-SocketIO + Redis infrastructure
2. **Frontend**: Create WebSocket service layer and live price components
3. **Database**: Implement price_history table with proper indexes
4. **DevOps**: Set up monitoring (consider Sentry for errors, Grafana for metrics)

### Long-Term Strategic Decisions
1. **Mobile Strategy**: Phase 5 PWA vs. React Native app? (Recommend PWA first)
2. **Monetization** (Optional): Premium features (advanced alerts, historical data) vs. fully free?
3. **Community**: Open-source on GitHub? Build plugin ecosystem?

---

## Appendix: Fintech Design Principles Applied

### 1. Information Density vs. Clarity
**Challenge**: Trading interfaces must show 20+ data points without overwhelming users.

**Stock Tracker Solution:**
- **Progressive Disclosure**: Basic view shows price/change/volume. Click for full indicators panel.
- **Visual Hierarchy**: Use type scale (2rem for price, 0.875rem for metadata)
- **Chunking**: Group related data (Price section, Target section, Analysis section)

### 2. Trust & Precision
**Challenge**: Users must trust the numbers are accurate and up-to-date.

**Stock Tracker Solution:**
- **Monospace Fonts**: All prices/percentages in Roboto Mono to prevent "jumping"
- **Timestamp Display**: Show "Updated 3s ago" with live indicator
- **Data Source Labels**: "Powered by Yahoo Finance" in footer
- **Error States**: Clear messaging when data fetch fails

### 3. Latency UX
**Challenge**: Network delays can make app feel sluggish.

**Stock Tracker Solution:**
- **Optimistic UI**: Update target immediately, sync in background
- **Skeleton Loaders**: Show layout structure while loading (Phase 2 ✅)
- **Inline Spinners**: For secondary actions (delete tag, remove note)
- **Debouncing**: Search input waits 300ms before filtering

### 4. Accessibility in High-Stakes Scenarios
**Challenge**: Users may be color-blind or using screen readers during volatile markets.

**Stock Tracker Solution:**
- **Color + Icon**: Never use color alone (✅ green up arrow, 🔻 red down arrow)
- **ARIA Labels**: All interactive elements have descriptive labels (Phase 1 ✅)
- **Keyboard Navigation**: Full keyboard support for all workflows (Phase 2 ✅)
- **Focus Indicators**: 3px blue outline at 4.5:1 contrast ratio

---

**Document Version**: 1.0
**Last Updated**: February 7, 2026
**Next Review**: After Phase 3 completion (April 2026)

---

## Feedback & Iteration

This roadmap is a living document. After each phase:
1. Conduct user testing sessions (5-10 participants)
2. Review analytics (feature usage, error rates, performance metrics)
3. Update priorities for next phase based on learnings
4. Document technical debt and refactoring needs

**Contact**: Product team should maintain this document in `/docs/PRODUCT_ROADMAP.md` with version control.
