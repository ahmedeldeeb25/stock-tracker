import { defineStore } from 'pinia'
import { stocksApi } from '@/api'

export const useStocksStore = defineStore('stocks', {
  state: () => ({
    stocks: [],
    currentStock: null,
    availableTags: [],
    loading: false,
    error: null,
    filters: {
      tag: null,
      search: ''
    }
  }),

  getters: {
    getStockBySymbol: (state) => (symbol) => {
      return state.stocks.find(s => s.symbol === symbol)
    },

    filteredStocks: (state) => {
      let filtered = state.stocks

      if (state.filters.tag) {
        filtered = filtered.filter(stock =>
          stock.tags.some(tag => tag.name === state.filters.tag)
        )
      }

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(stock =>
          stock.symbol.toLowerCase().includes(search) ||
          (stock.company_name && stock.company_name.toLowerCase().includes(search))
        )
      }

      return filtered
    }
  },

  actions: {
    async fetchStocks(includePrices = false) {
      this.loading = true
      this.error = null

      try {
        const response = await stocksApi.getAll({ include_prices: includePrices })
        this.stocks = response.data.stocks
        this.availableTags = response.data.available_tags
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error fetching stocks:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchStockDetails(symbol) {
      this.loading = true
      this.error = null

      try {
        const response = await stocksApi.getBySymbol(symbol)
        this.currentStock = response.data
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error fetching stock details:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async createStock(stockData) {
      this.loading = true
      this.error = null

      try {
        const response = await stocksApi.create(stockData)
        await this.fetchStocks()
        return response.data
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error creating stock:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteStock(stockId) {
      this.loading = true
      this.error = null

      try {
        await stocksApi.delete(stockId)
        this.stocks = this.stocks.filter(s => s.id !== stockId)
      } catch (error) {
        this.error = error.response?.data?.error || error.message
        console.error('Error deleting stock:', error)
        throw error
      } finally {
        this.loading = false
      }
    },

    setFilter(filterType, value) {
      this.filters[filterType] = value
    },

    clearFilters() {
      this.filters.tag = null
      this.filters.search = ''
    }
  }
})
