import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import { RefreshCw, Download, Settings, RotateCcw } from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

const ActionsNew = () => {
  const [filterStage, setFilterStage] = useState([]);
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('last_updated');
  const [sortDirection, setSortDirection] = useState('desc');
  const [pageSize, setPageSize] = useState(20);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedActions, setSelectedActions] = useState(new Set());
  const [showColumnSelector, setShowColumnSelector] = useState(false);

  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState({
    title: true,
    fmp: true,
    progress_stage: true,
    progress: true,
    last_updated: true,
    description: false,
    type: false,
  });

  // Define all available columns with widths
  const [columnOrder, setColumnOrder] = useState([
    { key: 'title', label: 'Title', core: true, locked: true, width: '300px' },
    { key: 'fmp', label: 'FMP', core: true, width: '150px' },
    { key: 'progress_stage', label: 'Stage', core: true, width: '180px' },
    { key: 'progress', label: 'Progress', core: true, width: '120px' },
    { key: 'last_updated', label: 'Last Action', core: true, width: '140px' },
    { key: 'description', label: 'Description', core: false, width: '300px' },
    { key: 'type', label: 'Type', core: false, width: '120px' },
  ]);

  const [draggedColumn, setDraggedColumn] = useState(null);

  useEffect(() => {
    fetchActions();
  }, []);

  const fetchActions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/actions`);
      const data = await response.json();

      if (data.success) {
        setActions(data.actions || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching actions:', error);
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
    setFilterStage([]);
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
  const uniqueStages = useMemo(() => {
    const stages = new Set(actions.map(a => a.progress_stage).filter(Boolean));
    return Array.from(stages).sort();
  }, [actions]);

  // Filter and sort actions
  const filteredAndSortedActions = useMemo(() => {
    // Apply all filters
    const filtered = actions.filter(action => {
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
  }, [actions, searchTerm, sortField, sortDirection, filterStage]);

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

  const getStageVariant = (stage) => {
    if (!stage) return 'neutral';

    const stageLower = stage.toLowerCase();
    if (stageLower.includes('scoping')) return 'warning';
    if (stageLower.includes('hearing')) return 'info';
    if (stageLower.includes('approval')) return 'success';
    if (stageLower.includes('implementation')) return 'purple';
    return 'neutral';
  };

  return (
    <div>
      {/* Description and Action Buttons Row */}
      <div className="page-description-container">
        <p className="page-description-text">
          Advanced table view for managing and exporting amendment data with customizable columns and filters.
        </p>
        <div className="page-description-actions">
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-slate-300 bg-gradient-to-r from-slate-50 to-gray-50 px-2.5 h-9 text-xs font-medium text-slate-700 shadow-sm hover:from-slate-100 hover:to-gray-100 hover:border-slate-400 transition-all"
            title="Reset filters, sorting, and selection"
          >
            <RotateCcw size={14} />
            Reset
          </button>
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-indigo-300 bg-gradient-to-r from-indigo-50 to-purple-50 px-2.5 h-9 text-xs font-medium text-indigo-700 shadow-sm hover:from-indigo-100 hover:to-purple-100 hover:border-indigo-400 transition-all"
          >
            <Settings size={14} />
            Columns
          </button>
          <div className="relative">
            <button
              className="inline-flex items-center gap-1.5 justify-center rounded-md border border-teal-300 bg-gradient-to-r from-teal-50 to-cyan-50 px-2.5 h-9 text-xs font-medium text-teal-700 shadow-sm hover:from-teal-100 hover:to-cyan-100 hover:border-teal-400 transition-all"
              onClick={(e) => {
                const menu = e.currentTarget.nextElementSibling;
                menu.classList.toggle('hidden');
              }}
            >
              <Download size={14} />
              Export
            </button>
            <div className="hidden absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
              <div className="py-1">
                <div className="px-4 py-2 text-xs text-gray-500 border-b">
                  {selectedActions.size > 0 ? `Export ${selectedActions.size} selected` : 'Export all actions'}
                </div>
                <button
                  onClick={exportToCSV}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  CSV Format (.csv)
                </button>
                <button
                  onClick={exportToTSV}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  TSV Format (.tsv)
                </button>
                <button
                  onClick={exportToExcel}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  Excel Format (.xls)
                </button>
              </div>
      </div>
          </div>
          <button
            onClick={syncActions}
            disabled={syncing}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-transparent bg-brand-blue px-2.5 h-9 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync'}
          </button>
        </div>
      </div>

      {/* Single row: Search → Filters → Show → Columns → Reset */}
      <PageControlsContainer>
        {/* Search input */}
        <SearchBar
          value={searchTerm}
          onChange={(value) => {
            setSearchTerm(value);
            setCurrentPage(1);
          }}
          placeholder="Search actions..."
          ariaLabel="Search actions by title, FMP, progress stage, or description"
        />

        {/* Progress Stage Filter */}
        <FilterDropdown
          label="Progress Stage"
          options={uniqueStages.map(stage => ({
            value: stage,
            label: stage,
            count: actions.filter(a => a.progress_stage === stage).length
          }))}
          selectedValues={filterStage}
          onChange={setFilterStage}
          showCounts={true}
        />

        {/* Page Size */}
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="h-9 bg-white dark:bg-gray-800 rounded-md border border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm px-3 text-gray-900 dark:text-gray-100 hover:border-gray-400 dark:hover:border-gray-500 transition-colors cursor-pointer"
          aria-label="Number of actions to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>

        {/* Columns Dropdown */}
        <FilterDropdown
          label="Columns"
          options={columnOrder.filter(col => !col.core).map(col => ({
            value: col.key,
            label: col.label
          }))}
          selectedValues={Object.entries(visibleColumns)
            .filter(([key, visible]) => {
              const col = columnOrder.find(c => c.key === key);
              return visible && col && !col.core;
            })
            .map(([key]) => key)
          }
          onChange={(selectedKeys) => {
            const newVisibleColumns = { ...visibleColumns };
            // Set all non-core columns to false first
            columnOrder.filter(col => !col.core).forEach(col => {
              newVisibleColumns[col.key] = false;
            });
            // Set selected columns to true
            selectedKeys.forEach(key => {
              newVisibleColumns[key] = true;
            });
            setVisibleColumns(newVisibleColumns);
          }}
          showCounts={false}
        />

        {/* Reset Button */}
        <button
          onClick={handleReset}
          className="inline-flex items-center gap-2 h-9 px-3 text-sm font-medium rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-600 hover:bg-red-100 dark:hover:bg-red-900/40 hover:border-red-400 dark:hover:border-red-500 transition-colors"
          title="Reset filters, sorting, and selection"
        >
          <RotateCcw size={14} />
          Reset
        </button>
      </PageControlsContainer>

      {/* Table Count */}
      <div className="mt-6 mb-2 flex items-center justify-between">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Showing <span className="font-medium text-gray-900 dark:text-gray-100">{filteredAndSortedActions.length}</span> of <span className="font-medium text-gray-900 dark:text-gray-100">{actions.length}</span> actions
        </p>
      </div>

      {/* Actions Table with Interview System padding pattern */}
      <div className="mt-6 bg-white shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-2 py-1.5 text-left">
                <input
                  type="checkbox"
                  checked={selectedActions.size === paginatedActions.length && paginatedActions.length > 0}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
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
                  style={{ width: col.width }}
                  className={`px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider select-none ${
                    !col.locked ? 'cursor-grab hover:bg-gray-200' : 'cursor-pointer hover:bg-gray-100'
                  } ${draggedColumn === index ? 'opacity-50 bg-gray-200' : ''}`}
                  onClick={() => handleSort(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.label}
                    {sortField === col.key && (
                      <span className="text-blue-600">
                        {sortDirection === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500">
                  Loading actions...
                </td>
              </tr>
            ) : paginatedActions.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500">
                  No actions found
                </td>
              </tr>
            ) : (
              paginatedActions.map((action, index) => (
                <tr key={action.id || index} className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-100'} hover:bg-gray-50 transition-colors duration-150`}>
                  <td className="px-2 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedActions.has(action.id)}
                      onChange={() => toggleSelectAction(action)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`Select action: ${action.title}`}
                    />
                  </td>
                  {getDisplayColumns().map(col => (
                    <td key={col.key} className="px-2 py-0.5" style={{ width: col.width }}>
                      {col.key === 'title' ? (
                        <>
                          {action.source_url ? (
                            <a
                              href={action.source_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm font-medium text-brand-blue hover:text-brand-green hover:underline"
                            >
                              {action.title}
                            </a>
                          ) : (
                            <div className="text-sm font-medium text-gray-900">{action.title}</div>
                          )}
                          {action.description && visibleColumns.description && (
                            <div className="text-sm text-gray-500 mt-0.5">{action.description.substring(0, 100)}...</div>
                          )}
                        </>
                      ) : col.key === 'progress_stage' ? (
                        <StatusBadge variant={getStageVariant(action.progress_stage)} size="sm">
                          {action.progress_stage || 'Unknown'}
                        </StatusBadge>
                      ) : col.key === 'progress' ? (
                        <div className="flex items-center gap-1">
                          <div className="w-16 bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-brand-blue h-1.5 rounded-full"
                              style={{ width: `${action.progress || 0}%` }}
                            ></div>
                          </div>
                          <span className="text-sm text-gray-700">{action.progress || 0}%</span>
                        </div>
                      ) : col.key === 'last_updated' ? (
                        <div className="text-sm text-gray-500">
                          {action.last_updated ? new Date(action.last_updated).toLocaleDateString() : 'N/A'}
                        </div>
                      ) : (
                        <div className="text-sm text-gray-900">{action[col.key] || 'N/A'}</div>
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
        <div className="mt-4 flex items-center justify-end">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="h-9 px-4 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Previous
            </button>
            <span className="px-3 text-sm text-gray-600 dark:text-gray-400">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="h-9 px-4 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActionsNew;
