import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import Button from '../components/Button';
import ButtonGroup from '../components/ButtonGroup';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import {
  RefreshCw, Download, Fish,
  TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, ArrowUpDown,
  LayoutGrid, Table
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';

// Species name synonyms and aliases for better matching
const SPECIES_SYNONYMS = {
  'dolphin': ['mahi mahi', 'mahi-mahi', 'dorado', 'dolphinfish'],
  'king mackerel': ['kingfish', 'king'],
  'spanish mackerel': ['spanish'],
  'wahoo': ['ono'],
  'greater amberjack': ['amberjack', 'aj'],
  'red snapper': ['snapper'],
  'vermilion snapper': ['vermilion', 'beeliners', 'beeliner'],
  'black sea bass': ['sea bass', 'blackfish'],
  'gag grouper': ['gag'],
  'red grouper': ['red grouper'],
  'snowy grouper': ['snowy'],
  'scamp': ['scamp grouper'],
  'golden tilefish': ['tilefish', 'golden tile'],
  'blueline tilefish': ['blueline', 'blueline tile'],
  'gray triggerfish': ['triggerfish', 'trigger'],
  'hogfish': ['hog snapper'],
  'yellowtail snapper': ['yellowtail'],
  'mutton snapper': ['mutton'],
  'spiny lobster': ['lobster', 'florida lobster', 'caribbean spiny lobster'],
  'golden crab': ['deep sea golden crab'],
  'rock shrimp': ['rock'],
  'pink shrimp': ['pink'],
  'goliath grouper': ['goliath', 'jewfish'],
  'wreckfish': ['wreck fish'],
};

// Normalize species name for comparison
const normalizeSpeciesName = (name) => {
  if (!name) return '';
  return name
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/south atlantic|atlantic|gulf of mexico|gulf|florida|keys/gi, '')
    .replace(/stock|complex|unit/gi, '')
    .trim();
};

// Find matching assessment for a species
const findMatchingAssessment = (speciesName, assessments) => {
  if (!speciesName || !assessments?.length) return null;

  const normalizedSpecies = normalizeSpeciesName(speciesName);

  // 1. Exact match
  let match = assessments.find(a =>
    normalizeSpeciesName(a.species) === normalizedSpecies
  );
  if (match) return match;

  // 2. Check synonyms - does species name match any assessment synonym?
  for (const [canonical, synonyms] of Object.entries(SPECIES_SYNONYMS)) {
    const allNames = [canonical, ...synonyms];
    const speciesMatches = allNames.some(syn =>
      normalizedSpecies.includes(syn) || syn.includes(normalizedSpecies)
    );

    if (speciesMatches) {
      match = assessments.find(a => {
        const normalizedAssessment = normalizeSpeciesName(a.species);
        return allNames.some(syn =>
          normalizedAssessment.includes(syn) || syn.includes(normalizedAssessment)
        );
      });
      if (match) return match;
    }
  }

  // 3. Partial match (contains)
  match = assessments.find(a => {
    const normalizedAssessment = normalizeSpeciesName(a.species);
    return normalizedSpecies.includes(normalizedAssessment) ||
           normalizedAssessment.includes(normalizedSpecies);
  });
  if (match) return match;

  // 4. Scientific name match
  match = assessments.find(a =>
    a.scientific_name &&
    normalizeSpeciesName(a.scientific_name).includes(normalizedSpecies)
  );

  return match;
};

