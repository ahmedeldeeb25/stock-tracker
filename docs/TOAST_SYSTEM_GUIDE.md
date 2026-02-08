# Toast Notification System - Quick Reference

## Overview

The toast notification system provides user feedback for operations throughout the application. It replaces `alert()` and provides consistent, accessible notifications.

## Basic Usage

### Import the Store

```javascript
import { useToastStore } from '@/stores/toast'

export default {
  setup() {
    const toast = useToastStore()

    // Use toast methods...
  }
}
```

## Methods

### Success Notifications
Display green checkmark toast, auto-dismiss after 4 seconds.

```javascript
toast.success('Stock added successfully')
toast.success('Target updated')
toast.success('Changes saved', 5000)  // Custom duration
```

### Error Notifications
Display red error toast, auto-dismiss after 6 seconds (longer for reading).

```javascript
toast.error('Failed to save changes')
toast.error('Network error occurred')
toast.error('Invalid input', 8000)  // Custom duration
```

### Warning Notifications
Display orange warning toast, auto-dismiss after 5 seconds.

```javascript
toast.warning('Target already exists')
toast.warning('Please save your changes')
```

### Info Notifications
Display blue info toast, auto-dismiss after 4 seconds.

```javascript
toast.info('Data refreshed')
toast.info('Loading complete')
```

### Manual Dismiss
Dismiss a specific toast by its ID.

```javascript
const toastId = toast.success('Processing...')
// Later...
toast.dismiss(toastId)
```

### Clear All
Clear all visible toasts.

```javascript
toast.clear()
```

## Common Patterns

### After Successful API Call

```javascript
async function saveData() {
  try {
    await api.save(data)
    toast.success('Data saved successfully')
  } catch (error) {
    toast.error('Failed to save: ' + error.message)
  }
}
```

### With Loading State

```javascript
async function refreshPrices() {
  loading.value = true
  try {
    await stocksStore.fetchStocks(true)
    toast.success('Prices refreshed')
  } catch (error) {
    toast.error('Failed to refresh prices')
  } finally {
    loading.value = false
  }
}
```

### Validation Warnings

```javascript
function validateForm() {
  if (targets.length === 0) {
    toast.warning('At least one target is required')
    return false
  }
  return true
}
```

### Long-Running Operations

```javascript
async function importData() {
  const toastId = toast.info('Importing data...', 0)  // 0 = no auto-dismiss

  try {
    await api.import(data)
    toast.dismiss(toastId)
    toast.success('Import complete')
  } catch (error) {
    toast.dismiss(toastId)
    toast.error('Import failed: ' + error.message)
  }
}
```

## Configuration

### Default Durations

| Type | Duration | Rationale |
|------|----------|-----------|
| Success | 4000ms | Quick confirmation |
| Error | 6000ms | More time to read error details |
| Warning | 5000ms | Medium importance |
| Info | 4000ms | Quick information |

### Custom Duration

```javascript
toast.success('Message', 3000)   // 3 seconds
toast.error('Message', 10000)    // 10 seconds
toast.info('Message', 0)         // No auto-dismiss
```

## Accessibility

The toast system is fully accessible:

- **ARIA Live Regions:** Errors use `assertive`, others use `polite`
- **Screen Reader Announcements:** All toasts are announced
- **Keyboard Accessible:** Close button can be focused and activated
- **Visual Indicators:** Color + icon for all types

## Styling

### Toast Types

Each toast type has a distinct color and icon:

| Type | Color | Icon | Border |
|------|-------|------|--------|
| Success | Green | ✓ Check circle | Green left border |
| Error | Red | ⊗ Exclamation circle | Red left border |
| Warning | Orange | ⚠ Triangle | Orange left border |
| Info | Blue | ⓘ Info circle | Blue left border |

### Position

- **Desktop:** Fixed top-right, 24px from edges, 360px wide
- **Mobile:** Fixed top, 16px from edges, full width minus margins

## Best Practices

### DO

✅ Use success toasts for completed actions
```javascript
toast.success('Stock deleted successfully')
```

