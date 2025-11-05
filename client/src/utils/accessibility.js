/**
 * Accessibility Utilities for 508 Compliance
 *
 * These utilities help ensure the application meets Section 508 standards
 * and WCAG 2.0 AA guidelines for accessibility.
 */

/**
 * Trap focus within a modal/dialog element
 * @param {HTMLElement} element - The element to trap focus within
 * @returns {Function} Cleanup function to remove focus trap
 */
export function trapFocus(element) {
  const focusableElements = element.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  };

  element.addEventListener('keydown', handleTabKey);

  // Focus first element
  if (firstFocusable) {
    firstFocusable.focus();
  }

  // Return cleanup function
  return () => {
    element.removeEventListener('keydown', handleTabKey);
  };
}

/**
 * Announce message to screen readers
 * @param {string} message - Message to announce
 * @param {string} priority - 'polite' or 'assertive'
 */
export function announceToScreenReader(message, priority = 'polite') {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}

/**
 * Generate unique ID for aria-describedby relationships
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
export function generateId(prefix = 'a11y') {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Check if element is visible to screen readers
 * @param {HTMLElement} element - Element to check
 * @returns {boolean} Whether element is visible
 */
export function isVisibleToScreenReader(element) {
  return (
    element.offsetParent !== null &&
    !element.hasAttribute('aria-hidden') &&
    element.getAttribute('aria-hidden') !== 'true'
  );
}

/**
 * Get accessible name for an element
 * @param {HTMLElement} element - Element to get name for
 * @returns {string} Accessible name
 */
export function getAccessibleName(element) {
  // Check aria-label
  if (element.hasAttribute('aria-label')) {
    return element.getAttribute('aria-label');
  }

  // Check aria-labelledby
  if (element.hasAttribute('aria-labelledby')) {
    const labelId = element.getAttribute('aria-labelledby');
    const labelElement = document.getElementById(labelId);
    if (labelElement) {
      return labelElement.textContent;
    }
  }

  // Check associated label
  if (element.id) {
    const label = document.querySelector(`label[for="${element.id}"]`);
    if (label) {
      return label.textContent;
    }
  }

  // Fall back to text content
  return element.textContent || element.value || '';
}

/**
 * Focus management - store and restore focus
 */
export class FocusManager {
  constructor() {
    this.previousFocus = null;
  }

  store() {
    this.previousFocus = document.activeElement;
  }

  restore() {
    if (this.previousFocus && this.previousFocus.focus) {
      this.previousFocus.focus();
    }
  }
}

/**
 * Color contrast checker (WCAG AA: 4.5:1 for normal, 3:1 for large text)
 * @param {string} foreground - Foreground color (hex)
 * @param {string} background - Background color (hex)
 * @returns {Object} Contrast ratio and compliance info
 */
export function checkColorContrast(foreground, background) {
  const getLuminance = (hex) => {
    const rgb = parseInt(hex.replace('#', ''), 16);
    const r = ((rgb >> 16) & 0xff) / 255;
    const g = ((rgb >> 8) & 0xff) / 255;
    const b = (rgb & 0xff) / 255;

    const [rs, gs, bs] = [r, g, b].map(c =>
      c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    );

    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const l1 = getLuminance(foreground);
  const l2 = getLuminance(background);
  const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);

  return {
    ratio: ratio.toFixed(2),
    passAA: ratio >= 4.5,
    passAALarge: ratio >= 3,
    passAAA: ratio >= 7,
  };
}

/**
 * Keyboard navigation helpers
 */
export const KeyCodes = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
};

/**
 * Handle roving tabindex for widget patterns (like tabs, menus)
 * @param {HTMLElement[]} items - Array of elements in the widget
 * @param {number} currentIndex - Currently focused index
 * @param {string} key - Key pressed
 * @returns {number} New index to focus
 */
export function handleRovingTabIndex(items, currentIndex, key) {
  let newIndex = currentIndex;

  switch (key) {
    case KeyCodes.ARROW_DOWN:
    case KeyCodes.ARROW_RIGHT:
      newIndex = currentIndex + 1;
      if (newIndex >= items.length) newIndex = 0;
      break;

    case KeyCodes.ARROW_UP:
    case KeyCodes.ARROW_LEFT:
      newIndex = currentIndex - 1;
      if (newIndex < 0) newIndex = items.length - 1;
      break;

    case KeyCodes.HOME:
      newIndex = 0;
      break;

    case KeyCodes.END:
      newIndex = items.length - 1;
      break;

    default:
      return currentIndex;
  }

  // Update tabindex
  items.forEach((item, index) => {
    item.setAttribute('tabindex', index === newIndex ? '0' : '-1');
  });

  // Focus new item
  if (items[newIndex]) {
    items[newIndex].focus();
  }

  return newIndex;
}

/**
 * Create visually hidden but screen-reader accessible element
 * @param {string} text - Text for screen readers
 * @returns {HTMLElement} Hidden element
 */
export function createSROnlyElement(text) {
  const element = document.createElement('span');
  element.className = 'sr-only';
  element.textContent = text;
  return element;
}

export default {
  trapFocus,
  announceToScreenReader,
  generateId,
  isVisibleToScreenReader,
  getAccessibleName,
  FocusManager,
  checkColorContrast,
  KeyCodes,
  handleRovingTabIndex,
  createSROnlyElement,
};
