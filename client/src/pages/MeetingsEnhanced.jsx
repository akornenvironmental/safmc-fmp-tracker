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
  const [organizationFilter, setOrganizationFilter] = useState([]);
  const [regionFilter, setRegionFilter] = useState([]);
  const [showOrgDropdown, setShowOrgDropdown] = useState(false);
  const [showRegionDropdown, setShowRegionDropdown] = useState(false);

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

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (!event.target.closest('.relative')) {
        setShowOrgDropdown(false);
        setShowRegionDropdown(false);
      }
    };

    if (showOrgDropdown || showRegionDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showOrgDropdown, showRegionDropdown]);

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
    setOrganizationFilter([]);
    setRegionFilter([]);
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

      // Organization filter (multi-select)
      const matchesOrganization = organizationFilter.length === 0 ||
        organizationFilter.some(org => meeting.council?.toLowerCase().includes(org.toLowerCase()));

      // Region filter (multi-select)
      const matchesRegion = regionFilter.length === 0 ||
        regionFilter.some(reg => meeting.region?.toLowerCase() === reg.toLowerCase());

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

      {/* Filters, Search and page size */}
      <div className="mt-6 flex flex-col lg:flex-row gap-3 items-start lg:items-center">
        {/* Organization multi-select filter */}
        <div className="relative">
          <button
            onClick={() => {
              setShowOrgDropdown(!showOrgDropdown);
              setShowRegionDropdown(false);
            }}
            className="min-w-[200px] flex items-center justify-between gap-2 px-4 py-2 text-sm bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-brand-green"
          >
            <span className="truncate">
              {organizationFilter.length === 0
                ? 'Organization'
                : organizationFilter.length === 1
                  ? organizationFilter[0].split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
                  : `${organizationFilter.length} selected`}
            </span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {showOrgDropdown && (
            <div className="absolute z-50 mt-1 w-80 bg-white border border-gray-300 rounded-md shadow-lg max-h-96 overflow-y-auto">
              <div className="p-2 space-y-1">
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('south atlantic')}
                    onChange={(e) => {
                      const val = 'south atlantic';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">South Atlantic Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('new england')}
                    onChange={(e) => {
                      const val = 'new england';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">New England Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('mid-atlantic')}
                    onChange={(e) => {
                      const val = 'mid-atlantic';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Mid-Atlantic Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('gulf of mexico')}
                    onChange={(e) => {
                      const val = 'gulf of mexico';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Gulf of Mexico Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('caribbean')}
                    onChange={(e) => {
                      const val = 'caribbean';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Caribbean Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('pacific fishery')}
                    onChange={(e) => {
                      const val = 'pacific fishery';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Pacific Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('north pacific')}
                    onChange={(e) => {
                      const val = 'north pacific';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">North Pacific Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('western pacific')}
                    onChange={(e) => {
                      const val = 'western pacific';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Western Pacific Fishery Management Council</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('atlantic states')}
                    onChange={(e) => {
                      const val = 'atlantic states';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Atlantic States Marine Fisheries Commission</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('gulf states')}
                    onChange={(e) => {
                      const val = 'gulf states';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Gulf States Marine Fisheries Commission</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('pacific states')}
                    onChange={(e) => {
                      const val = 'pacific states';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Pacific States Marine Fisheries Commission</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('noaa')}
                    onChange={(e) => {
                      const val = 'noaa';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">NOAA Fisheries</span>
                </label>
                <div className="border-t border-gray-200 my-1"></div>
                <div className="px-2 py-1 text-xs font-medium text-gray-500">State Agencies</div>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('north carolina')}
                    onChange={(e) => {
                      const val = 'north carolina';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">North Carolina Division of Marine Fisheries</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('south carolina')}
                    onChange={(e) => {
                      const val = 'south carolina';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">South Carolina Department of Natural Resources</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('georgia')}
                    onChange={(e) => {
                      const val = 'georgia';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Georgia Department of Natural Resources</span>
                </label>
                <label className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                  <input
                    type="checkbox"
                    checked={organizationFilter.includes('florida')}
                    onChange={(e) => {
                      const val = 'florida';
                      setOrganizationFilter(prev =>
                        e.target.checked ? [...prev, val] : prev.filter(v => v !== val)
                      );
                      setCurrentPage(1);
                    }}
                    className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                  />
                  <span className="text-sm">Florida Fish and Wildlife Conservation Commission</span>
                </label>
                {organizationFilter.length > 0 && (
                  <div className="border-t border-gray-200 mt-2 pt-2">
                    <button
                      onClick={() => {
                        setOrganizationFilter([]);
                        setCurrentPage(1);
                      }}
                      className="w-full text-xs text-brand-blue hover:text-brand-green px-2 py-1 text-center"
                    >
                      Clear All
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Region multi-select filter */}
        <div className="relative">
          <button
            onClick={() => {
              setShowRegionDropdown(!showRegionDropdown);
              setShowOrgDropdown(false);
            }}
            className="min-w-[180px] flex items-center justify-between gap-2 px-4 py-2 text-sm bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-brand-green"
          >
            <span className="truncate">
              {regionFilter.length === 0
                ? 'Region'
                : regionFilter.length === 1
                  ? regionFilter[0].charAt(0).toUpperCase() + regionFilter[0].slice(1)
                  : `${regionFilter.length} selected`}
            </span>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          {showRegionDropdown && (
            <div className="absolute z-50 mt-1 w-64 bg-white border border-gray-300 rounded-md shadow-lg max-h-96 overflow-y-auto">
              <div className="p-2 space-y-1">
                {['northeast', 'mid-atlantic', 'southeast', 'gulf of mexico', 'caribbean', 'west coast', 'alaska', 'pacific islands', 'atlantic coast', 'gulf states', 'pacific states', 'north carolina', 'south carolina', 'georgia', 'florida'].map(region => (
                  <label key={region} className="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-50 rounded cursor-pointer">
                    <input
                      type="checkbox"
                      checked={regionFilter.includes(region)}
                      onChange={(e) => {
                        setRegionFilter(prev =>
                          e.target.checked ? [...prev, region] : prev.filter(v => v !== region)
                        );
                        setCurrentPage(1);
                      }}
                      className="h-4 w-4 rounded border-gray-300 text-brand-green focus:ring-brand-green"
                    />
                    <span className="text-sm capitalize">{region}</span>
                  </label>
                ))}
                {regionFilter.length > 0 && (
                  <div className="border-t border-gray-200 mt-2 pt-2">
                    <button
                      onClick={() => {
                        setRegionFilter([]);
                        setCurrentPage(1);
                      }}
                      className="w-full text-xs text-brand-blue hover:text-brand-green px-2 py-1 text-center"
                    >
                      Clear All
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Search input */}
        <input
          type="text"
          placeholder="Search meetings..."
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setCurrentPage(1);
          }}
          className="flex-1 min-w-[200px] rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm px-4 py-2 border"
          aria-label="Search meetings by title, council, location, or type"
        />

        {/* Page size selector */}
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
