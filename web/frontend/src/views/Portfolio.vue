<template>
  <div class="portfolio-view">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h2 mb-0">
        <i class="bi bi-briefcase me-2"></i>
        Portfolio
      </h1>
      <div class="d-flex gap-2">
        <button
          class="btn btn-outline-secondary"
          @click="fetchData"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise me-1"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Portfolio Summary Cards -->
    <div class="row g-3 mb-4" v-if="summary">
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Total Value</div>
            <div class="summary-value h4 mb-0">{{ formatPrice(summary.totalValue) }}</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Cost Basis</div>
            <div class="summary-value h4 mb-0">{{ formatPrice(summary.totalCostBasis) }}</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Total P/L</div>
            <div class="summary-value h4 mb-0" :class="getPLClass(summary.totalPL)">
              {{ formatPL(summary.totalPL) }}
            </div>
            <div class="small" :class="getPLClass(summary.totalPLPercent)">
              {{ formatPLPercent(summary.totalPLPercent) }}
            </div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Day P/L</div>
            <div class="summary-value h4 mb-0" :class="getPLClass(summary.dayPL)">
              {{ formatPL(summary.dayPL) }}
            </div>
            <div class="small" :class="getPLClass(summary.dayPLPercent)">
              {{ formatPLPercent(summary.dayPLPercent) }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger">
      <i class="bi bi-exclamation-triangle me-2"></i>
      {{ error }}
    </div>

    <!-- Empty State -->
    <div v-else-if="!holdings.length" class="text-center py-5">
      <i class="bi bi-briefcase display-1 text-muted"></i>
      <p class="lead text-muted mt-3">No holdings yet</p>
      <p class="text-muted">Add shares to your stocks to see them here</p>
      <router-link to="/" class="btn btn-primary">
        <i class="bi bi-arrow-left me-1"></i>
        Go to Dashboard
      </router-link>
    </div>

    <!-- Holdings Table -->
    <div v-else class="card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0 portfolio-table">
          <thead class="table-light sticky-top">
            <tr>
              <th class="sortable" @click="sortBy('symbol')">
                Symbol
                <i v-if="sortKey === 'symbol'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('shares')">
                Shares
                <i v-if="sortKey === 'shares'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('avgCost')">
                Avg Cost
                <i v-if="sortKey === 'avgCost'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('currentPrice')">
                Price
                <i v-if="sortKey === 'currentPrice'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('dayChange')">
                Day Change
                <i v-if="sortKey === 'dayChange'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('marketValue')">
                Mkt Value
                <i v-if="sortKey === 'marketValue'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('costBasis')">
                Cost Basis
                <i v-if="sortKey === 'costBasis'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('pl')">
                P/L
                <i v-if="sortKey === 'pl'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('plPercent')">
                P/L %
                <i v-if="sortKey === 'plPercent'" :class="sortIcon"></i>
              </th>
              <th class="text-end">% of Portfolio</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="holding in sortedHoldings"
              :key="holding.symbol"
              class="holding-row"
              @click="goToStock(holding.symbol)"
            >
              <td>
                <div class="d-flex align-items-center">
                  <div>
                    <div class="fw-bold">{{ holding.symbol }}</div>
                    <small class="text-muted">{{ truncate(holding.companyName, 20) }}</small>
                  </div>
                </div>
              </td>
              <td class="text-end">{{ formatNumber(holding.shares) }}</td>
              <td class="text-end">{{ formatPrice(holding.avgCost) }}</td>
              <td class="text-end">
                <div>{{ formatPrice(holding.currentPrice) }}</div>
                <div v-if="holding.afterHours" class="after-hours-mini">
                  <small class="text-muted">{{ holding.afterHours.isPremarket ? 'PM' : 'AH' }}:</small>
                  <small :class="holding.afterHours.change >= 0 ? 'text-success' : 'text-danger'">
                    {{ formatPrice(holding.afterHours.price) }}
                  </small>
                </div>
              </td>
              <td class="text-end" :class="getPLClass(holding.dayChange)">
                <div>{{ formatPL(holding.dayChange) }}</div>
                <small>{{ formatPLPercent(holding.dayChangePercent) }}</small>
              </td>
              <td class="text-end fw-medium">{{ formatPrice(holding.marketValue) }}</td>
              <td class="text-end text-muted">{{ formatPrice(holding.costBasis) }}</td>
              <td class="text-end fw-medium" :class="getPLClass(holding.pl)">
                {{ formatPL(holding.pl) }}
              </td>
              <td class="text-end" :class="getPLClass(holding.plPercent)">
                <span class="badge" :class="holding.plPercent >= 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger'">
                  {{ formatPLPercent(holding.plPercent) }}
                </span>
              </td>
              <td class="text-end">
                <div class="portfolio-percent">
                  <div class="progress" style="height: 4px; width: 60px;">
                    <div
                      class="progress-bar bg-primary"
                      :style="{ width: holding.portfolioPercent + '%' }"
                    ></div>
                  </div>
                  <small class="text-muted">{{ holding.portfolioPercent?.toFixed(1) }}%</small>
                </div>
              </td>
            </tr>
          </tbody>
          <tfoot class="table-light fw-bold">
            <tr>
              <td>Total ({{ holdings.length }} positions)</td>
              <td class="text-end">-</td>
              <td class="text-end">-</td>
              <td class="text-end">-</td>
              <td class="text-end" :class="getPLClass(summary?.dayPL)">
                {{ formatPL(summary?.dayPL) }}
              </td>
              <td class="text-end">{{ formatPrice(summary?.totalValue) }}</td>
              <td class="text-end">{{ formatPrice(summary?.totalCostBasis) }}</td>
              <td class="text-end" :class="getPLClass(summary?.totalPL)">
                {{ formatPL(summary?.totalPL) }}
              </td>
              <td class="text-end" :class="getPLClass(summary?.totalPLPercent)">
                {{ formatPLPercent(summary?.totalPLPercent) }}
              </td>
              <td class="text-end">100%</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stocksApi } from '@/api'

