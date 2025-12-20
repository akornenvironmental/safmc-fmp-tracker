import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import { RefreshCw } from 'lucide-react';
import Button from '../components/Button';
import StatusBadge from '../components/StatusBadge';

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
      {/* Description and Action Buttons Row */}
      <div className="page-description-container">
        <p className="page-description-text">
          Overview of amendment actions, meetings, and fishery management activities across all FMPs.
        </p>
        <div className="page-description-actions">
          <Button
            variant="primary"
            onClick={triggerScrape}
            disabled={scraping}
            icon={scraping ? RefreshCw : RefreshCw}
            className={`gap-1.5 px-2.5 h-9 ${scraping ? '[&_svg]:animate-spin' : ''}`}
          >
            {scraping ? 'Syncing...' : 'Sync'}
          </Button>
        </div>
      </div>

      {/* Stats Grid */}
      <h2 className="text-2xl font-heading font-semibold text-gray-900 dark:text-white mb-4">Key Statistics</h2>
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
            <caption className="sr-only">Recent fishery management actions and amendments</caption>
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Action
                </th>
                <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Type
                </th>
                <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase">
                  FMP
                </th>
                <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Stage
                </th>
                <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Progress
                </th>
                <th scope="col" className="px-2 py-1.5 text-left text-xs font-medium text-gray-500 uppercase">
                  Updated
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                    <div role="status" aria-live="polite">
                      <span className="sr-only">Loading actions, please wait...</span>
                      Loading actions...
                    </div>
                  </td>
                </tr>
              ) : recentActions.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-4 text-center text-sm text-gray-500">
                    No actions found. Click "Sync" to scrape SAFMC website.
                  </td>
                </tr>
              ) : (
                recentActions.map((action, index) => (
                  <tr key={action.id || index} className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-100'} hover:bg-gray-50 transition-colors duration-150 cursor-pointer`} onClick={() => navigate(`/actions?highlight=${action.action_id || action.id}`)}>
                    <td className="px-2 py-0.5">
                      {action.source_url ? (
                        <a
                          href={action.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs font-medium text-brand-blue hover:text-brand-green hover:underline"
                          onClick={(e) => e.stopPropagation()}
                        >
                          {action.title}
                        </a>
                      ) : (
                        <div className="text-xs font-medium text-gray-900">{action.title}</div>
                      )}
                      {action.description && (
                        <div className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                          {action.description.substring(0, 120)}...
                        </div>
                      )}
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap">
                      <span className="text-xs text-gray-600">{action.type || 'Amendment'}</span>
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap">
                      <span className="text-xs text-gray-900">{action.fmp || 'N/A'}</span>
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap">
                      <StatusBadge variant="info" size="sm">
                        {action.progress_stage || 'Unknown'}
                      </StatusBadge>
                    </td>
                    <td className="px-2 py-0.5 whitespace-nowrap">
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
                    <td className="px-2 py-0.5 whitespace-nowrap text-xs text-gray-500">
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
