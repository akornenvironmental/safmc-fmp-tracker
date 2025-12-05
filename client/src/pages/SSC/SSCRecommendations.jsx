/**
 * SSC Recommendations Page
 * Track SSC recommendations to the Council including ABC values, stock assessments, and status
 */

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../config';
import Breadcrumb from '../../components/Breadcrumb';
import {
  FileText,
  Search,
  Filter,
  ChevronDown,
  AlertCircle,
  TrendingUp,
  Fish,
  CheckCircle2,
  Clock,
  XCircle,
  Edit3
} from 'lucide-react';

const SSCRecommendations = () => {
  const [recommendations, setRecommendations] = useState([]);
  const [filteredRecommendations, setFilteredRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [speciesFilter, setSpeciesFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);

  // Fetch SSC recommendations
  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/ssc/recommendations?per_page=100`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch SSC recommendations');
      }

      setRecommendations(data.recommendations || []);
      setFilteredRecommendations(data.recommendations || []);
    } catch (err) {
      console.error('Error fetching SSC recommendations:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Apply filters
  useEffect(() => {
    let filtered = [...recommendations];

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(rec =>
        rec.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        rec.recommendation_text?.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(rec => rec.status === statusFilter);
    }

    // Type filter
    if (typeFilter !== 'all') {
      filtered = filtered.filter(rec => rec.recommendation_type === typeFilter);
    }

    // Species filter
    if (speciesFilter !== 'all') {
      filtered = filtered.filter(rec => rec.species && rec.species.includes(speciesFilter));
    }

    setFilteredRecommendations(filtered);
  }, [searchQuery, statusFilter, typeFilter, speciesFilter, recommendations]);

  // Get unique species
  const allSpecies = [...new Set(
    recommendations.flatMap(r => r.species || [])
  )].filter(Boolean).sort();

  // Get unique types
  const allTypes = [...new Set(
    recommendations.map(r => r.recommendation_type).filter(Boolean)
  )].sort();

  // Get status badge
  const getStatusBadge = (status) => {
    const badges = {
      'pending': { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300', icon: Clock },
      'adopted': { color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300', icon: CheckCircle2 },
      'rejected': { color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300', icon: XCircle },
      'modified': { color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300', icon: Edit3 }
    };
    return badges[status] || { color: 'bg-gray-100 text-gray-800', icon: Clock };
  };

  // Format ABC value
  const formatABC = (value, units) => {
    if (!value) return null;
    const formatted = parseFloat(value).toLocaleString();
    return units ? `${formatted} ${units}` : formatted;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading SSC recommendations...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Breadcrumb */}
      <Breadcrumb />

      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <FileText className="w-8 h-8 text-brand-blue" />
          <div>
            <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-white">
              SSC Recommendations
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Scientific advice to the Council on stock assessments and management measures
            </p>
          </div>
        </div>
        <p className="text-gray-700 dark:text-gray-300">
          Track SSC recommendations including ABC values, overfishing limits, and Council responses.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error loading SSC recommendations</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Filters Bar */}
      <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Filters
          </h3>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center gap-2 text-sm text-brand-blue hover:text-brand-blue-light"
          >
            <Filter className="w-4 h-4" />
            {showFilters ? 'Hide' : 'Show'} Filters
            <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>
        </div>

        {/* Search Bar */}
        <div className="mb-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search recommendations by title or content..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>
        </div>

        {/* Filter Dropdowns */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Status
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="adopted">Adopted</option>
                <option value="modified">Modified</option>
                <option value="rejected">Rejected</option>
              </select>
            </div>

            {/* Type Filter */}
            {allTypes.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Type
                </label>
                <select
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="all">All Types</option>
                  {allTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Species Filter */}
            {allSpecies.length > 0 && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Species
                </label>
                <select
                  value={speciesFilter}
                  onChange={(e) => setSpeciesFilter(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="all">All Species</option>
                  {allSpecies.map(species => (
                    <option key={species} value={species}>{species}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        )}

        {/* Results Count */}
        <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredRecommendations.length} of {recommendations.length} recommendations
        </div>
      </div>

      {/* Recommendations List */}
      <div className="space-y-4">
        {filteredRecommendations.map((rec) => {
          const statusInfo = getStatusBadge(rec.status);
          const StatusIcon = statusInfo.icon;

          return (
            <div
              key={rec.id}
              className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow border border-gray-200 dark:border-gray-700"
            >
              {/* Recommendation Header */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1 pr-4">
                    {rec.title}
                  </h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium inline-flex items-center gap-1 ${statusInfo.color} flex-shrink-0`}>
                    <StatusIcon className="w-3 h-3" />
                    {rec.status}
                  </span>
                </div>

                <div className="flex flex-wrap items-center gap-3 text-sm">
                  {rec.recommendation_number && (
                    <span className="text-gray-600 dark:text-gray-400 font-mono">
                      #{rec.recommendation_number}
                    </span>
                  )}
                  {rec.recommendation_type && (
                    <span className="px-2 py-1 rounded-md text-xs bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300">
                      {rec.recommendation_type}
                    </span>
                  )}
                  {rec.fmp && (
                    <span className="px-2 py-1 rounded-md text-xs bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300">
                      {rec.fmp}
                    </span>
                  )}
                </div>
              </div>

              {/* Recommendation Body */}
              <div className="p-4">
                {/* Recommendation Text */}
                <p className="text-gray-700 dark:text-gray-300 text-sm mb-4">
                  {rec.recommendation_text}
                </p>

                {/* ABC Values */}
                {(rec.abc_value || rec.overfishing_limit) && (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4 p-3 bg-green-50 dark:bg-green-900/10 rounded-lg">
                    {rec.abc_value && (
                      <div>
                        <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">
                          ABC (Acceptable Biological Catch)
                        </div>
                        <div className="text-lg font-bold text-green-700 dark:text-green-300">
                          {formatABC(rec.abc_value, rec.abc_units)}
                        </div>
                      </div>
                    )}
                    {rec.overfishing_limit && (
                      <div>
                        <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">
                          Overfishing Limit (OFL)
                        </div>
                        <div className="text-lg font-bold text-red-700 dark:text-red-300">
                          {formatABC(rec.overfishing_limit, rec.abc_units)}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Species Tags */}
                {rec.species && rec.species.length > 0 && (
                  <div className="mb-4">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                      Species
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {rec.species.map((species, idx) => (
                        <span
                          key={idx}
                          className="inline-flex items-center gap-1 px-2 py-1 rounded-md text-xs bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
                        >
                          <Fish className="w-3 h-3" />
                          {species}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Council Response */}
                {rec.council_response && (
                  <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                      Council Response
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {rec.council_response}
                    </p>
                    {rec.council_action_taken && (
                      <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        <strong>Action Taken:</strong> {rec.council_action_taken}
                      </div>
                    )}
                  </div>
                )}

                {/* Notes */}
                {rec.notes && (
                  <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-lg">
                    <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-1">
                      Notes
                    </div>
                    <p className="text-sm text-gray-700 dark:text-gray-300">
                      {rec.notes}
                    </p>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* No Results */}
      {filteredRecommendations.length === 0 && !loading && (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <FileText className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No recommendations found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {recommendations.length === 0
              ? 'SSC recommendations will appear here once they are created.'
              : 'Try adjusting your search or filters to see more recommendations.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default SSCRecommendations;
