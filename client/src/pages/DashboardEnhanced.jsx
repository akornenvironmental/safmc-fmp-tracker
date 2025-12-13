import { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import {
  RefreshCw, FileText, Calendar, MessageSquare, Fish,
  TrendingUp, Clock, AlertCircle, ChevronRight, BarChart3, LayoutDashboard
} from 'lucide-react';
import PageHeader from '../components/PageHeader';
import Button from '../components/Button';

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

      // Fetch all data in parallel
      const [statsRes, actionsRes, meetingsRes, speciesRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/dashboard/stats`),
        fetch(`${API_BASE_URL}/api/actions`),
        fetch(`${API_BASE_URL}/api/meetings?limit=5`),
        fetch(`${API_BASE_URL}/api/species/stats`)
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
        alert('Please log in to update data.');
        setScraping(false);
        return;
      }

      // List of all scraper endpoints to trigger
      const scrapers = [
        { endpoint: '/api/scrape/all', name: 'SAFMC Actions' },
        { endpoint: '/api/ssc/import/meetings', name: 'SSC Meetings', body: { download_documents: true } },
        { endpoint: '/api/cmod/import/workshops', name: 'CMOD Workshops' },
        { endpoint: '/api/ecosystem/import', name: 'Ecosystem Data' },
      ];

      let successCount = 0;
      let failCount = 0;

      // Run all scrapers sequentially
      for (const scraper of scrapers) {
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
          } else {
            failCount++;
            console.error(`${scraper.name} failed:`, data.error);
          }
        } catch (error) {
          failCount++;
          console.error(`${scraper.name} error:`, error);
        }

        // Wait 1 second between scrapers
        if (scrapers.indexOf(scraper) < scrapers.length - 1) {
          await new Promise(resolve => setTimeout(resolve, 1000));
        }
      }

      // Refresh dashboard data after all scrapers complete
      setTimeout(() => fetchDashboardData(), 2000);

      if (failCount === 0) {
        alert(`All data updated successfully! (${successCount} scrapers completed)`);
      } else if (successCount > 0) {
        alert(`Partial update complete. ${successCount} succeeded, ${failCount} failed. Check console for details.`);
      } else {
        alert('All scrapers failed. Please check your connection and try again.');
      }
    } catch (error) {
      console.error('Error triggering scrape:', error);
      alert('Failed to update data. Please check your connection and try again.');
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

  // Get stage colors - with dark mode support
  const getStageColor = (stage) => {
    if (!stage) return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200';
    const s = stage.toLowerCase();
    if (s.includes('scoping')) return 'bg-yellow-100 dark:bg-yellow-900/50 text-yellow-800 dark:text-yellow-200';
    if (s.includes('hearing')) return 'bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200';
    if (s.includes('approval')) return 'bg-green-100 dark:bg-green-900/50 text-green-800 dark:text-green-200';
    if (s.includes('implementation')) return 'bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200';
    return 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200';
  };

  return (
    <div>
      <PageHeader
        icon={LayoutDashboard}
        title="Dashboard"
        subtitle="Real-time overview"
        description="Monitor active amendments, upcoming meetings, and FMP progress across all fishery management plans in the South Atlantic region."
      />

      <Button
        variant="primary"
        icon={RefreshCw}
        onClick={triggerScrape}
        disabled={scraping}
        className="mb-6"
      >
        {scraping ? 'Updating...' : 'Update Data'}
      </Button>

      <div className="space-y-3">

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-2">
        <Link to="/actions" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Total Actions</p>
              <p className="text-2xl font-bold text-brand-blue dark:text-blue-400">{loading ? '-' : stats.totalActions}</p>
            </div>
            <FileText className="w-8 h-8 text-blue-200 dark:text-blue-800" />
          </div>
        </Link>

        <Link to="/meetings" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Upcoming Meetings</p>
              <p className="text-2xl font-bold text-green-600 dark:text-green-400">{loading ? '-' : stats.upcomingMeetings}</p>
            </div>
            <Calendar className="w-8 h-8 text-green-200 dark:text-green-800" />
          </div>
        </Link>

        <Link to="/comments" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Recent Comments</p>
              <p className="text-2xl font-bold text-purple-600 dark:text-purple-400">{loading ? '-' : stats.recentComments}</p>
            </div>
            <MessageSquare className="w-8 h-8 text-purple-200 dark:text-purple-800" />
          </div>
        </Link>

        <Link to="/stocks" className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-500 dark:text-gray-400">Species & Stocks</p>
              <p className="text-2xl font-bold text-cyan-600 dark:text-cyan-400">{loading ? '-' : (speciesStats?.totalSpecies || 0)}</p>
            </div>
            <Fish className="w-8 h-8 text-cyan-200 dark:text-cyan-800" />
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-3">
        {/* FMP Progress */}
        <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-gray-400 dark:text-gray-500" />
              FMP Progress Overview
            </h2>
            <Link to="/actions" className="text-sm text-brand-blue dark:text-blue-400 hover:underline">
              View all
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading...</div>
          ) : fmpStats.length === 0 ? (
            <div className="text-center py-8 text-gray-500 dark:text-gray-400">No FMP data available</div>
          ) : (
            <div className="space-y-6">
              {fmpStats.slice(0, 6).map(fmp => (
                <div key={fmp.fmp} className="space-y-2">
                  {/* FMP Header */}
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-gray-900 dark:text-gray-100">{fmp.fmp}</span>
                    <span className="text-xs text-gray-500 dark:text-gray-400">{fmp.total} total</span>
                  </div>

                  {/* Stacked Bar Chart */}
                  <div className="relative w-full h-8 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden flex">
                    {fmp.completed > 0 && (
                      <div
                        className="bg-gray-400 dark:bg-gray-600 flex items-center justify-center text-xs font-medium text-white"
                        style={{ width: `${(fmp.completed / fmp.total) * 100}%` }}
                        title={`${fmp.completed} completed`}
                      >
                        {fmp.completed > 5 && fmp.completed}
                      </div>
                    )}
                    {fmp.inProgress > 0 && (
                      <div
                        className="bg-blue-500 dark:bg-blue-600 flex items-center justify-center text-xs font-medium text-white"
                        style={{ width: `${(fmp.inProgress / fmp.total) * 100}%` }}
                        title={`${fmp.inProgress} in progress`}
                      >
                        {fmp.inProgress > 2 && fmp.inProgress}
                      </div>
                    )}
                    {fmp.planned > 0 && (
                      <div
                        className="bg-yellow-500 dark:bg-yellow-600 flex items-center justify-center text-xs font-medium text-white"
                        style={{ width: `${(fmp.planned / fmp.total) * 100}%` }}
                        title={`${fmp.planned} planned`}
                      >
                        {fmp.planned > 2 && fmp.planned}
                      </div>
                    )}
                  </div>

                  {/* Legend */}
                  <div className="flex items-center gap-4 text-xs">
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 bg-gray-400 dark:bg-gray-600 rounded"></div>
                      <span className="text-gray-700 dark:text-gray-300">
                        <span className="font-semibold">{fmp.completed}</span> Done
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 bg-blue-500 dark:bg-blue-600 rounded"></div>
                      <span className="text-gray-700 dark:text-gray-300">
                        <span className="font-semibold">{fmp.inProgress}</span> Active
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <div className="w-3 h-3 bg-yellow-500 dark:bg-yellow-600 rounded"></div>
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
        <div className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3">
          <h2 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2 mb-2 text-sm">
            <Clock className="w-4 h-4 text-gray-400 dark:text-gray-500" />
            Recent Activity
          </h2>

          {loading ? (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">Loading...</div>
          ) : recentActivity.length === 0 ? (
            <div className="text-center py-4 text-gray-500 dark:text-gray-400 text-sm">No recent activity</div>
          ) : (
            <div className="space-y-1.5">
              {recentActivity.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={idx}
                    to={item.link}
                    className="flex items-start gap-2 p-1.5 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <div className={`p-1 rounded ${
                      item.type === 'action' ? 'bg-blue-100 dark:bg-blue-900/50' : 'bg-green-100 dark:bg-green-900/50'
                    }`}>
                      <Icon className={`w-3 h-3 ${
                        item.type === 'action' ? 'text-blue-600 dark:text-blue-400' : 'text-green-600 dark:text-green-400'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-medium text-gray-900 dark:text-gray-100 truncate">
                        {item.title}
                      </p>
                      <p className="text-[10px] text-gray-500 dark:text-gray-400 truncate">{item.subtitle}</p>
                    </div>
                    <ChevronRight className="w-3 h-3 text-gray-400 dark:text-gray-500 flex-shrink-0" />
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
        <Link
          to="/stocks"
          className="flex items-center gap-2 p-2.5 bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
        >
          <Fish className="w-6 h-6 text-cyan-500" />
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Species & Stock Status</p>
            <p className="text-[10px] text-gray-500 dark:text-gray-400">View species and assessments</p>
          </div>
        </Link>

        <Link
          to="/compare"
          className="flex items-center gap-2 p-2.5 bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
        >
          <TrendingUp className="w-6 h-6 text-purple-500" />
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Compare Actions</p>
            <p className="text-[10px] text-gray-500 dark:text-gray-400">Side-by-side analysis</p>
          </div>
        </Link>

        <Link
          to="/workplan"
          className="flex items-center gap-2 p-2.5 bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow"
        >
          <FileText className="w-6 h-6 text-orange-500" />
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100">Workplan</p>
            <p className="text-[10px] text-gray-500 dark:text-gray-400">Amendment schedule</p>
          </div>
        </Link>
      </div>

      {/* Top Species */}
      {speciesStats && speciesStats.topSpecies && (
        <div className="bg-white dark:bg-gray-800 rounded shadow-sm border border-gray-200 dark:border-gray-700 p-3">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2 text-sm">
              <Fish className="w-4 h-4 text-gray-400 dark:text-gray-500" />
              Most Active Species
            </h2>
            <Link to="/stocks" className="text-xs text-brand-blue dark:text-blue-400 hover:underline">
              View all
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
            {speciesStats.topSpecies.slice(0, 5).map((sp, idx) => (
              <Link
                key={idx}
                to={`/species/${sp.name.toLowerCase().replace(/\s+/g, '-')}`}
                className="p-2 bg-gray-50 dark:bg-gray-700 rounded hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors text-center"
              >
                <p className="font-medium text-gray-900 dark:text-gray-100">{sp.name}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{sp.actionCount} actions</p>
              </Link>
            ))}
          </div>
        </div>
      )}
      </div>
    </div>
  );
};

export default DashboardEnhanced;
