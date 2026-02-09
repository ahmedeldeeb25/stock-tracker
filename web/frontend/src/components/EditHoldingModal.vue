<template>
  <div
    class="modal fade"
    id="editHoldingModal"
    tabindex="-1"
    aria-labelledby="editHoldingModalLabel"
    aria-modal="true"
    role="dialog"
  >
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title" id="editHoldingModalLabel">
            {{ hasExistingHolding ? 'Edit Holdings' : 'Add Holdings' }}
          </h5>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSubmit">
            <!-- Shares -->
            <div class="mb-3">
              <label for="holdingShares" class="form-label">
                Shares Owned <span class="text-danger">*</span>
              </label>
              <input
                id="holdingShares"
                type="number"
                step="0.000001"
                min="0.000001"
                class="form-control"
                v-model.number="formData.shares"
                required
                aria-required="true"
                aria-describedby="sharesHelp"
              >
              <small id="sharesHelp" class="form-text text-muted">
                Number of shares you currently own
              </small>
            </div>

            <!-- Average Cost -->
            <div class="mb-3">
              <label for="holdingCost" class="form-label">
                Average Cost Per Share
              </label>
              <div class="input-group">
                <span class="input-group-text">$</span>
                <input
                  id="holdingCost"
                  type="number"
                  step="0.01"
                  min="0.01"
                  class="form-control"
                  v-model.number="formData.average_cost"
                  aria-describedby="costHelp"
                >
              </div>
              <small id="costHelp" class="form-text text-muted">
                Leave empty to hide gain/loss calculations
              </small>
            </div>

            <!-- Preview -->
            <div v-if="preview.positionValue" class="alert alert-light mb-3">
              <strong>Preview:</strong>
              <div>Position Value: {{ formatPrice(preview.positionValue) }}</div>
              <div v-if="preview.costBasis">
                Cost Basis: {{ formatPrice(preview.costBasis) }}
              </div>
            </div>

            <!-- Info Notice -->
            <div class="alert alert-info small mb-0">
              <i class="bi bi-info-circle me-1" aria-hidden="true"></i>
              This is for tracking purposes only. It does not execute any trades.
            </div>
          </form>
        </div>
        <div class="modal-footer justify-content-between">
          <button
            v-if="hasExistingHolding"
            type="button"
            class="btn btn-outline-danger"
            @click="handleDelete"
            :disabled="submitting"
          >
            <i class="bi bi-trash me-1" aria-hidden="true"></i>
            Delete
          </button>
          <div v-else></div>
          <div>
            <button
              type="button"
              class="btn btn-outline-secondary me-2"
              data-bs-dismiss="modal"
            >
              Cancel
            </button>
            <button
              type="button"
              class="btn btn-primary"
              @click="handleSubmit"
              :disabled="submitting || !isValid"
            >
              <span
                v-if="submitting"
                class="spinner-border spinner-border-sm me-1"
                aria-hidden="true"
              ></span>
              {{ submitting ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { stocksApi } from '@/api'
import { formatPrice } from '@/utils/formatters'
import { useToastStore } from '@/stores/toast'

export default {
  name: 'EditHoldingModal',
  props: {
    stockId: {
      type: Number,
      required: true
    },
    currentPrice: {
      type: Number,
      default: null
    },
    existingHolding: {
      type: Object,
      default: null
    }
  },
  emits: ['holding-updated', 'holding-deleted'],
  setup(props, { emit }) {
    const toast = useToastStore()

    const formData = ref({
      shares: null,
      average_cost: null
    })

    const submitting = ref(false)

    const hasExistingHolding = computed(() => !!props.existingHolding)

    const isValid = computed(() => {
      return formData.value.shares && formData.value.shares > 0
    })

    const preview = computed(() => {
      if (!formData.value.shares || !props.currentPrice) {
        return {}
      }

      return {
        positionValue: formData.value.shares * props.currentPrice,
        costBasis: formData.value.average_cost
          ? formData.value.shares * formData.value.average_cost
          : null
      }
    })

    // Initialize form when existingHolding changes
    watch(() => props.existingHolding, (newHolding) => {
      if (newHolding) {
        formData.value = {
          shares: newHolding.shares,
          average_cost: newHolding.average_cost
        }
      } else {
        formData.value = {
          shares: null,
          average_cost: null
        }
      }
    }, { immediate: true })

    const handleSubmit = async () => {
      if (!isValid.value) return

      submitting.value = true

      try {
        await stocksApi.updateHolding(props.stockId, {
          shares: formData.value.shares,
          average_cost: formData.value.average_cost || null
        })

        // Close modal
        const modal = document.getElementById('editHoldingModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('holding-updated')
        toast.success('Holdings updated successfully')
      } catch (error) {
        toast.error('Failed to update holdings: ' + (error.response?.data?.error || error.message))
      } finally {
        submitting.value = false
      }
    }

    const handleDelete = async () => {
      if (!confirm('Are you sure you want to delete this holding?')) return

      submitting.value = true

      try {
        await stocksApi.deleteHolding(props.stockId)

        // Close modal
        const modal = document.getElementById('editHoldingModal')
        const modalInstance = window.bootstrap.Modal.getInstance(modal)
        modalInstance.hide()

        emit('holding-deleted')
        toast.success('Holdings deleted successfully')
      } catch (error) {
        toast.error('Failed to delete holdings: ' + (error.response?.data?.error || error.message))
      } finally {
        submitting.value = false
      }
    }

    return {
      formData,
      submitting,
      hasExistingHolding,
      isValid,
      preview,
      formatPrice,
      handleSubmit,
      handleDelete
    }
  }
}
</script>
