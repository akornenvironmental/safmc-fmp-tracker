import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { RefreshCw, TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Search, ArrowUpDown } from 'lucide-react';

const StockAssessments = () => {
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [fmpFilter, setFmpFilter] = useState('all');
  const [managementFilter, setManagementFilter] = useState('all');
  const [sortColumn, setSortColumn] = useState('species');
  const [sortDirection, setSortDirection] = useState('asc');
  const [assessments, setAssessments] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    overfished: 0,
    overfishing: 0,
    healthy: 0,
    in_progress: 0,
    safmc_only: {
      total: 0,
      overfished: 0,
      overfishing: 0,
      healthy: 0
    },
    jointly_managed: {
      total: 0,
      overfished: 0,
      overfishing: 0,
      healthy: 0
    }
  });
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchAssessments();
    fetchStats();
  }, []);

  const fetchAssessments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assessments`);
      const data = await response.json();

      if (data.success) {
        setAssessments(data.assessments || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching assessments:', error);
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/assessments/stats`);
      const data = await response.json();

      if (data.success) {
        setStats(data.stats || {});
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const syncAssessments = async () => {
    try {
      setSyncing(true);

      // Run both scrapers
      const sedarResponse = await fetch(`${API_BASE_URL}/api/scrape/sedar`, {
        method: 'POST',
      });

      const stocksmartResponse = await fetch(`${API_BASE_URL}/api/scrape/stocksmart`, {
        method: 'POST',
      });

      const sedarData = await sedarResponse.json();
      const stocksmartData = await stocksmartResponse.json();

      if (sedarData.success || stocksmartData.success) {
        alert('Sync complete! Data updated from SEDAR and StockSMART.');
        fetchAssessments();
        fetchStats();
      } else {
        alert('Sync completed with errors. Check console for details.');
      }
    } catch (error) {
      console.error('Error syncing assessments:', error);
      alert('Error syncing assessments');
    } finally {
      setSyncing(false);
    }
  };

  // Get unique FMPs for filter dropdown
  const uniqueFmps = [...new Set(assessments.flatMap(a => a.fmps_affected || []))].sort();

  // Filter and search assessments
  const filteredAssessments = assessments.filter(assessment => {
    // Status filter
    if (filterStatus !== 'all') {
      if (filterStatus === 'overfished' && !assessment.overfished) return false;
      if (filterStatus === 'overfishing' && !assessment.overfishing_occurring) return false;
      if (filterStatus === 'healthy' && (assessment.overfished || assessment.overfishing_occurring)) return false;
      if (filterStatus === 'in_progress' && assessment.status !== 'In Progress' && assessment.status !== 'Planning') return false;
    }

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      const matchesSpecies = assessment.species?.toLowerCase().includes(searchLower);
      const matchesScientific = assessment.scientific_name?.toLowerCase().includes(searchLower);
      const matchesSedar = assessment.sedar_number?.toString().toLowerCase().includes(searchLower);
      if (!matchesSpecies && !matchesScientific && !matchesSedar) return false;
    }

    // FMP filter
    if (fmpFilter !== 'all') {
      if (!assessment.fmps_affected || !assessment.fmps_affected.includes(fmpFilter)) return false;
    }

    // Management filter (SAFMC-only vs Jointly-managed)
    if (managementFilter !== 'all') {
      const fmpCount = assessment.fmps_affected?.length || 0;
      if (managementFilter === 'safmc' && fmpCount > 1) return false;
      if (managementFilter === 'joint' && fmpCount <= 1) return false;
    }

    return true;
  });

  // Sort assessments
  const sortedAssessments = [...filteredAssessments].sort((a, b) => {
    let aVal, bVal;

    switch (sortColumn) {
      case 'species':
        aVal = a.species || '';
        bVal = b.species || '';
        break;
      case 'sedar':
        aVal = a.sedar_number || 0;
        bVal = b.sedar_number || 0;
        break;
      case 'status':
        aVal = getStatusLabel(a);
        bVal = getStatusLabel(b);
        break;
      case 'b_bmsy':
        aVal = a.b_bmsy || 0;
        bVal = b.b_bmsy || 0;
        break;
      case 'f_fmsy':
        aVal = a.f_fmsy || 0;
        bVal = b.f_fmsy || 0;
        break;
      case 'updated':
        aVal = new Date(a.updated_at || 0);
        bVal = new Date(b.updated_at || 0);
        break;
      default:
        aVal = a.species || '';
        bVal = b.species || '';
    }

    if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
    if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
    return 0;
  });

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const getStatusColor = (assessment) => {
    if (assessment.overfished && assessment.overfishing_occurring) {
      return 'bg-red-100 text-red-800'; // Critical
    } else if (assessment.overfished) {
      return 'bg-orange-100 text-orange-800'; // Overfished
    } else if (assessment.overfishing_occurring) {
      return 'bg-yellow-100 text-yellow-800'; // Overfishing
    } else {
      return 'bg-green-100 text-green-800'; // Healthy
    }
  };

  const getStatusLabel = (assessment) => {
    if (assessment.overfished && assessment.overfishing_occurring) {
      return 'Critical';
    } else if (assessment.overfished) {
      return 'Overfished';
    } else if (assessment.overfishing_occurring) {
      return 'Overfishing';
    } else if (assessment.stock_status) {
      return assessment.stock_status;
    } else {
      return 'Unknown';
    }
  };

  const getStatusIcon = (assessment) => {
    if (assessment.overfished && assessment.overfishing_occurring) {
      return <AlertTriangle className="w-4 h-4 inline mr-1" />;
    } else if (assessment.overfished || assessment.overfishing_occurring) {
      return <TrendingDown className="w-4 h-4 inline mr-1" />;
    } else {
      return <CheckCircle2 className="w-4 h-4 inline mr-1" />;
    }
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Stocks</h1>
          <p className="mt-2 text-sm text-gray-600">
            <span className="font-medium">SAFMC-only:</span> {stats.safmc_only?.total || 0} total ({stats.safmc_only?.overfished || 0} overfished, {stats.safmc_only?.overfishing || 0} overfishing, {stats.safmc_only?.healthy || 0} healthy) •
            <span className="font-medium ml-2">Jointly-managed:</span> {stats.jointly_managed?.total || 0} total ({stats.jointly_managed?.overfished || 0} overfished, {stats.jointly_managed?.overfishing || 0} overfishing, {stats.jointly_managed?.healthy || 0} healthy)
          </p>
          <p className="mt-1 text-xs text-gray-500 italic">
            Stock assessments sync weekly from SEDAR and StockSMART
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={syncAssessments}
            disabled={syncing}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Data'}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-brand-blue">{stats.total || 0}</div>
              <div className="text-xs text-gray-500">Total Stocks</div>
            </div>
            <TrendingUp className="w-8 h-8 text-brand-blue opacity-50" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-red-600">{stats.overfished || 0}</div>
              <div className="text-xs text-gray-500">Overfished</div>
            </div>
            <TrendingDown className="w-8 h-8 text-red-600 opacity-50" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-yellow-600">{stats.overfishing || 0}</div>
              <div className="text-xs text-gray-500">Overfishing</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-600 opacity-50" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-600">{stats.healthy || 0}</div>
              <div className="text-xs text-gray-500">Healthy</div>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600 opacity-50" />
          </div>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className="mt-6 bg-white shadow rounded-lg p-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <label className="block text-xs font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search species, scientific name, or SEDAR #..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white"
              />
            </div>
          </div>

          {/* FMP Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">FMP</label>
            <select
              value={fmpFilter}
              onChange={(e) => setFmpFilter(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white"
            >
              <option value="all">All FMPs</option>
              {uniqueFmps.map(fmp => (
                <option key={fmp} value={fmp}>{fmp}</option>
              ))}
            </select>
          </div>

          {/* Management Filter */}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">Management</label>
            <select
              value={managementFilter}
              onChange={(e) => setManagementFilter(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white"
            >
              <option value="all">All</option>
              <option value="safmc">SAFMC-only</option>
              <option value="joint">Jointly-managed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="mt-6">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === 'all'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            All ({assessments.length})
          </button>
          <button
            onClick={() => setFilterStatus('healthy')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === 'healthy'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Healthy ({assessments.filter(a => !a.overfished && !a.overfishing_occurring).length})
          </button>
          <button
            onClick={() => setFilterStatus('overfished')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === 'overfished'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Overfished ({assessments.filter(a => a.overfished).length})
          </button>
          <button
            onClick={() => setFilterStatus('overfishing')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === 'overfishing'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Overfishing ({assessments.filter(a => a.overfishing_occurring).length})
          </button>
          <button
            onClick={() => setFilterStatus('in_progress')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStatus === 'in_progress'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            In Progress ({assessments.filter(a => a.status === 'In Progress' || a.status === 'Planning').length})
          </button>
        </div>
      </div>

      {/* Assessments Table */}
      <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('species')}
              >
                <div className="flex items-center gap-1">
                  Species
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                scope="col"
                className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('sedar')}
              >
                <div className="flex items-center gap-1">
                  SEDAR #
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                scope="col"
                className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('status')}
              >
                <div className="flex items-center gap-1">
                  Status
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                scope="col"
                className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('b_bmsy')}
              >
                <div className="flex items-center gap-1">
                  B/BMSY
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th
                scope="col"
                className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('f_fmsy')}
              >
                <div className="flex items-center gap-1">
                  F/FMSY
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
              <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                FMP
              </th>
              <th
                scope="col"
                className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('updated')}
              >
                <div className="flex items-center gap-1">
                  Updated
                  <ArrowUpDown className="w-3 h-3" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="7" className="px-6 py-12 text-center text-sm text-gray-500">
                  Loading assessments...
                </td>
              </tr>
            ) : sortedAssessments.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-12 text-center text-sm text-gray-500">
                  No assessments found. Try adjusting your search and filters.
                </td>
              </tr>
            ) : (
              sortedAssessments.map((assessment, index) => (
                <tr key={assessment.id || index} className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-100'} hover:bg-gray-50 transition-colors duration-150`}>
                  <td className="px-2 py-0.5">
                    {assessment.source_url ? (
                      <a
                        href={assessment.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs font-medium text-brand-blue hover:text-brand-green hover:underline"
                      >
                        {assessment.species}
                      </a>
                    ) : (
                      <div className="text-xs font-medium text-gray-900">{assessment.species}</div>
                    )}
                    {assessment.scientific_name && (
                      <div className="text-xs text-gray-500 italic">{assessment.scientific_name}</div>
                    )}
                  </td>
                  <td className="px-2 py-0.5 whitespace-nowrap">
                    <div className="text-xs text-gray-900">{assessment.sedar_number || 'N/A'}</div>
                  </td>
                  <td className="px-2 py-0.5 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2 py-0.5 text-xs font-semibold rounded-full ${getStatusColor(assessment)}`}>
                      {getStatusIcon(assessment)}
                      {getStatusLabel(assessment)}
                    </span>
                  </td>
                  <td className="px-2 py-0.5 whitespace-nowrap">
                    <div className="text-xs text-gray-900">
                      {assessment.b_bmsy ? (
                        <span className={assessment.b_bmsy >= 1.0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                          {assessment.b_bmsy.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </div>
                  </td>
                  <td className="px-2 py-0.5 whitespace-nowrap">
                    <div className="text-xs text-gray-900">
                      {assessment.f_fmsy ? (
                        <span className={assessment.f_fmsy <= 1.0 ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                          {assessment.f_fmsy.toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </div>
                  </td>
                  <td className="px-2 py-0.5">
                    {assessment.fmps_affected && assessment.fmps_affected.length > 0 ? (
                      <div className="flex flex-wrap gap-1">
                        {assessment.fmps_affected.map((fmp, idx) => (
                          <span key={idx} className="inline-flex px-1.5 py-0.5 text-xs rounded bg-blue-100 text-blue-800">
                            {fmp}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <span className="text-xs text-gray-400">N/A</span>
                    )}
                  </td>
                  <td className="px-2 py-0.5 whitespace-nowrap text-xs text-gray-500">
                    {assessment.updated_at ? new Date(assessment.updated_at).toLocaleDateString() : 'N/A'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Showing {sortedAssessments.length} of {assessments.length} assessments
      </div>

      {/* Note about data sources */}
      <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
        <p className="text-xs text-gray-700">
          <strong>Data Sources:</strong> Stock assessment data from SEDAR (sedarweb.org) and stock status metrics from NOAA StockSMART.
          B/BMSY ratios ≥ 1.0 indicate healthy biomass levels. F/FMSY ratios ≤ 1.0 indicate sustainable fishing mortality.
        </p>
      </div>
    </div>
  );
};

export default StockAssessments;
