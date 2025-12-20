import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import { SearchBar, FilterDropdown, PageControlsContainer } from '../components/PageControls';
import StatusBadge from '../components/StatusBadge';
import { RefreshCw, Download, Fish, X } from 'lucide-react';

const Species = () => {
  const navigate = useNavigate();
  const [species, setSpecies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFMP, setFilterFMP] = useState([]);
  const [sortField, setSortField] = useState('actionCount');
  const [sortDirection, setSortDirection] = useState('desc');

  useEffect(() => {
    fetchSpecies();
  }, []);

  const fetchSpecies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/species`);
      const data = await response.json();

      if (data.success) {
        setSpecies(data.species || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching species:', error);
      setLoading(false);
    }
  };

  // Get unique FMPs
  const uniqueFMPs = useMemo(() => {
    const fmpSet = new Set();
    species.forEach(sp => {
      sp.fmps?.forEach(fmp => fmpSet.add(fmp));
    });
    return Array.from(fmpSet).sort();
  }, [species]);

  // Toggle FMP filter (for active filter badges)
  const toggleFMPFilter = (fmp) => {
    setFilterFMP(prev => prev.filter(f => f !== fmp));
  };

  // Handle sorting
  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection(field === 'name' ? 'asc' : 'desc');
    }
  };

  // Filter and sort species
  const filteredSpecies = useMemo(() => {
    let result = [...species];

    // Search filter
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      result = result.filter(sp =>
        sp.name?.toLowerCase().includes(searchLower) ||
        sp.fmps?.some(fmp => fmp.toLowerCase().includes(searchLower))
      );
    }

    // FMP filter
    if (filterFMP.length > 0) {
      result = result.filter(sp =>
        sp.fmps?.some(fmp => filterFMP.includes(fmp))
      );
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
  }, [species, searchTerm, filterFMP, sortField, sortDirection]);

  // Export to CSV
  const exportToCSV = () => {
    const headers = ['Species', 'Action Count', 'FMPs', 'First Mention', 'Last Mention'];
    const rows = filteredSpecies.map(sp => [
      sp.name,
      sp.actionCount,
      (sp.fmps || []).join('; '),
      sp.firstMention || 'N/A',
      sp.lastMention || 'N/A'
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(val => `"${val}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `species-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  // Get variant based on action count
  const getActionCountVariant = (count) => {
    if (count >= 20) return 'error';
    if (count >= 10) return 'warning';
    if (count >= 5) return 'warning';
    return 'success';
  };

  // Get FMP badge variant
  const getFMPVariant = (fmp) => {
    const variants = {
      'Snapper Grouper': 'info',
      'Coastal Migratory Pelagics': 'purple',
      'Dolphin Wahoo': 'info',
      'Spiny Lobster': 'error',
      'Golden Crab': 'warning',
      'Shrimp': 'error',
      'Coral': 'warning',
      'Sargassum': 'success',
    };
    return variants[fmp] || 'neutral';
  };

  // Calculate stats
  const stats = useMemo(() => {
    const totalActions = species.reduce((sum, sp) => sum + (sp.actionCount || 0), 0);
    return {
      totalSpecies: species.length,
      totalActions,
      avgActions: species.length > 0 ? (totalActions / species.length).toFixed(1) : 0
    };
  }, [species]);

  return (
    <div>
      {/* Description and Action Buttons Row */}
      <div className="page-description-container">
        <p className="page-description-text">
          Browse species profiles and their associated management actions across all FMPs.
        </p>
        <div className="page-description-actions">
          <button
            onClick={exportToCSV}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-teal-300 bg-gradient-to-r from-teal-50 to-cyan-50 px-2.5 h-9 text-xs font-medium text-teal-700 shadow-sm hover:from-teal-100 hover:to-cyan-100 hover:border-teal-400 transition-all"
          >
            <Download size={14} />
            Export CSV
          </button>
          <button
            onClick={fetchSpecies}
            className="inline-flex items-center gap-1.5 justify-center rounded-md border border-transparent bg-brand-blue px-2.5 h-9 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="mt-6 grid grid-cols-1 gap-5 sm:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <Fish className="h-6 w-6 text-brand-blue" />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Species</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.totalSpecies}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-brand-green" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Total Actions</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.totalActions}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-purple-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">Avg. Actions/Species</dt>
                  <dd className="text-2xl font-semibold text-gray-900">{stats.avgActions}</dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <PageControlsContainer>
        <SearchBar
          value={searchTerm}
          onChange={setSearchTerm}
          placeholder="Search species..."
          ariaLabel="Search species by name or FMP"
        />

        {/* FMP Filter Dropdown */}
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
        />
      </PageControlsContainer>

      {/* Active Filters */}
      {filterFMP.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {filterFMP.map(fmp => (
            <StatusBadge key={fmp} variant="info" size="sm" className="gap-1">
              {fmp}
              <button
                onClick={() => toggleFMPFilter(fmp)}
                className="hover:opacity-70"
                aria-label={`Remove ${fmp} filter`}
              >
                <X size={14} aria-hidden="true" />
              </button>
            </StatusBadge>
          ))}
        </div>
      )}

      {/* Species Grid */}
      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {loading ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            Loading species data...
          </div>
        ) : filteredSpecies.length === 0 ? (
          <div className="col-span-full text-center py-12 text-gray-500">
            No species found matching your criteria
          </div>
        ) : (
          filteredSpecies.map((sp) => (
            <div
              key={sp.name}
              onClick={() => navigate(`/species/${encodeURIComponent(sp.name.toLowerCase().replace(/\s+/g, '-'))}`)}
              className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer border border-gray-200 overflow-hidden"
            >
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <h3 className="text-lg font-semibold text-gray-900 hover:text-brand-blue">
                    {sp.name}
                  </h3>
                  <StatusBadge variant={getActionCountVariant(sp.actionCount)} size="sm">
                    {sp.actionCount} actions
                  </StatusBadge>
                </div>

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

                {/* Recent Actions Preview */}
                {sp.actions?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <p className="text-xs text-gray-500 mb-1">Recent actions:</p>
                    <ul className="text-xs text-gray-600 space-y-0.5">
                      {sp.actions.slice(0, 2).map((action, idx) => (
                        <li key={idx} className="truncate">
                          {action.title}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Date Range */}
                {(sp.firstMention || sp.lastMention) && (
                  <div className="mt-2 text-xs text-gray-500">
                    {sp.firstMention && sp.lastMention ? (
                      <>Tracked: {new Date(sp.firstMention).getFullYear()} - {new Date(sp.lastMention).getFullYear()}</>
                    ) : sp.lastMention ? (
                      <>Last tracked: {new Date(sp.lastMention).toLocaleDateString()}</>
                    ) : null}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Sort Controls */}
      <div className="mt-6 flex items-center justify-between">
        <div className="text-sm text-gray-500">
          Showing {filteredSpecies.length} of {species.length} species
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500">Sort by:</span>
          <button
            onClick={() => handleSort('actionCount')}
            className={`px-3 py-1 text-xs rounded ${
              sortField === 'actionCount'
                ? 'bg-brand-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Actions {sortField === 'actionCount' && (sortDirection === 'desc' ? '↓' : '↑')}
          </button>
          <button
            onClick={() => handleSort('name')}
            className={`px-3 py-1 text-xs rounded ${
              sortField === 'name'
                ? 'bg-brand-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Species;
