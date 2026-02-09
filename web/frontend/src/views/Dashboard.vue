<template>
  <div>
    <!-- Header with Add Button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h1 class="h2 mb-0">
        <i class="bi bi-speedometer2 me-2" aria-hidden="true"></i>
        Stock Dashboard
      </h1>
      <button
        class="btn btn-primary"
        data-bs-toggle="modal"
        data-bs-target="#addStockModal"
        aria-label="Add new stock to portfolio"
      >
        <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>
        Add Stock
      </button>
    </div>

    <!-- Market Overview Section -->
    <MarketOverview />

    <!-- Filters -->
    <div class="row mb-4 g-3">
      <div class="col-md-6">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search" aria-hidden="true"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Search stocks..."
            v-model="searchQuery"
            @input="handleSearch"
            aria-label="Search stocks by symbol or company name"
            ref="searchInputRef"
            title="Press / to focus (keyboard shortcut)"
          >
        </div>
      </div>
      <div class="col-md-3">
        <button
          class="btn btn-outline-secondary w-100"
          @click="refreshPrices"
          aria-label="Refresh stock prices"
        >
          <i class="bi bi-arrow-clockwise me-1" aria-hidden="true"></i>
          Refresh Prices
        </button>
      </div>
      <div class="col-md-3">
        <button
          class="btn btn-outline-info w-100"
          @click="updateExchanges"
          :disabled="updatingExchanges"
          aria-label="Update exchange information for all stocks"
          title="Fetches correct exchange (NYSE, NASDAQ, etc.) for stocks missing this data"
        >
          <span v-if="updatingExchanges">
            <span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span>
            Updating...
          </span>
          <span v-else>
            <i class="bi bi-building me-1" aria-hidden="true"></i>
            Update Exchanges
          </span>
        </button>
      </div>
    </div>

    <!-- Tag Filters -->
    <div class="mb-4" v-if="availableTags.length">
      <div class="d-flex flex-wrap gap-2">
        <button
          class="btn btn-sm"
          :class="selectedTag === null ? 'btn-primary' : 'btn-outline-primary'"
          @click="filterByTag(null)"
          aria-pressed="selectedTag === null"
        >
          All Stocks
        </button>
        <button
          v-for="tag in availableTags"
          :key="tag.id"
          class="btn btn-sm"
          :class="selectedTag === tag.name ? 'btn-primary' : 'btn-outline-secondary'"
          :style="selectedTag === tag.name ? { backgroundColor: tag.color, borderColor: tag.color } : {}"
          @click="filterByTag(tag.name)"
          :aria-pressed="selectedTag === tag.name"
          :aria-label="`Filter by ${tag.name} tag, ${tag.count} stocks`"
        >
          {{ tag.name }} ({{ tag.count }})
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" role="status" aria-live="polite">
      <div class="row g-3">
        <div v-for="n in 8" :key="`skeleton-${n}`" class="col-12 col-sm-6 col-md-4 col-lg-3 col-xl-3">
          <StockCardSkeleton />
        </div>
      </div>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
      {{ error }}
    </div>

    <!-- Stocks Grid -->
    <div v-else-if="filteredStocks.length" class="row g-3">
      <div v-for="stock in filteredStocks" :key="stock.id" class="col-12 col-sm-6 col-md-4 col-lg-3 col-xl-3">
        <StockCard :stock="stock" @delete="handleDelete" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-inbox display-1 text-muted" aria-hidden="true"></i>
      <p class="lead text-muted mt-3">No stocks found</p>
      <button
        class="btn btn-primary"
        data-bs-toggle="modal"
        data-bs-target="#addStockModal"
        aria-label="Add your first stock to portfolio"
      >
        <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>
        Add Your First Stock
      </button>
    </div>

    <!-- Add Stock Modal -->
    <AddStockModal @stock-added="handleStockAdded" />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStocksStore } from '@/stores/stocks'
