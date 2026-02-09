<template>
  <div class="watchlist-view">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h2 mb-0">
        <i class="bi bi-eye me-2"></i>
        Watchlist
      </h1>
      <div class="d-flex gap-2">
        <button
          class="btn btn-primary"
          data-bs-toggle="modal"
          data-bs-target="#addStockModal"
        >
          <i class="bi bi-plus-circle me-1"></i>
          Add Stock
        </button>
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

    <!-- Summary Cards -->
    <div class="row g-3 mb-4" v-if="stocks.length">
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Watching</div>
            <div class="summary-value h4 mb-0">{{ stocks.length }}</div>
            <div class="small text-muted">stocks</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Near Buy Target</div>
            <div class="summary-value h4 mb-0 text-success">{{ nearBuyTargetCount }}</div>
            <div class="small text-muted">within 5%</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Gainers Today</div>
            <div class="summary-value h4 mb-0 text-success">{{ gainersCount }}</div>
            <div class="small text-muted">stocks up</div>
          </div>
        </div>
      </div>
      <div class="col-6 col-md-3">
        <div class="card summary-card">
          <div class="card-body text-center">
            <div class="summary-label text-muted small">Losers Today</div>
            <div class="summary-value h4 mb-0 text-danger">{{ losersCount }}</div>
            <div class="small text-muted">stocks down</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="mb-3" v-if="stocks.length">
      <ul class="nav nav-pills nav-fill nav-pills-sm">
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: filter === 'all' }"
            @click="filter = 'all'"
          >
            All ({{ stocks.length }})
          </button>
        </li>
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: filter === 'nearBuy' }"
            @click="filter = 'nearBuy'"
          >
            <i class="bi bi-bullseye me-1"></i>
            Near Buy ({{ nearBuyTargetCount }})
          </button>
        </li>
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: filter === 'gainers' }"
            @click="filter = 'gainers'"
          >
            <i class="bi bi-graph-up-arrow me-1 text-success"></i>
            Gainers ({{ gainersCount }})
          </button>
        </li>
        <li class="nav-item">
          <button
            class="nav-link"
            :class="{ active: filter === 'losers' }"
            @click="filter = 'losers'"
          >
            <i class="bi bi-graph-down-arrow me-1 text-danger"></i>
            Losers ({{ losersCount }})
          </button>
        </li>
      </ul>
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
    <div v-else-if="!stocks.length" class="text-center py-5">
      <i class="bi bi-eye display-1 text-muted"></i>
      <p class="lead text-muted mt-3">No stocks in watchlist</p>
      <p class="text-muted">Add stocks without holdings to watch them here</p>
      <button
        class="btn btn-primary"
        data-bs-toggle="modal"
        data-bs-target="#addStockModal"
      >
        <i class="bi bi-plus-circle me-1"></i>
        Add Stock to Watch
      </button>
    </div>

    <!-- Watchlist Table -->
    <div v-else class="card">
      <div class="table-responsive">
        <table class="table table-hover align-middle mb-0 watchlist-table">
          <thead class="table-light sticky-top">
            <tr>
              <th class="sortable" @click="sortBy('symbol')">
                Symbol
                <i v-if="sortKey === 'symbol'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('currentPrice')">
                Price
                <i v-if="sortKey === 'currentPrice'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('dayChangePercent')">
                Day Change
                <i v-if="sortKey === 'dayChangePercent'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('buyTarget')">
                Buy Target
                <i v-if="sortKey === 'buyTarget'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('distanceToBuy')">
                To Target
                <i v-if="sortKey === 'distanceToBuy'" :class="sortIcon"></i>
              </th>
              <th class="text-end sortable" @click="sortBy('sellTarget')">
                Sell Target
                <i v-if="sortKey === 'sellTarget'" :class="sortIcon"></i>
              </th>
              <th class="text-center">Tags</th>
              <th class="text-center sortable" @click="sortBy('notesCount')">
                Notes
                <i v-if="sortKey === 'notesCount'" :class="sortIcon"></i>
              </th>
              <th class="text-center">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="stock in filteredStocks"
              :key="stock.symbol"
              class="stock-row"
              :class="{ 'near-target': stock.isNearBuyTarget }"
              @click="goToStock(stock.symbol)"
            >
              <td>
                <div class="d-flex align-items-center">
                  <div>
                    <div class="fw-bold">{{ stock.symbol }}</div>
                    <small class="text-muted">{{ truncate(stock.companyName, 25) }}</small>
                  </div>
                </div>
              </td>
              <td class="text-end">
                <div class="fw-medium">{{ formatPrice(stock.currentPrice) }}</div>
                <div v-if="stock.afterHours" class="after-hours-mini">
                  <small class="text-muted">{{ stock.afterHours.isPremarket ? 'PM' : 'AH' }}:</small>
                  <small :class="stock.afterHours.change >= 0 ? 'text-success' : 'text-danger'">
                    {{ formatPrice(stock.afterHours.price) }}
                  </small>
                </div>
              </td>
              <td class="text-end" :class="getPLClass(stock.dayChangePercent)">
                <div>{{ formatPL(stock.dayChange) }}</div>
                <small class="fw-medium">{{ formatPercent(stock.dayChangePercent) }}</small>
              </td>
              <td class="text-end">
                <span v-if="stock.buyTarget" class="text-success">
                  {{ formatPrice(stock.buyTarget) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <span
                  v-if="stock.distanceToBuy !== null"
                  class="badge"
                  :class="getDistanceClass(stock.distanceToBuy)"
                >
                  {{ formatPercent(stock.distanceToBuy) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-end">
                <span v-if="stock.sellTarget" class="text-danger">
                  {{ formatPrice(stock.sellTarget) }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-center">
                <span
                  v-for="tag in stock.tags.slice(0, 2)"
                  :key="tag.id"
                  class="badge badge-sm me-1"
                  :style="{ backgroundColor: tag.color || '#6c757d' }"
                >
                  {{ tag.name }}
                </span>
                <span v-if="stock.tags.length > 2" class="badge badge-sm bg-secondary">
                  +{{ stock.tags.length - 2 }}
                </span>
              </td>
              <td class="text-center">
                <span v-if="stock.notesCount" class="badge bg-light text-dark">
                  <i class="bi bi-journal-text me-1"></i>{{ stock.notesCount }}
                </span>
                <span v-else class="text-muted">-</span>
              </td>
              <td class="text-center" @click.stop>
                <div class="btn-group btn-group-sm">
                  <button
                    class="btn btn-outline-primary btn-sm"
                    @click="goToStock(stock.symbol)"
                    title="View details"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button
                    class="btn btn-outline-danger btn-sm"
                    @click="deleteStock(stock.id)"
                    title="Remove from watchlist"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Stock Modal -->
    <AddStockModal @stock-added="handleStockAdded" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { stocksApi } from '@/api'
import { useToastStore } from '@/stores/toast'
import { useConfirmStore } from '@/stores/confirm'
import AddStockModal from '@/components/AddStockModal.vue'

export default {
  name: 'Watchlist',
  components: {
    AddStockModal
  },
  setup() {
    const router = useRouter()
    const toast = useToastStore()
    const confirm = useConfirmStore()
    const loading = ref(false)
    const error = ref(null)
    const stocks = ref([])
    const sortKey = ref('distanceToBuy')
    const sortAsc = ref(true)
    const filter = ref('all')

    const fetchData = async () => {
      loading.value = true
      error.value = null

      try {
        const response = await stocksApi.getAll({ include_prices: true })
        const allStocks = response.data.stocks

        // Filter to only stocks WITHOUT holdings (watchlist)
        const watchlistStocks = allStocks.filter(s => !s.holding)

        // Transform data for table
        stocks.value = watchlistStocks.map(stock => {
          const currentPrice = stock.current_price || 0
          const dayChangePercent = stock.price_change_percent || 0
          const prevPrice = currentPrice / (1 + dayChangePercent / 100)
          const dayChange = currentPrice - prevPrice

          // Find closest buy target (below current price)
          const buyTargets = (stock.targets || [])
            .filter(t => t.target_type === 'Buy' && t.is_active)
            .sort((a, b) => b.target_price - a.target_price)
          const buyTarget = buyTargets[0]?.target_price || null

          // Find closest sell target (above current price)
          const sellTargets = (stock.targets || [])
            .filter(t => t.target_type === 'Sell' && t.is_active)
            .sort((a, b) => a.target_price - b.target_price)
          const sellTarget = sellTargets[0]?.target_price || null

          // Calculate distance to buy target
          const distanceToBuy = buyTarget && currentPrice
            ? ((currentPrice - buyTarget) / currentPrice) * 100
            : null

          const isNearBuyTarget = distanceToBuy !== null && distanceToBuy <= 5

          return {
            id: stock.id,
            symbol: stock.symbol,
            companyName: stock.company_name,
            currentPrice,
            dayChange,
            dayChangePercent,
            buyTarget,
            sellTarget,
            distanceToBuy,
            isNearBuyTarget,
            tags: stock.tags || [],
            notesCount: stock.notes_count || 0,
            afterHours: stock.after_hours ? {
              price: stock.after_hours.price,
              change: stock.after_hours.change,
              isPremarket: stock.after_hours.is_premarket
            } : null
          }
        })

      } catch (err) {
        console.error('Error fetching watchlist:', err)
        error.value = err.message || 'Failed to load watchlist'
      } finally {
        loading.value = false
      }
    }

    const nearBuyTargetCount = computed(() => {
      return stocks.value.filter(s => s.isNearBuyTarget).length
    })

    const gainersCount = computed(() => {
      return stocks.value.filter(s => s.dayChangePercent > 0).length
    })

    const losersCount = computed(() => {
      return stocks.value.filter(s => s.dayChangePercent < 0).length
    })

    const filteredStocks = computed(() => {
      let result = [...stocks.value]

      // Apply filter
      if (filter.value === 'nearBuy') {
        result = result.filter(s => s.isNearBuyTarget)
      } else if (filter.value === 'gainers') {
        result = result.filter(s => s.dayChangePercent > 0)
      } else if (filter.value === 'losers') {
        result = result.filter(s => s.dayChangePercent < 0)
      }

      // Apply sort
      result.sort((a, b) => {
        let aVal = a[sortKey.value]
        let bVal = b[sortKey.value]

        // Handle null values
        if (aVal === null) aVal = sortAsc.value ? Infinity : -Infinity
        if (bVal === null) bVal = sortAsc.value ? Infinity : -Infinity

        if (typeof aVal === 'string') {
          return sortAsc.value ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
        }

        return sortAsc.value ? aVal - bVal : bVal - aVal
      })

      return result
    })

    const sortIcon = computed(() => {
      return sortAsc.value ? 'bi bi-caret-up-fill' : 'bi bi-caret-down-fill'
    })

    const sortBy = (key) => {
      if (sortKey.value === key) {
        sortAsc.value = !sortAsc.value
      } else {
        sortKey.value = key
        sortAsc.value = key === 'symbol' ? true : false
      }
    }

    const goToStock = (symbol) => {
      router.push(`/stock/${symbol}`)
    }

    const deleteStock = async (stockId) => {
      const confirmed = await confirm.show({
        title: 'Remove from Watchlist?',
        message: 'This will remove the stock and all its targets and notes.',
        variant: 'danger',
        confirmText: 'Remove',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      try {
        await stocksApi.delete(stockId)
        toast.success('Stock removed from watchlist')
        fetchData()
      } catch (err) {
        toast.error('Failed to remove stock: ' + (err.message || 'Unknown error'))
      }
    }

    const handleStockAdded = () => {
      fetchData()
    }

    const truncate = (str, length) => {
      if (!str) return ''
      return str.length > length ? str.substring(0, length) + '...' : str
    }

    const formatPrice = (value) => {
      if (value === null || value === undefined) return '-'
      return '$' + value.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatPL = (value) => {
      if (value === null || value === undefined) return '-'
      const prefix = value >= 0 ? '+' : ''
      return prefix + '$' + Math.abs(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    const formatPercent = (value) => {
      if (value === null || value === undefined) return '-'
      const prefix = value >= 0 ? '+' : ''
      return prefix + value.toFixed(2) + '%'
    }

    const getPLClass = (value) => {
      if (value === null || value === undefined) return ''
      return value >= 0 ? 'text-success' : 'text-danger'
    }

    const getDistanceClass = (value) => {
      if (value === null) return 'bg-secondary'
      if (value <= 2) return 'bg-success text-white'
      if (value <= 5) return 'bg-success-subtle text-success'
      if (value <= 10) return 'bg-warning-subtle text-warning'
      return 'bg-light text-muted'
    }

    onMounted(() => {
      fetchData()
    })

    return {
      loading,
      error,
      stocks,
      sortKey,
      sortAsc,
      filter,
      filteredStocks,
      nearBuyTargetCount,
      gainersCount,
      losersCount,
      sortIcon,
      sortBy,
      goToStock,
      deleteStock,
      handleStockAdded,
      truncate,
      formatPrice,
      formatPL,
      formatPercent,
      getPLClass,
      getDistanceClass,
      fetchData
    }
  }
}
</script>

<style scoped>
.watchlist-view {
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

.nav-pills-sm .nav-link {
  padding: 0.4rem 0.8rem;
  font-size: 0.85rem;
}

.watchlist-table {
  font-size: 0.875rem;
}

.watchlist-table th {
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #6c757d;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.watchlist-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.watchlist-table th.sortable:hover {
  color: #212529;
  background-color: #e9ecef;
}

.watchlist-table th i {
  font-size: 0.65rem;
  margin-left: 4px;
}

.stock-row {
  cursor: pointer;
  transition: background-color 0.15s;
}

.stock-row:hover {
  background-color: #f8f9fa !important;
}

.stock-row.near-target {
  background-color: rgba(25, 135, 84, 0.05);
}

.stock-row.near-target:hover {
  background-color: rgba(25, 135, 84, 0.1) !important;
}

.after-hours-mini {
  font-size: 0.7rem;
  line-height: 1;
}

.badge-sm {
  font-size: 0.65rem;
  padding: 0.2em 0.45em;
  font-weight: 500;
}

/* Bootstrap 5.3+ subtle backgrounds fallback */
.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.15) !important;
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.15) !important;
}

.bg-warning-subtle {
  background-color: rgba(255, 193, 7, 0.2) !important;
}

/* Responsive */
@media (max-width: 992px) {
  .watchlist-table {
    font-size: 0.8rem;
  }

  .watchlist-table th {
    font-size: 0.7rem;
  }
}

/* Sticky header */
.table-responsive {
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

thead.sticky-top th {
  position: sticky;
  top: 0;
  z-index: 1;
  background-color: #f8f9fa;
}
</style>
