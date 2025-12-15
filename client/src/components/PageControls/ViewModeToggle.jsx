/**
 * Standardized ViewModeToggle Component
 * Provides consistent view mode switching (grid/table/calendar/list)
 */

const ViewModeToggle = ({
  modes = [],
  selectedMode,
  onChange,
  className = ""
}) => {
  return (
    <div className={`inline-flex rounded-md shadow-sm ${className}`}>
      {modes.map((mode, index) => {
        const Icon = mode.icon;
        const isActive = selectedMode === mode.value;
        const isFirst = index === 0;
        const isLast = index === modes.length - 1;

        let roundedClass = '';
        if (isFirst && isLast) {
          roundedClass = 'rounded-md';
        } else if (isFirst) {
          roundedClass = 'rounded-l-md';
        } else if (isLast) {
          roundedClass = 'rounded-r-md';
        }

        let borderClass = '';
        if (isFirst) {
          borderClass = 'border';
        } else {
          borderClass = 'border-t border-r border-b';
        }

        return (
          <button
            key={mode.value}
            onClick={() => onChange(mode.value)}
            className={`inline-flex items-center gap-1.5 h-9 px-3 text-sm font-medium transition-colors ${roundedClass} ${borderClass} ${
              isActive
                ? 'bg-brand-blue text-white border-brand-blue z-10'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
            }`}
            title={mode.label}
          >
            <Icon className="w-4 h-4" />
            {mode.showLabel !== false && <span>{mode.label}</span>}
          </button>
        );
      })}
    </div>
  );
};

export default ViewModeToggle;
