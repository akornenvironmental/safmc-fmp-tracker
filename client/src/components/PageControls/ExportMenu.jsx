/**
 * Standardized ExportMenu Component
 * Provides consistent export dropdown with multiple format options
 */

import { useState, useRef, useEffect } from 'react';
import { Download, ChevronDown, FileSpreadsheet, FileText } from 'lucide-react';

const ExportMenu = ({
  onExport,
  formats = ['csv', 'tsv', 'excel'],
  selectedCount = 0,
  totalCount = 0,
  disabled = false,
  className = ""
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const formatOptions = {
    csv: { label: 'CSV Format', icon: FileSpreadsheet, ext: '.csv' },
    tsv: { label: 'TSV Format', icon: FileText, ext: '.tsv' },
    excel: { label: 'Excel Format', icon: FileSpreadsheet, ext: '.xls' }
  };

  const handleExport = (format) => {
    onExport(format);
    setIsOpen(false);
  };

  const exportLabel = selectedCount > 0
    ? `Export ${selectedCount} selected`
    : `Export all ${totalCount}`;

  return (
    <div className={`relative ${className}`} ref={menuRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
        className="inline-flex items-center gap-1.5 h-9 px-3 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Download className="w-4 h-4" />
        Export
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 z-50 mt-1 w-56 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700">
          <div className="p-2">
            <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
              {exportLabel}
            </div>
            <div className="mt-1 space-y-1">
              {formats.map((format) => {
                const option = formatOptions[format];
                if (!option) return null;

                const Icon = option.icon;
                return (
                  <button
                    key={format}
                    onClick={() => handleExport(format)}
                    className="flex items-center gap-2 w-full px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 rounded transition-colors"
                  >
                    <Icon className="w-4 h-4 text-gray-400" />
                    <span>{option.label}</span>
                    <span className="ml-auto text-xs text-gray-400">{option.ext}</span>
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ExportMenu;
