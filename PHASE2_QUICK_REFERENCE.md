# Phase 2 Quick Reference Guide

Quick reference for using Phase 2 UI/UX improvements in the stock-tracker application.

---

## 1. Custom Confirm Modal

Replace native `confirm()` with custom accessible modal.

### Import:
```javascript
import { useConfirmStore } from '@/stores/confirm'
```

### Basic Usage:
```javascript
const confirm = useConfirmStore()

const handleDelete = async () => {
  const isConfirmed = await confirm.show({
    title: 'Delete Item?',
    message: 'This action cannot be undone.',
    variant: 'danger',
    confirmText: 'Delete',
    cancelText: 'Cancel'
  })

  if (isConfirmed) {
    // Proceed with action
  }
}
```

### Variants:
- `default` - Info/neutral (blue icon)
- `danger` - Destructive action (red icon)
- `warning` - Warning/caution (orange icon)

---

## 2. Skeleton Loaders

### Import:
```javascript
import SkeletonLoader from '@/components/SkeletonLoader.vue'
import StockCardSkeleton from '@/components/StockCardSkeleton.vue'
import StockDetailSkeleton from '@/components/StockDetailSkeleton.vue'
```

### Usage:
```vue
<!-- Generic skeleton -->
<SkeletonLoader variant="text" width="80%" />
<SkeletonLoader variant="heading" />
<SkeletonLoader variant="circle" width="64px" height="64px" />

<!-- Stock card skeleton -->
<StockCardSkeleton />

<!-- Stock detail page skeleton -->
<StockDetailSkeleton />
```

### Variants:
- `text` - Single line of text
- `heading` - Larger heading text
- `circle` - Circular (avatars)
- `rectangle` - Rectangular (images)
- `card` - Full card layout

---

## 3. Keyboard Shortcuts

### Import:
```javascript
import { useKeyboardShortcuts, CommonShortcuts } from '@/composables/useKeyboardShortcuts'
```

### Register Shortcut:
```javascript
const { registerShortcut, unregisterShortcut } = useKeyboardShortcuts()

onMounted(() => {
  const shortcutId = registerShortcut({
    id: 'my-shortcut',
    key: '/',
    description: 'Focus search',
    handler: () => searchRef.value?.focus(),
    allowInInput: false,
    preventDefault: true
  })
})
```

### Common Shortcuts:
```javascript
CommonShortcuts.SEARCH          // / key
CommonShortcuts.SEARCH_ALT      // Ctrl+K
CommonShortcuts.ESCAPE          // Esc key
CommonShortcuts.HELP            // Shift+?
CommonShortcuts.SAVE            // Ctrl+S
```

---

## 4. Focus Management

### Import:
```javascript
import { useModal } from '@/composables/useModal'
```

### Usage:
```javascript
const {
  modalRef,
  isOpen,
  hasUnsavedChanges,
  open,
  close,
  markUnsaved,
  markSaved
} = useModal({
  modalId: 'myModal',
  onClose: () => resetForm(),
  closeOnEscape: true,
  trapFocus: true,
  preventBodyScroll: true
})

// Mark form as having unsaved changes
const handleInput = () => {
  markUnsaved()
}

// Mark form as saved
const handleSubmit = () => {
  // Save logic
  markSaved()
  close()
}
```

---

## 5. Modal Accessibility Checklist

When creating or updating a modal, ensure:

```vue
<div
  class="modal fade"
  id="modalId"
  tabindex="-1"
  aria-labelledby="modalLabelId"
  aria-modal="true"
  role="dialog"
>
  <div class="modal-dialog modal-dialog-scrollable">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="modalLabelId">Title</h5>
        <button class="btn-close" aria-label="Close"></button>
      </div>
      <div class="modal-body">
        <!-- Form fields with labels -->
        <label for="inputId">Field <span class="text-danger">*</span></label>
        <input id="inputId" required aria-required="true">
      </div>
    </div>
  </div>
</div>
```

**Requirements:**
- ✅ `aria-labelledby` points to modal title
- ✅ `aria-modal="true"` present
- ✅ `role="dialog"` present
- ✅ All inputs have labels with `for` attribute
- ✅ Required fields marked with `*` and `aria-required`
- ✅ Close button has `aria-label="Close"`
- ✅ Icon-only buttons have `aria-label`
- ✅ Error messages have `role="alert"`

---

## 6. Design Tokens

Use CSS variables for consistency:

### Colors:
```css
var(--color-primary)        /* #2563EB */
var(--color-success)        /* #059669 */
var(--color-danger)         /* #DC2626 */
var(--color-warning)        /* #D97706 */
var(--color-info)           /* #0891B2 */
```

### Spacing:
```css
var(--space-0-5)           /* 4px */
var(--space-1)             /* 8px */
var(--space-2)             /* 16px */
var(--space-3)             /* 24px */
var(--space-4)             /* 32px */
```

### Typography:
```css
var(--font-size-h1)        /* 2rem - 32px */
var(--font-size-h2)        /* 1.67rem - 26.72px */
var(--font-size-h4)        /* 1.17rem - 18.72px */
var(--font-size-body)      /* 1rem - 16px */
var(--font-size-small)     /* 0.83rem - 13.28px */
```

### Animations:
```css
var(--duration-instant)    /* 100ms */
var(--duration-fast)       /* 200ms */
var(--duration-normal)     /* 300ms */
var(--ease-out)           /* cubic-bezier(0, 0, 0.2, 1) */
```

---

## 7. Common Patterns

### Loading Button:
```vue
<button :disabled="loading" class="btn btn-primary">
  <span v-if="loading" class="spinner-border spinner-border-sm me-2" aria-hidden="true"></span>
  {{ loading ? 'Saving...' : 'Save' }}
</button>
```

### Icon Button:
```vue
<button class="btn btn-outline-primary" aria-label="Edit this item">
  <i class="bi bi-pencil me-1" aria-hidden="true"></i>
  Edit
</button>
```

### Error Alert:
```vue
<div v-if="error" class="alert alert-danger" role="alert">
  <i class="bi bi-exclamation-triangle me-2" aria-hidden="true"></i>
  {{ error }}
</div>
```

### Loading State:
```vue
<div v-if="loading">
  <StockCardSkeleton />
</div>
<div v-else>
  <!-- Content -->
</div>
```

---

## 8. Accessibility Quick Tips

1. **Always use semantic HTML:**
   - `<button>` for clickable actions
   - `<a>` for navigation
   - `<article>` for self-contained content

2. **All images/icons need alt text or aria-hidden:**
   ```vue
   <i class="bi bi-check" aria-hidden="true"></i>
   ```

3. **Form inputs need labels:**
   ```vue
   <label for="input">Label</label>
   <input id="input">
   ```

4. **Loading states need ARIA:**
   ```vue
   <div role="status" aria-live="polite">
     <span class="visually-hidden">Loading...</span>
   </div>
   ```

5. **Buttons need descriptive labels:**
   ```vue
   <button aria-label="Delete this stock">
     <i class="bi bi-trash"></i>
   </button>
   ```

---

## Quick Links

- [Phase 2 Full Documentation](/Users/aeldeeb/Ahmed/git/stock-tracker/PHASE2_IMPLEMENTATION_COMPLETE.md)
- [Phase 1 Documentation](/Users/aeldeeb/Ahmed/git/stock-tracker/PHASE1_IMPLEMENTATION_COMPLETE.md)
- [UI/UX Specification](/Users/aeldeeb/Ahmed/git/stock-tracker/docs/ui-spec.md)
