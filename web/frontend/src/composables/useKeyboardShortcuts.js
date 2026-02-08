/**
 * useKeyboardShortcuts Composable
 *
 * Provides keyboard shortcut functionality for improved accessibility
 * and user experience.
 *
 * Features:
 * - / or Ctrl+K: Focus search input
 * - Esc: Close modal (with unsaved changes check)
 * - ?: Show keyboard shortcuts help (optional)
 * - Custom shortcuts registration
 *
 * @example
 * import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'
 *
 * const { registerShortcut, unregisterShortcut } = useKeyboardShortcuts()
 *
 * // Register search focus shortcut
 * registerShortcut({
 *   key: '/',
 *   description: 'Focus search',
 *   handler: () => searchInputRef.value?.focus()
 * })
 */

import { onMounted, onUnmounted } from 'vue'

/**
 * Global shortcut registry
 */
const shortcuts = new Map()

/**
 * Keyboard shortcuts composable
 *
 * @returns {Object} Shortcut registration methods
 */
export function useKeyboardShortcuts() {
  /**
   * Check if element is input-like
   */
  const isInputElement = (element) => {
    if (!element) return false

    const tagName = element.tagName.toLowerCase()
    const isContentEditable = element.contentEditable === 'true'

    return (
      tagName === 'input' ||
      tagName === 'textarea' ||
      tagName === 'select' ||
      isContentEditable
    )
  }

  /**
   * Check if modifier keys match
   */
  const modifiersMatch = (event, shortcut) => {
    const ctrl = shortcut.ctrl || false
    const alt = shortcut.alt || false
    const shift = shortcut.shift || false
    const meta = shortcut.meta || false

    return (
      (event.ctrlKey || event.metaKey) === (ctrl || meta) &&
      event.altKey === alt &&
      event.shiftKey === shift
    )
  }

  /**
   * Handle keyboard events
   */
  const handleKeydown = (event) => {
    // Don't trigger shortcuts if user is typing in an input
    // unless the shortcut explicitly allows it
    const activeElement = document.activeElement
    const isInInput = isInputElement(activeElement)

    // Check each registered shortcut
    for (const [id, shortcut] of shortcuts.entries()) {
      // Skip if in input and shortcut doesn't allow input
      if (isInInput && !shortcut.allowInInput) {
        continue
      }

      // Check if key matches
      const keyMatches = event.key === shortcut.key ||
        event.key.toLowerCase() === shortcut.key.toLowerCase()

      // Check if modifiers match
      const modsMatch = modifiersMatch(event, shortcut)

      if (keyMatches && modsMatch) {
        // Prevent default if specified
        if (shortcut.preventDefault !== false) {
          event.preventDefault()
        }

        // Prevent propagation if specified
        if (shortcut.stopPropagation) {
          event.stopPropagation()
        }

        // Call handler
        if (shortcut.handler) {
          shortcut.handler(event)
        }

        // Break after first match unless allowMultiple is true
        if (!shortcut.allowMultiple) {
          break
        }
      }
    }
  }

  /**
   * Register a keyboard shortcut
   *
   * @param {Object} shortcut - Shortcut configuration
   * @param {string} shortcut.id - Unique shortcut identifier
   * @param {string} shortcut.key - Key to trigger shortcut (e.g., '/', 'k', 'Escape')
   * @param {Function} shortcut.handler - Function to call when shortcut is triggered
   * @param {string} [shortcut.description] - Human-readable description
   * @param {boolean} [shortcut.ctrl=false] - Require Ctrl key
   * @param {boolean} [shortcut.alt=false] - Require Alt key
   * @param {boolean} [shortcut.shift=false] - Require Shift key
   * @param {boolean} [shortcut.meta=false] - Require Meta/Cmd key
   * @param {boolean} [shortcut.allowInInput=false] - Allow in input elements
   * @param {boolean} [shortcut.preventDefault=true] - Prevent default browser behavior
   * @param {boolean} [shortcut.stopPropagation=false] - Stop event propagation
   * @param {boolean} [shortcut.allowMultiple=false] - Allow multiple shortcuts to fire
   * @returns {string} Shortcut ID
   */
  const registerShortcut = (shortcut) => {
    const id = shortcut.id || `shortcut-${Date.now()}-${Math.random()}`

    shortcuts.set(id, {
      key: shortcut.key,
      handler: shortcut.handler,
      description: shortcut.description || '',
      ctrl: shortcut.ctrl || false,
      alt: shortcut.alt || false,
      shift: shortcut.shift || false,
      meta: shortcut.meta || false,
      allowInInput: shortcut.allowInInput || false,
      preventDefault: shortcut.preventDefault !== false,
      stopPropagation: shortcut.stopPropagation || false,
      allowMultiple: shortcut.allowMultiple || false
    })

    return id
  }

  /**
   * Unregister a keyboard shortcut
   *
   * @param {string} id - Shortcut ID to remove
   */
  const unregisterShortcut = (id) => {
    shortcuts.delete(id)
  }

  /**
   * Get all registered shortcuts
   *
   * @returns {Array} Array of shortcut objects
   */
  const getShortcuts = () => {
    return Array.from(shortcuts.entries()).map(([id, shortcut]) => ({
      id,
      ...shortcut
    }))
  }

  /**
   * Format shortcut key combination for display
   *
   * @param {Object} shortcut - Shortcut object
   * @returns {string} Formatted key combination
   */
  const formatShortcut = (shortcut) => {
    const keys = []

    // Add modifier keys
    if (shortcut.ctrl) keys.push('Ctrl')
    if (shortcut.meta) keys.push('Cmd')
    if (shortcut.alt) keys.push('Alt')
    if (shortcut.shift) keys.push('Shift')

    // Add main key
    const mainKey = shortcut.key === ' ' ? 'Space' : shortcut.key
    keys.push(mainKey)

    return keys.join('+')
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
  })

  return {
    registerShortcut,
    unregisterShortcut,
    getShortcuts,
    formatShortcut
  }
}

/**
 * Common keyboard shortcuts
 */
export const CommonShortcuts = {
  SEARCH: {
    key: '/',
    description: 'Focus search input',
    allowInInput: false
  },
  SEARCH_ALT: {
    key: 'k',
    ctrl: true,
    description: 'Focus search input',
    allowInInput: false
  },
  ESCAPE: {
    key: 'Escape',
    description: 'Close modal or clear input',
    allowInInput: true
  },
  HELP: {
    key: '?',
    shift: true,
    description: 'Show keyboard shortcuts',
    allowInInput: false
  },
  SAVE: {
    key: 's',
    ctrl: true,
    description: 'Save current form',
    allowInInput: true
  },
  SUBMIT: {
    key: 'Enter',
    ctrl: true,
    description: 'Submit form',
    allowInInput: true
  }
}
