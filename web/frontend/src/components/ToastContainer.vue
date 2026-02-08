<template>
  <div class="toast-container" aria-live="polite" aria-atomic="false">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast-notification', `toast-${toast.type}`]"
        :role="toast.type === 'error' ? 'alert' : 'status'"
        :aria-live="toast.type === 'error' ? 'assertive' : 'polite'"
      >
        <!-- Icon -->
        <div class="toast-icon">
          <i
            :class="getIconClass(toast.type)"
            :aria-hidden="true"
          ></i>
        </div>

        <!-- Message Content -->
        <div class="toast-content">
          {{ toast.message }}
        </div>

        <!-- Close Button -->
        <button
          class="toast-close"
          @click="dismissToast(toast.id)"
          aria-label="Dismiss notification"
          type="button"
        >
          <i class="bi bi-x" aria-hidden="true"></i>
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useToastStore } from '@/stores/toast'

export default {
  name: 'ToastContainer',
  setup() {
    const toastStore = useToastStore()
    const toasts = computed(() => toastStore.toasts)

    const getIconClass = (type) => {
      const icons = {
        success: 'bi bi-check-circle-fill text-success',
        error: 'bi bi-exclamation-circle-fill text-danger',
        warning: 'bi bi-exclamation-triangle-fill text-warning',
        info: 'bi bi-info-circle-fill text-info'
      }
      return icons[type] || icons.info
    }

    const dismissToast = (id) => {
      toastStore.dismiss(id)
    }

    return {
      toasts,
      getIconClass,
      dismissToast
    }
  }
}
</script>
