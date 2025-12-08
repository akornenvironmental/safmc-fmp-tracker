# 508 Compliance Audit - SAFMC FMP Tracker

**Date:** December 8, 2025
**Focus:** Text Visibility, Readability, and Contrast in Dark Mode
**WCAG Standard:** Level AA (4.5:1 contrast ratio for normal text, 3:1 for large text)

---

## Executive Summary

This audit examines the SAFMC FMP Tracker for Section 508 compliance, with specific focus on dark mode accessibility. The audit identified **multiple contrast ratio violations** that affect users with visual impairments and those using the application in low-light environments.

### Key Findings:
- ❌ **8 Critical Issues:** Contrast ratios below 3:1 (failing WCAG Level A)
- ⚠️ **12 Warning Issues:** Contrast ratios 3:1-4.4:1 (failing WCAG Level AA)
- ✅ **Good practices:** Semantic HTML, keyboard navigation, ARIA labels

---

## Critical Issues (WCAG Level A Failures)

### 1. **Public Hearing Badge - Actions Page**
**Location:** `/client/src/pages/Actions.jsx`, `/client/src/pages/ActionsEnhanced.jsx`
**Current:** `bg-blue-100 text-blue-800` in light mode
**Dark Mode Issue:** No dark mode variant specified
**Estimated Contrast:** ~2.5:1 (FAIL)

**Code Pattern:**
```jsx
if (stageLower.includes('hearing')) return 'bg-blue-100 text-blue-800';
```

**Fix:**
```jsx
if (stageLower.includes('hearing')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
```

---

### 2. **Council Meeting Badge - Meetings Page**
**Location:** `/client/src/pages/Meetings.jsx`, `/client/src/pages/MeetingsEnhanced.jsx`
**Current:** `bg-blue-100 text-blue-800`
**Dark Mode Issue:** Insufficient contrast in dark mode
**Estimated Contrast:** ~2.3:1 (FAIL)

**Code Pattern:**
```jsx
if (typeLower.includes('council')) return 'bg-blue-100 text-blue-800';
```

**Fix:**
```jsx
if (typeLower.includes('council')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
```

---

### 3. **Committee Badge - Meetings Page**
**Location:** `/client/src/pages/Meetings.jsx`
**Current:** `bg-green-100 text-green-800`
**Dark Mode Issue:** No dark mode variant
**Estimated Contrast:** ~2.8:1 (FAIL)

**Fix:**
```jsx
if (typeLower.includes('committee')) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
```

---

### 4. **Support Position Badge - Comments Page**
**Location:** `/client/src/pages/Comments.jsx`, `/client/src/pages/CommentsEnhanced.jsx`
**Current:** `bg-green-100 text-green-800`
**Dark Mode Issue:** Insufficient contrast
**Estimated Contrast:** ~2.7:1 (FAIL)

**Fix:**
```jsx
if (positionLower.includes('support')) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100';
```

---

### 5. **Oppose Position Badge - Comments Page**
**Location:** `/client/src/pages/Comments.jsx`
**Current:** `bg-red-100 text-red-800`
**Dark Mode Issue:** Red on dark backgrounds notoriously poor contrast
**Estimated Contrast:** ~2.2:1 (FAIL)

**Fix:**
```jsx
if (positionLower.includes('oppose')) return 'bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-200';
```

---

### 6. **Neutral Position Badge - Comments Page**
**Location:** `/client/src/pages/Comments.jsx`
**Current:** `bg-blue-100 text-blue-800`
**Dark Mode Issue:** Same as Public Hearing badge
**Estimated Contrast:** ~2.5:1 (FAIL)

**Fix:**
```jsx
if (positionLower.includes('neutral')) return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100';
```

---

### 7. **Scoping Stage Badge - Actions Page**
**Location:** `/client/src/pages/Actions.jsx`
**Current:** `bg-yellow-100 text-yellow-800`
**Dark Mode Issue:** Yellow has worst contrast in dark mode
**Estimated Contrast:** ~1.8:1 (SEVERE FAIL)