export default {
  name: 'Portfolio',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref(null)
    const holdings = ref([])
    const summary = ref(null)
    const sortKey = ref('marketValue')
    const sortAsc = ref(false)

    const fetchData = async () => {
      loading.value = true
      error.value = null

      try {
        // Fetch all stocks with prices
        const response = await stocksApi.getAll({ include_prices: true })
        const stocks = response.data.stocks

        // Filter to only stocks with holdings
        const stocksWithHoldings = stocks.filter(s => s.holding)

        // Transform data for table
        const holdingsData = stocksWithHoldings.map(stock => {
          const holding = stock.holding
          const currentPrice = stock.current_price || 0
          const avgCost = holding.average_cost || 0
          const shares = holding.shares || 0
          const marketValue = shares * currentPrice
          const costBasis = shares * avgCost
          const pl = avgCost ? marketValue - costBasis : null
          const plPercent = avgCost && costBasis ? ((marketValue - costBasis) / costBasis) * 100 : null

          // Day change calculation
          const dayChangePercent = stock.price_change_percent || 0
          const prevPrice = currentPrice / (1 + dayChangePercent / 100)
          const dayChange = (currentPrice - prevPrice) * shares

          return {
            symbol: stock.symbol,
            companyName: stock.company_name,
            shares,
            avgCost,
            currentPrice,
            marketValue,
            costBasis,
            pl,
            plPercent,
            dayChange,
            dayChangePercent,
            afterHours: stock.after_hours ? {
              price: stock.after_hours.price,
              change: stock.after_hours.change,
              isPremarket: stock.after_hours.is_premarket
            } : null,
            portfolioPercent: 0 // Will be calculated after
          }
        })

        // Calculate portfolio percentages
        const totalValue = holdingsData.reduce((sum, h) => sum + h.marketValue, 0)
        holdingsData.forEach(h => {
          h.portfolioPercent = totalValue > 0 ? (h.marketValue / totalValue) * 100 : 0
        })

        holdings.value = holdingsData

        // Calculate summary
        const totalCostBasis = holdingsData.reduce((sum, h) => sum + (h.costBasis || 0), 0)
        const totalPL = holdingsData.reduce((sum, h) => sum + (h.pl || 0), 0)
        const dayPL = holdingsData.reduce((sum, h) => sum + (h.dayChange || 0), 0)

        summary.value = {
          totalValue,
          totalCostBasis,
          totalPL,
          totalPLPercent: totalCostBasis > 0 ? (totalPL / totalCostBasis) * 100 : 0,
          dayPL,
          dayPLPercent: totalValue > 0 ? (dayPL / (totalValue - dayPL)) * 100 : 0
        }

      } catch (err) {
        console.error('Error fetching portfolio:', err)
        error.value = err.message || 'Failed to load portfolio'
      } finally {
        loading.value = false
      }
    }

    const sortedHoldings = computed(() => {
      const sorted = [...holdings.value]
      sorted.sort((a, b) => {
        let aVal = a[sortKey.value]
        let bVal = b[sortKey.value]

        // Handle null values
        if (aVal === null) aVal = sortAsc.value ? Infinity : -Infinity
        if (bVal === null) bVal = sortAsc.value ? Infinity : -Infinity

        // Handle string comparison
        if (typeof aVal === 'string') {
          return sortAsc.value
            ? aVal.localeCompare(bVal)
            : bVal.localeCompare(aVal)
        }

        return sortAsc.value ? aVal - bVal : bVal - aVal
      })
      return sorted
    })

    const sortIcon = computed(() => {
      return sortAsc.value ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'
    })

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortAsc.value = !sortAsc.value
      } else {
        sortKey.value = key
        sortAsc.value = false
      }
    }

    const goToStock = (symbol) => {
      router.push(`/stock/${symbol}`)
    }

    const truncate = (str, length) => {
      if (!str) return ''
      return str.length > length ? str.substring(0, length) + '...' : str
    }

    const formatPrice = (value) => {
      if (value === null || value === undefined) return '-'
      return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatNumber = (value) => {
      if (value === null || value === undefined) return '-'
      return value.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 4 })
    }

    const formatPL = (value) => {
      if (value === null || value === undefined) return '-'
      const prefix = value >= 0 ? '+' : ''
      return prefix + '$' + Math.abs(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatPLPercent = (value) => {
      if (value === null || value === undefined) return '-'
      const prefix = value >= 0 ? '+' : ''
      return prefix + value.toFixed(2) + '%'
    }

    const getPLClass = (value) => {
      if (value === null || value === undefined) return ''
      return value >= 0 ? 'text-success' : 'text-danger'
    }

    onMounted(() => {
      fetchData()
    })

    return {
      loading,
      error,
      holdings,
      summary,
      sortKey,
      sortAsc,
      sortedHoldings,
      sortIcon,
      sortBy,
      goToStock,
      truncate,
      formatPrice,
      formatNumber,
      formatPL,
      formatPLPercent,
      getPLClass,
      fetchData
    }
  }
}
</script>