const SpeciesStocks = () => {
  const navigate = useNavigate();

  // Shared state
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'table'
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFMP, setFilterFMP] = useState([]);
  const [filterStatus, setFilterStatus] = useState('all');
  const [sortField, setSortField] = useState('actionCount');
  const [sortDirection, setSortDirection] = useState('desc');

  // Data
  const [species, setSpecies] = useState([]);
  const [assessments, setAssessments] = useState([]);
  const [stats, setStats] = useState({
    total: 0,
    overfished: 0,
    overfishing: 0,
    healthy: 0,
    unknown: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch both species and assessments
      const [speciesRes, assessmentsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/species`),
        fetch(`${API_BASE_URL}/api/assessments`)
      ]);

      const speciesData = await speciesRes.json();
      const assessmentsData = await assessmentsRes.json();

      if (speciesData.success) {
        setSpecies(speciesData.species || []);
      }

      if (assessmentsData.success) {
        setAssessments(assessmentsData.assessments || []);
        // Calculate stats
        const overfished = assessmentsData.assessments.filter(a => a.overfished).length;
        const overfishing = assessmentsData.assessments.filter(a => a.overfishing_occurring).length;
        const healthy = assessmentsData.assessments.filter(a => !a.overfished && !a.overfishing_occurring && a.stock_status).length;
        const unknown = assessmentsData.assessments.filter(a => !a.overfished && !a.overfishing_occurring && !a.stock_status).length;
        setStats({
          total: assessmentsData.assessments.length,
          overfished,
          overfishing,
          healthy,
          unknown
        });
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const syncData = async () => {
    try {
      setSyncing(true);
      await Promise.all([
        fetch(`${API_BASE_URL}/api/scrape/sedar`, { method: 'POST' }),
        fetch(`${API_BASE_URL}/api/scrape/stocksmart`, { method: 'POST' })
      ]);
      await fetchData();
      alert('Sync complete! Data updated from SEDAR and StockSMART.');
    } catch (error) {
      console.error('Error syncing:', error);
      alert('Error syncing data');
    } finally {
      setSyncing(false);
    }
  };

  // Get unique FMPs from both sources
  const uniqueFMPs = useMemo(() => {
    const fmpSet = new Set();
    species.forEach(sp => sp.fmps?.forEach(fmp => fmpSet.add(fmp)));
    assessments.forEach(a => a.fmps_affected?.forEach(fmp => fmpSet.add(fmp)));
    return Array.from(fmpSet).sort();
  }, [species, assessments]);


  // Merge species with assessment data using improved matching
  const mergedData = useMemo(() => {
    return species.map(sp => {
      // Find matching assessment using improved matching logic
      const assessment = findMatchingAssessment(sp.name, assessments);

      return {
        ...sp,
        assessment: assessment || null,
        stockStatus: assessment ? getStockStatus(assessment) : 'unknown',
        b_bmsy: assessment?.b_bmsy || null,
        f_fmsy: assessment?.f_fmsy || null,
        sedar_number: assessment?.sedar_number || null,
        overfished: assessment?.overfished || false,
        overfishing: assessment?.overfishing_occurring || false,
        scientific_name: assessment?.scientific_name || null
      };
    });
  }, [species, assessments]);

  // Filter and sort
  const filteredData = useMemo(() => {
    let result = [...mergedData];

    // Search
    if (searchTerm) {
      const s = searchTerm.toLowerCase();
      result = result.filter(sp =>
        sp.name?.toLowerCase().includes(s) ||
        sp.fmps?.some(fmp => fmp.toLowerCase().includes(s)) ||
        sp.assessment?.scientific_name?.toLowerCase().includes(s)
      );
    }

    // FMP filter
    if (filterFMP.length > 0) {
      result = result.filter(sp => sp.fmps?.some(fmp => filterFMP.includes(fmp)));
    }

    // Status filter
    if (filterStatus !== 'all') {
      result = result.filter(sp => {
        if (filterStatus === 'overfished') return sp.overfished;
        if (filterStatus === 'overfishing') return sp.overfishing;
        if (filterStatus === 'healthy') return sp.stockStatus === 'healthy';
        if (filterStatus === 'unknown') return sp.stockStatus === 'unknown';
        return true;
      });
    }

    // Sort
    result.sort((a, b) => {
      let aVal = a[sortField];
      let bVal = b[sortField];

      if (sortField === 'name') {
        aVal = aVal?.toLowerCase() || '';
        bVal = bVal?.toLowerCase() || '';
      }

      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [mergedData, searchTerm, filterFMP, filterStatus, sortField, sortDirection]);

  // Helper functions
  function getStockStatus(assessment) {
    if (assessment.overfished && assessment.overfishing_occurring) return 'critical';
    if (assessment.overfished) return 'overfished';
    if (assessment.overfishing_occurring) return 'overfishing';
    if (assessment.stock_status) return 'healthy';
    return 'unknown';
  }

  const getStatusVariant = (status) => {
    switch (status) {
      case 'critical': return 'error';
      case 'overfished': return 'warning';
      case 'overfishing': return 'warning';
      case 'healthy': return 'success';
      default: return 'neutral';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'critical':
      case 'overfished':
      case 'overfishing':
        return <AlertTriangle className="w-3 h-3" />;
      case 'healthy':
        return <CheckCircle2 className="w-3 h-3" />;
      default:
        return null;
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'critical': return 'Critical';
      case 'overfished': return 'Overfished';
      case 'overfishing': return 'Overfishing';
      case 'healthy': return 'Healthy';
      default: return 'No Data';
    }
  };

  const getFMPVariant = (fmp) => {
    const variants = {
      'Snapper Grouper': 'info',
      'Coastal Migratory Pelagics': 'purple',
      'Dolphin Wahoo': 'info',
      'Spiny Lobster': 'error',
      'Golden Crab': 'warning',
      'Shrimp': 'purple',
      'Coral': 'warning',
      'Sargassum': 'success',
    };
    return variants[fmp] || 'neutral';
  };

  const exportToCSV = () => {
    const headers = ['Species', 'Stock Status', 'B/BMSY', 'F/FMSY', 'SEDAR #', 'Action Count', 'FMPs'];
    const rows = filteredData.map(sp => [
      sp.name,
      getStatusLabel(sp.stockStatus),
      sp.b_bmsy || 'N/A',
      sp.f_fmsy || 'N/A',
      sp.sedar_number || 'N/A',
      sp.actionCount || 0,
      (sp.fmps || []).join('; ')
    ]);
    const csv = [headers.join(','), ...rows.map(row => row.map(val => `"${val}"`).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `species-stocks-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection(field === 'name' ? 'asc' : 'desc');
    }
  };

  return (
    <div>
      {/* Description and Action Buttons Row */}
      <div className="page-description-container">
        <p className="page-description-text">
          Scientific stock assessments and fishery data for managed species in the South Atlantic region.
        </p>
        <div className="page-description-actions">
          <Button
            variant="secondary"
            icon={Download}
            onClick={exportToCSV}
            className="gap-1.5 px-2.5 h-9"
          >
            Export
          </Button>
          <Button
            variant="primary"
            icon={RefreshCw}
            onClick={syncData}
            disabled={syncing}
            className={`gap-1.5 px-2.5 h-9 ${syncing ? '[&_svg]:animate-spin' : ''}`}
          >
            {syncing ? 'Syncing...' : 'Sync'}
          </Button>
          <div className="flex rounded-md shadow-sm">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 h-9 text-sm font-medium rounded-l-md border ${
                viewMode === 'grid'
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <LayoutGrid size={16} />
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`px-3 h-9 text-sm font-medium rounded-r-md border-t border-r border-b ${
                viewMode === 'table'
                  ? 'bg-brand-blue text-white border-brand-blue'
                  : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
              }`}
            >
              <Table size={16} />
            </button>
          </div>
        </div>
      </div>


      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-2 sm:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-brand-blue dark:text-blue-400">{stats.total}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Total Stocks</div>
            </div>
            <TrendingUp className="w-8 h-8 text-brand-blue opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.healthy}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Healthy</div>
            </div>
            <CheckCircle2 className="w-8 h-8 text-green-600 opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.overfished}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Overfished</div>
            </div>
            <TrendingDown className="w-8 h-8 text-red-600 opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.overfishing}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">Overfishing</div>
            </div>
            <AlertTriangle className="w-8 h-8 text-yellow-600 opacity-50" />
          </div>
        </div>
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-2xl font-bold text-gray-600 dark:text-gray-400">{stats.unknown}</div>
              <div className="text-xs text-gray-500 dark:text-gray-400">No Data</div>
            </div>
            <Fish className="w-8 h-8 text-gray-400 opacity-50" />
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <PageControlsContainer>
        <SearchBar
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Search species..."
          ariaLabel="Search species by name, FMP, or scientific name"
        />

        <FilterDropdown
          label="Filter by FMP"
          options={uniqueFMPs.map(fmp => ({
            value: fmp,
            label: fmp,
            count: species.filter(sp => sp.fmps?.includes(fmp)).length
          }))}
          selectedValues={filterFMP}
          onChange={setFilterFMP}
          showCounts={true}
          width="w-72"
        />

        {/* Status Filter Buttons */}
        {['all', 'healthy', 'overfished', 'overfishing', 'unknown'].map(status => (
          <button
            key={status}
            onClick={() => setFilterStatus(status)}
            className={`px-4 h-9 text-sm font-medium rounded-md transition-colors ${
              filterStatus === status
                ? 'bg-brand-blue text-white border border-brand-blue'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 hover:border-gray-400 dark:hover:border-gray-500'
            }`}
          >
            {status === 'all' ? 'All' : status === 'unknown' ? 'No Data' : status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </PageControlsContainer>

      {/* Grid View */}
      {viewMode === 'grid' && (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {loading ? (
            <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">Loading...</div>
          ) : filteredData.length === 0 ? (
            <div className="col-span-full text-center py-12 text-gray-500 dark:text-gray-400">No species found</div>
          ) : (
            filteredData.map((sp) => (
              <div
                key={sp.name}
                onClick={() => navigate(`/species/${encodeURIComponent(sp.name.toLowerCase().replace(/\s+/g, '-'))}`)}
                className="bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 dark:border-gray-700 overflow-hidden"
              >
                <div className="p-4">
                  <div className="flex items-start justify-between">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 hover:text-brand-blue dark:hover:text-blue-400">
                      {sp.name}
                    </h3>
                    <StatusBadge variant={getStatusVariant(sp.stockStatus)} size="sm">
                      {getStatusIcon(sp.stockStatus)}
                      {getStatusLabel(sp.stockStatus)}
                    </StatusBadge>
                  </div>

                  {/* Stock Metrics */}
                  {sp.assessment && (
                    <div className="mt-2 flex gap-4 text-xs">
                      {sp.b_bmsy && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">B/BMSY:</span>{' '}
                          <span className={sp.b_bmsy >= 1.0 ? 'text-green-600 dark:text-green-400 font-medium' : 'text-red-600 dark:text-red-400 font-medium'}>
                            {sp.b_bmsy.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {sp.f_fmsy && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">F/FMSY:</span>{' '}
                          <span className={sp.f_fmsy <= 1.0 ? 'text-green-600 dark:text-green-400 font-medium' : 'text-red-600 dark:text-red-400 font-medium'}>
                            {sp.f_fmsy.toFixed(2)}
                          </span>
                        </div>
                      )}
                      {sp.sedar_number && (
                        <div>
                          <span className="text-gray-500 dark:text-gray-400">SEDAR:</span>{' '}
                          <span className="text-gray-700 dark:text-gray-300">{sp.sedar_number}</span>
                        </div>
                      )}
                    </div>
                  )}

                  {/* FMP Tags */}
                  <div className="mt-3 flex flex-wrap gap-1">
                    {(sp.fmps || []).slice(0, 3).map(fmp => (
                      <StatusBadge key={fmp} variant={getFMPVariant(fmp)} size="sm">
                        {fmp}
                      </StatusBadge>
                    ))}
                    {(sp.fmps?.length || 0) > 3 && (
                      <StatusBadge variant="neutral" size="sm">
                        +{sp.fmps.length - 3} more
                      </StatusBadge>
                    )}
                  </div>

                  {/* Action Count */}
                  <div className="mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
                    <span className="text-xs text-gray-500 dark:text-gray-400">{sp.actionCount || 0} management actions</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        <div className="mt-6 bg-white dark:bg-gray-800 shadow overflow-x-auto sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700" onClick={() => handleSort('name')}>
                  <div className="flex items-center gap-1">Species <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700" onClick={() => handleSort('b_bmsy')}>
                  <div className="flex items-center gap-1">B/BMSY <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700" onClick={() => handleSort('f_fmsy')}>
                  <div className="flex items-center gap-1">F/FMSY <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">SEDAR</th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700" onClick={() => handleSort('actionCount')}>
                  <div className="flex items-center gap-1">Actions <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">FMPs</th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {loading ? (
                <tr><td colSpan="7" className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">Loading...</td></tr>
              ) : filteredData.length === 0 ? (
                <tr><td colSpan="7" className="px-6 py-12 text-center text-sm text-gray-500 dark:text-gray-400">No species found</td></tr>
              ) : (
                filteredData.map((sp, index) => (
                  <tr
                    key={sp.name}
                    onClick={() => navigate(`/species/${encodeURIComponent(sp.name.toLowerCase().replace(/\s+/g, '-'))}`)}
                    className={`${index % 2 === 0 ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900'} hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer`}
                  >
                    <td className="px-3 py-2 text-sm font-medium text-gray-900 dark:text-gray-100">{sp.name}</td>
                    <td className="px-3 py-2">
                      <StatusBadge variant={getStatusVariant(sp.stockStatus)} size="sm">
                        {getStatusIcon(sp.stockStatus)}
                        {getStatusLabel(sp.stockStatus)}
                      </StatusBadge>
                    </td>
                    <td className="px-3 py-2 text-sm">
                      {sp.b_bmsy ? (
                        <span className={sp.b_bmsy >= 1.0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                          {sp.b_bmsy.toFixed(2)}
                        </span>
                      ) : <span className="text-gray-400">-</span>}
                    </td>
                    <td className="px-3 py-2 text-sm">
                      {sp.f_fmsy ? (
                        <span className={sp.f_fmsy <= 1.0 ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}>
                          {sp.f_fmsy.toFixed(2)}
                        </span>
                      ) : <span className="text-gray-400">-</span>}
                    </td>
                    <td className="px-3 py-2 text-sm text-gray-700 dark:text-gray-300">{sp.sedar_number || '-'}</td>
                    <td className="px-3 py-2 text-sm text-gray-700 dark:text-gray-300">{sp.actionCount || 0}</td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">
                        {(sp.fmps || []).slice(0, 2).map(fmp => (
                          <StatusBadge key={fmp} variant="info" size="sm">
                            {fmp.split(' ')[0]}
                          </StatusBadge>
                        ))}
                        {(sp.fmps?.length || 0) > 2 && <span className="text-xs text-gray-400">+{sp.fmps.length - 2}</span>}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Footer */}
      <div className="mt-4 flex items-center justify-between">
        <div className="text-sm text-gray-500 dark:text-gray-400">
          Showing {filteredData.length} of {mergedData.length} species
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 dark:text-gray-400">Sort:</span>
          <button onClick={() => handleSort('actionCount')} className={`px-3 h-9 text-sm rounded-md transition-colors ${sortField === 'actionCount' ? 'bg-brand-blue text-white border border-brand-blue' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'}`}>
            Actions {sortField === 'actionCount' && (sortDirection === 'desc' ? '↓' : '↑')}
          </button>
          <button onClick={() => handleSort('name')} className={`px-3 h-9 text-sm rounded-md transition-colors ${sortField === 'name' ? 'bg-brand-blue text-white border border-brand-blue' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'}`}>
            Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
        </div>
      </div>

      {/* Data Sources Note */}
      <div className="mt-4 p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-md">
        <p className="text-xs text-gray-700 dark:text-gray-300">
          <strong>Data Sources:</strong> Stock status from SEDAR (sedarweb.org) and NOAA StockSMART.
          B/BMSY ratios &ge; 1.0 indicate healthy biomass. F/FMSY ratios &le; 1.0 indicate sustainable fishing mortality.
        </p>
      </div>
    </div>
  );
};

export default SpeciesStocks;
