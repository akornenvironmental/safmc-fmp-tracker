/**
 * Standardized FilterButtonGroup Component
 * Provides consistent button-based filters (e.g., status filters)
 */

const FilterButtonGroup = ({
  options = [],
  selectedValue,
  onChange,
  showCounts = false,
  className = ""
}) => {
  return (
    <div className={`flex flex-wrap items-center gap-2 ${className}`}>
      {options.map((option) => {
        const value = typeof option === 'string' ? option : option.value;
        const label = typeof option === 'string' ? option : option.label;
        const count = typeof option === 'object' ? option.count : null;
        const isActive = selectedValue === value;

        return (
          <button
            key={value}
            onClick={() => onChange(value)}
            className={`inline-flex items-center gap-1.5 h-9 px-4 py-2 text-sm font-medium rounded-md transition-colors shadow-sm ${
              isActive
                ? 'bg-brand-blue text-white border border-brand-blue'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            {label}
            {showCounts && count !== null && count !== undefined && (
              <span className={`text-xs ${isActive ? 'text-white/90' : 'text-gray-500 dark:text-gray-400'}`}>
                ({count})
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};

export default FilterButtonGroup;
