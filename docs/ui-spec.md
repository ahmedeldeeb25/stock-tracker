# Stock Tracker - UI/UX Specification
**Version:** 1.0
**Date:** February 7, 2026
**Designer:** Senior UX/UI & Product Designer
**Status:** Initial Analysis & Recommendations

---

## Executive Summary

The Stock Tracker application demonstrates a functional financial tracking interface built with Vue.js 3, Bootstrap 5, and Vite. This specification documents the current UI state and provides actionable recommendations to improve:

- Mobile responsiveness (critical gaps identified)
- WCAG 2.1 AA accessibility compliance (~35% currently)
- Visual consistency and design system
- User feedback and interactive states
- Information hierarchy and readability

**Estimated Impact:** 6-8 weeks for comprehensive improvements
**Priority:** Critical fixes for mobile + accessibility (Weeks 1-2)

---

## 1. Design System Foundation

### 1.1 Typography Scale (Modular 1.2x)

```
H1: 2.0rem (32px) - Page titles
H2: 1.67rem (26.72px) - Section headers
H3: 1.39rem (22.27px) - Subsection headers
H4: 1.17rem (18.72px) - Card titles
Body: 1rem (16px) - Default text
Small: 0.83rem (13.28px) - Secondary info
```

**Current Issues:**
- No H1 present (missing page hierarchy)
- Inconsistent heading structure (H2 → H5, skipping H3/H4)
- Mixed font-weight usage (`fw-bold`, `fw-semibold`, inline styles)

### 1.2 Spacing Scale (8pt Grid System)

```
4px (0.5x) - Inline elements
8px (1x) - Between components
16px (2x) - Between components
24px (3x) - Between sections
32px (4x) - Between major sections
```

**Current Issues:**
- Inconsistent gap values (mb-4, mb-3, mb-2, g-4)
- No adherence to 8px base unit
- Excessive nested spacing

### 1.3 Color Palette

**Primary Colors:**
```
Primary: #0D6EFD (current) → Proposed: #2563EB (Tailwind blue-600)
Success: #198754 → Proposed: #059669 (better contrast)
Danger: #DC3545 → Proposed: #DC2626
Warning: #FFC107 → Proposed: #D97706 (WCAG compliant)
Info: #0DCAF0 → Proposed: #0891B2
```

**Grayscale:**
```
Gray-50: #F9FAFB (very light backgrounds)
Gray-100: #F3F4F6 (light backgrounds)
Gray-600: #6C757D (muted text)
Gray-900: #111827 (headings)
```