<style scoped>
.portfolio-view {
  max-width: 1400px;
  margin: 0 auto;
}

.summary-card {
  border: none;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  transition: transform 0.2s;
}

.summary-card:hover {
  transform: translateY(-2px);
}

.summary-label {
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.75rem;
}

.summary-value {
  font-weight: 600;
}

.portfolio-table {
  font-size: 0.875rem;
}

.portfolio-table th {
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.portfolio-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.portfolio-table th.sortable:hover {
  color: #212529;
  background-color: #e9ecef;
}

.portfolio-table th i {
  font-size: 0.65rem;
  margin-left: 4px;
}

.holding-row {
  cursor: pointer;
  transition: background-color 0.15s;
}

.holding-row:hover {
  background-color: #f8f9fa !important;
}

.after-hours-mini {
  font-size: 0.7rem;
  line-height: 1;
}

.portfolio-percent {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.portfolio-percent .progress {
  border-radius: 2px;
}

/* Bootstrap 5.3+ subtle backgrounds fallback */
.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.15) !important;
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.15) !important;
}

/* Responsive adjustments */
@media (max-width: 992px) {
  .portfolio-table {
    font-size: 0.8rem;
  }

  .portfolio-table th {
    font-size: 0.7rem;
  }
}

/* Sticky header */
.table-responsive {
  max-height: calc(100vh - 350px);
  overflow-y: auto;
}

thead.sticky-top th {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #f8f9fa;
}
</style>
