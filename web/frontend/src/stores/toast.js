import { defineStore } from 'pinia'

/**
 * Toast Notification Store
 * Manages application-wide toast notifications for user feedback
 *
 * Usage:
 * import { useToastStore } from '@/stores/toast'
 * const toast = useToastStore()
 * toast.success('Operation completed successfully')
 * toast.error('Something went wrong')
 */

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: [],
    nextId: 1
  }),

  actions: {
    /**
     * Show a toast notification
     * @param {Object} options - Toast options
     * @param {string} options.message - Message to display
     * @param {string} options.type - Type: 'success', 'error', 'warning', 'info'
     * @param {number} options.duration - Auto-dismiss duration in ms (default: 4000)
     */
    show({ message, type = 'info', duration = 4000 }) {
      const id = this.nextId++
      const toast = {
        id,
        message,
        type,
        duration
      }

      this.toasts.push(toast)

      // Auto-dismiss after duration
      if (duration > 0) {
        setTimeout(() => {
          this.dismiss(id)
        }, duration)
      }

      return id
    },

    /**
     * Dismiss a toast by ID
     * @param {number} id - Toast ID to dismiss
     */
    dismiss(id) {
      const index = this.toasts.findIndex(t => t.id === id)
      if (index !== -1) {
        this.toasts.splice(index, 1)
      }
    },

    /**
     * Clear all toasts
     */
    clear() {
      this.toasts = []
    },

    // Convenience methods for common toast types

    success(message, duration = 4000) {
      return this.show({ message, type: 'success', duration })
    },

    error(message, duration = 6000) {
      return this.show({ message, type: 'error', duration })
    },

    warning(message, duration = 5000) {
      return this.show({ message, type: 'warning', duration })
    },

    info(message, duration = 4000) {
      return this.show({ message, type: 'info', duration })
    }
  }
})
