/**
 * Standardized FilterDropdown Component
 * Provides consistent multi-select dropdown filters across all pages
 */

import { useState, useRef, useEffect } from 'react';
import { ChevronDown, X } from 'lucide-react';

const FilterDropdown = ({
  label,
  options = [],
  selectedValues = [],
  onChange,
  showCounts = false,
  width = "w-64",
  className = ""
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleOption = (value) => {
    const newValues = selectedValues.includes(value)
      ? selectedValues.filter(v => v !== value)
      : [...selectedValues, value];
    onChange(newValues);
  };

  const clearAll = () => {
    onChange([]);
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 h-9 px-3 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-colors shadow-sm"
      >
        {label}
        {selectedValues.length > 0 && (
          <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-brand-blue rounded-full">
            {selectedValues.length}
          </span>
        )}
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className={`absolute z-50 mt-1 ${width} bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700`}>
          <div className="p-2 max-h-60 overflow-y-auto">
            {options.length === 0 ? (
              <div className="px-2 py-1.5 text-sm text-gray-500 dark:text-gray-400">
                No options available
              </div>
            ) : (
              options.map((option) => {
                const value = typeof option === 'string' ? option : option.value;
                const displayLabel = typeof option === 'string' ? option : option.label;
                const count = typeof option === 'object' ? option.count : null;

                return (
                  <label
                    key={value}
                    className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer group"
                  >
                    <input
                      type="checkbox"
                      checked={selectedValues.includes(value)}
                      onChange={() => toggleOption(value)}
                      className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-brand-blue focus:ring-brand-blue focus:ring-offset-0"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300 flex-1">
                      {displayLabel}
                    </span>
                    {showCounts && count !== null && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        ({count})
                      </span>
                    )}
                  </label>
                );
              })
            )}
          </div>

          {selectedValues.length > 0 && (
            <div className="border-t border-gray-200 dark:border-gray-700 p-2">
              <button
                onClick={clearAll}
                className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
              >
                Clear all filters
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default FilterDropdown;
