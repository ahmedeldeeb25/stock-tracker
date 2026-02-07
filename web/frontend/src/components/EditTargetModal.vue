<template>
  <div class="modal fade" id="editTargetModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Edit Price Target</h5>
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
            <div class="d-flex gap-2">
              <button type="submit" class="btn btn-primary flex-grow-1" :disabled="submitting">
                <span v-if="submitting" class="spinner-border spinner-border-sm me-2"></span>
                {{ submitting ? 'Updating...' : 'Update Target' }}
              </button>
              <button
                type="button"
                class="btn btn-outline-danger"
                @click="handleDelete"
                :disabled="submitting || deleting"
              >
                <span v-if="deleting" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-trash"></i>
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
import { targetsApi } from '@/api'

export default {
  name: 'EditTargetModal',
  props: {
    target: {
      type: Object,
      default: null
    }
  },
  emits: ['target-updated', 'target-deleted'],
  setup(props, { emit }) {
    const formData = ref({
      target_type: 'Buy',
      target_price: null,
      trim_percentage: null,
      alert_note: ''
    })

    const submitting = ref(false)
    const deleting = ref(false)
    const errorMessage = ref('')

    // Watch for target changes and populate form
    watch(() => props.target, (newTarget) => {
      if (newTarget) {
        formData.value = {
          target_type: newTarget.target_type,
          target_price: newTarget.target_price,
          trim_percentage: newTarget.trim_percentage,
          alert_note: newTarget.alert_note || ''
        }
      }
    }, { immediate: true })

    const handleSubmit = async () => {
      submitting.value = true
      errorMessage.value = ''

      try {
        await targetsApi.update(props.target.id, formData.value)

        // Close modal
        const modal = document.getElementById('editTargetModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('target-updated')
      } catch (error) {
        errorMessage.value = error.response?.data?.error || 'Failed to update target'
      } finally {
        submitting.value = false
      }
    }

    const handleDelete = async () => {
      if (!confirm('Are you sure you want to delete this target?')) {
        return
      }

      deleting.value = true

      try {
        await targetsApi.delete(props.target.id)

        // Close modal
        const modal = document.getElementById('editTargetModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('target-deleted')
      } catch (error) {
        alert('Failed to delete target: ' + (error.response?.data?.error || error.message))
      } finally {
        deleting.value = false
      }
    }

    return {
      formData,
      submitting,
      deleting,
      errorMessage,
      handleSubmit,
      handleDelete
    }
  }
}
</script>
