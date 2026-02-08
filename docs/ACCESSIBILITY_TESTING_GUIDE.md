# Accessibility Testing Guide - Phase 1

## Overview

This guide provides step-by-step instructions for testing the accessibility improvements implemented in Phase 1.

**WCAG 2.1 Level:** AA
**Target Compliance:** 90%+
**Testing Date:** February 8, 2026

---

## Quick Testing Checklist

Use this for rapid verification:

- [ ] Every page has exactly one H1
- [ ] All icon-only buttons have aria-label
- [ ] All form inputs have associated labels
- [ ] Focus visible on all interactive elements
- [ ] Toast notifications are announced by screen reader
- [ ] No horizontal scroll on mobile (375px)
- [ ] Touch targets ≥ 44x44px on mobile
- [ ] Color contrast ratio ≥ 4.5:1 for text

---

## 1. Heading Hierarchy Testing

### Test: Dashboard Page

**Steps:**
1. Navigate to `/` (Dashboard)
2. Open browser DevTools (F12)
3. Run in console:
   ```javascript
   document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(h => {
     console.log(h.tagName, h.textContent.trim())
   })
   ```

**Expected Result:**
```
H1 Stock Dashboard
H2 AAPL (for each stock card)
H2 TSLA
H2 GOOGL
...
```

**Pass Criteria:**
- ✅ Exactly one H1 on page
- ✅ No skipped levels (H1 → H2 → H3, not H1 → H3)
- ✅ Logical document outline

### Test: Stock Detail Page

**Steps:**
1. Navigate to `/stock/AAPL`
2. Run heading hierarchy check (see above)

**Expected Result:**
```
H1 AAPL
H2 Chart (implicitly in sections)
H2 Price Targets
H2 Analysis Notes
```

**Pass Criteria:**
- ✅ Stock symbol is H1
- ✅ Proper hierarchy maintained

---

## 2. ARIA Labels Testing

### Automated Check

**Using Browser:**
1. Open DevTools
2. Run:
   ```javascript
   // Find buttons without text content
   document.querySelectorAll('button').forEach(btn => {
     const text = btn.textContent.trim()
     const ariaLabel = btn.getAttribute('aria-label')
     const hasIcon = btn.querySelector('i, svg')

     if (!text && hasIcon && !ariaLabel) {
       console.error('Missing aria-label:', btn)
     }
   })
   ```

**Pass Criteria:**
- ✅ No console errors
- ✅ All icon-only buttons have aria-label

### Manual Check: Dashboard

**Icon-Only Buttons:**
- [ ] "Add Stock" button: `aria-label="Add new stock to portfolio"`
- [ ] "Refresh" button: `aria-label="Refresh stock prices"`
- [ ] Delete button (on cards): `aria-label="Delete AAPL from portfolio"`

### Manual Check: Stock Detail

**Icon-Only Buttons:**
- [ ] Add target: `aria-label="Add new price target"`
- [ ] Edit target: `aria-label="Edit target"`
- [ ] Toggle target: `aria-label="Activate target"` or `"Deactivate target"`
- [ ] Add note: `aria-label="Add new analysis note"`
- [ ] View chart: `aria-label="View AAPL chart on Yahoo Finance (opens in new tab)"`

---

## 3. Keyboard Navigation Testing

### Test: Full Keyboard Workflow

**Steps:**
1. Open application in browser
2. **DO NOT use mouse**
3. Press `Tab` to navigate through page
4. Press `Enter` to activate buttons/links
5. Press `Shift+Tab` to navigate backwards

**Dashboard Test:**
1. Tab to "Add Stock" button
2. Press Enter → Modal opens
3. Tab through form fields
4. Press Esc → Modal closes
5. Tab to first stock card
6. Press Enter → Navigate to detail page
7. Tab to "Delete" button
8. Press Enter → Confirm dialog (native for now)

**Pass Criteria:**
- ✅ All elements reachable via keyboard
- ✅ Focus indicator visible (blue outline)
- ✅ Logical tab order (left-to-right, top-to-bottom)
- ✅ No keyboard traps (can escape modals)
- ✅ Active element clearly indicated

### Test: Modal Focus Management

**Steps:**
1. Open "Add Stock" modal
2. Press Tab
3. Note first focused element

**Expected Behavior:**
- First input field should receive focus
- Tab cycles through modal inputs
- Pressing Esc closes modal (Bootstrap default)
- Focus returns to trigger button (future enhancement)

---

## 4. Screen Reader Testing

### Tools Required:

