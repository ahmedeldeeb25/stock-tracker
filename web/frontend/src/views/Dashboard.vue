<template>
  <div>
    <!-- Header with Add Button -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="bi bi-speedometer2 me-2"></i>
        Stock Dashboard
      </h2>
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addStockModal">
        <i class="bi bi-plus-circle me-1"></i>
        Add Stock
      </button>
    </div>

    <!-- Filters -->
    <div class="row mb-4">
      <div class="col-md-8">
        <div class="input-group">
          <span class="input-group-text">
            <i class="bi bi-search"></i>
          </span>
          <input
            type="text"
            class="form-control"
            placeholder="Search stocks..."
            v-model="searchQuery"
            @input="handleSearch"
          >
        </div>
      </div>
      <div class="col-md-4">
        <button class="btn btn-outline-secondary w-100" @click="refreshPrices">
          <i class="bi bi-arrow-clockwise me-1"></i>
          Refresh Prices
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
        >
          {{ tag.name }} ({{ tag.count }})
        </button>
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

    <!-- Stocks Grid -->
    <div v-else-if="filteredStocks.length" class="row g-4">
      <div v-for="stock in filteredStocks" :key="stock.id" class="col-md-6 col-lg-4">
        <StockCard :stock="stock" @delete="handleDelete" />
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="text-center py-5">
      <i class="bi bi-inbox display-1 text-muted"></i>
      <p class="lead text-muted mt-3">No stocks found</p>
      <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#addStockModal">
        <i class="bi bi-plus-circle me-1"></i>
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
import StockCard from '@/components/StockCard.vue'
import AddStockModal from '@/components/AddStockModal.vue'

export default {
  name: 'Dashboard',
  components: {
    StockCard,
    AddStockModal
  },
  setup() {
    const stocksStore = useStocksStore()
    const searchQuery = ref('')
    const selectedTag = ref(null)

    const loading = computed(() => stocksStore.loading)
    const error = computed(() => stocksStore.error)
    const availableTags = computed(() => stocksStore.availableTags)
    const filteredStocks = computed(() => stocksStore.filteredStocks)

    onMounted(() => {
      stocksStore.fetchStocks(true)
    })

    const handleSearch = () => {
      stocksStore.setFilter('search', searchQuery.value)
    }

    const filterByTag = (tag) => {
      selectedTag.value = tag
      stocksStore.setFilter('tag', tag)
    }

    const refreshPrices = async () => {
      await stocksStore.fetchStocks(true)
    }

    const handleDelete = async (stockId) => {
      if (confirm('Are you sure you want to delete this stock?')) {
        try {
          await stocksStore.deleteStock(stockId)
        } catch (error) {
          alert('Failed to delete stock: ' + error.message)
        }
      }
    }

    const handleStockAdded = () => {
      stocksStore.fetchStocks(true)
    }

    return {
      loading,
      error,
      availableTags,
      filteredStocks,
      searchQuery,
      selectedTag,
      handleSearch,
      filterByTag,
      refreshPrices,
      handleDelete,
      handleStockAdded
    }
  }
}
</script>
