/**
 * CMOD Topics
 * Track implementation of CMOD workshop topics across councils
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../../components/PageHeader';
import { GraduationCap, TrendingUp, Filter, Search } from 'lucide-react';
import { API_BASE_URL } from '../../config';
import { toast } from 'react-toastify';

const CMODTopics = () => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    council_name: '',
    implementation_status: '',
    search: ''
  });

  useEffect(() => {
    fetchTopics();
  }, [filters]);

  const fetchTopics = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const params = new URLSearchParams();

      if (filters.council_name) params.append('council_name', filters.council_name);
      if (filters.implementation_status) params.append('implementation_status', filters.implementation_status);
      if (filters.search) params.append('topic', filters.search);

      const response = await fetch(`${API_BASE_URL}/api/cmod/topics?${params}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch CMOD topics');
      }

      const data = await response.json();
      setTopics(data.topics || []);
    } catch (err) {
      console.error('Error fetching topics:', err);
      toast.error('Failed to load CMOD topics');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const statusColors = {
      'Not Started': 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300',
      'Planning': 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300',
      'In Progress': 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300',
      'Implemented': 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300'
    };

    return statusColors[status] || statusColors['Not Started'];
  };

  const councils = [
    'South Atlantic',
    'New England',
    'Mid-Atlantic',
    'Gulf of Mexico',
    'Caribbean',
    'Pacific',
    'North Pacific',
    'Western Pacific'
  ];

  const implementationStatuses = ['Not Started', 'Planning', 'In Progress', 'Implemented'];

  return (
    <div>
      {/* Header */}
      <PageHeader
        icon={GraduationCap}
        title="CMOD Topics"
        subtitle="Educational topics"
        description="Educational topics and resources for Council members."
      />

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          <h2 className="font-semibold text-gray-900 dark:text-white">Filters</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Council
            </label>
            <select
              value={filters.council_name}
              onChange={(e) => setFilters({ ...filters, council_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-blue focus:border-transparent"
            >
              <option value="">All Councils</option>
              {councils.map((council) => (
                <option key={council} value={council}>{council}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Implementation Status
            </label>
            <select
              value={filters.implementation_status}
              onChange={(e) => setFilters({ ...filters, implementation_status: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-blue focus:border-transparent"
            >
              <option value="">All Statuses</option>
              {implementationStatuses.map((status) => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Search Topics
            </label>
            <div className="relative">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
              <input
                type="text"
                value={filters.search}
                onChange={(e) => setFilters({ ...filters, search: e.target.value })}
                placeholder="Search topics..."
                className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Topics List */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-heading text-xl font-bold text-gray-900 dark:text-white">
            Topics ({topics.length})
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-blue"></div>
          </div>
        ) : topics.length === 0 ? (
          <div className="text-center py-12">
            <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600 dark:text-gray-400">
              {filters.council_name || filters.implementation_status || filters.search
                ? 'No topics match your filters'
                : 'No topics tracked yet'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200 dark:divide-gray-700">
            {topics.map((topic) => (
              <div key={topic.id} className="p-6 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="font-semibold text-gray-900 dark:text-white">{topic.topic}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(topic.implementation_status)}`}>
                        {topic.implementation_status}
                      </span>
                    </div>
                    {topic.council_name && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                        <span className="font-medium">Council:</span> {topic.council_name}
                      </p>
                    )}
                    {topic.description && (
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                        {topic.description}
                      </p>
                    )}
                  </div>
                </div>

                {/* Implementation Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                  {topic.first_discussed && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700 dark:text-gray-300">First Discussed: </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        {new Date(topic.first_discussed).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </span>
                    </div>
                  )}
                  {topic.last_updated_council && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700 dark:text-gray-300">Last Updated: </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        {new Date(topic.last_updated_council).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                      </span>
                    </div>
                  )}
                  {(topic.related_actions?.length || topic.related_meetings?.length || topic.related_amendments?.length) > 0 && (
                    <div className="text-sm">
                      <span className="font-medium text-gray-700 dark:text-gray-300">Related Items: </span>
                      <span className="text-gray-600 dark:text-gray-400">
                        {(topic.related_actions?.length || 0) + (topic.related_meetings?.length || 0) + (topic.related_amendments?.length || 0)}
                      </span>
                    </div>
                  )}
                </div>

                {/* Outcomes and Challenges */}
                {topic.outcomes_achieved && topic.outcomes_achieved.length > 0 && (
                  <div className="mb-3">
                    <h4 className="text-sm font-semibold text-green-700 dark:text-green-400 mb-1">
                      Outcomes Achieved
                    </h4>
                    <ul className="list-disc list-inside space-y-1">
                      {topic.outcomes_achieved.map((outcome, idx) => (
                        <li key={idx} className="text-sm text-gray-600 dark:text-gray-400">{outcome}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {topic.challenges && topic.challenges.length > 0 && (
                  <div className="mb-3">
                    <h4 className="text-sm font-semibold text-yellow-700 dark:text-yellow-400 mb-1">
                      Challenges
                    </h4>
                    <ul className="list-disc list-inside space-y-1">
                      {topic.challenges.map((challenge, idx) => (
                        <li key={idx} className="text-sm text-gray-600 dark:text-gray-400">{challenge}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {topic.implementation_notes && (
                  <div className="bg-gray-50 dark:bg-gray-700/50 rounded p-3">
                    <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                      Implementation Notes
                    </h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {topic.implementation_notes}
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Info Box */}
      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">About Topic Tracking</h3>
        <p className="text-sm text-gray-700 dark:text-gray-300">
          Topic tracking links CMOD workshop themes and recommendations to actual Council activities.
          This helps demonstrate how cross-council professional development translates into concrete
          management actions and policy changes across the Regional Fishery Management Council system.
        </p>
      </div>
    </div>
  );
};

export default CMODTopics;
