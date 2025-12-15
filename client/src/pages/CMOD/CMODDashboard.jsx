/**
 * CMOD Dashboard
 * Overview of Council Member Ongoing Development workshops and cross-council collaboration
 */

import { useState, useEffect } from 'react';
import { GraduationCap, Calendar, FileText, Users, TrendingUp, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../../config';
import { toast } from 'react-toastify';

const CMODDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [workshops, setWorkshops] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const token = localStorage.getItem('authToken');

      // Fetch workshops and analytics in parallel
      const [workshopsRes, analyticsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/cmod/workshops`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch(`${API_BASE_URL}/api/cmod/analytics`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (!workshopsRes.ok || !analyticsRes.ok) {
        throw new Error('Failed to fetch CMOD data');
      }

      const workshopsData = await workshopsRes.json();
      const analyticsData = await analyticsRes.json();

      setWorkshops(workshopsData.workshops || []);
      setAnalytics(analyticsData.analytics || {});
    } catch (err) {
      console.error('Error fetching CMOD data:', err);
      toast.error('Failed to load CMOD data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      'completed': { bg: 'bg-green-100 dark:bg-green-900/30', text: 'text-green-800 dark:text-green-300', label: 'Completed' },
      'scheduled': { bg: 'bg-blue-100 dark:bg-blue-900/30', text: 'text-blue-800 dark:text-blue-300', label: 'Scheduled' },
      'cancelled': { bg: 'bg-red-100 dark:bg-red-900/30', text: 'text-red-800 dark:text-red-300', label: 'Cancelled' }
    };

    const config = statusConfig[status] || statusConfig['scheduled'];

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
        {config.label}
      </span>
    );
  };

  return (
    <div>
      {/* Description */}
      <div className="page-description-container">
        <p className="page-description-text">
          Council Member Ongoing Development program providing training and resources for effective fishery management governance.
        </p>
        <div className="page-description-actions"></div>
      </div>

      {/* Stats Grid */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-5 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Total Workshops</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                  {analytics.total_workshops || 0}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-brand-blue" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-5 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                <p className="text-2xl font-bold text-green-600 dark:text-green-400 mt-1">
                  {analytics.completed_workshops || 0}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600 dark:text-green-400" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-5 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Scheduled</p>
                <p className="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-1">
                  {analytics.scheduled_workshops || 0}
                </p>
              </div>
              <Calendar className="w-8 h-8 text-blue-600 dark:text-blue-400" />
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-5 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Councils Participating</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">8</p>
              </div>
              <Users className="w-8 h-8 text-brand-blue" />
            </div>
          </div>
        </div>
      )}

      {/* Quick Links Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Link
          to="/cmod/workshops"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700 group"
        >
          <Calendar className="w-10 h-10 text-brand-blue mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Workshop Timeline</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            View all CMOD workshops by year
          </p>
        </Link>

        <Link
          to="/cmod/topics"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700 group"
        >
          <FileText className="w-10 h-10 text-brand-blue mb-3 group-hover:scale-110 transition-transform" />
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">Topic Tracking</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Track implementation of workshop topics
          </p>
        </Link>

        <a
          href="https://www.fisherycouncils.org/cmod"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow p-6 border border-gray-200 dark:border-gray-700 group"
        >
          <div className="flex items-center justify-between mb-3">
            <ExternalLink className="w-10 h-10 text-brand-blue group-hover:scale-110 transition-transform" />
          </div>
          <h3 className="font-semibold text-gray-900 dark:text-white mb-1">CMOD Resources</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Visit official CMOD website
          </p>
        </a>
      </div>

      {/* Workshop Timeline */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 mb-8">
        <div className="p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="font-heading text-xl font-bold text-gray-900 dark:text-white">
            Workshop Timeline
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
            CMOD workshops from 2022 to present
          </p>
        </div>
        <div className="p-6">
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brand-blue"></div>
            </div>
          ) : workshops.length === 0 ? (
            <div className="text-center py-12">
              <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-3" />
              <p className="text-gray-600 dark:text-gray-400">No workshops found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {workshops.map((workshop) => (
                <Link
                  key={workshop.id}
                  to={`/cmod/workshops/${workshop.id}`}
                  className="block border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-lg font-bold text-brand-blue">{workshop.year}</span>
                        {getStatusBadge(workshop.status)}
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
                        {workshop.title}
                      </h3>
                      <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">
                        <span className="font-medium">Theme:</span> {workshop.theme}
                      </p>
                      <div className="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-gray-400">
                        <div className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          <span>
                            {workshop.start_date ? new Date(workshop.start_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'Date TBD'}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          <span>Host: {workshop.host_council || 'TBD'}</span>
                        </div>
                        {workshop.location && (
                          <div className="flex items-center gap-1">
                            <span>📍 {workshop.location}</span>
                          </div>
                        )}
                      </div>
                      {workshop.focus_areas && workshop.focus_areas.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                          {workshop.focus_areas.slice(0, 5).map((area, idx) => (
                            <span
                              key={idx}
                              className="px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-md"
                            >
                              {area}
                            </span>
                          ))}
                          {workshop.focus_areas.length > 5 && (
                            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs rounded-md">
                              +{workshop.focus_areas.length - 5} more
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Top Focus Areas */}
      {analytics && analytics.top_focus_areas && analytics.top_focus_areas.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-heading text-lg font-bold text-gray-900 dark:text-white">
                Top Focus Areas
              </h3>
            </div>
            <div className="p-6">
              <div className="space-y-3">
                {analytics.top_focus_areas.slice(0, 8).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <span className="text-sm text-gray-700 dark:text-gray-300">{item.focus_area}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-brand-blue rounded-full h-2"
                          style={{ width: `${(item.count / analytics.top_focus_areas[0].count) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900 dark:text-white w-8 text-right">
                        {item.count}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="p-6 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-heading text-lg font-bold text-gray-900 dark:text-white">
                About CMOD
              </h3>
            </div>
            <div className="p-6">
              <div className="space-y-4 text-sm text-gray-700 dark:text-gray-300">
                <p>
                  <strong>Council Member Ongoing Development (CMOD)</strong> workshops provide professional
                  development and training opportunities for members of all eight Regional Fishery Management Councils.
                </p>
                <p>
                  Each workshop focuses on emerging topics in fishery management, combining:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Technical presentations from scientists and experts</li>
                  <li>Interactive discussions and case studies</li>
                  <li>Skills training sessions</li>
                  <li>Cross-council collaboration and knowledge sharing</li>
                </ul>
                <p className="text-xs text-gray-600 dark:text-gray-400 pt-2">
                  CMOD workshops are coordinated by the Council Coordination Committee (CCC) and hosted
                  by different Regional Fishery Management Councils.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CMODDashboard;