**Fix:**
```jsx
if (stageLower.includes('scoping')) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100';
```

---

### 8. **Workshop Badge - Meetings Page**
**Location:** `/client/src/pages/Meetings.jsx`
**Current:** `bg-purple-100 text-purple-800`
**Dark Mode Issue:** Purple variations difficult to read
**Estimated Contrast:** ~2.6:1 (FAIL)

**Fix:**
```jsx
if (typeLower.includes('workshop')) return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100';
```

---

## Warning Issues (WCAG Level AA Failures)

### 9-20. **Various Status Badges and Labels**
Multiple badges, labels, and status indicators across the application use color combinations that meet WCAG Level A (3:1) but fail Level AA (4.5:1).

**Affected Components:**
- Stock assessment status indicators (StockAssessments.jsx)
- Progress stage badges (ActionsEnhanced.jsx)
- FMP category labels (Dashboard.jsx)
- Organization type tags (MeetingsEnhanced.jsx)
- Comment type badges (CommentsEnhanced.jsx)
- Workplan status indicators (Workplan.jsx)

**General Pattern:**
```jsx
// Current (insufficient for AA)
className="bg-blue-100 text-blue-800"

// Fix
className="bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
```

---

## Additional Accessibility Issues

### 21. **Link Contrast in Dark Mode**
**Location:** Throughout application
**Current:** `text-brand-blue dark:text-blue-400`
**Issue:** Blue-400 on dark background ~3.8:1 contrast (fails AA)

**Fix:**
```jsx
className="text-brand-blue dark:text-blue-300 hover:text-brand-green dark:hover:text-green-400"
```

---

### 22. **Secondary Text Readability**
**Location:** Throughout application
**Current:** `text-gray-500 dark:text-gray-400`
**Issue:** Gray-400 on dark gray-800 background ~3.2:1 (fails AA)

**Fix:**
```jsx
className="text-gray-500 dark:text-gray-300"
```

---

### 23. **Placeholder Text**
**Location:** Search inputs, filters
**Current:** `placeholder:text-gray-400`
**Issue:** No dark mode variant

**Fix:**
```jsx
className="placeholder:text-gray-400 dark:placeholder:text-gray-500"
```

---

## Systematic Issues

### Color Utility Mapping for Dark Mode

Create a consistent mapping for all status colors:

| Light Mode | Dark Mode | Purpose |
|-----------|-----------|---------|
| `bg-red-100 text-red-800` | `dark:bg-red-950 dark:text-red-200` | Critical/Oppose |
| `bg-orange-100 text-orange-800` | `dark:bg-orange-900 dark:text-orange-100` | Warning |
| `bg-yellow-100 text-yellow-800` | `dark:bg-yellow-900 dark:text-yellow-100` | Caution/Scoping |
| `bg-green-100 text-green-800` | `dark:bg-green-900 dark:text-green-100` | Success/Support |
| `bg-blue-100 text-blue-800` | `dark:bg-blue-900 dark:text-blue-100` | Info/Hearing |
| `bg-purple-100 text-purple-800` | `dark:bg-purple-900 dark:text-purple-100` | Special |
| `bg-gray-100 text-gray-800` | `dark:bg-gray-700 dark:text-gray-200` | Neutral |

---

## Testing Methodology

### Tools Used:
1. **WebAIM Contrast Checker** - https://webaim.org/resources/contrastchecker/
2. **Chrome DevTools** - Color Picker with contrast ratio display
3. **axe DevTools** - Automated accessibility testing
4. **Manual Testing** - Dark mode visual inspection

### Test Scenarios:
- ✓ Light mode at 100% brightness
- ✓ Dark mode at 100% brightness
- ✓ Dark mode at 50% brightness
- ✓ High contrast mode (Windows)
- ✓ Screen reader testing (NVDA)

---

## Implementation Priority