**Accessibility Note:**
Current warning color (#FFC107) fails WCAG AA contrast ratio on white backgrounds (ratio < 2:1).

---

## 2. Critical Issues Summary

### 2.1 Mobile Responsiveness (CRITICAL)

**Issues:**
- StockDetail sidebar forces horizontal scroll below md breakpoint
- Modals overflow viewport on small screens
- Touch targets below 44px minimum
- Grid layout doesn't adapt properly on xs/sm

**Fix Priority:** Week 1

### 2.2 Accessibility Compliance (CRITICAL)

**WCAG 2.1 Failures:**
| Criterion | Status | Impact |
|-----------|--------|--------|
| 1.1.1 Non-text Content | FAIL | No alt text for icons |
| 1.4.3 Contrast | FAIL | Warning color, muted text |
| 2.1.1 Keyboard | PARTIAL | No shortcuts, poor focus management |
| 4.1.2 Name, Role, Value | FAIL | Missing aria-labels on icon buttons |
| 4.1.3 Status Messages | FAIL | No aria-live regions |

**Current Compliance:** ~35-40%
**Target:** 100% WCAG 2.1 AA

**Fix Priority:** Week 1-2

### 2.3 Visual Hierarchy (HIGH)

**Issues:**
- No H1 on any page
- Information scattered across multiple elements
- Price display hierarchy unclear
- Badge overuse creates visual noise

**Fix Priority:** Week 3

---

## 3. Component Specifications

### 3.1 Dashboard (Dashboard.vue)

**Current Layout:**
```
Header
├─ Title (H2)
├─ Add Stock button
└─ Refresh Prices button

Filters
├─ Search input
└─ Tag filter dropdown

Stock Grid
└─ 3 columns (lg), 2 columns (md), 1 column (sm/xs)
```

**Proposed Improvements:**

**Visual Tokens:**
```css
--dashboard-padding: 24px
--card-gap: 16px
--header-margin: 32px
--filter-bar-height: 56px
```

**Behavior:**
- Add breadcrumb: Home > Dashboard
- Sticky filter bar on scroll
- Add skeleton loaders instead of spinner
- Add view toggle (Grid / List)
- Add sort dropdown (Symbol, Price Change, Date Added)

**Responsive Breakpoints:**
- lg (≥1024px): 3 columns
- md (≥768px): 2 columns
- sm/xs (<768px): 1 column

**Empty State:**
```
[Inbox icon - display-1]
"No stocks in your portfolio"
"Track stock prices and get alerts when targets hit"
[Add Your First Stock - btn-primary]
```

### 3.2 StockCard Component (StockCard.vue)

**Current Hierarchy (Issues):**
```
Stock Symbol (H5) + Price (H5) → Same level (confusing)
Company Name (small muted)
Price change (small colored)
After-hours (very small)
Tags (very small badges)
Targets (small text)
```

**Proposed Hierarchy:**
```
[Priority 1] Stock Symbol (H4, 1.17rem)
[Priority 2] Current Price (1.5rem, bold)
[Priority 3] Change: +$2.30 (+2.5%) (0.9rem, colored, fw-semibold)
[Priority 4] After Hours: $157.20 +0.19% (0.75rem, muted)
[Priority 5] Company Name (0.83rem, muted)
[Priority 6] Tags (badges, 0.75rem)
[Priority 7] Active Targets (0.83rem)
[Priority 8] Note count (0.75rem, bottom-right)
```

**Visual Tokens:**
```css
--card-padding: 16px
--card-border: 1px solid #E5E7EB
--card-radius: 8px
--card-shadow-hover: 0 4px 12px rgba(0, 0, 0, 0.1)
--price-size: 1.5rem
--symbol-size: 1.17rem
```

**Behavior:**
- Hover: Lift card 2px, add shadow
- Click: Navigate to stock detail
- Loading: Skeleton loader, not blank card

**States:**
```
Default: Standard card
Hover: Transform translateY(-2px), shadow
Active: N/A (navigates away)
Loading: Skeleton loader with pulsing animation
Error: Red border + error icon
```

**Accessibility:**
- Link wraps entire card (not just symbol)
- aria-label: "View details for AAPL, Apple Inc, Current price $156.90, up 2.5%"
- Keyboard accessible (tab to card, Enter to open)

### 3.3 StockDetail View (StockDetail.vue)

**Current Layout:**
```
Header (Symbol + Price + Refresh)
Tags Section
Two-Column Layout:
├─ Left (8/12): Chart, Targets, Alert History
└─ Right (4/12): Analysis Notes
```

**Issues:**
- Sidebar doesn't stack on mobile
- Chart height fixed (500px)
- No breadcrumb navigation
- Too much content on one page

**Proposed Layout (Responsive):**

**Desktop (≥1024px):**
```
Breadcrumb: Dashboard > AAPL
Header Section (Sticky):
├─ Symbol (H1) + Google Finance link
├─ Company Name
├─ Current Price + Change + After Hours + RSI
└─ Tags (clickable)

Tabbed Interface:
├─ Overview (Chart + Key Metrics)
├─ Targets (Price Targets List)
├─ Notes (Analysis Notes)
└─ History (Alert History)
```

**Mobile (<768px):**
```
Single column stack:
1. Header (sticky)
2. Price display
3. Tags
4. Tabs (full-width)
5. Tab content (full-width)
```

**Visual Tokens:**
```css
--detail-header-height: 120px
--detail-padding: 24px
--sticky-offset: 0px
--tab-height: 48px
--content-padding: 16px
```

**Behavior:**
- Sticky header on scroll
- Tab navigation with URL hash (#overview, #targets, #notes, #history)
- Chart auto-height (responsive)
- Lazy load tabs (don't load all content upfront)

**Accessibility:**
- H1: Stock symbol
- Tab navigation keyboard accessible
- Focus management: Tab → Card → Button
- ARIA: role="tablist", aria-selected, aria-controls

### 3.4 Modal Components

**Current Issues:**
- Modals can stack (ViewNote → EditNote)
- No focus trap
- No unsaved changes warning
- Forms feel cramped
- No progress indication for multi-step flows

**Proposed Modal System:**

**Visual Tokens:**
```css
--modal-backdrop: rgba(0, 0, 0, 0.5)
--modal-width-sm: 400px
--modal-width-md: 600px
--modal-width-lg: 800px
--modal-padding: 24px
--modal-header-height: 60px
--modal-footer-height: 72px
--modal-radius: 12px
--modal-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1)
```

**Behavior:**
```
1. Modal opens: Fade in backdrop + scale in modal
2. Focus trap: Tab cycles within modal
3. Escape key: Close with confirmation if form dirty
4. Click backdrop: Close with confirmation if form dirty
5. Form submit: Loading state → Success toast → Close
6. Error: Show inline error + shake animation
```

**States:**
```
Opening: opacity 0 → 1, scale 0.95 → 1 (200ms)
Open: Default state
Loading: Disable form, button shows spinner
Error: Red border on invalid fields, error message below
Closing: opacity 1 → 0, scale 1 → 0.95 (150ms)
```

**Accessibility:**
- Focus on first input on open
- Return focus to trigger button on close
- aria-modal="true"
- aria-labelledby points to modal title
- role="dialog"

---

## 4. Interactive Elements

### 4.1 Button System

**Button Hierarchy:**
```
Primary: Main action (Add Stock, Save, Submit)
Secondary: Supporting actions (Cancel, Back)
Tertiary: Less important (View More, Learn More)
Destructive: Dangerous actions (Delete, Remove)
Ghost: Minimal (icon-only actions)
```

**Visual Tokens:**
```css
/* Primary Button */
--btn-primary-bg: #2563EB
--btn-primary-hover: #1D4ED8
--btn-primary-active: #1E40AF
--btn-primary-disabled: #93C5FD
--btn-primary-shadow: 0 1px 2px rgba(0, 0, 0, 0.05)

/* Button Sizing */
--btn-height-sm: 32px
--btn-height-md: 40px
--btn-height-lg: 48px
--btn-padding-x-sm: 12px
--btn-padding-x-md: 16px
--btn-padding-x-lg: 20px
--btn-radius: 6px
```

**Button States (All buttons must define):**
```
Default: Standard appearance
Hover: Darker background (8-10%)
Active: Even darker (12-15%)
Focus: 2px outline, 2px offset
Disabled: 40% opacity, cursor not-allowed
Loading: Spinner + disabled state
```

**Accessibility:**
- Minimum touch target: 44x44px
- All icon-only buttons need aria-label
- Focus visible on all buttons (2px outline)
- Loading state announced to screen readers

### 4.2 Form Elements

**Input Field:**
```css
--input-height: 40px
--input-padding: 12px
--input-border: 1px solid #D1D5DB
--input-border-focus: 2px solid #2563EB
--input-radius: 6px
--input-label-spacing: 4px
```

**States:**
```
Default: Gray border
Hover: Darker gray border
Focus: Blue 2px border, remove outline
Error: Red 2px border, red text below
Disabled: Gray background, not-allowed cursor
```

**Required Fields:**
- Asterisk (*) after label in red
- aria-required="true"
- Validate on blur (not on keypress)

**Validation:**
- Show error on blur or submit
- Inline error message below field
- Icon in field (✗ for error, ✓ for success)
- Error message: Red text, 0.83rem, specific

**Accessibility:**
- Label always visible (never placeholder-only)
- aria-describedby for helper text
- aria-invalid="true" on error
- Error message has role="alert"

### 4.3 Toast Notifications

**Proposed System (Currently Missing):**

**Visual Tokens:**
```css
--toast-width: 360px
--toast-height: auto
--toast-padding: 16px
--toast-radius: 8px
--toast-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1)
--toast-position: top-right
--toast-offset: 24px
```

**Variants:**
```
Success: Green background, checkmark icon
Error: Red background, error icon
Warning: Orange background, warning icon
Info: Blue background, info icon
```

**Behavior:**
```
1. Slide in from right (200ms)
2. Display for 4 seconds (configurable)
3. User can dismiss by clicking X
4. Auto-dismiss: Fade out + slide right (200ms)
5. Multiple toasts stack vertically
```

**Copy Examples:**
```
✓ Stock added successfully
✓ Target updated
✓ Note saved
⚠ Warning: Target already exists
✗ Error: Failed to save. Please try again.
```

**Accessibility:**
- role="alert" for errors
- role="status" for success
- aria-live="polite" or "assertive" based on severity
- Screen reader announces content

---

## 5. Responsive Design Specifications

### 5.1 Breakpoint System

```
xs: 0-575px (Mobile portrait)
sm: 576-767px (Mobile landscape)
md: 768-1023px (Tablet)
lg: 1024-1279px (Desktop)
xl: 1280px+ (Large desktop)
```

### 5.2 Component Behavior by Breakpoint

**Dashboard:**
| Breakpoint | Columns | Card Width | Filters |
|------------|---------|------------|---------|
| xl | 3 | ~33% | Horizontal |
| lg | 3 | ~33% | Horizontal |
| md | 2 | ~50% | Horizontal |
| sm | 1 | 100% | Vertical |
| xs | 1 | 100% | Vertical |

**StockDetail:**
| Breakpoint | Layout | Chart | Sidebar |
|------------|--------|-------|---------|
| xl | 2-col | 500px | Visible |
| lg | 2-col | 500px | Visible |
| md | 2-col | 400px | Visible |
| sm | 1-col | 100% | Below |
| xs | Tabs | 100% | Tab |

**Modals:**
| Breakpoint | Width | Height | Padding |
|------------|-------|--------|---------|
| xl | 800px | auto | 24px |
| lg | 600px | auto | 24px |
| md | 90% | auto | 20px |
| sm | 95% | 90vh | 16px |
| xs | 100% | 100vh | 12px |

### 5.3 Touch Targets (Mobile)

**Minimum Sizes:**
- Buttons: 44x44px (iOS/Android guideline)
- Links: 44x44px
- Form inputs: 48px height
- Clickable cards: Full card area (minimum 60px height)
- Icon buttons: 44x44px (add padding if icon smaller)

**Spacing:**
- Minimum 8px between touch targets
- Recommended 12-16px for comfortable tapping

---

## 6. Accessibility Requirements

### 6.1 WCAG 2.1 AA Compliance Checklist

**Perceivable:**
- [ ] Add alt text to all icons and images
- [ ] Ensure contrast ratio ≥ 4.5:1 for text
- [ ] Ensure contrast ratio ≥ 3:1 for UI elements
- [ ] Don't rely on color alone (add icons/text)
- [ ] Support text resize to 200%

**Operable:**
- [ ] All functionality available via keyboard
- [ ] Visible focus indicators on all interactive elements
- [ ] Reasonable focus order (logical tab order)
- [ ] No keyboard traps
- [ ] Provide skip links ("Skip to main content")

**Understandable:**
- [ ] Use clear, concise language
- [ ] Provide input labels and instructions
- [ ] Identify input errors clearly
- [ ] Suggest error corrections
- [ ] Warn users before actions that lose data

**Robust:**
- [ ] Use semantic HTML (nav, main, article, etc.)
- [ ] Provide ARIA labels where needed
- [ ] Ensure compatibility with screen readers
- [ ] Use valid HTML (passes W3C validator)

### 6.2 Screen Reader Testing

**Test with:**
- NVDA (Windows, free)
- JAWS (Windows, paid)
- VoiceOver (macOS, built-in)
- TalkBack (Android, built-in)

**Test Scenarios:**
1. Navigate through dashboard using only keyboard
2. Create a new stock via modal
3. Edit a price target
4. Read stock detail page
5. Understand alert notifications

### 6.3 Keyboard Shortcuts

**Proposed Shortcuts:**
```
/ or Ctrl+K: Focus search
Esc: Close modal (with confirmation if dirty)
Enter: Submit form / Activate button
Tab: Next element
Shift+Tab: Previous element
Arrow keys: Navigate dropdown/select options
Space: Toggle checkbox/radio
```

**Accessibility:**
- Document shortcuts in help modal
- Show shortcuts on hover tooltips
- Don't conflict with browser shortcuts
- Provide alternatives for mouse-only actions

---

## 7. Loading & Error States

### 7.1 Loading States

**Skeleton Loaders (Preferred over spinners):**

**Dashboard:**
```
┌──────────────────────────────┐
│ ████████        ████████████ │  ← Animated gradient pulse
│ ████ ████████                │
│                              │
│ ██████  ██████  ██████       │
│ ████████████  ████████       │
└──────────────────────────────┘
```

**Implementation:**
```css
.skeleton {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s ease-in-out infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

**Spinner (For modals and inline loading):**
```html
<button disabled>
  <span class="spinner-border spinner-border-sm me-2"></span>
  Loading...
</button>
```

### 7.2 Error States

**Inline Errors (Form fields):**
```html
<div class="form-group">
  <label>Stock Symbol</label>
  <input class="form-control is-invalid" value="INVALID">
  <div class="invalid-feedback">
    ✗ Symbol not found. Please check the ticker.
  </div>
</div>
```

**Page-Level Errors:**
```html
<div class="alert alert-danger" role="alert">
  <i class="bi bi-exclamation-triangle me-2"></i>
  <strong>Error:</strong> Failed to load data.
  <button class="btn btn-sm btn-outline-danger ms-3">Retry</button>
</div>
```

**Visual Tokens:**
```css
--error-color: #DC2626
--error-bg: #FEE2E2
--error-border: #FCA5A5
--error-icon-size: 20px
```

### 7.3 Empty States

**Guidelines:**
1. Show large icon (48-64px) at top
2. Primary message: What's missing
3. Secondary message: Why it matters or what to do
4. Call-to-action button
5. Optional: Example or help link

**Dashboard Empty State:**
```
[Inbox icon - 64px]

No stocks in your portfolio

Start tracking stocks to monitor prices and get alerts when
your targets are hit.

[Add Your First Stock]
```

**Notes Empty State:**
```
[Journal icon - 48px]

No analysis notes yet

Add notes to track your research, decisions, and market insights.

[Add First Note]
```

---

## 8. Animation & Transitions

### 8.1 Transition Timing

```css
/* Micro-interactions (button hover, icon change) */
--duration-instant: 100ms

/* UI elements (dropdowns, tooltips, small modals) */
--duration-fast: 200ms

/* Page transitions, large modals, slide-outs */
--duration-normal: 300ms

/* Page loads, complex animations */
--duration-slow: 500ms
```

**Easing Functions:**
```css
--ease-in: cubic-bezier(0.4, 0, 1, 1)
--ease-out: cubic-bezier(0, 0, 0.2, 1)
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1)
```

### 8.2 Component Animations

**Modal:**
```css
/* Opening */
.modal-enter-active {
  transition: all 200ms ease-out;
}
.modal-enter-from {
  opacity: 0;
  transform: scale(0.95);
}

/* Closing */
.modal-leave-active {
  transition: all 150ms ease-in;
}
.modal-leave-to {
  opacity: 0;
  transform: scale(0.95);
}
```

**Toast:**
```css
.toast-enter-active {
  transition: all 200ms ease-out;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-active {
  transition: all 200ms ease-in;
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
```

**Card Hover:**
```css
.card {
  transition: all 200ms ease-out;
}
.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
```

### 8.3 Loading Animations

**Skeleton Pulse:**
```css
@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}
```

**Spinner Rotation:**
```css
@keyframes spin {
  to { transform: rotate(360deg); }
}

.spinner {
  animation: spin 1s linear infinite;
}
```

---

## 9. Microcopy & Messaging

### 9.1 Button Labels

**Be specific and action-oriented:**
```
Good:
- "Add Stock to Portfolio"
- "Save Price Target"
- "Delete Note Permanently"

Bad:
- "Submit"
- "OK"
- "Cancel"
```

### 9.2 Error Messages

**Be helpful, not technical:**
```
Good:
- "We couldn't find that stock symbol. Please double-check the ticker."
- "The target price must be a positive number."
- "Something went wrong. Please try again or contact support."

Bad:
- "ERROR 404"
- "Invalid input"
- "Network request failed"
```

### 9.3 Empty States

**Be encouraging and actionable:**
```
Good:
- "No stocks yet. Add your first one to get started!"
- "Start tracking your favorite stocks"
- "Add analysis notes to remember your research"

Bad:
- "No data"
- "Empty list"
- "Nothing to display"
```

### 9.4 Success Messages

**Be brief and positive:**
```
Good:
- "Stock added ✓"
- "Target saved ✓"
- "Note deleted ✓"

Bad:
- "The stock has been successfully added to your portfolio."
- "Operation completed successfully."
```

---

## 10. Implementation Roadmap

### Phase 1: Critical Fixes (Week 1-2)

**Priority: CRITICAL**

**Tasks:**
1. Mobile Responsiveness
   - [ ] Fix StockDetail sidebar stacking on mobile
   - [ ] Make modals responsive (max-height, overflow)
   - [ ] Increase touch targets to 44px minimum
   - [ ] Test on iPhone SE, iPhone 12, iPad

2. Accessibility Compliance
   - [ ] Add aria-labels to all icon-only buttons
   - [ ] Fix heading hierarchy (add H1 to all pages)
   - [ ] Add focus trap to modals
   - [ ] Add color + text/icon for price changes and badges
   - [ ] Fix contrast ratio on warning color

3. Error Recovery
   - [ ] Add retry button on error states
   - [ ] Implement toast notification system
   - [ ] Add unsaved changes confirmation

**Deliverables:**
- Mobile-responsive views (tested on 5+ devices)
- WCAG 2.1 AA compliance for critical paths
- Toast notification component

### Phase 2: UX Improvements (Week 3-4)

**Priority: HIGH**

**Tasks:**
1. Visual Hierarchy
   - [ ] Implement typography scale (1.2x modular)
   - [ ] Implement 8pt spacing grid
   - [ ] Standardize card styling
   - [ ] Unify badge system

2. Interactive Feedback
   - [ ] Add skeleton loaders (replace spinners)
   - [ ] Add loading states to all async actions
   - [ ] Add success notifications
   - [ ] Add unsaved changes detection

3. Modal System
   - [ ] Replace Bootstrap modals with custom Vue modals
   - [ ] Implement focus management
   - [ ] Add modal state management (prevent stacking)

**Deliverables:**
- Design system documentation (typography, spacing, colors)
- Custom modal component
- Loading state patterns

### Phase 3: Design System (Week 5-6)

**Priority: MEDIUM**

**Tasks:**
1. Component Library
   - [ ] Create breadcrumb component
   - [ ] Create tooltip component
   - [ ] Create skeleton loader component
   - [ ] Create progress stepper component

2. Documentation
   - [ ] Set up Storybook
   - [ ] Document all components
   - [ ] Create accessibility guidelines
   - [ ] Create responsive patterns guide

3. Testing
   - [ ] Set up visual regression testing (Chromatic/Percy)
   - [ ] Set up accessibility testing (Axe/WAVE)
   - [ ] Create responsive testing matrix
   - [ ] Set up CI/CD checks

**Deliverables:**
- Storybook with all components
- Comprehensive documentation
- Automated testing suite

---

## 11. Testing Strategy

### 11.1 Manual Testing Checklist

**Responsive Testing:**
- [ ] iPhone SE (375px)
- [ ] iPhone 12 (390px)
- [ ] Android (412px)
- [ ] iPad (768px)
- [ ] Desktop (1920px)
- [ ] Ultrawide (3440px)

**Browser Testing:**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

**Accessibility Testing:**
- [ ] Keyboard navigation (Tab, Enter, Esc)
- [ ] Screen reader (NVDA/VoiceOver)
- [ ] Color contrast (WAVE/Axe DevTools)
- [ ] Zoom to 200%
- [ ] Color blindness simulation

### 11.2 Automated Testing

**Visual Regression:**
```bash
# Using Chromatic
npm run chromatic

# Using Percy
npm run percy
```

**Accessibility:**
```bash
# Using Axe
npm run test:a11y

# Using Pa11y
npm run test:pa11y
```

**Unit Tests:**
```bash
# Using Vitest
npm run test

# With coverage
npm run test:coverage
```

### 11.3 Success Metrics

**Performance:**
- Lighthouse score: ≥ 90 (Performance, Accessibility, Best Practices)
- First Contentful Paint (FCP): < 1.5s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3s

**Accessibility:**
- WCAG 2.1 AA: 100% compliance
- Keyboard navigation: 100% functionality
- Screen reader: All content accessible

**Responsiveness:**
- All breakpoints tested: xs, sm, md, lg, xl
- Touch targets: ≥ 44px
- Text resize: Functional at 200%

---

## 12. Handoff to Frontend Engineer

### 12.1 Design Assets

**Required:**
1. Figma/Sketch files (if created)
2. Exported SVG icons
3. Color palette as CSS variables
4. Typography scale as CSS classes
5. Component specifications (this document)

**Optional:**
6. Animation prototypes
7. User flow diagrams
8. Wireframes

### 12.2 Technical Constraints

**Don't:**
- Modify backend API
- Change data models
- Alter .env configuration
- Introduce TypeScript (unless discussed)

**Do:**
- Use existing Vue 3 Composition API
- Maintain Bootstrap 5 base (customize with CSS)
- Follow existing component structure
- Use existing tools (Vite, Pinia, Vue Router)

### 12.3 Questions to Resolve

**Before implementation, confirm:**
1. Toast notification library (custom vs. third-party)
2. Modal system (custom vs. Bootstrap replacement)
3. Dark mode requirement (yes/no)
4. Internationalization (i18n) requirement (yes/no)
5. Browser support requirements (specific versions)

---

## 13. Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Feb 7, 2026 | UX/UI Designer | Initial analysis and recommendations |

---

## 14. Next Steps

1. **Review with stakeholders** - Get approval on recommendations
2. **Prioritize fixes** - Confirm roadmap and timeline
3. **Frontend agent review** - Technical feasibility check
4. **Begin Phase 1** - Start critical fixes (mobile + a11y)
5. **Weekly sync** - Review progress and adjust

**Contact:**
For questions or clarifications, reference this document in design reviews.

---

*End of UI/UX Specification Document*
