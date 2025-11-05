import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import { User, Building2, RefreshCw, Download, Settings, RotateCcw } from 'lucide-react';

const CommentsEnhanced = () => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterPosition, setFilterPosition] = useState('all');
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('submitted_date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [pageSize, setPageSize] = useState(20);
  const [currentPage, setCurrentPage] = useState(1);
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [selectedComments, setSelectedComments] = useState(new Set());

  // Column visibility state for export
  const [visibleColumns, setVisibleColumns] = useState({
    name: true,
    organization: true,
    state: true,
    position: true,
    comment_text: true,
    submitted_date: true,
  });

  // Define all available columns (for export)
  const allColumns = [
    { key: 'name', label: 'Name', core: true },
    { key: 'organization', label: 'Organization', core: false },
    { key: 'state', label: 'State', core: false },
    { key: 'position', label: 'Position', core: true },
    { key: 'comment_text', label: 'Comment', core: true },
    { key: 'submitted_date', label: 'Submitted', core: true },
  ];

  useEffect(() => {
    fetchComments();
  }, []);

  const fetchComments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/comments`);
      const data = await response.json();

      if (data.success) {
        setComments(data.comments || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching comments:', error);
      setLoading(false);
    }
  };

  const syncComments = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/comments`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchComments();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing comments:', error);
      alert('Error syncing comments');
    } finally {
      setSyncing(false);
    }
  };

  // Reset all filters and sorting
  const handleReset = () => {
    setSearchTerm('');
    setSortField('submitted_date');
    setSortDirection('desc');
    setCurrentPage(1);
    setSelectedComments(new Set());
    setShowColumnSelector(false);
    setFilterPosition('all');
  };

  // Filter and sort comments
  const filteredAndSortedComments = useMemo(() => {
    // First apply position filter
    const positionFiltered = comments.filter(comment => {
      if (filterPosition === 'all') return true;
      return comment.position && comment.position.toLowerCase() === filterPosition.toLowerCase();
    });

    // Then apply search filter
    const filtered = positionFiltered.filter(comment => {
      const searchLower = searchTerm.toLowerCase();
      return (
        comment.name?.toLowerCase().includes(searchLower) ||
        comment.organization?.toLowerCase().includes(searchLower) ||
        comment.position?.toLowerCase().includes(searchLower) ||
        comment.comment_text?.toLowerCase().includes(searchLower) ||
        comment.state?.toLowerCase().includes(searchLower)
      );
    });

    // Then sort
    return [...filtered].sort((a, b) => {
      let aVal = a[sortField] || '';
      let bVal = b[sortField] || '';

      // Handle date sorting
      if (sortField === 'submitted_date') {
        aVal = new Date(aVal || 0).getTime();
        bVal = new Date(bVal || 0).getTime();
      } else if (typeof aVal === 'string') {
        aVal = aVal.toLowerCase();
        bVal = bVal ? bVal.toLowerCase() : '';
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [comments, searchTerm, sortField, sortDirection, filterPosition]);

  // Pagination
  const paginatedComments = useMemo(() => {
    if (pageSize >= 999999) return filteredAndSortedComments;
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedComments.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedComments, currentPage, pageSize]);

  const totalPages = pageSize >= 999999 ? 1 : Math.ceil(filteredAndSortedComments.length / pageSize);

  // Get comments to export (selected or all)
  const getCommentsToExport = () => {
    if (selectedComments.size > 0) {
      return filteredAndSortedComments.filter(c => selectedComments.has(c.id));
    }
    return filteredAndSortedComments;
  };

  // Selection handlers
  const toggleSelectAll = () => {
    if (selectedComments.size === paginatedComments.length) {
      setSelectedComments(new Set());
    } else {
      const allKeys = new Set(paginatedComments.map(c => c.id));
      setSelectedComments(allKeys);
    }
  };

  const toggleSelectComment = (comment) => {
    const newSelected = new Set(selectedComments);
    if (newSelected.has(comment.id)) {
      newSelected.delete(comment.id);
    } else {
      newSelected.add(comment.id);
    }
    setSelectedComments(newSelected);
  };

  // Export functions
  const exportToCSV = () => {
    const commentsToExport = getCommentsToExport();
    const visibleCols = getDisplayColumns();
    const headers = visibleCols.map(col => col.label).join(',');
    const rows = commentsToExport.map(comment =>
      visibleCols.map(col => {
        let value = comment[col.key] || '';
        if (col.key === 'submitted_date' && value) {
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
    a.download = `comments-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const exportToTSV = () => {
    const commentsToExport = getCommentsToExport();
    const visibleCols = getDisplayColumns();
    const headers = visibleCols.map(col => col.label).join('\t');
    const rows = commentsToExport.map(comment =>
      visibleCols.map(col => {
        let value = comment[col.key] || '';
        if (col.key === 'submitted_date' && value) {
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
    a.download = `comments-${new Date().toISOString().split('T')[0]}.tsv`;
    a.click();
  };

  const exportToExcel = () => {
    const commentsToExport = getCommentsToExport();
    const visibleCols = getDisplayColumns();

    const headers = visibleCols.map(col => col.label).join('</th><th>');
    const rows = commentsToExport.map(comment =>
      '<tr><td>' + visibleCols.map(col => {
        let value = comment[col.key] || '';
        if (col.key === 'submitted_date' && value) {
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
    a.download = `comments-${new Date().toISOString().split('T')[0]}.xls`;
    a.click();
  };

  // Helper to get columns that should be displayed
  const getDisplayColumns = () => {
    return allColumns.filter(col => visibleColumns[col.key]);
  };

  const toggleColumn = (columnKey) => {
    const column = allColumns.find(col => col.key === columnKey);
    if (column && !column.core) {
      setVisibleColumns(prev => ({
        ...prev,
        [columnKey]: !prev[columnKey]
      }));
    }
  };

  const getPositionColor = (position) => {
    if (!position) return 'bg-gray-100 text-gray-800';

    const positionLower = position.toLowerCase();
    if (positionLower.includes('support')) return 'bg-green-100 text-green-800';
    if (positionLower.includes('oppose')) return 'bg-red-100 text-red-800';
    if (positionLower.includes('neutral')) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Public Comments</h1>
          <p className="mt-2 text-sm text-gray-700">
            Showing {filteredAndSortedComments.length} of {comments.length} comments
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
            Export Columns
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
                  {selectedComments.size > 0 ? `Export ${selectedComments.size} selected` : 'Export all comments'}
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
            onClick={syncComments}
            disabled={syncing}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Comments'}
          </button>
        </div>
      </div>

      {/* Column selector for export */}
      {showColumnSelector && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Export Columns</h3>
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
            onClick={() => {
              setFilterPosition('all');
              setCurrentPage(1);
            }}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'all'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            All ({comments.length})
          </button>
          <button
            onClick={() => {
              setFilterPosition('support');
              setCurrentPage(1);
            }}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'support'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Support ({comments.filter(c => c.position?.toLowerCase().includes('support')).length})
          </button>
          <button
            onClick={() => {
              setFilterPosition('oppose');
              setCurrentPage(1);
            }}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'oppose'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Oppose ({comments.filter(c => c.position?.toLowerCase().includes('oppose')).length})
          </button>
          <button
            onClick={() => {
              setFilterPosition('neutral');
              setCurrentPage(1);
            }}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'neutral'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Neutral ({comments.filter(c => c.position?.toLowerCase().includes('neutral')).length})
          </button>
        </div>
      </div>

      {/* Search, sort, and page size */}
      <div className="mt-6 flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Search comments..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
        />
        <select
          value={sortField}
          onChange={(e) => {
            setSortField(e.target.value);
            setCurrentPage(1);
          }}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
        >
          <option value="submitted_date">Sort by Date</option>
          <option value="name">Sort by Name</option>
          <option value="organization">Sort by Organization</option>
          <option value="position">Sort by Position</option>
        </select>
        <button
          onClick={() => setSortDirection(d => d === 'asc' ? 'desc' : 'asc')}
          className="px-4 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          {sortDirection === 'asc' ? '↑ Asc' : '↓ Desc'}
        </button>
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>
      </div>

      {/* Select All Checkbox */}
      {filteredAndSortedComments.length > 0 && (
        <div className="mt-4 flex items-center gap-2">
          <input
            type="checkbox"
            checked={selectedComments.size === paginatedComments.length && paginatedComments.length > 0}
            onChange={toggleSelectAll}
            className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">
            Select all {paginatedComments.length} on this page
            {selectedComments.size > 0 && ` (${selectedComments.size} selected)`}
          </span>
        </div>
      )}

      {/* Comments List */}
      <div className="mt-4 space-y-3">
        {loading ? (
          <div className="bg-white shadow sm:rounded-lg p-8 text-center text-sm text-gray-500">
            Loading comments...
          </div>
        ) : paginatedComments.length === 0 ? (
          <div className="bg-white shadow sm:rounded-lg p-8 text-center text-sm text-gray-500">
            No comments found
          </div>
        ) : (
          paginatedComments.map((comment, index) => (
            <div
              key={comment.id || index}
              className={`bg-white shadow sm:rounded-lg p-4 hover:shadow-md transition-shadow ${
                selectedComments.has(comment.id) ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <div className="flex items-start gap-3">
                <input
                  type="checkbox"
                  checked={selectedComments.has(comment.id)}
                  onChange={() => toggleSelectComment(comment)}
                  className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1.5">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <h3 className="text-base font-medium text-gray-900">
                        {comment.name || 'Anonymous'}
                      </h3>
                    </div>
                    {comment.state && (
                      <span className="text-xs text-gray-500">• {comment.state}</span>
                    )}
                  </div>
                  {comment.organization && (
                    <div className="flex items-center gap-2 mb-2">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      <p className="text-xs text-gray-600">{comment.organization}</p>
                    </div>
                  )}
                  <p className="text-sm text-gray-900 mb-2">{comment.comment_text}</p>
                  {comment.submitted_date && (
                    <p className="text-xs text-gray-500">
                      Submitted: {new Date(comment.submitted_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="ml-3">
                  <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${getPositionColor(comment.position)}`}>
                    {comment.position || 'No Position'}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-between">
          <div className="text-sm text-gray-700">
            Showing {filteredAndSortedComments.length} of {comments.length} comments
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

export default CommentsEnhanced;