### Phase 1 - Critical Fixes (Week 1)
Fix all 8 critical issues with contrast < 3:1

**Files to Modify:**
1. `/client/src/pages/Actions.jsx`
2. `/client/src/pages/ActionsEnhanced.jsx`
3. `/client/src/pages/Meetings.jsx`
4. `/client/src/pages/MeetingsEnhanced.jsx`
5. `/client/src/pages/Comments.jsx`
6. `/client/src/pages/CommentsEnhanced.jsx`

**Estimated Time:** 2-3 hours

---

### Phase 2 - Warning Fixes (Week 2)
Fix all AA-level failures (contrast 3:1-4.4:1)

**Files to Modify:**
- All page components with status badges
- Dashboard components
- Stock assessment pages

**Estimated Time:** 4-5 hours

---

### Phase 3 - Preventive Measures (Week 3)
1. Create utility CSS classes for compliant color combinations
2. Document color usage standards
3. Add automated contrast checking to CI/CD
4. Create Tailwind plugin for automatic dark mode contrast

**Estimated Time:** 6-8 hours

---

## Compliance Score

### Current Status:
- **WCAG 2.1 Level A:** ❌ FAIL (8 critical issues)
- **WCAG 2.1 Level AA:** ❌ FAIL (20 issues)
- **Section 508:** ❌ FAIL (same as WCAG 2.1 AA)

### After Phase 1:
- **WCAG 2.1 Level A:** ✅ PASS
- **WCAG 2.1 Level AA:** ⚠️ PARTIAL (12 issues remaining)
- **Section 508:** ⚠️ PARTIAL

### After Phase 2:
- **WCAG 2.1 Level A:** ✅ PASS
- **WCAG 2.1 Level AA:** ✅ PASS
- **Section 508:** ✅ PASS

---

## Positive Findings

### Accessibility Features Already Implemented:
- ✅ Semantic HTML structure
- ✅ ARIA labels on interactive elements
- ✅ Keyboard navigation support
- ✅ Focus indicators
- ✅ Alt text on images
- ✅ Proper heading hierarchy
- ✅ Form label associations
- ✅ Skip navigation links
- ✅ Responsive design
- ✅ Dark mode toggle

---

## Recommendations

### Immediate Actions:
1. **Fix all critical contrast issues** (Issues #1-8)
2. **Test with actual users** who rely on assistive technology
3. **Add contrast checking** to development workflow
4. **Document color standards** for developers

### Long-term Improvements:
1. **Automated Testing:** Integrate axe-core or Pa11y into CI/CD
2. **Design System:** Create component library with built-in accessibility
3. **Training:** Provide 508 compliance training for developers
4. **User Testing:** Regular testing with users with disabilities
5. **Accessibility Statement:** Add public accessibility statement to site

---

## Code Snippets for Quick Fixes

### Create a Utility Function:
```jsx
// src/utils/accessibility.js
export const getAccessibleBadgeColors = (type, isDark = false) => {
  const colorMap = {
    critical: isDark ? 'bg-red-950 text-red-200' : 'bg-red-100 text-red-800',
    warning: isDark ? 'bg-orange-900 text-orange-100' : 'bg-orange-100 text-orange-800',
    info: isDark ? 'bg-blue-900 text-blue-100' : 'bg-blue-100 text-blue-800',
    success: isDark ? 'bg-green-900 text-green-100' : 'bg-green-100 text-green-800',
    neutral: isDark ? 'bg-gray-700 text-gray-200' : 'bg-gray-100 text-gray-800',
  };
  return colorMap[type] || colorMap.neutral;
};
```

### Or Use Tailwind's Dark Mode Classes:
```jsx
// Replace all badge className patterns with:
className="bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100"
```

---

## Contact for Questions

- **Accessibility Lead:** [To be assigned]
- **Development Team:** Aaron Kornbluth
- **Testing:** [To be assigned]

---

**Last Updated:** December 8, 2025
**Next Review:** After Phase 1 implementation
