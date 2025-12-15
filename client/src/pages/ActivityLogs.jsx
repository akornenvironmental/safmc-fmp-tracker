/**
 * ActivityLogs Page
 *
 * Comprehensive activity logging interface for admins and super admins.
 * View, filter, search, and export user activity across the system.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import Button from '../components/Button';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import {
  Activity,
  Download,
  Calendar,
  User,
  AlertCircle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

const ActivityLogs = () => {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();

  // State
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [exporting, setExporting] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [activityFilter, setActivityFilter] = useState('all');
  const [userFilter, setUserFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [page, setPage] = useState(1);
  const [limit] = useState(50);
  const [totalLogs, setTotalLogs] = useState(0);

  // Check permissions
  useEffect(() => {
    if (!isAdmin()) {
      navigate('/');
    }
  }, [isAdmin, navigate]);

  // Fetch stats
  useEffect(() => {
    fetchStats();
  }, []);

  // Fetch logs
  useEffect(() => {
    fetchLogs();
  }, [page, activityFilter, userFilter, dateFrom, dateTo, searchQuery]);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/admin/activity-logs/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (response.ok) {
        setStats(data.stats);
      }
    } catch (err) {
      console.error('Error fetching stats:', err);
    }
  };

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const params = new URLSearchParams({
        page: page.toString(),
        limit: limit.toString()
      });

      if (activityFilter && activityFilter !== 'all') {
        params.append('activity_type', activityFilter);
      }
      if (userFilter) {
        params.append('user_email', userFilter);
      }
      if (dateFrom) {
        params.append('date_from', dateFrom);
      }
      if (dateTo) {
        params.append('date_to', dateTo);
      }
      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await fetch(`${API_BASE_URL}/api/admin/activity-logs?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch activity logs');
      }

      setLogs(data.logs || []);
      setTotalLogs(data.total || 0);
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      setExporting(true);

      const token = localStorage.getItem('authToken');
      const params = new URLSearchParams();

      if (activityFilter && activityFilter !== 'all') {
        params.append('activity_type', activityFilter);
      }
      if (userFilter) {
        params.append('user_email', userFilter);
      }
      if (dateFrom) {
        params.append('date_from', dateFrom);
      }
      if (dateTo) {
        params.append('date_to', dateTo);
      }
      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await fetch(`${API_BASE_URL}/api/admin/activity-logs/export?${params}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to export logs');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `activity-logs-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error exporting logs:', err);
      alert(`Error: ${err.message}`);
    } finally {
      setExporting(false);
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setActivityFilter('all');
    setUserFilter('');
    setDateFrom('');
    setDateTo('');
    setPage(1);
  };

  // Get activity type badge color
  const getActivityBadgeClass = (type) => {
    if (type.includes('login') || type.includes('logout')) {
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300';
    }
    if (type.includes('created') || type.includes('added')) {
      return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
    }
    if (type.includes('deleted') || type.includes('failed')) {
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
    }
    if (type.includes('updated') || type.includes('edited')) {
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
    }
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  };

  const totalPages = Math.ceil(totalLogs / limit);

  if (loading && logs.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading activity logs...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="page-description-container">
        <p className="page-description-text">
          Monitor user activity, system events, and administrative actions across the platform.
        </p>
        <div className="page-description-actions">
          <Button
            variant="primary"
            icon={Download}
            onClick={handleExport}
            disabled={exporting || logs.length === 0}
            className="gap-1.5 px-2.5 h-9"
          >
            {exporting ? 'Exporting...' : 'Export CSV'}
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Total Activities</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total_activities?.toLocaleString() || 0}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Active Users</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.unique_users || 0}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">Today's Activities</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.today_count || 0}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 border border-gray-200 dark:border-gray-700">
            <div className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">This Week</div>
            <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.week_count || 0}</div>
          </div>
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-600 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error loading logs</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <PageControlsContainer>
        {/* Search */}
        <SearchBar
          value={searchQuery}
          onChange={(value) => {
            setSearchQuery(value);
            setPage(1);
          }}
          placeholder="Search logs..."
          ariaLabel="Search activity logs by user, activity, or description"
        />

        {/* Activity Type Filter */}
        <FilterDropdown
          label="Activity Type"
          options={[
            { value: 'login', label: 'Login' },
            { value: 'logout', label: 'Logout' },
            { value: 'created', label: 'Created' },
            { value: 'updated', label: 'Updated' },
            { value: 'deleted', label: 'Deleted' },
            { value: 'viewed', label: 'Viewed' },
            { value: 'exported', label: 'Exported' }
          ]}
          selectedValues={activityFilter === 'all' ? [] : [activityFilter]}
          onChange={(values) => {
            setActivityFilter(values.length === 0 ? 'all' : values[0]);
            setPage(1);
          }}
          showCounts={false}
        />

        {/* User Email */}
        <div className="relative flex-1 min-w-[150px]">
          <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none z-10" />
          <input
            type="text"
            placeholder="Filter by user..."
            value={userFilter}
            onChange={(e) => {
              setUserFilter(e.target.value);
              setPage(1);
            }}
            className="w-full h-9 pl-10 pr-4 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 focus:border-blue-500 dark:focus:border-blue-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors shadow-sm"
          />
        </div>

        {/* Date From */}
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none z-10" />
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => {
              setDateFrom(e.target.value);
              setPage(1);
            }}
            className="h-9 pl-10 pr-4 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 focus:border-blue-500 dark:focus:border-blue-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors shadow-sm"
          />
        </div>

        {/* Date To */}
        <div className="relative">
          <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-gray-500 pointer-events-none z-10" />
          <input
            type="date"
            value={dateTo}
            onChange={(e) => {
              setDateTo(e.target.value);
              setPage(1);
            }}
            className="h-9 pl-10 pr-4 text-sm font-medium rounded-md bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 focus:border-blue-500 dark:focus:border-blue-400 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 transition-colors shadow-sm"
          />
        </div>

        {/* Clear Filters Button */}
        {(searchQuery || activityFilter !== 'all' || userFilter || dateFrom || dateTo) && (
          <button
            onClick={clearFilters}
            className="inline-flex items-center gap-2 h-9 px-3 text-sm font-medium rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 border border-red-300 dark:border-red-600 hover:bg-red-100 dark:hover:bg-red-900/40 hover:border-red-400 dark:hover:border-red-500 transition-colors shadow-sm"
          >
            Clear Filters
          </button>
        )}
      </PageControlsContainer>

      {/* Results count */}
      <div className="mb-6 text-sm text-gray-600 dark:text-gray-400">
        Showing {logs.length} of {totalLogs.toLocaleString()} logs
        {searchQuery && ` matching "${searchQuery}"`}
      </div>

      {/* Activity Logs Table */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden border border-gray-200 dark:border-gray-700">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Timestamp
                </th>
                <th className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  User
                </th>
                <th className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Activity
                </th>
                <th className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Details
                </th>
                <th className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  IP Address
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {logs.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500 dark:text-gray-400">
                    <Activity className="w-12 h-12 text-gray-300 dark:text-gray-600 mx-auto mb-3" />
                    <p>No activity logs found</p>
                    {(searchQuery || activityFilter !== 'all' || userFilter || dateFrom || dateTo) && (
                      <p className="text-sm mt-1">Try adjusting your filters</p>
                    )}
                  </td>
                </tr>
              ) : (
                logs.map((log, index) => (
                  <tr key={log.id} className={`${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-100 dark:bg-gray-850'} hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-150`}>
                    <td className="px-2 py-0.5 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-gray-100">{log.user_name || 'Unknown'}</div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">{log.user_email}</div>
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getActivityBadgeClass(log.activity_type)}`}>
                        {log.activity_type}
                      </span>
                    </td>
                    <td className="px-2 py-0.5 text-sm text-gray-900 dark:text-gray-100 max-w-md truncate">
                      {log.description || 'No description'}
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {log.ip_address || 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-white dark:bg-gray-800 px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 sm:px-6">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="relative inline-flex items-center h-9 px-4 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="ml-3 relative inline-flex items-center h-9 px-4 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Showing page <span className="font-medium">{page}</span> of{' '}
                  <span className="font-medium">{totalPages}</span>
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center h-9 px-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                  <span className="relative inline-flex items-center h-9 px-4 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-700 dark:text-gray-300">
                    Page {page} of {totalPages}
                  </span>
                  <button
                    onClick={() => setPage(Math.min(totalPages, page + 1))}
                    disabled={page === totalPages}
                    className="relative inline-flex items-center h-9 px-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>
                </nav>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ActivityLogs;
