import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import StatusBadge from '../components/StatusBadge';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import { User, Building2, RefreshCw, Download, BarChart3, Facebook, Twitter, Instagram, Youtube, ExternalLink } from 'lucide-react';

const Comments = () => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterPosition, setFilterPosition] = useState([]);
  const [filterOrganization, setFilterOrganization] = useState([]);
  const [filterState, setFilterState] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [sortField, setSortField] = useState('submitted_date');
  const [sortDirection, setSortDirection] = useState('desc');
  const [syncing, setSyncing] = useState(false);
  const [showStats, setShowStats] = useState(false);

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

  // Get unique values for filters
  const uniqueOrganizations = useMemo(() => {
    const orgs = new Set(comments.map(c => c.organization).filter(Boolean));
    return Array.from(orgs).sort();
  }, [comments]);

  const uniqueStates = useMemo(() => {
    const states = new Set(comments.map(c => c.state).filter(Boolean));
    return Array.from(states).sort();
  }, [comments]);

  const uniquePositions = useMemo(() => {
    const positions = new Set(comments.map(c => c.position).filter(Boolean));
    return Array.from(positions).sort();
  }, [comments]);

  // Filter and sort comments
  const filteredAndSortedComments = useMemo(() => {
    let filtered = comments.filter(comment => {
      // Position filter
      if (filterPosition.length > 0) {
        const hasPosition = filterPosition.some(pos =>
          comment.position?.toLowerCase().includes(pos.toLowerCase())
        );
        if (!hasPosition) return false;
      }

      // Organization filter
      if (filterOrganization.length > 0 && !filterOrganization.includes(comment.organization)) {
        return false;
      }

      // State filter
      if (filterState.length > 0 && !filterState.includes(comment.state)) {
        return false;
      }

      // Search filter
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        const matchesSearch =
          comment.name?.toLowerCase().includes(search) ||
          comment.organization?.toLowerCase().includes(search) ||
          comment.comment_text?.toLowerCase().includes(search) ||
          comment.state?.toLowerCase().includes(search);
        if (!matchesSearch) return false;
      }

      // Date range filter
      if (dateRange.start && comment.submitted_date) {
        const commentDate = new Date(comment.submitted_date);
        const startDate = new Date(dateRange.start);
        if (commentDate < startDate) return false;
      }
      if (dateRange.end && comment.submitted_date) {
        const commentDate = new Date(comment.submitted_date);
        const endDate = new Date(dateRange.end);
        endDate.setHours(23, 59, 59, 999); // End of day
        if (commentDate > endDate) return false;
      }

      return true;
    });

    // Sort
    return [...filtered].sort((a, b) => {
      let aVal = a[sortField] || '';
      let bVal = b[sortField] || '';

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
  }, [comments, filterPosition, filterOrganization, filterState, searchTerm, dateRange, sortField, sortDirection]);

  // Calculate statistics
  const stats = useMemo(() => {
    const total = comments.length;
    const byPosition = {
      support: comments.filter(c => c.position?.toLowerCase().includes('support')).length,
      oppose: comments.filter(c => c.position?.toLowerCase().includes('oppose')).length,
      neutral: comments.filter(c => c.position?.toLowerCase().includes('neutral')).length,
    };

    const topOrgs = {};
    comments.forEach(c => {
      if (c.organization) {
        topOrgs[c.organization] = (topOrgs[c.organization] || 0) + 1;
      }
    });
    const sortedOrgs = Object.entries(topOrgs)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5);

    const byMonth = {};
    comments.forEach(c => {
      if (c.submitted_date) {
        const date = new Date(c.submitted_date);
        const monthKey = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        byMonth[monthKey] = (byMonth[monthKey] || 0) + 1;
      }
    });

    return { total, byPosition, topOrgs: sortedOrgs, byMonth };
  }, [comments]);

  // Export functions
  const exportToCSV = () => {
    const headers = ['Name', 'Organization', 'State', 'Position', 'Comment', 'Submitted Date'];
    const rows = filteredAndSortedComments.map(c => [
      c.name || '',
      c.organization || '',
      c.state || '',
      c.position || '',
      c.comment_text || '',
      c.submitted_date ? new Date(c.submitted_date).toLocaleDateString() : ''
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `safmc-comments-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const exportToExcel = () => {
    const headers = ['Name', 'Organization', 'State', 'Position', 'Comment', 'Submitted Date'];
    const rows = filteredAndSortedComments.map(c =>
      `<tr>
        <td>${c.name || ''}</td>
        <td>${c.organization || ''}</td>
        <td>${c.state || ''}</td>
        <td>${c.position || ''}</td>
        <td>${c.comment_text || ''}</td>
        <td>${c.submitted_date ? new Date(c.submitted_date).toLocaleDateString() : ''}</td>
      </tr>`
    ).join('');

    const html = `
      <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel">
      <head><meta charset="UTF-8"></head>
      <body>
        <table>
          <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
          <tbody>${rows}</tbody>
        </table>
      </body>
      </html>
    `;

    const blob = new Blob([html], { type: 'application/vnd.ms-excel' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `safmc-comments-${new Date().toISOString().split('T')[0]}.xls`;
    a.click();
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const resetFilters = () => {
    setFilterPosition([]);
    setFilterOrganization([]);
    setFilterState([]);
    setSearchTerm('');
    setDateRange({ start: '', end: '' });
    setSortField('submitted_date');
    setSortDirection('desc');
  };

  const getPositionVariant = (position) => {
    if (!position) return 'neutral';

    const positionLower = position.toLowerCase();
    if (positionLower.includes('support')) return 'success';
    if (positionLower.includes('oppose')) return 'error';
    if (positionLower.includes('neutral')) return 'info';
    return 'neutral';
  };

  return (
    <div>
      {/* Description and Action Buttons Row */}
      <div className="page-description-container">
        <p className="page-description-text">
          Official public comments submitted on fishery management actions and regulatory proposals.
        </p>
        <div className="page-description-actions">
          <button
            onClick={() => setShowStats(!showStats)}
            className="inline-flex items-center gap-1.5 px-2.5 h-9 justify-center rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2"
          >
            <BarChart3 className="w-4 h-4" />
            {showStats ? 'Hide Stats' : 'Show Stats'}
          </button>
          <div className="relative">
            <button
              className="inline-flex items-center gap-1.5 px-2.5 h-9 justify-center rounded-md border border-teal-300 bg-gradient-to-r from-teal-50 to-cyan-50 text-sm font-medium text-teal-700 shadow-sm hover:from-teal-100 hover:to-cyan-100 hover:border-teal-400 transition-all"
              onClick={(e) => {
                const menu = e.currentTarget.nextElementSibling;
                menu.classList.toggle('hidden');
              }}
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <div className="hidden absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 z-10">
              <div className="py-1">
                <button
                  onClick={exportToCSV}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  Export as CSV
                </button>
                <button
                  onClick={exportToExcel}
                  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
                >
                  Export as Excel
                </button>
              </div>
            </div>
          </div>
          <button
            onClick={syncComments}
            disabled={syncing}
            className="inline-flex items-center gap-1.5 px-2.5 h-9 justify-center rounded-md border border-transparent bg-brand-blue text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync'}
          </button>
        </div>
      </div>

      {/* Statistics Dashboard */}
      {showStats && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Position Breakdown */}
          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Comments by Position</h3>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Support</span>
                <StatusBadge variant="success" size="sm">{stats.byPosition.support}</StatusBadge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Oppose</span>
                <StatusBadge variant="error" size="sm">{stats.byPosition.oppose}</StatusBadge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Neutral</span>
                <StatusBadge variant="info" size="sm">{stats.byPosition.neutral}</StatusBadge>
              </div>
              <div className="pt-2 border-t border-gray-200 flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">Total</span>
                <StatusBadge variant="neutral" size="sm">{stats.total}</StatusBadge>
              </div>
            </div>
          </div>

          {/* Top Organizations */}
          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Most Active Organizations</h3>
            <div className="space-y-2">
              {stats.topOrgs.length > 0 ? (
                stats.topOrgs.map(([org, count]) => (
                  <div key={org} className="flex items-center justify-between">
                    <span className="text-xs text-gray-600 truncate flex-1 mr-2">{org}</span>
                    <StatusBadge variant="info" size="sm">{count}</StatusBadge>
                  </div>
                ))
              ) : (
                <p className="text-xs text-gray-500">No organization data</p>
              )}
            </div>
          </div>

          {/* Submission Timeline */}
          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Submissions</h3>
            <div className="space-y-2">
              {Object.entries(stats.byMonth)
                .sort((a, b) => b[0].localeCompare(a[0]))
                .slice(0, 5)
                .map(([month, count]) => (
                  <div key={month} className="flex items-center justify-between">
                    <span className="text-xs text-gray-600">{month}</span>
                    <StatusBadge variant="purple" size="sm">{count}</StatusBadge>
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <PageControlsContainer className="mt-6">
        <SearchBar
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Search comments..."
          ariaLabel="Search by name, organization, or comment text"
        />

        <FilterDropdown
          label="Position"
          options={uniquePositions.map(pos => ({
            value: pos,
            label: pos,
            count: comments.filter(c => c.position === pos).length
          }))}
          selectedValues={filterPosition}
          onChange={setFilterPosition}
          showCounts={true}
        />

        <FilterDropdown
          label="Organization"
          options={uniqueOrganizations.map(org => ({
            value: org,
            label: org,
            count: comments.filter(c => c.organization === org).length
          }))}
          selectedValues={filterOrganization}
          onChange={setFilterOrganization}
          showCounts={true}
        />

        <FilterDropdown
          label="State"
          options={uniqueStates.map(state => ({
            value: state,
            label: state,
            count: comments.filter(c => c.state === state).length
          }))}
          selectedValues={filterState}
          onChange={setFilterState}
          showCounts={true}
        />

        <div className="flex items-center gap-2">
          <input
            type="date"
            value={dateRange.start}
            onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
            className="h-9 px-3 text-sm border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            aria-label="Start date filter"
          />
          <span className="text-sm text-gray-500">to</span>
          <input
            type="date"
            value={dateRange.end}
            onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
            className="h-9 px-3 text-sm border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            aria-label="End date filter"
          />
        </div>

        <button
          onClick={resetFilters}
          className="inline-flex items-center gap-2 h-9 px-3 text-sm font-medium rounded-md bg-red-50 text-red-700 border border-red-300 hover:bg-red-100 hover:border-red-400 transition-colors"
        >
          Reset
        </button>
      </PageControlsContainer>

      {/* Sort Controls */}
      <div className="mt-4 flex items-center gap-4">
        <span className="text-sm text-gray-600">Sort by:</span>
        <button
          onClick={() => handleSort('submitted_date')}
          className={`text-sm px-3 py-1 rounded ${
            sortField === 'submitted_date' ? 'bg-brand-blue text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Date {sortField === 'submitted_date' && (sortDirection === 'asc' ? '↑' : '↓')}
        </button>
        <button
          onClick={() => handleSort('name')}
          className={`text-sm px-3 py-1 rounded ${
            sortField === 'name' ? 'bg-brand-blue text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
        </button>
        <button
          onClick={() => handleSort('organization')}
          className={`text-sm px-3 py-1 rounded ${
            sortField === 'organization' ? 'bg-brand-blue text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Organization {sortField === 'organization' && (sortDirection === 'asc' ? '↑' : '↓')}
        </button>
      </div>

      {/* Comments List */}
      <div className="mt-6 space-y-3">
        {loading ? (
          <div className="bg-white shadow sm:rounded-lg p-8 text-center text-sm text-gray-500">
            Loading comments...
          </div>
        ) : filteredAndSortedComments.length === 0 ? (
          <div className="bg-white shadow sm:rounded-lg p-8 text-center text-sm text-gray-500">
            No comments found matching your filters
          </div>
        ) : (
          filteredAndSortedComments.map((comment, index) => (
            <div key={comment.id || index} className="bg-white shadow sm:rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1.5">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" aria-hidden="true" />
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
                      <Building2 className="w-4 h-4 text-gray-400" aria-hidden="true" />
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
                  <StatusBadge variant={getPositionVariant(comment.position)} size="sm">
                    {comment.position || 'No Position'}
                  </StatusBadge>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Showing {filteredAndSortedComments.length} of {comments.length} comments
      </div>

      {/* Social Media Links Section */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border border-blue-200 dark:border-blue-800 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
          Join the Conversation on Social Media
        </h3>
        <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
          Follow SAFMC on social media for updates, discussions, and public engagement on fishery management issues.
        </p>
        <div className="flex flex-wrap gap-3">
          <a
            href="https://www.facebook.com/SouthAtlanticCouncil/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all group"
          >
            <Facebook className="w-5 h-5 text-blue-600 dark:text-blue-400" aria-hidden="true" />
            <span className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-600 dark:group-hover:text-blue-400">
              Facebook
            </span>
            <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" aria-hidden="true" />
          </a>
          <a
            href="https://twitter.com/SAFMC"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 hover:shadow-md transition-all group"
          >
            <Twitter className="w-5 h-5 text-blue-400 dark:text-blue-300" aria-hidden="true" />
            <span className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-blue-400 dark:group-hover:text-blue-300">
              Twitter/X
            </span>
            <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-blue-400 dark:group-hover:text-blue-300" aria-hidden="true" />
          </a>
          <a
            href="https://www.instagram.com/southatlanticcouncil/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-700 hover:border-pink-500 dark:hover:border-pink-400 hover:shadow-md transition-all group"
          >
            <Instagram className="w-5 h-5 text-pink-600 dark:text-pink-400" aria-hidden="true" />
            <span className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-pink-600 dark:group-hover:text-pink-400">
              Instagram
            </span>
            <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-pink-600 dark:group-hover:text-pink-400" aria-hidden="true" />
          </a>
          <a
            href="https://www.youtube.com/channel/UC7oL5uQA_31Kfkwh4r6q6ig"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 rounded-lg border border-gray-300 dark:border-gray-700 hover:border-red-500 dark:hover:border-red-400 hover:shadow-md transition-all group"
          >
            <Youtube className="w-5 h-5 text-red-600 dark:text-red-400" aria-hidden="true" />
            <span className="text-sm font-medium text-gray-900 dark:text-white group-hover:text-red-600 dark:group-hover:text-red-400">
              YouTube
            </span>
            <ExternalLink className="w-3.5 h-3.5 text-gray-400 group-hover:text-red-600 dark:group-hover:text-red-400" aria-hidden="true" />
          </a>
        </div>
        <p className="text-xs text-gray-600 dark:text-gray-400 mt-4">
          Note: Comments shown above are official public comments submitted through SAFMC's formal comment process. Social media discussions are informal and not part of the official administrative record.
        </p>
      </div>
    </div>
  );
};

export default Comments;
