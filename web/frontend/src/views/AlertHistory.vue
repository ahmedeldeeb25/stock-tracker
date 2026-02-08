<template>
  <div>
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>
        <i class="bi bi-bell me-2"></i>
        Alert History
      </h2>
      <router-link to="/" class="btn btn-outline-primary">
        <i class="bi bi-arrow-left me-1"></i>
        Back to Dashboard
      </router-link>
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

    <!-- Alerts List -->
    <div v-else>
      <div class="card">
        <div class="card-body">
          <div v-if="alerts.length === 0" class="text-center py-5 text-muted">
            <i class="bi bi-inbox display-1"></i>
            <p class="lead mt-3">No alerts yet</p>
            <p>Alerts will appear here when price targets are met</p>
          </div>

          <div v-else>
            <div
              v-for="alert in alerts"
              :key="alert.id"
              class="d-flex justify-content-between align-items-start p-3 mb-3 border rounded"
            >
              <div class="flex-grow-1">
                <div class="d-flex align-items-center mb-2">
                  <h5 class="mb-0 me-3">{{ alert.symbol }}</h5>
                  <span
                    class="badge"
                    :class="getTargetBadgeClass(alert.target_type)"
                  >
                    {{ alert.target_type }}
                  </span>
                </div>

                <div class="row mb-2">
                  <div class="col-md-6">
                    <small class="text-muted">Current Price:</small>
                    <div class="h6 mb-0">{{ formatPrice(alert.current_price) }}</div>
                  </div>
                  <div class="col-md-6">
                    <small class="text-muted">Target Price:</small>
                    <div class="h6 mb-0">{{ formatPrice(alert.target_price) }}</div>
                  </div>
                </div>

                <div v-if="alert.alert_note" class="mb-2">
                  <small class="text-muted">Note:</small>
                  <p class="mb-0">{{ alert.alert_note }}</p>
                </div>

                <div class="d-flex align-items-center gap-3">
                  <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>
                    {{ formatDateTime(alert.triggered_at) }}
                  </small>
                  <span
                    v-if="alert.email_sent"
                    class="badge bg-success"
                  >
                    <i class="bi bi-envelope-check me-1"></i>
                    Email Sent
                  </span>
                </div>
              </div>

              <div>
                <button
                  class="btn btn-sm btn-outline-danger"
                  @click="handleDelete(alert.id)"
                  title="Delete alert"
                >
                  <i class="bi bi-trash"></i>
                </button>
              </div>
            </div>

            <!-- Pagination Info -->
            <div class="d-flex justify-content-between align-items-center mt-4">
              <div class="text-muted">
                Showing {{ alerts.length }} of {{ total }} alerts
              </div>
              <div v-if="total > limit">
                <button
                  class="btn btn-outline-primary btn-sm"
                  @click="loadMore"
                  :disabled="alerts.length >= total"
                >
                  Load More
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useAlertsStore } from '@/stores/alerts'
import { useConfirmStore } from '@/stores/confirm'
import { useToastStore } from '@/stores/toast'
import { formatPrice, formatDateTime, getTargetBadgeClass } from '@/utils/formatters'

export default {
  name: 'AlertHistory',
  setup() {
    const alertsStore = useAlertsStore()
    const confirm = useConfirmStore()
    const toast = useToastStore()

    const loading = computed(() => alertsStore.loading)
    const error = computed(() => alertsStore.error)
    const alerts = computed(() => alertsStore.alerts)
    const total = computed(() => alertsStore.total)
    const limit = computed(() => alertsStore.limit)

    onMounted(() => {
      alertsStore.fetchAlerts()
    })

    const loadMore = () => {
      const newOffset = alerts.value.length
      alertsStore.fetchAlerts({ offset: newOffset })
    }

    const handleDelete = async (alertId) => {
      const isConfirmed = await confirm.show({
        title: 'Delete Alert?',
        message: 'Are you sure you want to delete this alert?',
        variant: 'danger',
        confirmText: 'Delete',
        cancelText: 'Cancel'
      })

      if (isConfirmed) {
        try {
          await alertsStore.deleteAlert(alertId)
          toast.success('Alert deleted successfully')
        } catch (error) {
          toast.error('Failed to delete alert: ' + error.message)
        }
      }
    }

    return {
      loading,
      error,
      alerts,
      total,
      limit,
      loadMore,
      handleDelete,
      formatPrice,
      formatDateTime,
      getTargetBadgeClass
    }
  }
}
</script>
