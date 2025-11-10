import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import { RefreshCw } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalActions: 0,
    pendingReview: 0,
    upcomingMeetings: 0,
    recentComments: 0
  });
  const [recentActions, setRecentActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Fetch stats
      const statsResponse = await fetch(`${API_BASE_URL}/api/dashboard/stats`);
      const statsData = await statsResponse.json();

      setStats({
        totalActions: statsData.totalActions || 0,
        pendingReview: statsData.pendingReview || 0,
        upcomingMeetings: statsData.upcomingMeetings || 0,
        recentComments: statsData.recentComments || 0
      });

      // Fetch recent actions
      const actionsResponse = await fetch(`${API_BASE_URL}/api/actions?limit=10`);
      const actionsData = await actionsResponse.json();

      if (actionsData.success) {
        setRecentActions(actionsData.actions || []);
      }

      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  const triggerScrape = async () => {
    try {
      setScraping(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/all`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert('Scraping started! Data will be updated shortly.');
        // Refresh dashboard after a delay
        setTimeout(() => {
          fetchDashboardData();
        }, 3000);
      } else {
        alert('Failed to trigger scraping: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error triggering scrape:', error);
      alert('Error triggering scrape');
    } finally {
      setScraping(false);
    }
  };

  return (
    <div>
      {/* DEBUG BANNER - IMPOSSIBLE TO MISS */}
      <div className="bg-red-600 text-white text-center py-4 mb-6 text-2xl font-bold border-4 border-yellow-400">
        🔴 DEBUG MODE v2 ACTIVE - YOU'RE SEEING THE NEW BUILD! 🔴
      </div>

      {/* Header with Update Button */}
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div className="sm:flex-auto">
          <div className="flex items-center gap-3">
            <h1 className="font-heading text-3xl font-bold text-gray-900">Dashboard</h1>
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 border border-green-300">
              Build: v2-debug
            </span>
          </div>
          <p className="mt-2 text-sm text-gray-700">
            Overview of FMP actions, meetings, and public comments
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={triggerScrape}
            disabled={scraping}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
            {scraping ? 'Updating...' : 'Update Data'}
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
          <div className="text-3xl font-bold text-brand-blue mb-2">
            {loading ? '-' : stats.totalActions}
          </div>
          <div className="text-sm text-gray-500">Total Actions</div>
        </div>

        <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
          <div className="text-3xl font-bold text-yellow-600 mb-2">
            {loading ? '-' : stats.pendingReview}
          </div>
          <div className="text-sm text-gray-500">Pending Review</div>
        </div>

        <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
          <div className="text-3xl font-bold text-green-600 mb-2">
            {loading ? '-' : stats.upcomingMeetings}
          </div>
          <div className="text-sm text-gray-500">Upcoming Meetings</div>
        </div>

        <div className="bg-white shadow rounded-lg p-6 hover:shadow-md transition-shadow">
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {loading ? '-' : stats.recentComments}
          </div>
          <div className="text-sm text-gray-500">Recent Comments</div>
        </div>
      </div>

      {/* Recent Actions */}
      <div className="bg-white shadow overflow-hidden sm:rounded-lg">
        <div className="px-4 py-3 sm:px-6 border-b border-gray-200">
          <h2 className="font-heading text-lg font-medium text-gray-900">Recent Actions</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Action
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Type
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  FMP
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Stage
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Progress
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                    Loading actions...
                  </td>
                </tr>
              ) : recentActions.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                    No actions found. Click "Update Data" to scrape SAFMC website.
                  </td>
                </tr>
              ) : (
                recentActions.map((action, index) => (
                  <tr key={action.id || index} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      {action.source_url ? (
                        <a
                          href={action.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm font-medium text-brand-blue hover:text-brand-green hover:underline"
                        >
                          {action.title}
                        </a>
                      ) : (
                        <div className="text-sm font-medium text-gray-900">{action.title}</div>
                      )}
                      {action.description && (
                        <div className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {action.description.substring(0, 120)}...
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-xs text-gray-600">{action.type || 'Amendment'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-xs text-gray-900">{action.fmp || 'N/A'}</span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-0.5 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                        {action.progress_stage || 'Unknown'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-1">
                        <div className="w-16 bg-gray-200 rounded-full h-1.5">
                          <div
                            className="bg-brand-blue h-1.5 rounded-full"
                            style={{ width: `${action.progress || 0}%` }}
                          ></div>
                        </div>
                        <span className="text-xs text-gray-600">{action.progress || 0}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                      {action.last_updated ? new Date(action.last_updated).toLocaleDateString() : 'N/A'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
