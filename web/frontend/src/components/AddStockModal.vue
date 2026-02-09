<template>
  <div class="modal fade" id="addStockModal" tabindex="-1" aria-labelledby="addStockModalLabel" aria-modal="true" role="dialog">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addStockModalLabel">Add New Stock</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Symbol with Autocomplete -->
            <div class="mb-3 position-relative">
              <label for="stockSymbol" class="form-label">
                Symbol <span class="text-danger">*</span>
              </label>
              <div class="position-relative">
                <input
                  id="stockSymbol"
                  type="text"
                  class="form-control"
                  :class="{
                    'is-invalid': symbolError,
                    'is-valid': symbolValidated && !symbolError
                  }"
                  v-model="formData.symbol"
                  @input="handleSymbolInput"
                  @focus="showSuggestions = true"
                  @blur="hideSuggestionsDelayed"
                  @keydown.down.prevent="navigateSuggestion(1)"
                  @keydown.up.prevent="navigateSuggestion(-1)"
                  @keydown.enter.prevent="selectHighlightedSuggestion"
                  @keydown.escape="showSuggestions = false"
                  placeholder="Search for a stock..."
                  required
                  aria-required="true"
                  autocomplete="off"
                  style="text-transform: uppercase"
                >
                <div v-if="searchingSymbol" class="position-absolute" style="right: 10px; top: 50%; transform: translateY(-50%);">
                  <span class="spinner-border spinner-border-sm text-muted"></span>
                </div>
              </div>

              <!-- Suggestions Dropdown -->
              <div
                v-if="showSuggestions && suggestions.length > 0"
                class="suggestions-dropdown"
              >
                <div
                  v-for="(suggestion, index) in suggestions"
                  :key="suggestion.symbol"
                  class="suggestion-item"
                  :class="{ 'highlighted': index === highlightedIndex }"
                  @mousedown.prevent="selectSuggestion(suggestion)"
                  @mouseenter="highlightedIndex = index"
                >
                  <div class="d-flex justify-content-between align-items-center">
                    <div>
                      <strong>{{ suggestion.symbol }}</strong>
                      <span class="text-muted ms-2">{{ suggestion.name }}</span>
                    </div>
                    <small class="text-muted">{{ suggestion.exchange }}</small>
                  </div>
                </div>
              </div>

              <!-- Validation Feedback -->
              <div v-if="symbolError" class="invalid-feedback d-block">
                {{ symbolError }}
              </div>
              <div v-else-if="symbolValidated && validatedSymbolInfo" class="valid-feedback d-block">
                <i class="bi bi-check-circle me-1"></i>
                {{ validatedSymbolInfo.name || formData.symbol.toUpperCase() }}
              </div>
            </div>

            <!-- Company Name -->
            <div class="mb-3">
              <label for="companyName" class="form-label">Company Name (Optional)</label>
              <input
                id="companyName"
                type="text"
                class="form-control"
                v-model="formData.company_name"
                placeholder="Will be fetched automatically if left empty"
                aria-describedby="companyNameHelp"
              >
              <small id="companyNameHelp" class="form-text text-muted">
                <i class="bi bi-info-circle me-1" aria-hidden="true"></i>
                Leave empty to auto-fetch from yfinance
              </small>
            </div>

            <!-- Tags -->
            <div class="mb-3">
              <label for="stockTags" class="form-label">Tags</label>
              <div class="input-group mb-2">
                <input
                  id="stockTags"
                  type="text"
                  class="form-control"
                  v-model="newTag"
                  placeholder="Add tag..."
                  @keyup.enter="addTag"
                  aria-label="New tag name"
                >
                <button
                  type="button"
                  class="btn btn-outline-secondary"
                  @click="addTag"
                  aria-label="Add tag"
                >
                  <i class="bi bi-plus" aria-hidden="true"></i>
                </button>
              </div>
              <div class="d-flex flex-wrap gap-2" role="list" aria-label="Selected tags">
                <span
                  v-for="(tag, index) in formData.tags"
                  :key="index"
                  class="badge bg-secondary"
                  role="listitem"
                >
                  {{ tag }}
                  <button
                    type="button"
                    @click="removeTag(index)"
                    class="btn-close btn-close-white ms-1"
                    :aria-label="`Remove ${tag} tag`"
                    style="font-size: 0.6rem; vertical-align: middle;"
                  ></button>
                </span>
              </div>
            </div>

            <!-- Targets -->
            <div class="mb-3">
              <label class="form-label">
                Price Targets <span class="text-muted small">(optional)</span>
              </label>
              <div
                v-for="(target, index) in formData.targets"
                :key="index"
                class="card mb-2"
              >
                <div class="card-body">
                  <div class="row g-2">
                    <div class="col-12 col-md-3">
                      <label :for="`targetType${index}`" class="visually-hidden">Target type</label>
                      <select
                        :id="`targetType${index}`"
                        class="form-select"
                        v-model="target.target_type"
                      >
                        <option value="Buy">Buy</option>
                        <option value="Sell">Sell</option>
                        <option value="DCA">DCA</option>
                        <option value="Trim">Trim</option>
                      </select>
                    </div>
                    <div class="col-12 col-md-3">
                      <label :for="`targetPrice${index}`" class="visually-hidden">Target price</label>
                      <input
                        :id="`targetPrice${index}`"
                        type="number"
                        step="0.01"
                        class="form-control"
                        v-model.number="target.target_price"
                        placeholder="Price"
                      >
                    </div>
                    <div class="col-12 col-md-2" v-if="target.target_type === 'Trim'">
                      <label :for="`trimPercentage${index}`" class="visually-hidden">Trim percentage</label>
                      <input
                        :id="`trimPercentage${index}`"
                        type="number"
                        step="1"
                        class="form-control"
                        v-model.number="target.trim_percentage"
                        placeholder="%"
                      >
                    </div>
                    <div class="col">
                      <label :for="`alertNote${index}`" class="visually-hidden">Alert note</label>
                      <input
                        :id="`alertNote${index}`"
                        type="text"
                        class="form-control"
                        v-model="target.alert_note"
                        placeholder="Alert note..."
                      >
                    </div>
                    <div class="col-auto">
                      <button
                        type="button"
                        class="btn btn-outline-danger"
                        @click="removeTarget(index)"
                        :aria-label="`Remove target ${index + 1}`"
                      >
                        <i class="bi bi-trash" aria-hidden="true"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="addTarget">
                <i class="bi bi-plus-circle me-1" aria-hidden="true"></i>
                Add Target
              </button>
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="alert alert-danger" role="alert">
              {{ errorMessage }}
            </div>

            <!-- Submit Button -->
            <div class="d-grid">
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="submitting || symbolError || !formData.symbol.trim()"
              >
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                {{ submitting ? 'Adding...' : 'Add Stock' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useStocksStore } from '@/stores/stocks'
import { useToastStore } from '@/stores/toast'
import { stocksApi } from '@/api'

export default {
  name: 'AddStockModal',
  emits: ['stock-added'],
  setup(props, { emit }) {
    const router = useRouter()
    const stocksStore = useStocksStore()
    const toast = useToastStore()

    const formData = ref({
      symbol: '',
      company_name: '',
      tags: [],
      targets: []
    })

    const newTag = ref('')
    const submitting = ref(false)
    const errorMessage = ref('')

    // Autocomplete state
    const suggestions = ref([])
    const showSuggestions = ref(false)
    const highlightedIndex = ref(-1)
    const searchingSymbol = ref(false)
    const symbolError = ref('')
    const symbolValidated = ref(false)
    const validatedSymbolInfo = ref(null)
    let searchTimeout = null
    let validateTimeout = null
    let lastAutoFilledSymbol = null

    const handleSymbolInput = () => {
      const symbol = formData.value.symbol.trim().toUpperCase()

      // Reset validation state
      symbolError.value = ''
      symbolValidated.value = false
      validatedSymbolInfo.value = null
      highlightedIndex.value = -1

      // Clear company name if symbol changed from what was auto-filled
      if (lastAutoFilledSymbol && symbol !== lastAutoFilledSymbol) {
        formData.value.company_name = ''
        lastAutoFilledSymbol = null
      }

      // Clear previous timeouts
      if (searchTimeout) clearTimeout(searchTimeout)
      if (validateTimeout) clearTimeout(validateTimeout)

      if (!symbol || symbol.length < 1) {
        suggestions.value = []
        formData.value.company_name = ''
        return
      }

      // Debounce search
      searchingSymbol.value = true
      searchTimeout = setTimeout(async () => {
        try {
          const response = await stocksApi.search(symbol, 8)
          suggestions.value = response.data.results || []
        } catch (error) {
          console.error('Search error:', error)
          suggestions.value = []
        } finally {
          searchingSymbol.value = false
        }
      }, 300)

      // Debounce validation (slightly longer delay)
      validateTimeout = setTimeout(async () => {
        await validateSymbol(symbol)
      }, 500)
    }

    const validateSymbol = async (symbol) => {
      if (!symbol) return

      try {
        const response = await stocksApi.validate(symbol)
        const data = response.data

        if (data.exists_in_db) {
          symbolError.value = data.message || `${symbol} is already in your watchlist`
          symbolValidated.value = false
        } else if (data.valid) {
          symbolValidated.value = true
          validatedSymbolInfo.value = data
          // Auto-fill company name if empty
          if (!formData.value.company_name && data.name) {
            formData.value.company_name = data.name
            lastAutoFilledSymbol = symbol
          }
        }
      } catch (error) {
        if (error.response?.status === 404) {
          symbolError.value = `Symbol '${symbol}' not found`
        }
        symbolValidated.value = false
      }
    }

    const selectSuggestion = (suggestion) => {
      formData.value.symbol = suggestion.symbol
      formData.value.company_name = suggestion.name
      lastAutoFilledSymbol = suggestion.symbol
      suggestions.value = []
      showSuggestions.value = false
      highlightedIndex.value = -1

      // Validate the selected symbol
      validateSymbol(suggestion.symbol)
    }

    const navigateSuggestion = (direction) => {
      if (!showSuggestions.value || suggestions.value.length === 0) return

      highlightedIndex.value += direction
      if (highlightedIndex.value < 0) {
        highlightedIndex.value = suggestions.value.length - 1
      } else if (highlightedIndex.value >= suggestions.value.length) {
        highlightedIndex.value = 0
      }
    }

    const selectHighlightedSuggestion = () => {
      if (highlightedIndex.value >= 0 && highlightedIndex.value < suggestions.value.length) {
        selectSuggestion(suggestions.value[highlightedIndex.value])
      }
    }

    const hideSuggestionsDelayed = () => {
      // Delay to allow click on suggestion
      setTimeout(() => {
        showSuggestions.value = false
      }, 200)
    }

    const addTag = () => {
      if (newTag.value.trim() && !formData.value.tags.includes(newTag.value.trim())) {
        formData.value.tags.push(newTag.value.trim().toLowerCase())
        newTag.value = ''
      }
    }

    const removeTag = (index) => {
      formData.value.tags.splice(index, 1)
    }

    const addTarget = () => {
      formData.value.targets.push({
        target_type: 'Buy',
        target_price: null,
        trim_percentage: null,
        alert_note: ''
      })
    }

    const removeTarget = (index) => {
      formData.value.targets.splice(index, 1)
    }

    const resetForm = () => {
      formData.value = {
        symbol: '',
        company_name: '',
        tags: [],
        targets: []
      }
      errorMessage.value = ''
      symbolError.value = ''
      symbolValidated.value = false
      validatedSymbolInfo.value = null
      suggestions.value = []
      showSuggestions.value = false
      highlightedIndex.value = -1
      lastAutoFilledSymbol = null
    }

    const handleSubmit = async () => {
      // Check for validation errors
      if (symbolError.value) {
        toast.error(symbolError.value)
        return
      }

      if (!formData.value.symbol.trim()) {
        errorMessage.value = 'Symbol is required'
        return
      }

      submitting.value = true
      errorMessage.value = ''

      try {
        // Filter to only include targets with prices
        const validTargets = formData.value.targets.filter(t => t.target_price)

        await stocksStore.createStock({
          ...formData.value,
          symbol: formData.value.symbol.toUpperCase(),
          targets: validTargets
        })

        // Save symbol before resetting form
        const createdSymbol = formData.value.symbol.toUpperCase()

        // Close modal
        const modal = document.getElementById('addStockModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        resetForm()
        emit('stock-added')

        // Redirect to stock details page
        router.push(`/stock/${createdSymbol}`)
      } catch (error) {
        errorMessage.value = error.message || 'Failed to add stock'
        toast.error('Failed to add stock: ' + (error.message || 'Unknown error'))
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      newTag,
      submitting,
      errorMessage,
      suggestions,
      showSuggestions,
      highlightedIndex,
      searchingSymbol,
      symbolError,
      symbolValidated,
      validatedSymbolInfo,
      handleSymbolInput,
      selectSuggestion,
      navigateSuggestion,
      selectHighlightedSuggestion,
      hideSuggestionsDelayed,
      addTag,
      removeTag,
      addTarget,
      removeTarget,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 1050;
}

.suggestion-item {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f0f0f0;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background-color: #f8f9fa;
}

.suggestion-item.highlighted {
  background-color: #e9ecef;
}
</style>
