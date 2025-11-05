import { useEffect } from 'react';

/**
 * Hook that handles click outside of the passed ref and Escape key press
 * @param {React.RefObject} ref - Reference to the element
 * @param {Function} handler - Function to call when clicking outside or pressing Escape
 * @param {boolean} enabled - Whether the listener is enabled (default: true)
 */
export function useClickOutside(ref, handler, enabled = true) {
  useEffect(() => {
    if (!enabled) return;

    const handleClickOutside = (event) => {
      if (ref.current && !ref.current.contains(event.target)) {
        handler();
      }
    };

    const handleEscapeKey = (event) => {
      if (event.key === 'Escape' || event.key === 'Esc') {
        handler();
      }
    };

    // Add event listeners
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleEscapeKey);

    // Cleanup
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscapeKey);
    };
  }, [ref, handler, enabled]);
}

export default useClickOutside;
