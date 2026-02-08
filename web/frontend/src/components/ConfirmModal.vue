<template>
  <Teleport to="body">
    <Transition name="confirm-fade">
      <div
        v-if="confirmStore.isVisible"
        class="confirm-backdrop"
        @click="handleBackdropClick"
        role="presentation"
      >
        <Transition name="confirm-scale">
          <div
            v-if="confirmStore.isVisible"
            class="confirm-dialog"
            :class="`confirm-dialog-${confirmStore.variant}`"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="dialogId + '-title'"
            :aria-describedby="dialogId + '-message'"
            @click.stop
            ref="dialogRef"
          >
            <!-- Icon -->
            <div class="confirm-icon" :class="`confirm-icon-${confirmStore.variant}`" aria-hidden="true">
              <i
                class="bi"
                :class="{
                  'bi-exclamation-triangle-fill': confirmStore.variant === 'danger',
                  'bi-exclamation-circle-fill': confirmStore.variant === 'warning',
                  'bi-question-circle-fill': confirmStore.variant === 'default'
                }"
              ></i>
            </div>

            <!-- Title -->
            <h2 class="confirm-title" :id="dialogId + '-title'">
              {{ confirmStore.title }}
            </h2>

            <!-- Message -->
            <p class="confirm-message" :id="dialogId + '-message'">
              {{ confirmStore.message }}
            </p>

            <!-- Actions -->
            <div class="confirm-actions">
              <button
                type="button"
                class="btn btn-secondary"
                @click="handleCancel"
                ref="cancelButtonRef"
              >
                {{ confirmStore.cancelText }}
              </button>
              <button
                type="button"
                class="btn"
                :class="{
                  'btn-danger': confirmStore.variant === 'danger',
                  'btn-warning': confirmStore.variant === 'warning',
                  'btn-primary': confirmStore.variant === 'default'
                }"
                @click="handleConfirm"
                ref="confirmButtonRef"
              >
                {{ confirmStore.confirmText }}
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { ref, watch, nextTick, onMounted } from 'vue'
import { useConfirmStore } from '@/stores/confirm'

export default {
  name: 'ConfirmModal',
  setup() {
    const confirmStore = useConfirmStore()
    const dialogRef = ref(null)
    const confirmButtonRef = ref(null)
    const cancelButtonRef = ref(null)
    const dialogId = 'confirm-dialog'
    const previouslyFocusedElement = ref(null)

    /**
     * Handle confirm action
     */
    const handleConfirm = () => {
      confirmStore.confirm()
    }

    /**
     * Handle cancel action
     */
    const handleCancel = () => {
      confirmStore.cancel()
    }

    /**
     * Handle backdrop click (should cancel)
     */
    const handleBackdropClick = () => {
      confirmStore.cancel()
    }

    /**
     * Handle keyboard events
     */
    const handleKeydown = (event) => {
      if (!confirmStore.isVisible) return

      // Enter key - confirm
      if (event.key === 'Enter') {
        event.preventDefault()
        handleConfirm()
      }

      // Escape key - cancel
      if (event.key === 'Escape') {
        event.preventDefault()
        handleCancel()
      }

      // Tab key - trap focus within dialog
      if (event.key === 'Tab') {
        const focusableElements = dialogRef.value?.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        )

        if (!focusableElements || focusableElements.length === 0) return

        const firstElement = focusableElements[0]
        const lastElement = focusableElements[focusableElements.length - 1]

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
     * Prevent body scroll when modal is open
     */
    const toggleBodyScroll = (disable) => {
      if (disable) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }

    /**
     * Watch for visibility changes
     */
    watch(() => confirmStore.isVisible, async (isVisible) => {
      if (isVisible) {
        // Store currently focused element
        previouslyFocusedElement.value = document.activeElement

        // Prevent body scroll
        toggleBodyScroll(true)

        // Focus confirm button after render
        await nextTick()
        if (confirmButtonRef.value) {
          confirmButtonRef.value.focus()
        }
      } else {
        // Re-enable body scroll
        toggleBodyScroll(false)

        // Return focus to previously focused element
        if (previouslyFocusedElement.value && previouslyFocusedElement.value.focus) {
          previouslyFocusedElement.value.focus()
        }
        previouslyFocusedElement.value = null
      }
    })

    /**
     * Setup keyboard event listener
     */
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })

    /**
     * Cleanup on unmount
     */
    onMounted(() => {
      return () => {
        document.removeEventListener('keydown', handleKeydown)
        toggleBodyScroll(false)
      }
    })

    return {
      confirmStore,
      dialogRef,
      confirmButtonRef,
      cancelButtonRef,
      dialogId,
      handleConfirm,
      handleCancel,
      handleBackdropClick
    }
  }
}
</script>

<style scoped>
/* Backdrop */
.confirm-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1060;
  padding: var(--space-2);
}

/* Dialog */
.confirm-dialog {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  padding: var(--space-4);
  max-width: 400px;
  width: 100%;
  text-align: center;
}

/* Icon */
.confirm-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--space-3);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
}

.confirm-icon-default {
  background-color: var(--color-info-light);
  color: var(--color-info);
}

.confirm-icon-warning {
  background-color: var(--color-warning-light);
  color: var(--color-warning);
}

.confirm-icon-danger {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

/* Title */
.confirm-title {
  font-size: var(--font-size-h3);
  font-weight: 600;
  margin: 0 0 var(--space-2);
  color: var(--color-gray-900);
}

/* Message */
.confirm-message {
  font-size: var(--font-size-body);
  color: var(--color-gray-600);
  margin: 0 0 var(--space-4);
  line-height: 1.5;
}

/* Actions */
.confirm-actions {
  display: flex;
  gap: var(--space-2);
  justify-content: center;
}

.confirm-actions .btn {
  flex: 1;
  min-width: 100px;
}

/* Animations */
.confirm-fade-enter-active,
.confirm-fade-leave-active {
  transition: opacity var(--duration-fast) var(--ease-out);
}

.confirm-fade-enter-from,
.confirm-fade-leave-to {
  opacity: 0;
}

.confirm-scale-enter-active {
  transition: all var(--duration-fast) var(--ease-out);
}

.confirm-scale-leave-active {
  transition: all 150ms cubic-bezier(0.4, 0, 1, 1);
}

.confirm-scale-enter-from,
.confirm-scale-leave-to {
  opacity: 0;
  transform: scale(0.95);
}

/* Mobile adjustments */
@media (max-width: 767px) {
  .confirm-backdrop {
    padding: var(--space-2);
  }

  .confirm-dialog {
    padding: var(--space-3);
    max-width: none;
  }

  .confirm-icon {
    width: 56px;
    height: 56px;
    font-size: 1.75rem;
  }

  .confirm-title {
    font-size: var(--font-size-h4);
  }

  .confirm-actions {
    flex-direction: column-reverse;
  }

  .confirm-actions .btn {
    width: 100%;
    min-height: var(--touch-target-min);
  }
}

/* Focus styles */
.confirm-dialog button:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
</style>