✅ Use error toasts for failures with helpful context
```javascript
toast.error('Failed to add stock: Symbol not found')
```

✅ Keep messages concise (1-2 sentences)
```javascript
toast.success('Target updated')  // Good
```

✅ Use consistent verb tense (past tense for completed actions)
```javascript
toast.success('Changes saved')  // Good
```

### DON'T

❌ Don't overuse toasts for every minor interaction
```javascript
// Bad: Too frequent
onClick: () => {
  expand.value = !expand.value
  toast.info('Section expanded')  // Unnecessary
}
```

❌ Don't use long, technical messages
```javascript
// Bad: Too technical
toast.error('HTTP 500 Internal Server Error: TypeError: Cannot read property...')

// Good: User-friendly
toast.error('Unable to save changes. Please try again.')
```

❌ Don't stack too many toasts
```javascript
// Bad: Overwhelming
toast.success('Item 1 added')
toast.success('Item 2 added')
toast.success('Item 3 added')

// Good: Combine
toast.success('3 items added successfully')
```

❌ Don't use toasts for critical information that needs user action
```javascript
// Bad: Toast dismisses automatically
toast.warning('You have unsaved changes!')

// Good: Use modal
showConfirmModal('You have unsaved changes. Discard?')
```

## Migration from alert()

### Before

```javascript
if (success) {
  alert('Stock added successfully')
} else {
  alert('Error: Failed to add stock')
}
```

### After

```javascript
if (success) {
  toast.success('Stock added successfully')
} else {
  toast.error('Failed to add stock')
}
```

## Testing

### Manual Testing

1. Trigger success action (e.g., add stock)
2. Verify green toast appears top-right
3. Verify toast auto-dismisses after 4s
4. Verify click on X dismisses immediately

### Accessibility Testing

1. Enable screen reader (NVDA/VoiceOver)
2. Trigger toast
3. Verify screen reader announces message
4. Tab to close button
5. Press Enter to dismiss

### Responsive Testing

1. Resize browser to 375px width
2. Trigger toast
3. Verify toast spans full width with margins
4. Verify no horizontal scroll

## Advanced Usage

### Multiple Toasts

Toasts automatically stack vertically:

```javascript
toast.success('Stock added')
toast.info('Fetching latest prices...')
toast.success('Prices updated')
```

Result: 3 toasts stacked, oldest at bottom.

### Conditional Display

```javascript
function handleSave(data) {
  const errors = validate(data)

  if (errors.length > 0) {
    toast.error(`Validation failed: ${errors.join(', ')}`)
    return
  }

  try {
    await save(data)
    toast.success('Changes saved')
  } catch (error) {
    toast.error('Save failed: ' + error.message)
  }
}
```

### Persistent Toasts

For operations that need manual dismissal:

```javascript
const uploadId = toast.info('Uploading file...', 0)  // duration: 0

// ... upload happens ...

if (success) {
  toast.dismiss(uploadId)
  toast.success('Upload complete')
} else {
  toast.dismiss(uploadId)
  toast.error('Upload failed')
}
```

## Troubleshooting

### Toast Not Appearing

**Check:**
1. Is `<ToastContainer />` in App.vue?
2. Is toast store imported correctly?
3. Are there console errors?

### Toast Dismissed Too Quickly

**Solution:**
```javascript
toast.error('Message', 8000)  // Increase duration
```

### Multiple Toasts Overlap

**Check:**
CSS may be overriding toast-container z-index:
```css
.toast-container {
  z-index: 1050;  /* Above modals (1055) */
}
```

### Toast Not Announced by Screen Reader

**Check:**
1. ARIA attributes present in ToastContainer.vue?
2. Screen reader in virtual cursor mode?
3. Browser supports ARIA live regions?

## Future Enhancements

Planned for Phase 2:

- [ ] Toast action buttons (Undo, Retry)
- [ ] Grouped/batched toasts
- [ ] Custom toast components
- [ ] Toast queue management
- [ ] Persistent toasts across page navigation
- [ ] Toast history log

---

**Version:** 1.0
**Last Updated:** February 8, 2026
