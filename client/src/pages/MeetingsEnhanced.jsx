import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import { Calendar, MapPin, RefreshCw, Download, Settings, RotateCcw } from 'lucide-react';

const MeetingsEnhanced = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncingFisheryPulse, setSyncingFisheryPulse] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('start_date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [pageSize, setPageSize] = useState(20);
  const [currentPage, setCurrentPage] = useState(1);
  const [showColumnSelector, setShowColumnSelector] = useState(false);
  const [selectedMeetings, setSelectedMeetings] = useState(new Set());
  const [organizationFilter, setOrganizationFilter] = useState('all');
  const [regionFilter, setRegionFilter] = useState('all');

  // Column visibility state
  const [visibleColumns, setVisibleColumns] = useState({
    title: true,
    council: true,
    start_date: true,
    location: true,
    type: true,
    region: true,
    source: false,
    description: false,
    organization_type: false,
  });

  // Define all available columns
  const allColumns = [
    { key: 'title', label: 'Title', core: true },
    { key: 'council', label: 'Organization', core: true },
    { key: 'region', label: 'Region', core: true },
    { key: 'start_date', label: 'Date', core: true },
    { key: 'location', label: 'Location', core: true },
    { key: 'type', label: 'Type', core: true },
    { key: 'source', label: 'Source', core: false },
    { key: 'description', label: 'Description', core: false },
    { key: 'organization_type', label: 'Org Type', core: false },
  ];

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/meetings`);
      const data = await response.json();

      if (data.success) {
        setMeetings(data.meetings || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching meetings:', error);
      setLoading(false);
    }
  };

  const syncMeetings = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/meetings`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchMeetings();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing meetings:', error);
      alert('Error syncing meetings');
    } finally {
      setSyncing(false);
    }
  };

  const syncFisheryPulse = async () => {
    try {
      setSyncingFisheryPulse(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/fisherypulse`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(data.message || `Sync complete! Found ${data.itemsFound} meetings, ${data.itemsNew} new.`);
        fetchMeetings();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing FisheryPulse:', error);
      alert('Error syncing FisheryPulse meetings');
    } finally {
      setSyncingFisheryPulse(false);
    }
  };

  // Reset all filters and sorting
  const handleReset = () => {
    setSearchTerm('');
    setSortField('start_date');
    setSortDirection('desc');
    setCurrentPage(1);
    setSelectedMeetings(new Set());
    setShowColumnSelector(false);
    setOrganizationFilter('all');
    setRegionFilter('all');
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

  // Filter and sort meetings
  const filteredAndSortedMeetings = useMemo(() => {
    const filtered = meetings.filter(meeting => {
      // Text search filter
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = (
        meeting.title?.toLowerCase().includes(searchLower) ||
        meeting.council?.toLowerCase().includes(searchLower) ||
        meeting.location?.toLowerCase().includes(searchLower) ||
        meeting.type?.toLowerCase().includes(searchLower) ||
        meeting.description?.toLowerCase().includes(searchLower) ||
        meeting.region?.toLowerCase().includes(searchLower)
      );

      // Organization filter
      const matchesOrganization = organizationFilter === 'all' ||
        meeting.council?.toLowerCase().includes(organizationFilter.toLowerCase());

      // Region filter
      const matchesRegion = regionFilter === 'all' ||
        meeting.region?.toLowerCase() === regionFilter.toLowerCase();

      return matchesSearch && matchesOrganization && matchesRegion;
    });

    return [...filtered].sort((a, b) => {
      let aVal = a[sortField] || '';
      let bVal = b[sortField] || '';

      // Handle date sorting
      if (sortField === 'start_date' || sortField === 'end_date') {
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
  }, [meetings, searchTerm, sortField, sortDirection, organizationFilter, regionFilter]);

  // Pagination
  const paginatedMeetings = useMemo(() => {
    if (pageSize >= 999999) return filteredAndSortedMeetings;
    const startIndex = (currentPage - 1) * pageSize;
    return filteredAndSortedMeetings.slice(startIndex, startIndex + pageSize);
  }, [filteredAndSortedMeetings, currentPage, pageSize]);

  const totalPages = pageSize >= 999999 ? 1 : Math.ceil(filteredAndSortedMeetings.length / pageSize);

  // Get meetings to export (selected or all)
  const getMeetingsToExport = () => {
    if (selectedMeetings.size > 0) {
      return filteredAndSortedMeetings.filter(m => selectedMeetings.has(m.id));
    }
    return filteredAndSortedMeetings;
  };

  // Selection handlers
  const toggleSelectAll = () => {
    if (selectedMeetings.size === paginatedMeetings.length) {
      setSelectedMeetings(new Set());
    } else {
      const allKeys = new Set(paginatedMeetings.map(m => m.id));
      setSelectedMeetings(allKeys);
    }
  };

  const toggleSelectMeeting = (meeting) => {
    const newSelected = new Set(selectedMeetings);
    if (newSelected.has(meeting.id)) {
      newSelected.delete(meeting.id);
    } else {
      newSelected.add(meeting.id);
    }
    setSelectedMeetings(newSelected);
  };

  // Export functions
  const exportToCSV = () => {
    const meetingsToExport = getMeetingsToExport();
    const visibleCols = getDisplayColumns();
    const headers = visibleCols.map(col => col.label).join(',');
    const rows = meetingsToExport.map(meeting =>
      visibleCols.map(col => {
        let value = meeting[col.key] || '';
        if (col.key === 'start_date' && value) {
          value = new Date(value).toLocaleDateString();
        }
        if (col.key === 'end_date' && value) {
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
    a.download = `meetings-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const exportToTSV = () => {
    const meetingsToExport = getMeetingsToExport();
    const visibleCols = getDisplayColumns();
    const headers = visibleCols.map(col => col.label).join('\t');
    const rows = meetingsToExport.map(meeting =>
      visibleCols.map(col => {
        let value = meeting[col.key] || '';
        if (col.key === 'start_date' && value) {
          value = new Date(value).toLocaleDateString();
        }
        if (col.key === 'end_date' && value) {
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
    a.download = `meetings-${new Date().toISOString().split('T')[0]}.tsv`;
    a.click();
  };

  const exportToExcel = () => {
    const meetingsToExport = getMeetingsToExport();
    const visibleCols = getDisplayColumns();

    const headers = visibleCols.map(col => col.label).join('</th><th>');
    const rows = meetingsToExport.map(meeting =>
      '<tr><td>' + visibleCols.map(col => {
        let value = meeting[col.key] || '';
        if (col.key === 'start_date' && value) {
          value = new Date(value).toLocaleDateString();
        }
        if (col.key === 'end_date' && value) {
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
    a.download = `meetings-${new Date().toISOString().split('T')[0]}.xls`;
    a.click();
  };

  // Helper to get columns that should be displayed
  const getDisplayColumns = () => {
    return allColumns.filter(col => {
      if (col.key === 'title' || col.key === 'council') return true;
      return visibleColumns[col.key];
    });
  };

  const toggleColumn = (columnKey) => {
    if (columnKey === 'title' || columnKey === 'council') return;
    const column = allColumns.find(col => col.key === columnKey);
    if (column && !column.core) {
      setVisibleColumns(prev => ({
        ...prev,
        [columnKey]: !prev[columnKey]
      }));
    }
  };

  const getTypeColor = (type) => {
    if (!type) return 'bg-gray-100 text-gray-800';

    const typeLower = type.toLowerCase();
    if (typeLower.includes('council')) return 'bg-blue-100 text-blue-800';
    if (typeLower.includes('committee')) return 'bg-green-100 text-green-800';
    if (typeLower.includes('workshop')) return 'bg-purple-100 text-purple-800';
    if (typeLower.includes('webinar')) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Meeting Calendar</h1>
          <p className="mt-2 text-sm text-gray-700">
            Showing {filteredAndSortedMeetings.length} of {meetings.length} meetings
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
                  {selectedMeetings.size > 0 ? `Export ${selectedMeetings.size} selected` : 'Export all meetings'}
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
            onClick={syncMeetings}
            disabled={syncing}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync SAFMC'}
          </button>
          <button
            onClick={syncFisheryPulse}
            disabled={syncingFisheryPulse}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-gradient-to-r from-brand-green to-green-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:from-green-600 hover:to-green-700 focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncingFisheryPulse ? 'animate-spin' : ''}`} />
            {syncingFisheryPulse ? 'Syncing...' : 'Sync All Councils'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="mt-4 flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Organization:</label>
          <select
            value={organizationFilter}
            onChange={(e) => {
              setOrganizationFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="rounded-md border-gray-300 shadow-sm focus:border-brand-green focus:ring-brand-green text-sm"
          >
            <option value="all">All Organizations</option>
            <option value="safmc">SAFMC</option>
            <option value="nefmc">NEFMC</option>
            <option value="mafmc">MAFMC</option>
            <option value="gmfmc">GMFMC</option>
            <option value="cfmc">CFMC</option>
            <option value="pfmc">PFMC</option>
            <option value="npfmc">NPFMC</option>
            <option value="wpfmc">WPFMC</option>
            <option value="asmfc">ASMFC</option>
            <option value="gsmfc">GSMFC</option>
            <option value="psmfc">PSMFC</option>
            <option value="noaa">NOAA</option>
            <optgroup label="State Agencies">
              <option value="ncdmf">NC Marine Fisheries</option>
              <option value="scdnr">SC DNR</option>
              <option value="gadnr">GA DNR</option>
              <option value="fwc">FL FWC</option>
            </optgroup>
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-sm font-medium text-gray-700">Region:</label>
          <select
            value={regionFilter}
            onChange={(e) => {
              setRegionFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="rounded-md border-gray-300 shadow-sm focus:border-brand-green focus:ring-brand-green text-sm"
          >
            <option value="all">All Regions</option>
            <option value="northeast">Northeast</option>
            <option value="mid-atlantic">Mid-Atlantic</option>
            <option value="southeast">Southeast</option>
            <option value="gulf of mexico">Gulf of Mexico</option>
            <option value="caribbean">Caribbean</option>
            <option value="west coast">West Coast</option>
            <option value="alaska">Alaska</option>
            <option value="pacific islands">Pacific Islands</option>
            <option value="atlantic coast">Atlantic Coast</option>
            <option value="gulf states">Gulf States</option>
            <option value="pacific states">Pacific States</option>
            <option value="north carolina">North Carolina</option>
            <option value="south carolina">South Carolina</option>
            <option value="georgia">Georgia</option>
            <option value="florida">Florida</option>
          </select>
        </div>
        {(organizationFilter !== 'all' || regionFilter !== 'all') && (
          <button
            onClick={() => {
              setOrganizationFilter('all');
              setRegionFilter('all');
              setCurrentPage(1);
            }}
            className="text-xs text-gray-600 hover:text-brand-blue underline"
          >
            Clear filters
          </button>
        )}
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
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className={`text-sm ${col.core ? 'text-gray-400' : 'text-gray-700'}`}>
                  {col.label} {col.core && '(required)'}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* Search and page size */}
      <div className="mt-6 flex flex-col sm:flex-row gap-4">
        <input
          type="text"
          placeholder="Search meetings..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="flex-1 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
          aria-label="Search meetings by title, council, location, or type"
        />
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
          aria-label="Number of meetings to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>
      </div>

      {/* Meetings Table */}
      <div className="mt-6 bg-white shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <caption className="sr-only">
            Meeting calendar with {filteredAndSortedMeetings.length} meetings. Table includes columns for selection, title, council, date, location, and type. Click column headers to sort.
          </caption>
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-2 py-1.5 text-left">
                <input
                  type="checkbox"
                  checked={selectedMeetings.size === paginatedMeetings.length && paginatedMeetings.length > 0}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  aria-label={`Select all ${paginatedMeetings.length} meetings on this page`}
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
                  Loading meetings...
                </td>
              </tr>
            ) : paginatedMeetings.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-3 py-8 text-center text-sm text-gray-500">
                  No meetings found
                </td>
              </tr>
            ) : (
              paginatedMeetings.map((meeting, index) => (
                <tr key={meeting.id || index} className="hover:bg-gray-50">
                  <td className="px-2 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedMeetings.has(meeting.id)}
                      onChange={() => toggleSelectMeeting(meeting)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`Select meeting: ${meeting.title}`}
                    />
                  </td>
                  {getDisplayColumns().map(col => (
                    <td key={col.key} className="px-3 py-2">
                      {col.key === 'title' ? (
                        meeting.source_url ? (
                          <a
                            href={meeting.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm font-medium text-brand-blue hover:text-brand-green hover:underline"
                          >
                            {meeting.title}
                          </a>
                        ) : (
                          <div className="text-sm font-medium text-gray-900">{meeting.title}</div>
                        )
                      ) : col.key === 'council' ? (
                        <div>
                          <div className="text-xs font-semibold text-brand-blue">{meeting.council || 'SAFMC'}</div>
                          {meeting.organization_type && visibleColumns.organization_type && (
                            <div className="text-xs text-gray-500">{meeting.organization_type}</div>
                          )}
                        </div>
                      ) : col.key === 'start_date' ? (
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <div>
                            <div className="text-xs text-gray-900">
                              {meeting.start_date ? new Date(meeting.start_date).toLocaleDateString() : 'TBD'}
                            </div>
                            {meeting.end_date && meeting.end_date !== meeting.start_date && (
                              <div className="text-xs text-gray-500">
                                to {new Date(meeting.end_date).toLocaleDateString()}
                              </div>
                            )}
                          </div>
                        </div>
                      ) : col.key === 'location' ? (
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                          <div className="text-xs text-gray-900">{meeting.location || 'TBD'}</div>
                        </div>
                      ) : col.key === 'type' ? (
                        <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${getTypeColor(meeting.type)}`}>
                          {meeting.type || 'Meeting'}
                        </span>
                      ) : col.key === 'description' ? (
                        meeting.description ? (
                          <div className="text-xs text-gray-500">{meeting.description.substring(0, 100)}...</div>
                        ) : null
                      ) : (
                        <div className="text-xs text-gray-900">{meeting[col.key] || ''}</div>
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
            Showing {filteredAndSortedMeetings.length} of {meetings.length} meetings
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Go to previous page"
            >
              Previous
            </button>
            <span className="px-4 py-2 text-sm text-gray-700" aria-current="page" aria-label={`Page ${currentPage} of ${totalPages}`}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Go to next page"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MeetingsEnhanced;
