<template>
  <div class="modal fade" id="addStockModal" tabindex="-1">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add New Stock</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Symbol -->
            <div class="mb-3">
              <label class="form-label">Symbol *</label>
              <input
                type="text"
                class="form-control"
                v-model="formData.symbol"
                placeholder="AAPL"
                required
                style="text-transform: uppercase"
              >
            </div>

            <!-- Company Name -->
            <div class="mb-3">
              <label class="form-label">Company Name (Optional)</label>
              <input
                type="text"
                class="form-control"
                v-model="formData.company_name"
                placeholder="Will be fetched automatically if left empty"
              >
              <small class="form-text text-muted">
                <i class="bi bi-info-circle me-1"></i>
                Leave empty to auto-fetch from yfinance
              </small>
            </div>

            <!-- Tags -->
            <div class="mb-3">
              <label class="form-label">Tags</label>
              <div class="input-group mb-2">
                <input
                  type="text"
                  class="form-control"
                  v-model="newTag"
                  placeholder="Add tag..."
                  @keyup.enter="addTag"
                >
                <button type="button" class="btn btn-outline-secondary" @click="addTag">
                  <i class="bi bi-plus"></i>
                </button>
              </div>
              <div class="d-flex flex-wrap gap-2">
                <span
                  v-for="(tag, index) in formData.tags"
                  :key="index"
                  class="badge bg-secondary"
                >
                  {{ tag }}
                  <i class="bi bi-x ms-1" @click="removeTag(index)" style="cursor: pointer"></i>
                </span>
              </div>
            </div>

            <!-- Targets -->
            <div class="mb-3">
              <label class="form-label">Price Targets *</label>
              <div
                v-for="(target, index) in formData.targets"
                :key="index"
                class="card mb-2"
              >
                <div class="card-body">
                  <div class="row">
                    <div class="col-md-3">
                      <select class="form-select" v-model="target.target_type" required>
                        <option value="Buy">Buy</option>
                        <option value="Sell">Sell</option>
                        <option value="DCA">DCA</option>
                        <option value="Trim">Trim</option>
                      </select>
                    </div>
                    <div class="col-md-3">
                      <input
                        type="number"
                        step="0.01"
                        class="form-control"
                        v-model.number="target.target_price"
                        placeholder="Price"
                        required
                      >
                    </div>
                    <div class="col-md-2" v-if="target.target_type === 'Trim'">
                      <input
                        type="number"
                        step="1"
                        class="form-control"
                        v-model.number="target.trim_percentage"
                        placeholder="%"
                      >
                    </div>
                    <div class="col">
                      <input
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
                        v-if="formData.targets.length > 1"
                      >
                        <i class="bi bi-trash"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              <button type="button" class="btn btn-sm btn-outline-primary" @click="addTarget">
                <i class="bi bi-plus-circle me-1"></i>
                Add Target
              </button>
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <!-- Submit Button -->
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
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
import { ref } from 'vue'
import { useStocksStore } from '@/stores/stocks'

export default {
  name: 'AddStockModal',
  emits: ['stock-added'],
  setup(props, { emit }) {
    const stocksStore = useStocksStore()

    const formData = ref({
      symbol: '',
      company_name: '',
      tags: [],
      targets: [
        {
          target_type: 'Buy',
          target_price: null,
          trim_percentage: null,
          alert_note: ''
        }
      ]
    })

    const newTag = ref('')
    const submitting = ref(false)
    const errorMessage = ref('')

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
        targets: [
          {
            target_type: 'Buy',
            target_price: null,
            trim_percentage: null,
            alert_note: ''
          }
        ]
      }
      errorMessage.value = ''
    }

    const handleSubmit = async () => {
      submitting.value = true
      errorMessage.value = ''

      try {
        // Validate targets
        const validTargets = formData.value.targets.filter(t => t.target_price)

        if (validTargets.length === 0) {
          errorMessage.value = 'At least one target with a price is required'
          submitting.value = false
          return
        }

        await stocksStore.createStock({
          ...formData.value,
          symbol: formData.value.symbol.toUpperCase(),
          targets: validTargets
        })

        // Close modal
        const modal = document.getElementById('addStockModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        resetForm()
        emit('stock-added')
      } catch (error) {
        errorMessage.value = error.message || 'Failed to add stock'
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      newTag,
      submitting,
      errorMessage,
      addTag,
      removeTag,
      addTarget,
      removeTarget,
      handleSubmit
    }
  }
}
</script>
