<template>
  <div class="modal fade" id="addTargetModal" tabindex="-1" aria-labelledby="addTargetModalLabel" aria-modal="true" role="dialog">
    <div class="modal-dialog modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="addTargetModalLabel">Add Price Target</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Target Type -->
            <div class="mb-3">
              <label for="targetType" class="form-label">
                Target Type <span class="text-danger">*</span>
              </label>
              <select
                id="targetType"
                class="form-select"
                v-model="formData.target_type"
                required
                aria-required="true"
              >
                <option value="Buy">Buy</option>
                <option value="Sell">Sell</option>
                <option value="DCA">DCA</option>
                <option value="Trim">Trim</option>
              </select>
            </div>

            <!-- Target Price -->
            <div class="mb-3">
              <label for="targetPrice" class="form-label">
                Target Price <span class="text-danger">*</span>
              </label>
              <input
                id="targetPrice"
                type="number"
                step="0.01"
                class="form-control"
                v-model.number="formData.target_price"
                placeholder="0.00"
                required
                aria-required="true"
              >
            </div>

            <!-- Trim Percentage (only for Trim type) -->
            <div class="mb-3" v-if="formData.target_type === 'Trim'">
              <label for="trimPercentage" class="form-label">Trim Percentage</label>
              <input
                id="trimPercentage"
                type="number"
                step="1"
                min="1"
                max="100"
                class="form-control"
                v-model.number="formData.trim_percentage"
                placeholder="25"
                aria-describedby="trimPercentageHelp"
              >
              <small id="trimPercentageHelp" class="form-text text-muted">
                Percentage of position to trim (1-100%)
              </small>
            </div>

            <!-- Alert Note -->
            <div class="mb-3">
              <label for="alertNote" class="form-label">Alert Note</label>
              <input
                id="alertNote"
                type="text"
                class="form-control"
                v-model="formData.alert_note"
                placeholder="Optional note for this target..."
              >
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="alert alert-danger" role="alert">
              {{ errorMessage }}
            </div>

            <!-- Submit Button -->
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
                {{ submitting ? 'Adding...' : 'Add Target' }}
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
import { stocksApi } from '@/api'
import { useToastStore } from '@/stores/toast'

export default {
  name: 'AddTargetModal',
  props: {
    stockId: {
      type: Number,
      required: true
    }
  },
  emits: ['target-added'],
  setup(props, { emit }) {
    const toast = useToastStore()
    const formData = ref({
      target_type: 'Buy',
      target_price: null,
      trim_percentage: null,
      alert_note: ''
    })

    const submitting = ref(false)
    const errorMessage = ref('')

    const resetForm = () => {
      formData.value = {
        target_type: 'Buy',
        target_price: null,
        trim_percentage: null,
        alert_note: ''
      }
      errorMessage.value = ''
    }

    const handleSubmit = async () => {
      submitting.value = true
      errorMessage.value = ''

      try {
        await stocksApi.addTarget(props.stockId, formData.value)

        // Close modal
        const modal = document.getElementById('addTargetModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        resetForm()
        emit('target-added')
      } catch (error) {
        errorMessage.value = error.response?.data?.error || 'Failed to add target'
        toast.error('Failed to add target: ' + (error.response?.data?.error || error.message))
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      submitting,
      errorMessage,
      handleSubmit
    }
  }
}
</script>
