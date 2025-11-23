import { useState, useEffect, useMemo, useRef } from 'react';
import { API_BASE_URL } from '../config';
import { RefreshCw, Download, Settings, RotateCcw, ChevronDown, X } from 'lucide-react';

const ActionsEnhanced = () => {
  const [filterStage, setFilterStage] = useState([]);
  const [filterFMP, setFilterFMP] = useState([]);
  const [filterType, setFilterType] = useState([]);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('last_updated');
  const [sortDirection, setSortDirection] = useState('desc');
  const [pageSize, setPageSize] = useState(20);
  const [currentPage, setCurrentPage] = useState(1);
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [selectedActions, setSelectedActions] = useState(new Set());
  const [showStageDropdown, setShowStageDropdown] = useState(false);
  const [showFMPDropdown, setShowFMPDropdown] = useState(false);
  const [showTypeDropdown, setShowTypeDropdown] = useState(false);

  const stageDropdownRef = useRef(null);
  const fmpDropdownRef = useRef(null);
  const typeDropdownRef = useRef(null);

  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState({
    title: true,
    fmp: true,
    species: true,
    progress_stage: true,
    progress: true,
    last_updated: true,
    description: false,
    type: false,
  });

  // Define all available columns with min-widths (using Tailwind classes, not inline styles)
  const [columnOrder, setColumnOrder] = useState([
    { key: 'title', label: 'Title', core: true, locked: true, minWidth: 'min-w-[300px]' },
    { key: 'fmp', label: 'FMP', core: true, minWidth: 'min-w-[150px]' },
    { key: 'species', label: 'Species', core: true, minWidth: 'min-w-[180px]' },
    { key: 'progress_stage', label: 'Stage', core: true, minWidth: 'min-w-[180px]' },
    { key: 'progress', label: 'Progress', core: true, minWidth: 'min-w-[120px]' },
    { key: 'last_updated', label: 'Last Action', core: true, minWidth: 'min-w-[140px]' },
    { key: 'description', label: 'Description', core: false, minWidth: 'min-w-[300px]' },
    { key: 'type', label: 'Type', core: false, minWidth: 'min-w-[120px]' },
  ]);

  const [draggedColumn, setDraggedColumn] = useState(null);

  useEffect(() => {
    fetchActions();
  }, []);

  // Click outside handler for dropdowns
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (stageDropdownRef.current && !stageDropdownRef.current.contains(event.target)) {
        setShowStageDropdown(false);
      }
      if (fmpDropdownRef.current && !fmpDropdownRef.current.contains(event.target)) {
        setShowFMPDropdown(false);
      }
      if (typeDropdownRef.current && !typeDropdownRef.current.contains(event.target)) {
        setShowTypeDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const fetchActions = async () => {
    try {
      // Use the enhanced endpoint that includes species with stock status
      const response = await fetch(`${API_BASE_URL}/api/actions/with-stock-status`);
      const data = await response.json();

      if (data.success) {
        setActions(data.actions || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching actions:', error);
      // Fallback to regular endpoint if enhanced fails
      try {
        const fallbackResponse = await fetch(`${API_BASE_URL}/api/actions`);
        const fallbackData = await fallbackResponse.json();
        if (fallbackData.success) {
          setActions(fallbackData.actions || []);
        }
      } catch (e) {
        console.error('Fallback also failed:', e);
      }
      setLoading(false);
    }
  };

  const syncActions = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/amendments`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchActions();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing actions:', error);
      alert('Error syncing actions');
    } finally {
      setSyncing(false);
    }
  };

  // Reset all filters and sorting
  const handleReset = () => {
    setSearchTerm('');
    setSortField('last_updated');
    setSortDirection('desc');
    setCurrentPage(1);
    setSelectedActions(new Set());
    setShowColumnSelector(false);
    setFilterStage([]);
    setFilterFMP([]);
    setFilterType([]);
    setShowStageDropdown(false);
    setShowFMPDropdown(false);
    setShowTypeDropdown(false);
  };

  // Toggle filter functions for multi-select
  const toggleStageFilter = (stage) => {
    setFilterStage(prev => {
      if (prev.includes(stage)) {
        return prev.filter(s => s !== stage);
      } else {
        return [...prev, stage];
      }
    });
    setCurrentPage(1);
  };

  const toggleFMPFilter = (fmp) => {
    setFilterFMP(prev => {
      if (prev.includes(fmp)) {
        return prev.filter(f => f !== fmp);
      } else {
        return [...prev, fmp];
      }
    });
    setCurrentPage(1);
  };

  const toggleTypeFilter = (type) => {
    setFilterType(prev => {
      if (prev.includes(type)) {
        return prev.filter(t => t !== type);
      } else {
        return [...prev, type];
      }
    });
    setCurrentPage(1);
  };

  // Handle sorting
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  // Get unique values for filters
  const uniqueFMPs = useMemo(() => {
    const fmps = new Set(actions.map(a => a.fmp).filter(Boolean));
    return Array.from(fmps).sort();
  }, [actions]);

  const uniqueTypes = useMemo(() => {
    const types = new Set(actions.map(a => a.type).filter(Boolean));
    return Array.from(types).sort();
  }, [actions]);

  const uniqueStages = useMemo(() => {
    const stages = new Set(actions.map(a => a.progress_stage).filter(Boolean));
    return Array.from(stages).sort();
  }, [actions]);

  // Filter and sort actions
  const filteredAndSortedActions = useMemo(() => {
    // Apply all filters
    const filtered = actions.filter(action => {
      // FMP filter
      if (filterFMP.length > 0 && !filterFMP.includes(action.fmp)) {
        return false;
      }

      // Type filter
      if (filterType.length > 0 && !filterType.includes(action.type)) {
        return false;
      }

      // Stage filter
      if (filterStage.length > 0 && !filterStage.includes(action.progress_stage)) {
        return false;
      }

      // Search filter
      if (searchTerm) {
        const searchLower = searchTerm.toLowerCase();
        return (
          action.title?.toLowerCase().includes(searchLower) ||
          action.fmp?.toLowerCase().includes(searchLower) ||
          action.progress_stage?.toLowerCase().includes(searchLower) ||
          action.description?.toLowerCase().includes(searchLower)
        );
      }

      return true;
    });

    // Then sort
    return [...filtered].sort((a, b) => {
      let aVal = a[sortField] || '';
      let bVal = b[sortField] || '';

      // Handle date sorting
      if (sortField === 'last_updated') {
        aVal = new Date(aVal || 0).getTime();
        bVal = new Date(bVal || 0).getTime();
      } else if (sortField === 'progress') {
        aVal = Number(aVal) || 0;
        bVal = Number(bVal) || 0;
      } else if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal ? bVal.toLowerCase() : '';
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [actions, searchTerm, sortField, sortDirection, filterStage, filterFMP, filterType]);

  // Pagination
  const paginatedActions = useMemo(() => {
    if (pageSize >= 999999) return filteredAndSortedActions;
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedActions.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedActions, currentPage, pageSize]);

  const totalPages = pageSize >= 999999 ? 1 : Math.ceil(filteredAndSortedActions.length / pageSize);

  // Get actions to export (selected or all)
  const getActionsToExport = () => {
    if (selectedActions.size > 0) {
      return filteredAndSortedActions.filter(a => selectedActions.has(a.id));
    }
    return filteredAndSortedActions;
  };

  // Selection handlers
  const toggleSelectAll = () => {
    if (selectedActions.size === paginatedActions.length) {
      setSelectedActions(new Set());
    } else {
      const allKeys = new Set(paginatedActions.map(a => a.id));
      setSelectedActions(allKeys);
    }
  };

  const toggleSelectAction = (action) => {
    const newSelected = new Set(selectedActions);
    if (newSelected.has(action.id)) {
      newSelected.delete(action.id);
    } else {
      newSelected.add(action.id);
    }
    setSelectedActions(newSelected);
  };

  // Export functions
  const exportToCSV = () => {
    const actionsToExport = getActionsToExport();
    const visibleCols = getDisplayColumns();
    const headers = visibleCols.map(col => col.label).join(',');
    const rows = actionsToExport.map(action =>
      visibleCols.map(col => {
        let value = action[col.key] || '';
        if (col.key === 'last_updated' && value) {
          value = new Date(value).toLocaleDateString();
        }
        return `"${value.toString().replace(/"/g, '""')}"`;
      }).join(',')
    );

    const csv = [headers, ...rows].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `actions-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const exportToTSV = () => {
    const actionsToExport = getActionsToExport();
    const visibleCols = getDisplayColumns();
    const headers = visibleCols.map(col => col.label).join('\t');
    const rows = actionsToExport.map(action =>
      visibleCols.map(col => {
        let value = action[col.key] || '';
        if (col.key === 'last_updated' && value) {
          value = new Date(value).toLocaleDateString();
        }
        return value;
      }).join('\t')
    );

    const tsv = [headers, ...rows].join('\n');
    const blob = new Blob([tsv], { type: 'text/tab-separated-values' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `actions-${new Date().toISOString().split('T')[0]}.tsv`;
    a.click();
  };

  const exportToExcel = () => {
    const actionsToExport = getActionsToExport();
    const visibleCols = getDisplayColumns();

    const headers = visibleCols.map(col => col.label).join('</th><th>');
    const rows = actionsToExport.map(action =>
      '<tr><td>' + visibleCols.map(col => {
        let value = action[col.key] || '';
        if (col.key === 'last_updated' && value) {
          value = new Date(value).toLocaleDateString();
        }
        return value;
      }).join('</td><td>') + '</td></tr>'
    ).join('');

    const html = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">
      <head><meta charset="UTF-8"></head>
      <body><table><thead><tr><th>${headers}</th></tr></thead><tbody>${rows}</tbody></table></body>
      </html>
    `;

    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `actions-${new Date().toISOString().split('T')[0]}.xls`;
    a.click();
  };

  // Helper to get columns that should be displayed
  const getDisplayColumns = () => {
    return columnOrder.filter(col => {
      if (col.key === 'title' || col.key === 'fmp') return true;
      return visibleColumns[col.key];
    });
  };

  const toggleColumn = (columnKey) => {
    if (columnKey === 'title' || columnKey === 'fmp') return;
    const column = columnOrder.find(col => col.key === columnKey);
    if (column && !column.core) {
      setVisibleColumns(prev => ({
        ...prev,
        [columnKey]: !prev[columnKey]
      }));
    }
  };

  // Column reordering handlers
  const handleDragStart = (e, columnIndex) => {
    const col = getDisplayColumns()[columnIndex];
    if (col.locked) {
      e.preventDefault();
      return;
    }
    setDraggedColumn(columnIndex);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e, columnIndex) => {
    e.preventDefault();
    const col = getDisplayColumns()[columnIndex];
    if (col.locked) return;
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (e, dropIndex) => {
    e.preventDefault();
    const displayedCols = getDisplayColumns();
    const dropCol = displayedCols[dropIndex];

    if (dropCol.locked || draggedColumn === null || draggedColumn === dropIndex) {
      setDraggedColumn(null);
      return;
    }

    const newOrder = [...columnOrder];
    const draggedCol = displayedCols[draggedColumn];

    // Find actual indices in full column order
    const draggedIndex = newOrder.findIndex(c => c.key === draggedCol.key);
    const targetIndex = newOrder.findIndex(c => c.key === dropCol.key);

    // Remove dragged column and insert at new position
    const [removed] = newOrder.splice(draggedIndex, 1);
    newOrder.splice(targetIndex, 0, removed);

    setColumnOrder(newOrder);
    setDraggedColumn(null);
  };

  const handleDragEnd = () => {
    setDraggedColumn(null);
  };

  const getStageColor = (stage) => {
    if (!stage) return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';

    const stageLower = stage.toLowerCase();
    if (stageLower.includes('scoping')) return 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200';
    if (stageLower.includes('hearing')) return 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200';
    if (stageLower.includes('approval')) return 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200';
    if (stageLower.includes('implementation')) return 'bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200';
    return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-gray-100">Actions & Amendments</h1>
          <p className="mt-2 text-sm text-gray-700 dark:text-gray-300">
            Showing {filteredAndSortedActions.length} of {actions.length} actions
          </p>
          <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
            Actions and amendments are automatically synced weekly
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 flex flex-wrap gap-2">
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            <Settings size={14} />
            Columns
          </button>
          <div className="relative">
            <button
              className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
              onClick={(e) => {
                const menu = e.currentTarget.nextElementSibling;
                menu.classList.toggle('hidden');
              }}
            >
              <Download size={14} />
              Export
            </button>
            <div className="hidden absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 dark:ring-gray-600 z-10">
              <div className="py-1">
                <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                  {selectedActions.size > 0 ? `Export ${selectedActions.size} selected` : 'Export all actions'}
                </div>
                <button
                  onClick={exportToCSV}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
                >
                  CSV Format (.csv)
                </button>
                <button
                  onClick={exportToTSV}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
                >
                  TSV Format (.tsv)
                </button>
                <button
                  onClick={exportToExcel}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left"
                >
                  Excel Format (.xls)
                </button>
              </div>
            </div>
          </div>
          <button
            onClick={syncActions}
            disabled={syncing}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-brand-blue text-white border border-brand-blue hover:bg-brand-blue-light disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Actions'}
          </button>
        </div>
      </div>

      {/* Column selector */}
      {showColumnSelector && (
        <div className="mt-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-gray-100 mb-3">Show/Hide Columns</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {columnOrder.map(col => (
              <label key={col.key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={visibleColumns[col.key]}
                  onChange={() => toggleColumn(col.key)}
                  disabled={col.core}
                  className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                />
                <span className={`text-sm ${col.core ? 'text-gray-400 dark:text-gray-500' : 'text-gray-700 dark:text-gray-300'}`}>
                  {col.label} {col.core && '(required)'}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Single row: Search → Filters → Show → Reset */}
      <div className="mt-6 flex flex-wrap items-center gap-2">
        {/* Search input */}
        <input
          type="text"
          placeholder="Search actions..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="flex-1 min-w-[150px] bg-white dark:bg-gray-800 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2 border text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
          aria-label="Search actions by title, FMP, progress stage, or description"
        />

        {/* Progress Stage Filter */}
        <div className="relative" ref={stageDropdownRef}>
          <button
            onClick={() => setShowStageDropdown(!showStageDropdown)}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Progress Stage
            {filterStage.length > 0 && (
              <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-brand-blue rounded-full">
                {filterStage.length}
              </span>
            )}
          </button>
          {showStageDropdown && (
            <div className="absolute z-10 mt-1 w-64 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="p-2 max-h-60 overflow-y-auto">
                {uniqueStages.map(stage => (
                  <label key={stage} className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filterStage.includes(stage)}
                      onChange={() => toggleStageFilter(stage)}
                      className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{stage}</span>
                    <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">
                      ({actions.filter(a => a.progress_stage === stage).length})
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* FMP Filter */}
        <div className="relative" ref={fmpDropdownRef}>
          <button
            onClick={() => setShowFMPDropdown(!showFMPDropdown)}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            FMP
            {filterFMP.length > 0 && (
              <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-brand-blue rounded-full">
                {filterFMP.length}
              </span>
            )}
          </button>
          {showFMPDropdown && (
            <div className="absolute z-10 mt-1 w-64 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="p-2 max-h-60 overflow-y-auto">
                {uniqueFMPs.map(fmp => (
                  <label key={fmp} className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filterFMP.includes(fmp)}
                      onChange={() => toggleFMPFilter(fmp)}
                      className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{fmp}</span>
                    <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">
                      ({actions.filter(a => a.fmp === fmp).length})
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Type Filter */}
        <div className="relative" ref={typeDropdownRef}>
          <button
            onClick={() => setShowTypeDropdown(!showTypeDropdown)}
            className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            Type
            {filterType.length > 0 && (
              <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-bold leading-none text-white bg-brand-blue rounded-full">
                {filterType.length}
              </span>
            )}
          </button>
          {showTypeDropdown && (
            <div className="absolute z-10 mt-1 w-64 bg-white dark:bg-gray-800 rounded-md shadow-lg border border-gray-200 dark:border-gray-700">
              <div className="p-2 max-h-60 overflow-y-auto">
                {uniqueTypes.map(type => (
                  <label key={type} className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={filterType.includes(type)}
                      onChange={() => toggleTypeFilter(type)}
                      className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 dark:text-gray-300">{type}</span>
                    <span className="ml-auto text-xs text-gray-500 dark:text-gray-400">
                      ({actions.filter(a => a.type === type).length})
                    </span>
                  </label>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Page Size */}
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="bg-white dark:bg-gray-800 rounded-md border-gray-300 dark:border-gray-600 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-sm px-3 py-2 border text-gray-900 dark:text-gray-100"
          aria-label="Number of actions to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>

        {/* Reset Button */}
        <button
          onClick={handleReset}
          className="inline-flex items-center gap-2 px-3 py-2 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700"
          title="Reset filters, sorting, and selection"
        >
          <RotateCcw size={14} />
          Reset
        </button>
      </div>

      {/* Actions Table */}
      <div className="mt-6 bg-white dark:bg-gray-800 shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <caption className="sr-only">
            Actions tracker with {filteredAndSortedActions.length} actions. Table includes columns for selection, title, FMP, progress stage, progress percentage, and last updated date. Click column headers to sort.
          </caption>
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" className="px-2 py-1.5 text-left">
                <input
                  type="checkbox"
                  checked={selectedActions.size === paginatedActions.length && paginatedActions.length > 0}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                  aria-label={`Select all ${paginatedActions.length} actions on this page`}
                />
              </th>
              {getDisplayColumns().map((col, index) => (
                <th
                  key={col.key}
                  scope="col"
                  draggable={!col.locked}
                  onDragStart={(e) => handleDragStart(e, index)}
                  onDragOver={(e) => handleDragOver(e, index)}
                  onDrop={(e) => handleDrop(e, index)}
                  onDragEnd={handleDragEnd}
                  className={`px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider select-none ${col.minWidth || ''} ${
                    !col.locked ? 'cursor-grab hover:bg-gray-200 dark:hover:bg-gray-700' : 'cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700'
                  } ${draggedColumn === index ? 'opacity-50 bg-gray-200 dark:bg-gray-700' : ''}`}
                  onClick={() => handleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {sortField === col.key && (
                      <span className="text-blue-600 dark:text-blue-400">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">
                  Loading actions...
                </td>
              </tr>
            ) : paginatedActions.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">
                  No actions found
                </td>
              </tr>
            ) : (
              paginatedActions.map((action, index) => (
                <tr key={action.id || index} className={`${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'} hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-150`}>
                  <td className="px-2 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedActions.has(action.id)}
                      onChange={() => toggleSelectAction(action)}
                      className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                      aria-label={`Select action: ${action.title}`}
                    />
                  </td>
                  {getDisplayColumns().map(col => (
                    <td key={col.key} className={`px-2 py-0.5 ${col.minWidth || ''}`}>
                      {col.key === 'title' ? (
                        <>
                          {action.source_url ? (
                            <a
                              href={action.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-xs font-medium text-brand-blue dark:text-blue-400 hover:text-brand-green dark:hover:text-green-400 hover:underline"
                            >
                              {action.title}
                            </a>
                          ) : (
                            <div className="text-xs font-medium text-gray-900 dark:text-gray-100">{action.title}</div>
                          )}
                          {action.description && visibleColumns.description && (
                            <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{action.description.substring(0, 100)}...</div>
                          )}
                        </>
                      ) : col.key === 'species' ? (
                        <div className="flex flex-wrap gap-1">
                          {action.species && action.species.length > 0 ? (
                            <>
                              {action.species.slice(0, 3).map((sp, idx) => (
                                <span
                                  key={idx}
                                  className={`inline-flex items-center px-1.5 py-0.5 text-xs rounded ${
                                    sp.overfished && sp.overfishing
                                      ? 'bg-red-100 dark:bg-red-900/50 text-red-800 dark:text-red-200'
                                      : sp.overfished
                                      ? 'bg-orange-100 dark:bg-orange-900/50 text-orange-800 dark:text-orange-200'
                                      : sp.overfishing
                                      ? 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200'
                                      : sp.stock_status && sp.stock_status !== 'Unknown'
                                      ? 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200'
                                      : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                                  }`}
                                  title={`${sp.name}: ${sp.stock_status || 'Unknown'}${sp.b_bmsy ? ` (B/BMSY: ${sp.b_bmsy.toFixed(2)})` : ''}`}
                                >
                                  {sp.name}
                                </span>
                              ))}
                              {action.species.length > 3 && (
                                <span className="text-xs text-gray-500 dark:text-gray-400">
                                  +{action.species.length - 3}
                                </span>
                              )}
                            </>
                          ) : (
                            <span className="text-xs text-gray-400 dark:text-gray-500">-</span>
                          )}
                        </div>
                      ) : col.key === 'progress_stage' ? (
                        <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${getStageColor(action.progress_stage)}`}>
                          {action.progress_stage || 'Unknown'}
                        </span>
                      ) : col.key === 'progress' ? (
                        <div className="flex items-center gap-1">
                          <div className="w-16 bg-gray-200 dark:bg-gray-600 rounded-full h-1.5">
                            <div
                              className="bg-brand-blue h-1.5 rounded-full"
                              style={{ width: `${action.progress || 0}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-700 dark:text-gray-300">{action.progress || 0}%</span>
                        </div>
                      ) : col.key === 'last_updated' ? (
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          {action.last_updated ? new Date(action.last_updated).toLocaleDateString() : 'N/A'}
                        </div>
                      ) : (
                        <div className="text-xs text-gray-900 dark:text-gray-100">{action[col.key] || 'N/A'}</div>
                      )}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-700 dark:text-gray-300">
            Showing {filteredAndSortedActions.length} of {actions.length} actions
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-700 dark:text-gray-300">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionsEnhanced;