import { useToastStore } from '@/stores/toast'
import { useConfirmStore } from '@/stores/confirm'
import { useKeyboardShortcuts, CommonShortcuts } from '@/composables/useKeyboardShortcuts'
import StockCard from '@/components/StockCard.vue'
import StockCardSkeleton from '@/components/StockCardSkeleton.vue'
import AddStockModal from '@/components/AddStockModal.vue'
import MarketOverview from '@/components/MarketOverview.vue'

export default {
  name: 'Dashboard',
  components: {
    StockCard,
    StockCardSkeleton,
    AddStockModal,
    MarketOverview
  },
  setup() {
    const stocksStore = useStocksStore()
    const toast = useToastStore()
    const confirm = useConfirmStore()
    const { registerShortcut } = useKeyboardShortcuts()
    const searchQuery = ref('')
    const selectedTag = ref(null)
    const searchInputRef = ref(null)
    const updatingExchanges = ref(false)

    const loading = computed(() => stocksStore.loading)
    const error = computed(() => stocksStore.error)
    const availableTags = computed(() => stocksStore.availableTags)
    const filteredStocks = computed(() => stocksStore.filteredStocks)

    onMounted(() => {
      stocksStore.fetchStocks(true)

      // Register keyboard shortcuts
      // Search focus with /
      registerShortcut({
        id: 'search-focus',
        ...CommonShortcuts.SEARCH,
        handler: () => {
          if (searchInputRef.value) {
            searchInputRef.value.focus()
          }
        }
      })

      // Search focus with Ctrl+K
      registerShortcut({
        id: 'search-focus-alt',
        ...CommonShortcuts.SEARCH_ALT,
        handler: () => {
          if (searchInputRef.value) {
            searchInputRef.value.focus()
          }
        }
      })
    })

    const handleSearch = () => {
      stocksStore.setFilter('search', searchQuery.value)
    }

    const filterByTag = (tag) => {
      selectedTag.value = tag
      stocksStore.setFilter('tag', tag)
    }

    const refreshPrices = async () => {
      try {
        await stocksStore.fetchStocks(true)
        toast.success('Stock prices refreshed')
      } catch (error) {
        toast.error('Failed to refresh prices')
      }
    }

    const updateExchanges = async () => {
      updatingExchanges.value = true
      try {
        const { stocksApi } = await import('@/api')
        const response = await stocksApi.batchUpdateExchanges()
        const data = response.data

        if (data.updated > 0) {
          toast.success(
            `Successfully updated ${data.updated} stock(s). ` +
            `Skipped: ${data.skipped}, Failed: ${data.failed}`
          )
          // Refresh the stock list to show updated exchange information
          await stocksStore.fetchStocks(true)
        } else if (data.skipped > 0) {
          toast.info('All stocks already have exchange information')
        } else {
          toast.warning('No stocks were updated')
        }
      } catch (error) {
        console.error('Exchange update error:', error)
        toast.error('Failed to update exchanges: ' + (error.response?.data?.error || error.message))
      } finally {
        updatingExchanges.value = false
      }
    }

    const handleDelete = async (stockId) => {
      const isConfirmed = await confirm.show({
        title: 'Delete Stock?',
        message: 'Are you sure you want to delete this stock? This action cannot be undone.',
        variant: 'danger',
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })

      if (isConfirmed) {
        try {
          await stocksStore.deleteStock(stockId)
          toast.success('Stock deleted successfully')
        } catch (error) {
          toast.error('Failed to delete stock: ' + error.message)
        }
      }
    }

    const handleStockAdded = () => {
      stocksStore.fetchStocks(true)
      toast.success('Stock added successfully')
    }

    return {
      loading,
      error,
      availableTags,
      filteredStocks,
      searchQuery,
      selectedTag,
      searchInputRef,
      updatingExchanges,
      handleSearch,
      filterByTag,
      refreshPrices,
      updateExchanges,
      handleDelete,
      handleStockAdded
    }
  }
}
</script>