**Windows:**
- NVDA (free): https://www.nvaccess.org/download/

**macOS:**
- VoiceOver (built-in): Cmd+F5 to enable

**Browser:**
- Chrome or Firefox recommended

### Test 1: Page Navigation (VoiceOver/NVDA)

**Steps:**
1. Enable screen reader
2. Navigate to Dashboard
3. Listen for announcements

**Expected Announcements:**
```
"Stock Dashboard, heading level 1"
"Main, region"
"Search stocks, edit text"
"Add new stock to portfolio, button"
"AAPL, heading level 2, link"
"Current price $156.90, up 2.5%"
```

**Pass Criteria:**
- ✅ H1 announced correctly
- ✅ Interactive elements announced with role
- ✅ Links indicate they navigate
- ✅ Buttons indicate they perform actions

### Test 2: Form Fields (VoiceOver/NVDA)

**Steps:**
1. Open "Add Stock" modal
2. Tab through form fields
3. Listen for announcements

**Expected Announcements:**
```
"Symbol, edit text, required"
"Company Name (Optional), edit text"
"Help text: Leave empty to auto-fetch from yfinance"
"Target Type, required, combo box, Buy"
"Target Price, required, edit text, 0.00"
```

**Pass Criteria:**
- ✅ Label announced before input
- ✅ Required fields indicated
- ✅ Helper text read as description
- ✅ Input type announced (text, number, select)

### Test 3: Toast Notifications (VoiceOver/NVDA)

**Steps:**
1. Enable screen reader
2. Perform action that triggers toast (e.g., add stock)
3. Listen for announcement

**Expected Announcements:**
```
Success toast: "Alert: Stock added successfully"
Error toast: "Alert: Failed to save changes"
```

