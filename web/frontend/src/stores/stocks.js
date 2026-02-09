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

    // Refresh stock data without loading state (no skeleton, chart stays)
    async refreshStockDetails(symbol) {
      try {
        const response = await stocksApi.getBySymbol(symbol)
        // Preserve the loading state, just update the data
        this.currentStock = response.data
        return response.data
      } catch (error) {
        console.error('Error refreshing stock details:', error)
        throw error
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
    },

    // Partial update methods to avoid full page reload
    updateCurrentStockTags(tags) {
      if (this.currentStock) {
        this.currentStock.tags = tags
      }
    },

    updateCurrentStockTimeframes(timeframes) {
      if (this.currentStock) {
        this.currentStock.timeframes = timeframes
      }
    },

    updateCurrentStockTargets(targets) {
      if (this.currentStock) {
        this.currentStock.targets = targets
      }
    },

    addTargetToCurrentStock(target) {
      if (this.currentStock) {
        this.currentStock.targets = [...(this.currentStock.targets || []), target]
      }
    },

    updateTargetInCurrentStock(updatedTarget) {
      if (this.currentStock && this.currentStock.targets) {
        const index = this.currentStock.targets.findIndex(t => t.id === updatedTarget.id)
        if (index !== -1) {
          this.currentStock.targets[index] = updatedTarget
        }
      }
    },

    removeTargetFromCurrentStock(targetId) {
      if (this.currentStock && this.currentStock.targets) {
        this.currentStock.targets = this.currentStock.targets.filter(t => t.id !== targetId)
      }
    },

    updateCurrentStockNotes(notes) {
      if (this.currentStock) {
        this.currentStock.notes = notes
      }
    },

    addNoteToCurrentStock(note) {
      if (this.currentStock) {
        this.currentStock.notes = [note, ...(this.currentStock.notes || [])]
      }
    },

    updateNoteInCurrentStock(updatedNote) {
      if (this.currentStock && this.currentStock.notes) {
        const index = this.currentStock.notes.findIndex(n => n.id === updatedNote.id)
        if (index !== -1) {
          this.currentStock.notes[index] = updatedNote
        }
      }
    },

    removeNoteFromCurrentStock(noteId) {
      if (this.currentStock && this.currentStock.notes) {
        this.currentStock.notes = this.currentStock.notes.filter(n => n.id !== noteId)
      }
    },

    updateCurrentStockHolding(holding) {
      if (this.currentStock) {
        this.currentStock.holding = holding
      }
    },

    removeCurrentStockHolding() {
      if (this.currentStock) {
        this.currentStock.holding = null
      }
    }
  }
})
