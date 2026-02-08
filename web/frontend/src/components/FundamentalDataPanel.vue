<template>
  <div class="card mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">
        <i class="bi bi-graph-up-arrow me-2" aria-hidden="true"></i>
        Fundamental Data
      </h5>
      <button
        class="btn btn-sm btn-outline-secondary"
        @click="$emit('refresh')"
        aria-label="Refresh fundamental data"
      >
        <i class="bi bi-arrow-clockwise" aria-hidden="true"></i>
      </button>
    </div>
    <div class="card-body">
      <div v-if="!data" class="text-center text-muted py-4">
        <i class="bi bi-hourglass-split display-6"></i>
        <p class="mt-2">Loading fundamental data...</p>
      </div>

      <div v-else class="fundamental-grid">
        <!-- Valuation Metrics Section -->
        <div class="section-group">
          <h6 class="section-title">Valuation</h6>
          <div class="data-row" v-if="data.market_cap">
            <span class="data-label">Market Cap</span>
            <span class="data-value">{{ formatLargeNumber(data.market_cap) }}</span>
          </div>
          <div class="data-row" v-if="data.pe_ratio">
            <span class="data-label">P/E Ratio (TTM)</span>
            <span class="data-value">{{ formatNumber(data.pe_ratio, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.forward_pe">
            <span class="data-label">Forward P/E</span>
            <span class="data-value">{{ formatNumber(data.forward_pe, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.peg_ratio">
            <span class="data-label">PEG Ratio</span>
            <span class="data-value">{{ formatNumber(data.peg_ratio, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.price_to_book">
            <span class="data-label">Price/Book</span>
            <span class="data-value">{{ formatNumber(data.price_to_book, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.price_to_sales">
            <span class="data-label">Price/Sales</span>
            <span class="data-value">{{ formatNumber(data.price_to_sales, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.enterprise_value">
            <span class="data-label">Enterprise Value</span>
            <span class="data-value">{{ formatLargeNumber(data.enterprise_value) }}</span>
          </div>
          <div class="data-row" v-if="data.enterprise_to_ebitda">
            <span class="data-label">EV/EBITDA</span>
            <span class="data-value">{{ formatNumber(data.enterprise_to_ebitda, 2) }}</span>
          </div>
        </div>

        <!-- Price Performance Section -->
        <div class="section-group">
          <h6 class="section-title">Price Performance</h6>
          <div class="data-row" v-if="data.fifty_two_week_high">
            <span class="data-label">52 Week High</span>
            <span class="data-value">{{ formatCurrency(data.fifty_two_week_high) }}</span>
          </div>
          <div class="data-row" v-if="data.fifty_two_week_low">
            <span class="data-label">52 Week Low</span>
            <span class="data-value">{{ formatCurrency(data.fifty_two_week_low) }}</span>
          </div>
          <div class="data-row" v-if="data.fifty_two_week_high && data.fifty_two_week_low && currentPrice">
            <span class="data-label">52 Week Range</span>
            <div class="range-bar-container">
              <div class="range-bar">
                <div class="range-fill" :style="{ width: get52WeekPercentage + '%' }"></div>
                <div class="range-marker" :style="{ left: get52WeekPercentage + '%' }"></div>
              </div>
              <div class="range-labels">
                <span>{{ formatCurrency(data.fifty_two_week_low) }}</span>
                <span>{{ formatCurrency(data.fifty_two_week_high) }}</span>
              </div>
            </div>
          </div>
          <div class="data-row" v-if="data.fifty_day_average">
            <span class="data-label">50-Day Avg</span>
            <span class="data-value">{{ formatCurrency(data.fifty_day_average) }}</span>
          </div>
          <div class="data-row" v-if="data.two_hundred_day_average">
            <span class="data-label">200-Day Avg</span>
            <span class="data-value">{{ formatCurrency(data.two_hundred_day_average) }}</span>
          </div>
          <div class="data-row" v-if="data.beta">
            <span class="data-label">Beta</span>
            <span class="data-value" :class="getBetaClass(data.beta)">
              {{ formatNumber(data.beta, 2) }}
            </span>
          </div>
        </div>

        <!-- Trading Information Section -->
        <div class="section-group">
          <h6 class="section-title">Trading Info</h6>
          <div class="data-row" v-if="data.volume">
            <span class="data-label">Volume</span>
            <span class="data-value">{{ formatLargeNumber(data.volume) }}</span>
          </div>
          <div class="data-row" v-if="data.average_volume">
            <span class="data-label">Avg Volume</span>
            <span class="data-value">{{ formatLargeNumber(data.average_volume) }}</span>
          </div>
          <div class="data-row" v-if="data.bid && data.ask">
            <span class="data-label">Bid × Ask</span>
            <span class="data-value">
              {{ formatCurrency(data.bid) }} × {{ formatCurrency(data.ask) }}
            </span>
          </div>
          <div class="data-row" v-if="data.bid_size && data.ask_size">
            <span class="data-label">Bid/Ask Size</span>
            <span class="data-value">
              {{ formatNumber(data.bid_size, 0) }} / {{ formatNumber(data.ask_size, 0) }}
            </span>
          </div>
        </div>

        <!-- Dividends Section -->
        <div class="section-group" v-if="data.dividend_rate || data.dividend_yield">
          <h6 class="section-title">Dividends</h6>
          <div class="data-row" v-if="data.dividend_rate">
            <span class="data-label">Dividend (Annual)</span>
            <span class="data-value">{{ formatCurrency(data.dividend_rate) }}</span>
          </div>
          <div class="data-row" v-if="data.dividend_yield">
            <span class="data-label">Dividend Yield</span>
            <span class="data-value">{{ formatPercent(data.dividend_yield * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.payout_ratio">
            <span class="data-label">Payout Ratio</span>
            <span class="data-value">{{ formatPercent(data.payout_ratio * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.ex_dividend_date">
            <span class="data-label">Ex-Dividend Date</span>
            <span class="data-value">{{ formatDate(data.ex_dividend_date) }}</span>
          </div>
        </div>

        <!-- Profitability Section -->
        <div class="section-group">
          <h6 class="section-title">Profitability</h6>
          <div class="data-row" v-if="data.profit_margins">
            <span class="data-label">Profit Margin</span>
            <span class="data-value">{{ formatPercent(data.profit_margins * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.operating_margins">
            <span class="data-label">Operating Margin</span>
            <span class="data-value">{{ formatPercent(data.operating_margins * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.gross_margins">
            <span class="data-label">Gross Margin</span>
            <span class="data-value">{{ formatPercent(data.gross_margins * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.return_on_assets">
            <span class="data-label">ROA</span>
            <span class="data-value">{{ formatPercent(data.return_on_assets * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.return_on_equity">
            <span class="data-label">ROE</span>
            <span class="data-value">{{ formatPercent(data.return_on_equity * 100) }}</span>
          </div>
          <div class="data-row" v-if="data.revenue">
            <span class="data-label">Revenue (TTM)</span>
            <span class="data-value">{{ formatLargeNumber(data.revenue) }}</span>
          </div>
          <div class="data-row" v-if="data.revenue_per_share">
            <span class="data-label">Revenue Per Share</span>
            <span class="data-value">{{ formatCurrency(data.revenue_per_share) }}</span>
          </div>
        </div>

        <!-- Financial Health Section -->
        <div class="section-group">
          <h6 class="section-title">Financial Health</h6>
          <div class="data-row" v-if="data.total_cash">
            <span class="data-label">Total Cash</span>
            <span class="data-value">{{ formatLargeNumber(data.total_cash) }}</span>
          </div>
          <div class="data-row" v-if="data.total_debt">
            <span class="data-label">Total Debt</span>
            <span class="data-value">{{ formatLargeNumber(data.total_debt) }}</span>
          </div>
          <div class="data-row" v-if="data.debt_to_equity">
            <span class="data-label">Debt/Equity</span>
            <span class="data-value">{{ formatNumber(data.debt_to_equity, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.current_ratio">
            <span class="data-label">Current Ratio</span>
            <span class="data-value">{{ formatNumber(data.current_ratio, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.quick_ratio">
            <span class="data-label">Quick Ratio</span>
            <span class="data-value">{{ formatNumber(data.quick_ratio, 2) }}</span>
          </div>
          <div class="data-row" v-if="data.free_cashflow">
            <span class="data-label">Free Cash Flow</span>
            <span class="data-value">{{ formatLargeNumber(data.free_cashflow) }}</span>
          </div>
        </div>

        <!-- Earnings & Growth Section -->
        <div class="section-group">
          <h6 class="section-title">Earnings & Growth</h6>
          <div class="data-row" v-if="data.earnings_date">
            <span class="data-label">Next Earnings Date</span>
            <span class="data-value earnings-date">
              <i class="bi bi-calendar-event me-1" aria-hidden="true"></i>
              {{ formatDate(data.earnings_date) }}
            </span>
          </div>
          <div class="data-row" v-if="data.trailing_eps">
            <span class="data-label">EPS (TTM)</span>
            <span class="data-value">{{ formatCurrency(data.trailing_eps) }}</span>
          </div>
          <div class="data-row" v-if="data.forward_eps">
            <span class="data-label">Forward EPS</span>
            <span class="data-value">{{ formatCurrency(data.forward_eps) }}</span>
          </div>
          <div class="data-row" v-if="data.earnings_growth">
            <span class="data-label">Earnings Growth</span>
            <span class="data-value" :class="getGrowthClass(data.earnings_growth)">
              {{ formatPercent(data.earnings_growth * 100) }}
            </span>
          </div>
          <div class="data-row" v-if="data.revenue_growth">
            <span class="data-label">Revenue Growth</span>
            <span class="data-value" :class="getGrowthClass(data.revenue_growth)">
              {{ formatPercent(data.revenue_growth * 100) }}
            </span>
          </div>
          <div class="data-row" v-if="data.earnings_quarterly_growth">
            <span class="data-label">Quarterly Earnings Growth</span>
            <span class="data-value" :class="getGrowthClass(data.earnings_quarterly_growth)">
              {{ formatPercent(data.earnings_quarterly_growth * 100) }}
            </span>
          </div>
        </div>

        <!-- Analyst Recommendations Section -->
        <div class="section-group" v-if="data.recommendation || data.target_mean_price">
          <h6 class="section-title">Analyst Ratings</h6>
          <div class="data-row" v-if="data.recommendation">
            <span class="data-label">Recommendation</span>
            <span class="data-value">
              <span class="badge" :class="getRecommendationClass(data.recommendation)">
                {{ formatRecommendation(data.recommendation) }}
              </span>
            </span>
          </div>
          <div class="data-row" v-if="data.target_mean_price">
            <span class="data-label">Analyst Target</span>
            <span class="data-value">{{ formatCurrency(data.target_mean_price) }}</span>
          </div>
          <div class="data-row" v-if="data.target_high_price && data.target_low_price">
            <span class="data-label">Target Range</span>
            <span class="data-value">
              {{ formatCurrency(data.target_low_price) }} - {{ formatCurrency(data.target_high_price) }}
            </span>
          </div>
          <div class="data-row" v-if="data.number_of_analyst_opinions">
            <span class="data-label">Analysts</span>
            <span class="data-value">{{ data.number_of_analyst_opinions }}</span>
          </div>
        </div>

        <!-- Company Info Section -->
        <div class="section-group">
          <h6 class="section-title">Company Info</h6>
          <div class="data-row" v-if="data.sector">
            <span class="data-label">Sector</span>
            <span class="data-value">{{ data.sector }}</span>
          </div>
          <div class="data-row" v-if="data.industry">
            <span class="data-label">Industry</span>
            <span class="data-value">{{ data.industry }}</span>
          </div>
          <div class="data-row" v-if="data.full_time_employees">
            <span class="data-label">Employees</span>
            <span class="data-value">{{ formatNumber(data.full_time_employees, 0) }}</span>
          </div>
          <div class="data-row" v-if="data.website">
            <span class="data-label">Website</span>
            <span class="data-value">
              <a :href="data.website" target="_blank" rel="noopener noreferrer" class="text-primary">
                {{ getDomain(data.website) }}
                <i class="bi bi-box-arrow-up-right ms-1" aria-hidden="true"></i>
              </a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  },
  currentPrice: {
    type: Number,
    default: null
  }
})

defineEmits(['refresh'])

// Formatting functions
const formatCurrency = (value) => {
  if (value === null || value === undefined) return 'N/A'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatNumber = (value, decimals = 2) => {
  if (value === null || value === undefined) return 'N/A'
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  }).format(value)
}

const formatLargeNumber = (value) => {
  if (value === null || value === undefined) return 'N/A'

  const absValue = Math.abs(value)
  if (absValue >= 1e12) {
    return (value / 1e12).toFixed(2) + 'T'
  } else if (absValue >= 1e9) {
    return (value / 1e9).toFixed(2) + 'B'
  } else if (absValue >= 1e6) {
    return (value / 1e6).toFixed(2) + 'M'
  } else if (absValue >= 1e3) {
    return (value / 1e3).toFixed(2) + 'K'
  }
  return formatNumber(value, 0)
}

const formatPercent = (value) => {
  if (value === null || value === undefined) return 'N/A'
  return formatNumber(value, 2) + '%'
}

const formatDate = (value) => {
  if (!value) return 'N/A'
  try {
    // Handle timestamp (epoch seconds)
    if (typeof value === 'number') {
      const date = new Date(value * 1000)
      return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
    }
    // Handle ISO string
    const date = new Date(value)
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch (e) {
    return 'N/A'
  }
}

const getDomain = (url) => {
  if (!url) return ''
  try {
    const domain = new URL(url).hostname
    return domain.replace('www.', '')
  } catch (e) {
    return url
  }
}

const formatRecommendation = (rec) => {
  if (!rec) return 'N/A'
  const mapping = {
    'strong_buy': 'Strong Buy',
    'buy': 'Buy',
    'hold': 'Hold',
    'sell': 'Sell',
    'strong_sell': 'Strong Sell'
  }
  return mapping[rec] || rec.toUpperCase()
}

// Computed values
const get52WeekPercentage = computed(() => {
  if (!props.data || !props.currentPrice) return 0
  const low = props.data.fifty_two_week_low
  const high = props.data.fifty_two_week_high
  if (!low || !high || low === high) return 0

  const percentage = ((props.currentPrice - low) / (high - low)) * 100
  return Math.max(0, Math.min(100, percentage))
})

// Styling classes
const getBetaClass = (beta) => {
  if (beta === null || beta === undefined) return ''
  if (beta < 0.8) return 'text-success'
  if (beta > 1.2) return 'text-danger'
  return ''
}

const getGrowthClass = (growth) => {
  if (growth === null || growth === undefined) return ''
  if (growth > 0) return 'text-success'
  if (growth < 0) return 'text-danger'
  return ''
}

const getRecommendationClass = (rec) => {
  if (!rec) return 'bg-secondary'
  if (rec.includes('buy')) return 'bg-success'
  if (rec === 'hold') return 'bg-warning'
  if (rec.includes('sell')) return 'bg-danger'
  return 'bg-secondary'
}
</script>

<style scoped>
.fundamental-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--space-4);
}

.section-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: var(--space-3);
}

.section-title {
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #495057;
  margin-bottom: var(--space-2);
  padding-bottom: var(--space-1);
  border-bottom: 2px solid #dee2e6;
}

.data-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-1) 0;
  border-bottom: 1px solid #e9ecef;
}

.data-row:last-child {
  border-bottom: none;
}

.data-label {
  font-size: 0.875rem;
  color: #6c757d;
  font-weight: 500;
}

.data-value {
  font-family: 'Roboto Mono', monospace;
  font-size: 0.875rem;
  font-weight: 600;
  color: #212529;
  text-align: right;
}

.earnings-date {
  color: var(--color-primary);
  font-weight: 700;
}

/* 52-Week Range Bar */
.range-bar-container {
  flex: 1;
  margin-left: var(--space-2);
  max-width: 200px;
}

.range-bar {
  position: relative;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.range-fill {
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  background: linear-gradient(90deg, var(--color-danger), var(--color-warning), var(--color-success));
  transition: width 0.5s ease;
}

.range-marker {
  position: absolute;
  top: -2px;
  width: 3px;
  height: 12px;
  background: #212529;
  border-radius: 2px;
  transform: translateX(-50%);
  transition: left 0.5s ease;
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #6c757d;
  font-family: 'Roboto Mono', monospace;
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .fundamental-grid {
    grid-template-columns: 1fr;
  }

  .data-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }

  .data-value {
    text-align: left;
  }

  .range-bar-container {
    width: 100%;
    max-width: none;
    margin-left: 0;
    margin-top: var(--space-1);
  }
}
</style>
