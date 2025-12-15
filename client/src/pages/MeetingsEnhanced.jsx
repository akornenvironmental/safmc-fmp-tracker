import { useState, useEffect, useMemo } from 'react';
import FavoriteButton from '../components/FavoriteButton';
import Button from '../components/Button';
import ButtonGroup from '../components/ButtonGroup';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import { API_BASE_URL } from '../config';
import {
  Calendar, MapPin, RefreshCw, Download, Settings, RotateCcw,
  Table, LayoutGrid, List, ChevronLeft, ChevronRight, Clock, ExternalLink
} from 'lucide-react';

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
  const [selectedMeetings, setSelectedMeetings] = useState(new Set());
  const [organizationFilter, setOrganizationFilter] = useState([]);
  const [regionFilter, setRegionFilter] = useState([]);
  const [fmpFilter, setFmpFilter] = useState([]);
  const [upcomingOnly, setUpcomingOnly] = useState(false);

  // View mode: 'table', 'calendar', 'agenda'
  const [viewMode, setViewMode] = useState('table');
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(null);

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
    setOrganizationFilter([]);
    setRegionFilter([]);
    setFmpFilter([]);
    setUpcomingOnly(false);
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
      // Text search filter - enhanced to search species and topics
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = (
        meeting.title?.toLowerCase().includes(searchLower) ||
        meeting.council?.toLowerCase().includes(searchLower) ||
        meeting.location?.toLowerCase().includes(searchLower) ||
        meeting.type?.toLowerCase().includes(searchLower) ||
        meeting.description?.toLowerCase().includes(searchLower) ||
        meeting.region?.toLowerCase().includes(searchLower) ||
        meeting.agenda_content?.toLowerCase().includes(searchLower) ||
        meeting.topics?.some(topic => topic.toLowerCase().includes(searchLower)) ||
        meeting.species_discussed?.some(species => species.toLowerCase().includes(searchLower))
      );

      // Organization filter (multi-select)
      const matchesOrganization = organizationFilter.length === 0 ||
        organizationFilter.some(org => meeting.council?.toLowerCase().includes(org.toLowerCase()));

      // Region filter (multi-select)
      const matchesRegion = regionFilter.length === 0 ||
        regionFilter.some(reg => meeting.region?.toLowerCase() === reg.toLowerCase());

      // FMP filter (multi-select)
      const matchesFmp = fmpFilter.length === 0 ||
        fmpFilter.some(fmp => {
          const titleLower = meeting.title?.toLowerCase() || '';
          const descLower = meeting.description?.toLowerCase() || '';
          return titleLower.includes(fmp.toLowerCase()) || descLower.includes(fmp.toLowerCase());
        });

      // Upcoming only filter
      const matchesUpcoming = !upcomingOnly ||
        (meeting.start_date && new Date(meeting.start_date) >= new Date());

      return matchesSearch && matchesOrganization && matchesRegion && matchesFmp && matchesUpcoming;
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
  }, [meetings, searchTerm, sortField, sortDirection, organizationFilter, regionFilter, fmpFilter, upcomingOnly]);

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

  const getTypeColor = (type) => {
    if (!type) return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';

    const typeLower = type.toLowerCase();
    if (typeLower.includes('council')) return 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200';
    if (typeLower.includes('committee')) return 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200';
    if (typeLower.includes('workshop')) return 'bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200';
    if (typeLower.includes('webinar')) return 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200';
    return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200';
  };

  // Calendar view helpers
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startPadding = firstDay.getDay();
    const days = [];

    for (let i = startPadding - 1; i >= 0; i--) {
      days.push({ date: new Date(year, month, -i), isCurrentMonth: false });
    }
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push({ date: new Date(year, month, i), isCurrentMonth: true });
    }
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({ date: new Date(year, month + 1, i), isCurrentMonth: false });
    }
    return days;
  }, [currentDate]);

  const meetingsByDate = useMemo(() => {
    const map = {};
    filteredAndSortedMeetings.forEach(meeting => {
      if (!meeting.start_date) return;
      const dateKey = meeting.start_date.split('T')[0];
      if (!map[dateKey]) map[dateKey] = [];
      map[dateKey].push(meeting);
    });
    return map;
  }, [filteredAndSortedMeetings]);

  const selectedDateMeetings = useMemo(() => {
    if (!selectedDate) return [];
    const dateKey = selectedDate.toISOString().split('T')[0];
    return meetingsByDate[dateKey] || [];
  }, [selectedDate, meetingsByDate]);

  const upcomingMeetings = useMemo(() => {
    const now = new Date();
    return filteredAndSortedMeetings
      .filter(m => m.start_date && new Date(m.start_date) >= now)
      .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
      .slice(0, 20);
  }, [filteredAndSortedMeetings]);

  const prevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const nextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  const goToToday = () => { setCurrentDate(new Date()); setSelectedDate(new Date()); };
  const isToday = (date) => date.toDateString() === new Date().toDateString();

  const getMeetingDotColor = (meeting) => {
    const title = (meeting.title || '').toLowerCase();
    if (title.includes('council')) return 'bg-blue-500';
    if (title.includes('committee')) return 'bg-green-500';
    if (title.includes('public')) return 'bg-purple-500';
    if (title.includes('webinar')) return 'bg-orange-500';
    return 'bg-gray-500';
  };

  return (
    <div>
      {/* Description and Actions */}
      <div className="page-description-container">
        <p className="page-description-text">
          View and track Council meeting schedules, agendas, and outcomes.
        </p>
        <div className="page-description-actions">
          {/* View Toggle */}
          <div className="inline-flex rounded-md shadow-sm" role="group">
            <button
              onClick={() => setViewMode('table')}
              className={`inline-flex items-center gap-1.5 h-9 px-2.5 text-sm font-medium rounded-l-md border transition-colors ${
                viewMode === 'table'
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400'
              }`}
            >
              <Table size={14} /> Table
            </button>
            <button
              onClick={() => setViewMode('calendar')}
              className={`inline-flex items-center gap-1.5 h-9 px-2.5 text-sm font-medium border-t border-b transition-colors ${
                viewMode === 'calendar'
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400'
              }`}
            >
              <LayoutGrid size={14} /> Calendar
            </button>
            <button
              onClick={() => setViewMode('agenda')}
              className={`inline-flex items-center gap-1.5 h-9 px-2.5 text-sm font-medium rounded-r-md border transition-colors ${
                viewMode === 'agenda'
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400'
              }`}
            >
              <List size={14} /> Agenda
            </button>
          </div>

          {/* Export Dropdown */}
          <div className="relative">
            <Button
              variant="secondary"
              icon={Download}
              onClick={(e) => {
                const menu = e.currentTarget.nextElementSibling;
                menu.classList.toggle('hidden');
              }}
              className="gap-1.5 px-2.5 h-9"
            >
              Export
            </Button>
            <div className="hidden absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 dark:ring-gray-600 z-10">
              <div className="py-1">
                <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                  {selectedMeetings.size > 0 ? `Export ${selectedMeetings.size} selected` : 'Export all meetings'}
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

          {/* Sync Dropdown - combining both sync options */}
          <div className="relative">
            <Button
              variant="primary"
              icon={RefreshCw}
              onClick={(e) => {
                const menu = e.currentTarget.nextElementSibling;
                menu.classList.toggle('hidden');
              }}
              className="gap-1.5 px-2.5 h-9"
            >
              Sync
            </Button>
            <div className="hidden absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 dark:ring-gray-600 z-10">
              <div className="py-1">
                <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                  Sync meetings from sources
                </div>
                <button
                  onClick={() => {
                    syncMeetings();
                    document.querySelector('.hidden.absolute')?.classList.add('hidden');
                  }}
                  disabled={syncing}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left disabled:opacity-50"
                >
                  {syncing ? 'Syncing SAFMC...' : 'Sync SAFMC Meetings'}
                </button>
                <button
                  onClick={() => {
                    syncFisheryPulse();
                    document.querySelector('.hidden.absolute')?.classList.add('hidden');
                  }}
                  disabled={syncingFisheryPulse}
                  className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 w-full text-left disabled:opacity-50"
                >
                  {syncingFisheryPulse ? 'Syncing All...' : 'Sync All Councils'}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Single row: Search → Filters → Show → Reset */}
      <PageControlsContainer>
        {/* Search input */}
        <SearchBar
          value={searchTerm}
          onChange={(value) => {
            setSearchTerm(value);
            setCurrentPage(1);
          }}
          placeholder="Search meetings, species, topics..."
          ariaLabel="Search meetings by title, council, location, species, or topics"
        />

        {/* Organization multi-select filter */}
        <FilterDropdown
          label="Organization"
          options={[
            { value: 'south atlantic', label: 'South Atlantic Fishery Management Council' },
            { value: 'new england', label: 'New England Fishery Management Council' },
            { value: 'mid-atlantic', label: 'Mid-Atlantic Fishery Management Council' },
            { value: 'gulf of mexico', label: 'Gulf of Mexico Fishery Management Council' },
            { value: 'caribbean', label: 'Caribbean Fishery Management Council' },
            { value: 'pacific fishery', label: 'Pacific Fishery Management Council' },
            { value: 'north pacific', label: 'North Pacific Fishery Management Council' },
            { value: 'western pacific', label: 'Western Pacific Fishery Management Council' },
            { value: 'atlantic states', label: 'Atlantic States Marine Fisheries Commission' },
            { value: 'gulf states', label: 'Gulf States Marine Fisheries Commission' },
            { value: 'pacific states', label: 'Pacific States Marine Fisheries Commission' },
            { value: 'noaa', label: 'NOAA Fisheries' },
            { value: 'north carolina', label: 'North Carolina Division of Marine Fisheries', section: 'State Agencies' },
            { value: 'south carolina', label: 'South Carolina Department of Natural Resources', section: 'State Agencies' },
            { value: 'georgia', label: 'Georgia Department of Natural Resources', section: 'State Agencies' },
            { value: 'florida', label: 'Florida Fish and Wildlife Conservation Commission', section: 'State Agencies' },
          ]}
          selectedValues={organizationFilter}
          onChange={(values) => {
            setOrganizationFilter(values);
            setCurrentPage(1);
          }}
          showCounts={false}
        />

        {/* Region multi-select filter */}
        <FilterDropdown
          label="Region"
          options={['northeast', 'mid-atlantic', 'southeast', 'gulf of mexico', 'caribbean', 'west coast', 'alaska', 'pacific islands', 'atlantic coast', 'gulf states', 'pacific states', 'north carolina', 'south carolina', 'georgia', 'florida'].map(region => ({
            value: region,
            label: region.split(' ').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
          }))}
          selectedValues={regionFilter}
          onChange={(values) => {
            setRegionFilter(values);
            setCurrentPage(1);
          }}
          showCounts={false}
        />

        {/* FMP multi-select filter */}
        <FilterDropdown
          label="FMP"
          options={[
            'Snapper Grouper',
            'Coastal Migratory Pelagics',
            'Dolphin Wahoo',
            'Spiny Lobster',
            'Golden Crab',
            'Shrimp',
            'Coral',
            'Sargassum'
          ].map(fmp => ({
            value: fmp,
            label: fmp
          }))}
          selectedValues={fmpFilter}
          onChange={(values) => {
            setFmpFilter(values);
            setCurrentPage(1);
          }}
          showCounts={false}
        />

        {/* Upcoming only filter */}
        <label className="inline-flex items-center gap-1.5 h-9 px-2.5 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 transition-colors">
          <input
            type="checkbox"
            checked={upcomingOnly}
            onChange={(e) => {
              setUpcomingOnly(e.target.checked);
              setCurrentPage(1);
            }}
            className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-brand-green focus:ring-brand-green"
          />
          <span className="whitespace-nowrap">Upcoming only</span>
        </label>

        {/* Page Size */}
        <select
          value={pageSize}
          onChange={(e) => {
            setPageSize(Number(e.target.value));
            setCurrentPage(1);
          }}
          className="h-9 bg-white dark:bg-gray-800 rounded-md border border-gray-300 dark:border-gray-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm px-3 text-gray-900 dark:text-gray-100 hover:border-gray-400 dark:hover:border-gray-500 transition-colors cursor-pointer"
          aria-label="Number of meetings to display per page"
        >
          <option value={20}>Show 20</option>
          <option value={50}>Show 50</option>
          <option value={100}>Show 100</option>
          <option value={999999}>Show ALL</option>
        </select>

        {/* Columns Dropdown (table view only) */}
        {viewMode === 'table' && (
          <FilterDropdown
            label="Columns"
            options={allColumns.filter(col => !col.core).map(col => ({
              value: col.key,
              label: col.label
            }))}
            selectedValues={Object.entries(visibleColumns)
              .filter(([key, visible]) => {
                const col = allColumns.find(c => c.key === key);
                return visible && col && !col.core;
              })
              .map(([key]) => key)
            }
            onChange={(selectedKeys) => {
              const newVisibleColumns = { ...visibleColumns };
              // Set all non-core columns to false first
              allColumns.filter(col => !col.core).forEach(col => {
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
        )}

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

      {/* Table View */}
      {viewMode === 'table' && (
        <>
      {/* Table Count */}
      <div className="mt-6 mb-2 flex items-center justify-between">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Showing <span className="font-medium text-gray-900 dark:text-gray-100">{filteredAndSortedMeetings.length}</span> of <span className="font-medium text-gray-900 dark:text-gray-100">{meetings.length}</span> meetings
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 shadow overflow-x-auto sm:rounded-lg">
        <table className="min-w-full">
          <caption className="sr-only">
            Meeting calendar with {filteredAndSortedMeetings.length} meetings. Table includes columns for selection, title, council, date, location, and type. Click column headers to sort.
          </caption>
          <thead className="bg-gray-50 dark:bg-gray-900">
            <tr>
              <th scope="col" className="px-2 py-2 text-left align-middle">
                <input
                  type="checkbox"
                  checked={selectedMeetings.size === paginatedMeetings.length && paginatedMeetings.length > 0}
                  onChange={toggleSelectAll}
                  className="h-4 w-4 rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                  aria-label={`Select all ${paginatedMeetings.length} meetings on this page`}
                />
              </th>
              {getDisplayColumns().map(col => (
                <th
                  key={col.key}
                  scope="col"
                  className="px-1.5 py-1 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 select-none align-middle"
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
          <tbody className="bg-white dark:bg-gray-800">
            {loading ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">
                  Loading meetings...
                </td>
              </tr>
            ) : paginatedMeetings.length === 0 ? (
              <tr>
                <td colSpan={getDisplayColumns().length + 1} className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">
                  No meetings found
                </td>
              </tr>
            ) : (
              paginatedMeetings.map((meeting, index) => (
                <tr key={meeting.id || index} className={`${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-850'} hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors`}>
                  <td className="px-1.5 py-0.5">
                    <input
                      type="checkbox"
                      checked={selectedMeetings.has(meeting.id)}
                      onChange={() => toggleSelectMeeting(meeting)}
                      className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                      aria-label={`Select meeting: ${meeting.title}`}
                    />
                  </td>
                  {getDisplayColumns().map(col => (
                    <td key={col.key} className="px-1.5 py-0.5">
                      {col.key === 'title' ? (
                        <div className="flex items-start gap-2">
                          <div className="flex-1">
                            {meeting.source_url ? (
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
                            )}
                          </div>
                          <FavoriteButton itemType="meeting" itemId={meeting.meeting_id} />
                        </div>
                      ) : col.key === 'council' ? (
                        <div>
                          <div className="text-sm font-semibold text-brand-blue">{meeting.council || 'SAFMC'}</div>
                          {meeting.organization_type && visibleColumns.organization_type && (
                            <div className="text-sm text-gray-500">{meeting.organization_type}</div>
                          )}
                        </div>
                      ) : col.key === 'start_date' ? (
                        <div className="flex items-center gap-2">
                          <Calendar className="w-4 h-4 text-gray-400" />
                          <div>
                            <div className="text-sm text-gray-900">
                              {meeting.start_date ? new Date(meeting.start_date).toLocaleDateString() : 'TBD'}
                            </div>
                            {meeting.end_date && meeting.end_date !== meeting.start_date && (
                              <div className="text-sm text-gray-500">
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

      {/* Pagination - Table View Only */}
      {totalPages > 1 && (
        <div className="mt-4 flex items-center justify-end">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="h-9 px-4 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Go to previous page"
            >
              Previous
            </button>
            <span className="px-3 text-sm text-gray-600 dark:text-gray-400" aria-current="page" aria-label={`Page ${currentPage} of ${totalPages}`}>
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="h-9 px-4 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label="Go to next page"
            >
              Next
            </button>
          </div>
        </div>
      )}
        </>
      )}

      {/* Calendar View */}
      {viewMode === 'calendar' && (
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Calendar Grid */}
          <div className="lg:col-span-3 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            {/* Calendar Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <button onClick={prevMonth} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <ChevronLeft size={20} className="text-gray-700 dark:text-gray-300" />
              </button>
              <div className="text-center">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </h2>
                <button onClick={goToToday} className="text-xs text-brand-blue hover:underline">Today</button>
              </div>
              <button onClick={nextMonth} className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
                <ChevronRight size={20} className="text-gray-700 dark:text-gray-300" />
              </button>
            </div>

            {/* Calendar Grid */}
            <div className="p-4">
              <div className="grid grid-cols-7 gap-1 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="text-center text-xs font-medium text-gray-500 dark:text-gray-400 py-2">{day}</div>
                ))}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {calendarDays.map((day, idx) => {
                  const dateKey = day.date.toISOString().split('T')[0];
                  const dayMeetings = meetingsByDate[dateKey] || [];
                  const isSelected = selectedDate && day.date.toDateString() === selectedDate.toDateString();
                  return (
                    <div
                      key={idx}
                      onClick={() => setSelectedDate(day.date)}
                      className={`min-h-[80px] p-1 border rounded-lg cursor-pointer transition-colors ${
                        day.isCurrentMonth ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'
                      } ${isSelected ? 'ring-2 ring-brand-blue' : ''} ${
                        isToday(day.date) ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-200 dark:border-blue-700' : 'border-gray-100 dark:border-gray-700'
                      } hover:border-gray-300 dark:hover:border-gray-500`}
                    >
                      <div className={`text-sm font-medium mb-1 ${
                        day.isCurrentMonth ? 'text-gray-900 dark:text-gray-100' : 'text-gray-400 dark:text-gray-600'
                      } ${isToday(day.date) ? 'text-brand-blue' : ''}`}>
                        {day.date.getDate()}
                      </div>
                      <div className="space-y-0.5">
                        {dayMeetings.slice(0, 3).map((meeting, midx) => (
                          <div key={midx} className={`text-[10px] text-white px-1 py-0.5 rounded truncate ${getMeetingDotColor(meeting)}`} title={meeting.title}>
                            {meeting.title}
                          </div>
                        ))}
                        {dayMeetings.length > 3 && <div className="text-[10px] text-gray-500 dark:text-gray-400">+{dayMeetings.length - 3} more</div>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Selected Date / Upcoming Sidebar */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
            {selectedDate ? (
              <>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">
                  {selectedDate.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </h3>
                {selectedDateMeetings.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">No meetings scheduled</p>
                ) : (
                  <div className="space-y-3">
                    {selectedDateMeetings.map((meeting, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                        <h4 className="font-medium text-gray-900 dark:text-gray-100 text-sm">{meeting.title}</h4>
                        {meeting.location && <p className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-1"><MapPin size={12} /> {meeting.location}</p>}
                        {meeting.council && <p className="text-xs text-gray-500 dark:text-gray-400">{meeting.council}</p>}
                        {meeting.source_url && (
                          <a href={meeting.source_url} target="_blank" rel="noopener noreferrer" className="text-xs text-brand-blue hover:underline flex items-center gap-1 mt-2">
                            Details <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <>
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-3">Upcoming Meetings</h3>
                <div className="space-y-2">
                  {upcomingMeetings.slice(0, 8).map((meeting, idx) => (
                    <div key={idx} className="p-2 hover:bg-gray-50 dark:hover:bg-gray-700 rounded cursor-pointer" onClick={() => setSelectedDate(new Date(meeting.start_date))}>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">{meeting.title}</p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">{new Date(meeting.start_date).toLocaleDateString()}</p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Agenda View */}
      {viewMode === 'agenda' && (
        <div className="mt-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Upcoming Meetings</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">{upcomingMeetings.length} upcoming meetings</p>
          </div>
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {loading ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">Loading...</div>
            ) : upcomingMeetings.length === 0 ? (
              <div className="p-8 text-center text-gray-500 dark:text-gray-400">No upcoming meetings match your filters</div>
            ) : (
              upcomingMeetings.map((meeting, idx) => (
                <div key={idx} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900 dark:text-gray-100">{meeting.title}</h3>
                      <div className="mt-1 flex flex-wrap gap-3 text-sm text-gray-500 dark:text-gray-400">
                        <span className="flex items-center gap-1">
                          <Calendar size={14} />
                          {new Date(meeting.start_date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' })}
                        </span>
                        {meeting.location && (
                          <span className="flex items-center gap-1"><MapPin size={14} /> {meeting.location}</span>
                        )}
                        {meeting.council && (
                          <span className="text-xs px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded">{meeting.council}</span>
                        )}
                      </div>
                      {meeting.description && (
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400 line-clamp-2">{meeting.description}</p>
                      )}
                    </div>
                    {meeting.source_url && (
                      <a href={meeting.source_url} target="_blank" rel="noopener noreferrer" className="ml-4 text-brand-blue hover:text-brand-green flex items-center gap-1 text-sm">
                        <ExternalLink size={16} />
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default MeetingsEnhanced;
