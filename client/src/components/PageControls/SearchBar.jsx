/**
 * Standardized SearchBar Component
 * Provides consistent search input across all pages
 */

import { Search } from 'lucide-react';

const SearchBar = ({
  value,
  onChange,
  placeholder = "Search...",
  ariaLabel,
  className = ""
}) => {
  return (
    <div className={`relative flex-1 min-w-[150px] ${className}`}>
      <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none z-10" aria-hidden="true" />
      <input
        type="text"
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        aria-label={ariaLabel || placeholder}
        className="w-full h-9 pl-10 pr-4 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 focus:border-blue-500 dark:focus:border-blue-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors shadow-sm"
      />
    </div>
  );
};

export default SearchBar;
