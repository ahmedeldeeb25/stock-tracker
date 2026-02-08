/**
 * Confirm Dialog Store
 *
 * Manages state for custom confirmation dialogs throughout the application.
 * Provides a Promise-based API for showing confirmation dialogs and
 * handling user responses.
 *
 * @example
 * import { useConfirmStore } from '@/stores/confirm'
 * const confirm = useConfirmStore()
 *
 * const isConfirmed = await confirm.show({
 *   title: 'Delete Stock?',
 *   message: 'Are you sure you want to delete this stock? This action cannot be undone.',
 *   variant: 'danger',
 *   confirmText: 'Delete',
 *   cancelText: 'Cancel'
 * })
 *
 * if (isConfirmed) {
 *   // User confirmed
 * }
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useConfirmStore = defineStore('confirm', () => {
  // State
  const isVisible = ref(false)
  const title = ref('')
  const message = ref('')
  const variant = ref('default') // 'default', 'danger', 'warning'
  const confirmText = ref('Confirm')
  const cancelText = ref('Cancel')
  const resolveCallback = ref(null)

  /**
   * Show confirmation dialog
   *
   * @param {Object} options - Confirmation dialog options
   * @param {string} options.title - Dialog title
   * @param {string} options.message - Dialog message/description
   * @param {string} [options.variant='default'] - Visual variant ('default', 'danger', 'warning')
   * @param {string} [options.confirmText='Confirm'] - Confirm button text
   * @param {string} [options.cancelText='Cancel'] - Cancel button text
   * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
   */
  const show = (options) => {
    return new Promise((resolve) => {
      title.value = options.title || 'Confirm'
      message.value = options.message || 'Are you sure?'
      variant.value = options.variant || 'default'
      confirmText.value = options.confirmText || 'Confirm'
      cancelText.value = options.cancelText || 'Cancel'
      resolveCallback.value = resolve
      isVisible.value = true
    })
  }

  /**
   * Confirm action
   */
  const confirm = () => {
    if (resolveCallback.value) {
      resolveCallback.value(true)
    }
    hide()
  }

  /**
   * Cancel action
   */
  const cancel = () => {
    if (resolveCallback.value) {
      resolveCallback.value(false)
    }
    hide()
  }

  /**
   * Hide dialog
   */
  const hide = () => {
    isVisible.value = false
    // Clean up after animation completes
    setTimeout(() => {
      title.value = ''
      message.value = ''
      variant.value = 'default'
      confirmText.value = 'Confirm'
      cancelText.value = 'Cancel'
      resolveCallback.value = null
    }, 300)
  }

  return {
    isVisible,
    title,
    message,
    variant,
    confirmText,
    cancelText,
    show,
    confirm,
    cancel,
    hide
  }
})
