<template>
  <div class="modal fade" id="addTargetModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Add Price Target</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Target Type -->
            <div class="mb-3">
              <label class="form-label">Target Type *</label>
              <select class="form-select" v-model="formData.target_type" required>
                <option value="Buy">Buy</option>
                <option value="Sell">Sell</option>
                <option value="DCA">DCA</option>
                <option value="Trim">Trim</option>
              </select>
            </div>

            <!-- Target Price -->
            <div class="mb-3">
              <label class="form-label">Target Price *</label>
              <input
                type="number"
                step="0.01"
                class="form-control"
                v-model.number="formData.target_price"
                placeholder="0.00"
                required
              >
            </div>

            <!-- Trim Percentage (only for Trim type) -->
            <div class="mb-3" v-if="formData.target_type === 'Trim'">
              <label class="form-label">Trim Percentage</label>
              <input
                type="number"
                step="1"
                min="1"
                max="100"
                class="form-control"
                v-model.number="formData.trim_percentage"
                placeholder="25"
              >
            </div>

            <!-- Alert Note -->
            <div class="mb-3">
              <label class="form-label">Alert Note</label>
              <input
                type="text"
                class="form-control"
                v-model="formData.alert_note"
                placeholder="Optional note for this target..."
              >
            </div>

            <!-- Error Message -->
            <div v-if="errorMessage" class="alert alert-danger">
              {{ errorMessage }}
            </div>

            <!-- Submit Button -->
            <div class="d-grid">
              <button type="submit" class="btn btn-primary" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
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
