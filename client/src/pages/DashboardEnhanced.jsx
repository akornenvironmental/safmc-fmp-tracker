import { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import {
  RefreshCw, FileText, Calendar, MessageSquare, Fish,
  TrendingUp, Clock, AlertCircle, ChevronRight, BarChart3
} from 'lucide-react';
import Button from '../components/Button';
import StatusBadge from '../components/StatusBadge';
import { toast } from 'react-toastify';

const DashboardEnhanced = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    totalActions: 0,
    pendingReview: 0,
    upcomingMeetings: 0,
    recentComments: 0
  });
  const [actions, setActions] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [speciesStats, setSpeciesStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // Get auth token for API calls
      const token = localStorage.getItem('authToken');
      const headers = token ? {
        'Authorization': `Bearer ${token}`
      } : {};

      // Fetch all data in parallel
      const [statsRes, actionsRes, meetingsRes, speciesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/dashboard/stats`, { headers, credentials: 'include' }),
        fetch(`${API_BASE_URL}/api/actions`, { headers, credentials: 'include' }),
        fetch(`${API_BASE_URL}/api/meetings?limit=5`, { headers, credentials: 'include' }),
        fetch(`${API_BASE_URL}/api/species/stats`, { headers, credentials: 'include' })
      ]);

      const [statsData, actionsData, meetingsData, speciesData] = await Promise.all([
        statsRes.json(),
        actionsRes.json(),
        meetingsRes.json(),
        speciesRes.json()
      ]);

      setStats({
        totalActions: statsData.totalActions || 0,
        pendingReview: statsData.pendingReview || 0,
        upcomingMeetings: statsData.upcomingMeetings || 0,
        recentComments: statsData.recentComments || 0
      });

      if (actionsData.success) {
        setActions(actionsData.actions || []);
      }

      if (meetingsData.success) {
        setMeetings(meetingsData.meetings || []);
      }

      if (speciesData.success) {
        setSpeciesStats(speciesData.stats);
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
      const token = localStorage.getItem('authToken');

      if (!token) {
        toast.error('Please log in to update data.', { autoClose: 3000 });
        setScraping(false);
        return;
      }

      // List of all scraper endpoints to trigger
      const scrapers = [
        { endpoint: '/api/scrape/all', name: 'SAFMC Data (Actions, Amendments, Meetings)' },
        { endpoint: '/api/ssc/import/meetings', name: 'SSC Meetings', body: { download_documents: true } },
      ];

      let successCount = 0;
      let failCount = 0;

      // Run all scrapers sequentially
      for (const scraper of scrapers) {
        // Show "Starting..." toast
        toast.info(`Starting: ${scraper.name}`, { autoClose: 3000 });

        try {
          const response = await fetch(`${API_BASE_URL}${scraper.endpoint}`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify(scraper.body || {})
          });

          const data = await response.json();

          if (response.ok && data.success) {
            successCount++;
            toast.success(`Completed: ${scraper.name}`, { autoClose: 3000 });
          } else {
            failCount++;
            toast.error(`Failed: ${scraper.name}`, { autoClose: 3000 });
            console.error(`${scraper.name} failed:`, data.error);
          }
        } catch (error) {
          failCount++;
          toast.error(`Error: ${scraper.name}`, { autoClose: 3000 });
          console.error(`${scraper.name} error:`, error);
        }

        // Wait 1 second between scrapers
        if (scrapers.indexOf(scraper) < scrapers.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }

      // Refresh dashboard data after all scrapers complete
      setTimeout(() => fetchDashboardData(), 2000);

      // Show final summary toast
      if (failCount === 0) {
        toast.success(`All data updated successfully! (${successCount} scrapers completed)`, { autoClose: 3000 });
      } else if (successCount > 0) {
        toast.warning(`Partial update complete. ${successCount} succeeded, ${failCount} failed.`, { autoClose: 3000 });
      } else {
        toast.error('All scrapers failed. Please check your connection and try again.', { autoClose: 3000 });
      }
    } catch (error) {
      console.error('Error triggering scrape:', error);
      toast.error('Failed to update data. Please check your connection and try again.', { autoClose: 3000 });
    } finally {
      setScraping(false);
    }
  };

  // Calculate FMP statistics
  const fmpStats = useMemo(() => {
    const fmpMap = {};
    actions.forEach(action => {
      if (!action.fmp) return;
      if (!fmpMap[action.fmp]) {
        fmpMap[action.fmp] = { total: 0, completed: 0, inProgress: 0, planned: 0 };
      }
      fmpMap[action.fmp].total++;

      const status = (action.status || '').toLowerCase();
      const stage = (action.progress_stage || '').toLowerCase();

      // Classify actions using progress_stage (primary) and status (fallback):
      // Priority order: Completed > In Progress > Planned

      // COMPLETED: Explicitly implemented or completed stages
      if (stage.includes('implement') || stage.includes('complete') ||
          stage.includes('final action') || stage.includes('adopted') ||
          status === 'completed' || status === 'implemented') {
        fmpMap[action.fmp].completed++;
      }
      // IN PROGRESS: Active work stages (mid-to-late process)
      else if (stage.includes('public hearing') || stage.includes('public comment') ||
               stage.includes('secretarial review') || stage.includes('final approval') ||
               stage.includes('council review') || stage.includes('council approval') ||
               stage.includes('rule making') || stage.includes('federal register') ||
               stage.includes('review') || stage.includes('approval') ||
               status === 'underway' || status === 'public comment' || status === 'in progress') {
        fmpMap[action.fmp].inProgress++;
      }
      // PLANNED: Early planning/scoping stages
      else if (stage.includes('scoping') || stage.includes('pre-scoping') ||
               stage.includes('planning') || stage.includes('development') ||
               stage.includes('drafting') || stage.includes('preparing') ||
               status === 'planned' || status === 'pending') {
        fmpMap[action.fmp].planned++;
      }
      // DEFAULT: If no clear indicators, treat as planned (safer assumption)
      else {
        fmpMap[action.fmp].planned++;
      }
    });

    const result = Object.entries(fmpMap)
      .map(([fmp, stats]) => ({
        fmp,
        ...stats
      }))
      .sort((a, b) => b.total - a.total);

    return result;
  }, [actions]);

  // Get recent activity - focus on active amendments and upcoming meetings
  const recentActivity = useMemo(() => {
    const activity = [];

    // Helper function to check if an action is active/planned
    const isActiveOrPlanned = (action) => {
      const status = (action.status || '').toLowerCase();
      const stage = (action.progress_stage || '').toLowerCase();

      // Not active if explicitly implemented/completed
      if (stage.includes('implement') || stage.includes('complete')) {
        return false;
      }

      // Active if status or stage indicates ongoing work
      return status === 'underway' || status === 'public comment' || status === 'planned' ||
             stage.includes('public hearing') || stage.includes('public comment') ||
             stage.includes('secretarial review') || stage.includes('final approval') ||
             stage.includes('council review') || stage.includes('rule making') ||
             stage.includes('federal register') || stage.includes('scoping') ||
             stage.includes('pre-scoping');
    };

    // Add active/planned amendments
    const activeActions = actions.filter(isActiveOrPlanned);

    // Sort by last_updated and take top 5
    activeActions
      .sort((a, b) => new Date(b.last_updated || 0) - new Date(a.last_updated || 0))
      .slice(0, 5)
      .forEach(action => {
        activity.push({
          type: 'action',
          title: action.title,
          subtitle: `${action.status} - ${action.fmp}`,
          date: action.last_updated,
          link: `/actions`,
          icon: FileText
        });
      });

    // Add upcoming meetings (future dates only)
    const now = new Date();
    meetings
      .filter(m => m.start_date && new Date(m.start_date) >= now)
      .slice(0, 5)
      .forEach(meeting => {
        activity.push({
          type: 'meeting',
          title: meeting.title,
          subtitle: meeting.location || 'TBD',
          date: meeting.start_date,
          link: `/meetings`,
          icon: Calendar
        });
      });

    return activity.sort((a, b) => {
      if (!a.date) return 1;
      if (!b.date) return -1;
      return new Date(a.date) - new Date(b.date); // Sort chronologically (upcoming first)
    }).slice(0, 8);
  }, [actions, meetings]);

  // Get stage variant for StatusBadge
  const getStageVariant = (stage) => {
    if (!stage) return 'neutral';
    const s = stage.toLowerCase();
    if (s.includes('scoping')) return 'warning';
    if (s.includes('hearing')) return 'info';
    if (s.includes('approval')) return 'success';
    if (s.includes('implementation')) return 'purple';
    return 'neutral';
  };

  return (
    <div>
      <div className="page-description-container">
        <p className="page-description-text">
          Monitor active amendments, upcoming meetings, and FMP progress across all fishery management plans in the South Atlantic region.
        </p>
        <div className="page-description-actions">
          <Button
            variant="primary"
            icon={RefreshCw}
            onClick={triggerScrape}
            disabled={scraping}
            className="h-9"
          >
            {scraping ? 'Syncing...' : 'Sync'}
          </Button>
        </div>
      </div>

      <div className="space-y-2">

      {/* Stats Cards */}
      <div className="grid grid-cols-3 lg:grid-cols-6 gap-1.5">
        <Link to="/actions" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-2 hover:shadow-md transition-shadow">
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <p className="text-body-lg font-medium text-gray-500 dark:text-gray-400">Actions</p>
              <FileText className="w-6 h-6 text-blue-300 dark:text-blue-700" />
            </div>
            <p className="text-h1 text-brand-blue dark:text-blue-400">{loading ? '-' : stats.totalActions}</p>
          </div>
        </Link>

        <Link to="/meetings" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-2 hover:shadow-md transition-shadow">
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <p className="text-body-lg font-medium text-gray-500 dark:text-gray-400">Meetings</p>
              <Calendar className="w-6 h-6 text-green-300 dark:text-green-700" />
            </div>
            <p className="text-h1 text-green-600 dark:text-green-400">{loading ? '-' : stats.upcomingMeetings}</p>
          </div>
        </Link>

        <Link to="/comments" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-2 hover:shadow-md transition-shadow">
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <p className="text-body-lg font-medium text-gray-500 dark:text-gray-400">Comments</p>
              <MessageSquare className="w-6 h-6 text-purple-300 dark:text-purple-700" />
            </div>
            <p className="text-h1 text-purple-600 dark:text-purple-400">{loading ? '-' : stats.recentComments}</p>
          </div>
        </Link>

        <Link to="/stocks" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-2 hover:shadow-md transition-shadow">
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <p className="text-body-lg font-medium text-gray-500 dark:text-gray-400">Species</p>
              <Fish className="w-6 h-6 text-cyan-300 dark:text-cyan-700" />
            </div>
            <p className="text-h1 text-cyan-600 dark:text-cyan-400">{loading ? '-' : (speciesStats?.totalSpecies || 0)}</p>
          </div>
        </Link>

        <Link to="/ssc" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-2 hover:shadow-md transition-shadow">
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <p className="text-body-lg font-medium text-gray-500 dark:text-gray-400">SSC</p>
              <AlertCircle className="w-6 h-6 text-orange-300 dark:text-orange-700" />
            </div>
            <p className="text-h1 text-orange-600 dark:text-orange-400">{loading ? '-' : '12'}</p>
          </div>
        </Link>

        <Link to="/cmod" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-2 hover:shadow-md transition-shadow">
          <div className="flex flex-col">
            <div className="flex items-center justify-between mb-1">
              <p className="text-body-lg font-medium text-gray-500 dark:text-gray-400">CMOD</p>
              <TrendingUp className="w-6 h-6 text-pink-300 dark:text-pink-700" />
            </div>
            <p className="text-h1 text-pink-600 dark:text-pink-400">{loading ? '-' : '8'}</p>
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-2 border-t-2 border-gray-200 dark:border-gray-700 pt-2">
        {/* FMP Progress */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded shadow-sm border-2 border-gray-200 dark:border-gray-700 p-2">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-heading font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2" style={{ fontSize: '24px', lineHeight: '1', fontWeight: '600' }}>
              <BarChart3 className="w-5 h-5 text-gray-400 dark:text-gray-500" />
              FMP Progress Overview
            </h2>
            <Link to="/actions" className="text-h5 text-brand-blue dark:text-blue-400 hover:underline">
              View all
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-6 text-body-lg text-gray-500 dark:text-gray-400">Loading...</div>
          ) : fmpStats.length === 0 ? (
            <div className="text-center py-6 text-body-lg text-gray-500 dark:text-gray-400">No FMP data available</div>
          ) : (
            <div className="space-y-3">
              {fmpStats.slice(0, 6).map(fmp => (
                <div key={fmp.fmp} className="space-y-1.5">
                  {/* FMP Header */}
                  <div className="flex items-center justify-between">
                    <span className="text-h3 font-semibold text-gray-900 dark:text-gray-100">{fmp.fmp}</span>
                    <span className="text-h5 font-medium text-gray-500 dark:text-gray-400">{fmp.total} total</span>
                  </div>

                  {/* Stacked Bar Chart */}
                  <div className="relative w-full h-8 bg-gray-200 dark:bg-gray-700 rounded overflow-hidden flex">
                    {fmp.completed > 0 && (
                      <div
                        className="bg-gray-400 dark:bg-gray-600 flex items-center justify-center text-body font-medium text-white"
                        style={{ width: `${(fmp.completed / fmp.total) * 100}%` }}
                        title={`${fmp.completed} completed`}
                      >
                        {fmp.completed > 5 && fmp.completed}
                      </div>
                    )}
                    {fmp.inProgress > 0 && (
                      <div
                        className="bg-blue-500 dark:bg-blue-600 flex items-center justify-center text-body font-medium text-white"
                        style={{ width: `${(fmp.inProgress / fmp.total) * 100}%` }}
                        title={`${fmp.inProgress} in progress`}
                      >
                        {fmp.inProgress > 2 && fmp.inProgress}
                      </div>
                    )}
                    {fmp.planned > 0 && (
                      <div
                        className="bg-yellow-500 dark:bg-yellow-600 flex items-center justify-center text-body font-medium text-white"
                        style={{ width: `${(fmp.planned / fmp.total) * 100}%` }}
                        title={`${fmp.planned} planned`}
                      >
                        {fmp.planned > 2 && fmp.planned}
                      </div>
                    )}
                  </div>

                  {/* Legend */}
                  <div className="flex items-center gap-3 text-body-lg">
                    <div className="flex items-center gap-1.5">
                      <div className="w-4 h-4 bg-gray-400 dark:bg-gray-600 rounded"></div>
                      <span className="text-gray-700 dark:text-gray-300">
                        <span className="font-semibold">{fmp.completed}</span> Done
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-4 h-4 bg-blue-500 dark:bg-blue-600 rounded"></div>
                      <span className="text-gray-700 dark:text-gray-300">
                        <span className="font-semibold">{fmp.inProgress}</span> Active
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-4 h-4 bg-yellow-500 dark:bg-yellow-600 rounded"></div>
                      <span className="text-gray-700 dark:text-gray-300">
                        <span className="font-semibold">{fmp.planned}</span> Planned
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity Feed */}
        <div className="bg-white dark:bg-gray-800 rounded shadow-sm border-2 border-gray-200 dark:border-gray-700 p-2">
          <h2 className="font-heading font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2 mb-2" style={{ fontSize: '24px', lineHeight: '1', fontWeight: '600' }}>
            <Clock className="w-5 h-5 text-gray-400 dark:text-gray-500" />
            Recent Activity
          </h2>

          {loading ? (
            <div className="text-center py-3 text-body-lg text-gray-500 dark:text-gray-400">Loading...</div>
          ) : recentActivity.length === 0 ? (
            <div className="text-center py-3 text-body-lg text-gray-500 dark:text-gray-400">No recent activity</div>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={idx}
                    to={item.link}
                    className="flex items-start gap-2 p-1.5 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className={`p-2 rounded ${
                      item.type === 'action' ? 'bg-blue-100 dark:bg-blue-900/50' : 'bg-green-100 dark:bg-green-900/50'
                    }`}>
                      <Icon className={`w-6 h-6 ${
                        item.type === 'action' ? 'text-blue-600 dark:text-blue-400' : 'text-green-600 dark:text-green-400'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-h5 font-medium text-gray-900 dark:text-gray-100 truncate">
                        {item.title}
                      </p>
                      <p className="text-body-lg text-gray-500 dark:text-gray-400 truncate">{item.subtitle}</p>
                    </div>
                    <ChevronRight className="w-6 h-6 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-1.5 border-t-2 border-gray-200 dark:border-gray-700 pt-2">
        <Link
          to="/stocks"
          className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded shadow-sm border-2 border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
        >
          <Fish className="w-7 h-7 text-cyan-500 flex-shrink-0" />
          <div>
            <p className="text-h5 font-medium text-gray-900 dark:text-gray-100">Species & Stock Status</p>
            <p className="text-body text-gray-500 dark:text-gray-400">View species and assessments</p>
          </div>
        </Link>

        <Link
          to="/compare"
          className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded shadow-sm border-2 border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
        >
          <TrendingUp className="w-7 h-7 text-purple-500 flex-shrink-0" />
          <div>
            <p className="text-h5 font-medium text-gray-900 dark:text-gray-100">Compare Actions</p>
            <p className="text-body text-gray-500 dark:text-gray-400">Side-by-side analysis</p>
          </div>
        </Link>

        <Link
          to="/workplan"
          className="flex items-center gap-3 p-3 bg-white dark:bg-gray-800 rounded shadow-sm border-2 border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
        >
          <FileText className="w-7 h-7 text-orange-500 flex-shrink-0" />
          <div>
            <p className="text-h5 font-medium text-gray-900 dark:text-gray-100">Workplan</p>
            <p className="text-body text-gray-500 dark:text-gray-400">Amendment schedule</p>
          </div>
        </Link>
      </div>
      </div>
    </div>
  );
};

export default DashboardEnhanced;