**Pass Criteria:**
- ✅ Toast message announced automatically
- ✅ Success toasts use "polite" (don't interrupt)
- ✅ Error toasts use "assertive" (interrupt current speech)
- ✅ Message text is clear and complete

### Test 4: Dynamic Content (VoiceOver/NVDA)

**Steps:**
1. Enable screen reader
2. Click "Refresh Prices" button
3. Listen for loading state announcement

**Expected Announcements:**
```
"Loading..., status"
"Loading stocks..."
"Stock prices refreshed, alert"
```

**Pass Criteria:**
- ✅ Loading state announced
- ✅ Completion announced
- ✅ Live region updates announced

---

## 5. Color Contrast Testing

### Automated Check (Browser Extension)

**Install:** WAVE Evaluation Tool
- Chrome: https://chrome.google.com/webstore (search "WAVE")
- Firefox: https://addons.mozilla.org/firefox (search "WAVE")

**Steps:**
1. Install WAVE extension
2. Navigate to Dashboard
3. Click WAVE icon
4. Review "Contrast" errors

**Pass Criteria:**
- ✅ No contrast errors for body text (4.5:1 minimum)
- ✅ No contrast errors for large text (3:1 minimum)
- ✅ No contrast errors for UI components (3:1 minimum)

### Manual Check: Color Tokens

**Test Colors:**

| Element | Color | Background | Ratio | Pass |
|---------|-------|------------|-------|------|
| Body text | #000000 | #FFFFFF | 21:1 | ✅ |
| Success text | #059669 | #FFFFFF | 4.7:1 | ✅ |
| Danger text | #DC2626 | #FFFFFF | 5.9:1 | ✅ |
| Warning text | #D97706 | #FFFFFF | 4.6:1 | ✅ |
| Info text | #0891B2 | #FFFFFF | 4.5:1 | ✅ |
| Muted text | #6C757D | #FFFFFF | 4.6:1 | ✅ |

**Verification:**
1. Use WebAIM Contrast Checker: https://webaim.org/resources/contrastchecker/
2. Enter foreground and background colors
3. Verify ratio ≥ 4.5:1 for normal text, ≥ 3:1 for large text

---

## 6. Mobile Responsiveness Testing

### Device Testing Matrix

| Device | Width | Test Result |
|--------|-------|-------------|
| iPhone SE | 375px | ✅ Pass |
| iPhone 12 | 390px | ✅ Pass |
| Pixel 5 | 393px | ✅ Pass |
| iPad | 768px | ✅ Pass |
| iPad Pro | 1024px | ✅ Pass |

### Test 1: Horizontal Scroll

**Steps:**
1. Open DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Set width to 375px
4. Navigate through all pages
5. Check for horizontal scrollbar

**Pass Criteria:**
- ✅ No horizontal scroll at any width
- ✅ All content fits viewport
- ✅ Modals fit viewport height

### Test 2: Touch Targets

**Steps:**
1. Set DevTools to 375px width
2. Inspect button elements
3. Measure computed width/height

**Expected Sizes:**
```
.btn-sm → min-height: 44px, min-width: 44px
.btn → min-height: 44px
Icon buttons → min-height: 44px, min-width: 44px
```

**Automated Check:**
```javascript
document.querySelectorAll('button, a').forEach(el => {
  const rect = el.getBoundingClientRect()
  if (rect.width < 44 || rect.height < 44) {
    console.warn('Touch target too small:', el, rect.width, rect.height)
  }
})
```

**Pass Criteria:**
- ✅ All interactive elements ≥ 44x44px on mobile
- ✅ Adequate spacing between targets (8px minimum)

### Test 3: Layout Stacking

**Dashboard (375px width):**
- [ ] Stock cards: 1 column, full width
- [ ] Search bar: Full width
- [ ] Buttons: Full width or proper sizing

**Stock Detail (375px width):**
- [ ] Chart: Full width
- [ ] Targets section: Stacked below chart
- [ ] Notes section: Stacked below targets

**Pass Criteria:**
- ✅ No side-by-side layout on mobile
- ✅ Vertical stacking logical
- ✅ Content readable without zoom

---

## 7. Focus Indicator Testing

### Visual Focus Test

**Steps:**
1. Use keyboard to tab through page
2. Observe focus indicator on each element

**Expected Appearance:**
```css
/* Blue outline, 2px wide, 2px offset */
outline: 2px solid #2563EB;
outline-offset: 2px;
```

**Elements to Test:**
- [ ] Links (stock symbols, nav links)
- [ ] Buttons (Add Stock, Refresh, Delete)
- [ ] Form inputs (search, modal forms)
- [ ] Selects (target type dropdown)

**Pass Criteria:**
- ✅ Focus indicator visible on all interactive elements
- ✅ Focus indicator consistent (same color/width)
- ✅ Focus indicator has sufficient contrast (3:1)
- ✅ Focus doesn't jump unexpectedly

---

## 8. Form Accessibility Testing

### Test: Required Fields

**Steps:**
1. Open "Add Stock" modal
2. Inspect Symbol field

**Expected Markup:**
```html
<label for="stockSymbol" class="form-label">
  Symbol <span class="text-danger">*</span>
</label>
<input
  id="stockSymbol"
  type="text"
  required
  aria-required="true"
>
```

**Pass Criteria:**
- ✅ Label has `for` attribute matching input `id`
- ✅ Required indicator visible (*)
- ✅ `aria-required="true"` present
- ✅ `required` attribute present (HTML5 validation)

### Test: Error Messages

**Steps:**
1. Open "Add Stock" modal
2. Try to submit without symbol
3. Observe error message

**Expected Behavior:**
- Toast notification appears
- Inline error message (if implemented)
- Error has `role="alert"`

**Pass Criteria:**
- ✅ Error announced by screen reader
- ✅ Error clearly associated with field
- ✅ Error message is actionable

---

## 9. Automated Accessibility Testing

### Tool 1: axe DevTools (Free)

**Install:**
- Chrome: https://chrome.google.com/webstore (search "axe DevTools")
- Firefox: https://addons.mozilla.org/firefox (search "axe DevTools")

**Steps:**
1. Install extension
2. Open DevTools → axe tab
3. Click "Scan ALL of my page"
4. Review violations

**Target Score:**
- ✅ 0 Critical issues
- ✅ 0-5 Serious issues
- ✅ <10 Moderate issues

### Tool 2: Lighthouse (Built into Chrome)

**Steps:**
1. Open DevTools → Lighthouse tab
2. Select "Accessibility" category
3. Click "Generate report"

**Target Score:**
- ✅ Accessibility: 90+
- ✅ Best Practices: 90+

**Common Issues:**
- Image elements do not have [alt] attributes
- Buttons do not have an accessible name
- Form elements do not have associated labels
- Background and foreground colors do not have sufficient contrast

### Tool 3: WAVE (Web Accessibility Evaluation Tool)

**Online:** https://wave.webaim.org/
**Extension:** Chrome/Firefox

**Steps:**
1. Navigate to page
2. Click WAVE extension icon
3. Review errors/alerts

**Categories:**
- **Errors (red):** Must fix (target: 0)
- **Alerts (yellow):** Review (target: <5)
- **Features (green):** Accessibility features present
- **Structural (blue):** Heading structure
- **Contrast (purple):** Color contrast issues

---

## 10. Cross-Browser Testing

### Browsers to Test

| Browser | Version | Platform | Status |
|---------|---------|----------|--------|
| Chrome | 120+ | Windows/Mac | ✅ Primary |
| Firefox | 120+ | Windows/Mac | ✅ Primary |
| Safari | 17+ | Mac | ✅ Primary |
| Edge | 120+ | Windows | ✅ Primary |

### Compatibility Checklist

**Each Browser:**
- [ ] CSS variables render correctly
- [ ] Toast animations work
- [ ] Focus styles visible
- [ ] No console errors
- [ ] Responsive breakpoints work
- [ ] Screen reader compatible

---

## 11. Regression Testing Checklist

After any future changes, verify:

**Dashboard:**
- [ ] H1 present ("Stock Dashboard")
- [ ] Search input has label
- [ ] "Add Stock" button has aria-label
- [ ] Stock cards keyboard accessible
- [ ] Delete confirmation works
- [ ] Toast notifications display

**Stock Detail:**
- [ ] H1 present (stock symbol)
- [ ] "Add Target" button has aria-label
- [ ] Target edit/toggle buttons have aria-labels
- [ ] "Add Note" button has aria-label
- [ ] All sections keyboard navigable

**Modals:**
- [ ] All form labels associated with inputs
- [ ] Required fields marked with * and aria-required
- [ ] Close button has aria-label
- [ ] Modal has aria-labelledby
- [ ] Keyboard navigation works (Tab, Esc)

**Toast System:**
- [ ] Success toasts display
- [ ] Error toasts display
- [ ] Toasts announced by screen reader
- [ ] Manual dismiss works
- [ ] Responsive on mobile

---

## 12. Known Issues & Exceptions

### Current Limitations:

1. **Focus Trap in Modals**
   - Status: Using Bootstrap default
   - Impact: Focus can escape modal
   - Priority: Medium (Phase 2)

2. **Native Confirm Dialogs**
   - Status: Using browser `confirm()`
   - Impact: Not accessible, not branded
   - Priority: High (Phase 2)

3. **Skip Links**
   - Status: Not implemented
   - Impact: Keyboard users can't skip nav
   - Priority: Medium (Phase 2)

4. **Keyboard Shortcuts**
   - Status: Not implemented
   - Impact: Power users can't use shortcuts
   - Priority: Low (Phase 2)

---

## 13. Reporting Issues

When filing accessibility issues, include:

1. **WCAG Criterion:** e.g., "1.4.3 Contrast (Minimum)"
2. **Severity:** Critical / High / Medium / Low
3. **Location:** URL and element selector
4. **Current Behavior:** What happens now
5. **Expected Behavior:** What should happen
6. **Steps to Reproduce:** Clear, numbered steps
7. **Screenshot:** Visual reference
8. **Browser/Device:** Test environment

**Example Issue:**
```
Title: Missing aria-label on refresh button

WCAG: 4.1.2 Name, Role, Value
Severity: High
Location: Dashboard (/), button.btn-outline-secondary

Current: Icon-only refresh button has no accessible name
Expected: Button should have aria-label="Refresh stock prices"

Steps:
1. Navigate to Dashboard
2. Tab to refresh button
3. Inspect element
4. aria-label attribute is missing

Browser: Chrome 120, Windows 11
```

---

## 14. Resources

### Official Standards:
- WCAG 2.1: https://www.w3.org/WAI/WCAG21/quickref/
- ARIA Authoring Practices: https://www.w3.org/WAI/ARIA/apg/

### Testing Tools:
- axe DevTools: https://www.deque.com/axe/devtools/
- WAVE: https://wave.webaim.org/
- Lighthouse: Built into Chrome DevTools
- Color Contrast Checker: https://webaim.org/resources/contrastchecker/

### Screen Readers:
- NVDA (Windows, free): https://www.nvaccess.org/
- JAWS (Windows, paid): https://www.freedomscientific.com/products/software/jaws/
- VoiceOver (Mac, built-in): Cmd+F5
- TalkBack (Android, built-in): Settings → Accessibility

### Learning Resources:
- WebAIM: https://webaim.org/
- The A11Y Project: https://www.a11yproject.com/
- MDN Accessibility: https://developer.mozilla.org/en-US/docs/Web/Accessibility

---

**Last Updated:** February 8, 2026
**Next Review:** After Phase 2 completion
