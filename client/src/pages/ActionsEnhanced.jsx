import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import { RefreshCw, Download, Settings, RotateCcw } from 'lucide-react';

const ActionsEnhanced = () => {
  const [filterStage, setFilterStage] = useState('all');
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

  // Define all available columns
  const allColumns = [
    { key: 'title', label: 'Title', core: true },
    { key: 'fmp', label: 'FMP', core: true },
    { key: 'progress_stage', label: 'Progress Stage', core: true },
    { key: 'progress', label: 'Progress', core: true },
    { key: 'last_updated', label: 'Last Updated', core: true },
    { key: 'description', label: 'Description', core: false },
    { key: 'type', label: 'Type', core: false },
  ];

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
    setShowColumnSelector(false);
    setFilterStage('all');
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

  // Filter and sort actions
  const filteredAndSortedActions = useMemo(() => {
    // First apply stage filter
    const stageFiltered = actions.filter(action => {
      if (filterStage === 'all') return true;
      return action.progress_stage && action.progress_stage.toLowerCase().includes(filterStage.toLowerCase());
    });

    // Then apply search filter
    const filtered = stageFiltered.filter(action => {
      const searchLower = searchTerm.toLowerCase();
      return (
        action.title?.toLowerCase().includes(searchLower) ||
        action.fmp?.toLowerCase().includes(searchLower) ||
        action.progress_stage?.toLowerCase().includes(searchLower) ||
        action.description?.toLowerCase().includes(searchLower)
      );
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
    return allColumns.filter(col => {
      if (col.key === 'title' || col.key === 'fmp') return true;
      return visibleColumns[col.key];
    });
  };

  const toggleColumn = (columnKey) => {
    if (columnKey === 'title' || columnKey === 'fmp') return;
    const column = allColumns.find(col => col.key === columnKey);
    if (column && !column.core) {
      setVisibleColumns(prev => ({
        ...prev,
        [columnKey]: !prev[columnKey]
      }));
    }
  };

  const getStageColor = (stage) => {
    if (!stage) return 'bg-gray-100 text-gray-800';

    const stageLower = stage.toLowerCase();
    if (stageLower.includes('scoping')) return 'bg-yellow-100 text-yellow-800';
    if (stageLower.includes('hearing')) return 'bg-blue-100 text-blue-800';
    if (stageLower.includes('approval')) return 'bg-green-100 text-green-800';
    if (stageLower.includes('implementation')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Actions & Amendments</h1>
          <p className="mt-2 text-sm text-gray-700">
            Showing {filteredAndSortedActions.length} of {actions.length} actions
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 flex flex-wrap gap-2">
          <button
            onClick={handleReset}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-slate-300 bg-gradient-to-r from-slate-50 to-gray-50 px-3 py-1.5 text-xs font-medium text-slate-700 shadow-sm hover:from-slate-100 hover:to-gray-100 hover:border-slate-400 transition-all"
            title="Reset filters, sorting, and selection"
          >
            <RotateCcw size={14} />
            Reset
          </button>
          <button
            onClick={() => setShowColumnSelector(!showColumnSelector)}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-indigo-300 bg-gradient-to-r from-indigo-50 to-purple-50 px-3 py-1.5 text-xs font-medium text-indigo-700 shadow-sm hover:from-indigo-100 hover:to-purple-100 hover:border-indigo-400 transition-all"
          >
            <Settings size={14} />
            Columns
          </button>
          <div className="relative">
            <button
              className="inline-flex items-center gap-1.5 justify-center rounded-md border border-teal-300 bg-gradient-to-r from-teal-50 to-cyan-50 px-3 py-1.5 text-xs font-medium text-teal-700 shadow-sm hover:from-teal-100 hover:to-cyan-100 hover:border-teal-400 transition-all"
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
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Actions'}
          </button>
        </div>
      </div>

      {/* Column selector */}
      {showColumnSelector && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Show/Hide Columns</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {allColumns.map(col => (
              <label key={col.key} className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={visibleColumns[col.key]}
                  onChange={() => toggleColumn(col.key)}
                  disabled={col.core}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className={`text-sm ${col.core ? 'text-gray-400' : 'text-gray-700'}`}>
                  {col.label} {col.core && '(required)'}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Filter Buttons */}
      <div className="mt-6">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterStage('all')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'all'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            All ({actions.length})
          </button>
          <button
            onClick={() => setFilterStage('scoping')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'scoping'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Scoping ({actions.filter(a => a.progress_stage?.toLowerCase().includes('scoping')).length})
          </button>
          <button
            onClick={() => setFilterStage('hearing')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'hearing'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Public Hearing ({actions.filter(a => a.progress_stage?.toLowerCase().includes('hearing')).length})
          </button>
          <button
            onClick={() => setFilterStage('approval')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'approval'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Approval ({actions.filter(a => a.progress_stage?.toLowerCase().includes('approval')).length})
          </button>
        </div>
      </div>

      {/* Search and page size */}
      <div className="mt-6 flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Search actions..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
          aria-label="Search actions by title, FMP, progress stage, or description"
        />
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
          aria-label="Number of actions to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>
      </div>

      {/* Actions Table */}
      <div className="mt-6 bg-white shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <caption className="sr-only">
            Actions tracker with {filteredAndSortedActions.length} actions. Table includes columns for selection, title, FMP, progress stage, progress percentage, and last updated date. Click column headers to sort.
          </caption>
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-2 py-1.5 text-left">
                <input
                  type="checkbox"
                  checked={selectedActions.size === paginatedActions.length && paginatedActions.length > 0}
                  onChange={toggleSelectAll}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  aria-label={`Select all ${paginatedActions.length} actions on this page`}
                />
              </th>
              {getDisplayColumns().map(col => (
                <th
                  key={col.key}
                  scope="col"
                  className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none"
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
                <td colSpan={getDisplayColumns().length + 1} className="px-3 py-8 text-center text-sm text-gray-500">
                  Loading actions...
                </td>
              </tr>
            ) : paginatedActions.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-3 py-8 text-center text-sm text-gray-500">
                  No actions found
                </td>
              </tr>
            ) : (
              paginatedActions.map((action, index) => (
                <tr key={action.id || index} className="hover:bg-gray-50">
                  <td className="px-2 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedActions.has(action.id)}
                      onChange={() => toggleSelectAction(action)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`Select action: ${action.title}`}
                    />
                  </td>
                  {getDisplayColumns().map(col => (
                    <td key={col.key} className="px-3 py-2">
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
                            <div className="text-xs text-gray-500 mt-0.5">{action.description.substring(0, 100)}...</div>
                          )}
                        </>
                      ) : col.key === 'progress_stage' ? (
                        <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${getStageColor(action.progress_stage)}`}>
                          {action.progress_stage || 'Unknown'}
                        </span>
                      ) : col.key === 'progress' ? (
                        <div className="flex items-center gap-1">
                          <div className="w-16 bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-brand-blue h-1.5 rounded-full"
                              style={{ width: `${action.progress || 0}%` }}
                            ></div>
                          </div>
                          <span className="text-xs text-gray-700">{action.progress || 0}%</span>
                        </div>
                      ) : col.key === 'last_updated' ? (
                        <div className="text-xs text-gray-500">
                          {action.last_updated ? new Date(action.last_updated).toLocaleDateString() : 'N/A'}
                        </div>
                      ) : (
                        <div className="text-xs text-gray-900">{action[col.key] || 'N/A'}</div>
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
          <div className="text-sm text-gray-700">
            Showing {filteredAndSortedActions.length} of {actions.length} actions
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-700">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
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
