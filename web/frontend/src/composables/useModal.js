/**
 * useModal Composable
 *
 * Provides focus management, keyboard handling, and body scroll prevention
 * for accessible modal dialogs.
 *
 * Features:
 * - Focus trap within modal
 * - Return focus to trigger element on close
 * - Escape key handling with unsaved changes detection
 * - Prevent body scroll when modal is open
 * - WCAG 2.1 AA compliant
 *
 * @example
 * import { useModal } from '@/composables/useModal'
 *
 * const {
 *   modalRef,
 *   isOpen,
 *   open,
 *   close,
 *   hasUnsavedChanges
 * } = useModal({
 *   onClose: () => console.log('Modal closed'),
 *   modalId: 'myModal'
 * })
 */

import { ref, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { useConfirmStore } from '@/stores/confirm'

/**
 * Modal composable
 *
 * @param {Object} options - Configuration options
 * @param {Function} [options.onClose] - Callback when modal closes
 * @param {Function} [options.onOpen] - Callback when modal opens
 * @param {string} [options.modalId] - Unique modal identifier for ARIA
 * @param {boolean} [options.closeOnEscape=true] - Allow closing with Escape key
 * @param {boolean} [options.closeOnBackdrop=true] - Allow closing by clicking backdrop
 * @param {boolean} [options.trapFocus=true] - Enable focus trapping
 * @param {boolean} [options.preventBodyScroll=true] - Prevent body scroll when open
 * @returns {Object} Modal control methods and refs
 */
export function useModal(options = {}) {
  const {
    onClose = null,
    onOpen = null,
    modalId = 'modal',
    closeOnEscape = true,
    closeOnBackdrop = true,
    trapFocus = true,
    preventBodyScroll = true
  } = options

  const confirm = useConfirmStore()

  // State
  const modalRef = ref(null)
  const isOpen = ref(false)
  const hasUnsavedChanges = ref(false)
  const previouslyFocusedElement = ref(null)
  const focusableElements = ref([])

  /**
   * Get all focusable elements within the modal
   */
  const getFocusableElements = () => {
    if (!modalRef.value) return []

    const selectors = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])'
    ]

    return Array.from(modalRef.value.querySelectorAll(selectors.join(', ')))
  }

  /**
   * Focus first focusable element in modal
   */
  const focusFirstElement = async () => {
    await nextTick()
    focusableElements.value = getFocusableElements()

    if (focusableElements.value.length > 0) {
      focusableElements.value[0].focus()
    } else if (modalRef.value) {
      modalRef.value.focus()
    }
  }

  /**
   * Handle keyboard events
   */
  const handleKeydown = async (event) => {
    if (!isOpen.value) return

    // Escape key - close modal (with confirmation if unsaved changes)
    if (event.key === 'Escape' && closeOnEscape) {
      event.preventDefault()

      if (hasUnsavedChanges.value) {
        const isConfirmed = await confirm.show({
          title: 'Unsaved Changes',
          message: 'You have unsaved changes. Are you sure you want to close without saving?',
          variant: 'warning',
          confirmText: 'Discard Changes',
          cancelText: 'Keep Editing'
        })

        if (isConfirmed) {
          close()
        }
      } else {
        close()
      }
    }

    // Tab key - trap focus within modal
    if (event.key === 'Tab' && trapFocus) {
      focusableElements.value = getFocusableElements()

      if (focusableElements.value.length === 0) return

      const firstElement = focusableElements.value[0]
      const lastElement = focusableElements.value[focusableElements.value.length - 1]

      if (event.shiftKey) {
        // Shift+Tab - move focus backwards
        if (document.activeElement === firstElement) {
          event.preventDefault()
          lastElement.focus()
        }
      } else {
        // Tab - move focus forwards
        if (document.activeElement === lastElement) {
          event.preventDefault()
          firstElement.focus()
        }
      }
    }
  }

  /**
   * Prevent body scroll
   */
  const toggleBodyScroll = (disable) => {
    if (!preventBodyScroll) return

    if (disable) {
      // Store current scroll position
      const scrollY = window.scrollY
      document.body.style.position = 'fixed'
      document.body.style.top = `-${scrollY}px`
      document.body.style.width = '100%'
    } else {
      // Restore scroll position
      const scrollY = document.body.style.top
      document.body.style.position = ''
      document.body.style.top = ''
      document.body.style.width = ''
      window.scrollTo(0, parseInt(scrollY || '0') * -1)
    }
  }

  /**
   * Open modal
   */
  const open = async () => {
    // Store currently focused element
    previouslyFocusedElement.value = document.activeElement

    isOpen.value = true

    // Prevent body scroll
    toggleBodyScroll(true)

    // Focus first element
    await focusFirstElement()

    // Call onOpen callback
    if (onOpen) {
      onOpen()
    }
  }

  /**
   * Close modal
   */
  const close = () => {
    isOpen.value = false
    hasUnsavedChanges.value = false

    // Re-enable body scroll
    toggleBodyScroll(false)

    // Return focus to previously focused element
    if (previouslyFocusedElement.value && previouslyFocusedElement.value.focus) {
      previouslyFocusedElement.value.focus()
    }
    previouslyFocusedElement.value = null

    // Call onClose callback
    if (onClose) {
      onClose()
    }
  }

  /**
   * Handle backdrop click
   */
  const handleBackdropClick = async (event) => {
    if (!closeOnBackdrop) return

    // Only close if clicking directly on backdrop (not modal content)
    if (event.target === event.currentTarget) {
      if (hasUnsavedChanges.value) {
        const isConfirmed = await confirm.show({
          title: 'Unsaved Changes',
          message: 'You have unsaved changes. Are you sure you want to close without saving?',
          variant: 'warning',
          confirmText: 'Discard Changes',
          cancelText: 'Keep Editing'
        })

        if (isConfirmed) {
          close()
        }
      } else {
        close()
      }
    }
  }

  /**
   * Mark as having unsaved changes
   */
  const markUnsaved = () => {
    hasUnsavedChanges.value = true
  }

  /**
   * Mark as saved (no unsaved changes)
   */
  const markSaved = () => {
    hasUnsavedChanges.value = false
  }

  /**
   * Setup keyboard event listener
   */
  onMounted(() => {
    document.addEventListener('keydown', handleKeydown)
  })

  /**
   * Cleanup on unmount
   */
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
    toggleBodyScroll(false)
  })

  /**
   * Watch for isOpen changes (for Bootstrap modal integration)
   */
  watch(isOpen, async (newValue) => {
    if (newValue) {
      await open()
    } else {
      close()
    }
  })

  return {
    // Refs
    modalRef,
    isOpen,
    hasUnsavedChanges,

    // Methods
    open,
    close,
    markUnsaved,
    markSaved,
    handleBackdropClick,

    // For Bootstrap modal integration
    modalId
  }
}
