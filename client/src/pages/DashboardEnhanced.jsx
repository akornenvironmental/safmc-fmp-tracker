import { useState, useEffect, useMemo } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import {
  RefreshCw, FileText, Calendar, MessageSquare, Fish,
  TrendingUp, Clock, AlertCircle, ChevronRight, BarChart3
} from 'lucide-react';

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
      const response = await fetch(`${API_BASE_URL}/api/scrape/all`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert('Scraping started! Data will be updated shortly.');
        setTimeout(() => fetchDashboardData(), 3000);
      }
    } catch (error) {
      console.error('Error triggering scrape:', error);
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
        fmpMap[action.fmp] = { total: 0, completed: 0, inProgress: 0, pending: 0 };
      }
      fmpMap[action.fmp].total++;

      const progress = action.progress || 0;
      if (progress >= 100) fmpMap[action.fmp].completed++;
      else if (progress > 0) fmpMap[action.fmp].inProgress++;
      else fmpMap[action.fmp].pending++;
    });

    return Object.entries(fmpMap)
      .map(([fmp, stats]) => ({
        fmp,
        ...stats,
        completionRate: stats.total > 0 ? Math.round((stats.completed / stats.total) * 100) : 0
      }))
      .sort((a, b) => b.total - a.total);
  }, [actions]);

  // Get recent activity
  const recentActivity = useMemo(() => {
    const activity = [];

    // Add recent actions
    actions.slice(0, 5).forEach(action => {
      activity.push({
        type: 'action',
        title: action.title,
        subtitle: action.fmp,
        date: action.last_updated,
        link: `/actions`,
        icon: FileText
      });
    });

    // Add upcoming meetings
    meetings.slice(0, 3).forEach(meeting => {
      activity.push({
        type: 'meeting',
        title: meeting.title,
        subtitle: meeting.location,
        date: meeting.start_date,
        link: `/meetings`,
        icon: Calendar
      });
    });

    return activity.sort((a, b) => {
      if (!a.date) return 1;
      if (!b.date) return -1;
      return new Date(b.date) - new Date(a.date);
    }).slice(0, 8);
  }, [actions, meetings]);

  // Get stage colors
  const getStageColor = (stage) => {
    if (!stage) return 'bg-gray-100 text-gray-700';
    const s = stage.toLowerCase();
    if (s.includes('scoping')) return 'bg-yellow-100 text-yellow-800';
    if (s.includes('hearing')) return 'bg-blue-100 text-blue-800';
    if (s.includes('approval')) return 'bg-green-100 text-green-800';
    if (s.includes('implementation')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="font-heading text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-sm text-gray-600">
            SAFMC FMP Tracker Overview
          </p>
        </div>
        <button
          onClick={triggerScrape}
          disabled={scraping}
          className="inline-flex items-center gap-2 px-4 py-2 bg-brand-blue text-white rounded-md text-sm font-medium hover:bg-brand-blue-light disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${scraping ? 'animate-spin' : ''}`} />
          {scraping ? 'Updating...' : 'Update Data'}
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Link to="/actions" className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Total Actions</p>
              <p className="text-3xl font-bold text-brand-blue">{loading ? '-' : stats.totalActions}</p>
            </div>
            <FileText className="w-10 h-10 text-blue-200" />
          </div>
        </Link>

        <Link to="/meetings" className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Upcoming Meetings</p>
              <p className="text-3xl font-bold text-green-600">{loading ? '-' : stats.upcomingMeetings}</p>
            </div>
            <Calendar className="w-10 h-10 text-green-200" />
          </div>
        </Link>

        <Link to="/comments" className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Recent Comments</p>
              <p className="text-3xl font-bold text-purple-600">{loading ? '-' : stats.recentComments}</p>
            </div>
            <MessageSquare className="w-10 h-10 text-purple-200" />
          </div>
        </Link>

        <Link to="/species" className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-500">Species Tracked</p>
              <p className="text-3xl font-bold text-cyan-600">{loading ? '-' : (speciesStats?.totalSpecies || 0)}</p>
            </div>
            <Fish className="w-10 h-10 text-cyan-200" />
          </div>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* FMP Progress */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-gray-400" />
              Progress by FMP
            </h2>
            <Link to="/actions" className="text-sm text-brand-blue hover:underline">
              View all
            </Link>
          </div>

          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : fmpStats.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No FMP data available</div>
          ) : (
            <div className="space-y-4">
              {fmpStats.slice(0, 6).map(fmp => (
                <div key={fmp.fmp}>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm font-medium text-gray-900">{fmp.fmp}</span>
                    <span className="text-xs text-gray-500">
                      {fmp.completed}/{fmp.total} completed
                    </span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-2.5">
                    <div className="flex h-2.5 rounded-full overflow-hidden">
                      <div
                        className="bg-green-500"
                        style={{ width: `${(fmp.completed / fmp.total) * 100}%` }}
                      ></div>
                      <div
                        className="bg-blue-500"
                        style={{ width: `${(fmp.inProgress / fmp.total) * 100}%` }}
                      ></div>
                      <div
                        className="bg-gray-300"
                        style={{ width: `${(fmp.pending / fmp.total) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="flex gap-4 mt-1 text-xs text-gray-500">
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                      {fmp.completed} done
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
                      {fmp.inProgress} active
                    </span>
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-gray-300 rounded-full"></span>
                      {fmp.pending} pending
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Activity Feed */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <Clock className="w-5 h-5 text-gray-400" />
            Recent Activity
          </h2>

          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading...</div>
          ) : recentActivity.length === 0 ? (
            <div className="text-center py-8 text-gray-500">No recent activity</div>
          ) : (
            <div className="space-y-3">
              {recentActivity.map((item, idx) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={idx}
                    to={item.link}
                    className="flex items-start gap-3 p-2 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className={`p-2 rounded-lg ${
                      item.type === 'action' ? 'bg-blue-100' : 'bg-green-100'
                    }`}>
                      <Icon className={`w-4 h-4 ${
                        item.type === 'action' ? 'text-blue-600' : 'text-green-600'
                      }`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {item.title}
                      </p>
                      <p className="text-xs text-gray-500 truncate">{item.subtitle}</p>
                      {item.date && (
                        <p className="text-xs text-gray-400 mt-0.5">
                          {new Date(item.date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  </Link>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Link
          to="/species"
          className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <Fish className="w-8 h-8 text-cyan-500" />
          <div>
            <p className="font-medium text-gray-900">Species Profiles</p>
            <p className="text-xs text-gray-500">View species data</p>
          </div>
        </Link>

        <Link
          to="/compare"
          className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <TrendingUp className="w-8 h-8 text-purple-500" />
          <div>
            <p className="font-medium text-gray-900">Compare Actions</p>
            <p className="text-xs text-gray-500">Side-by-side analysis</p>
          </div>
        </Link>

        <Link
          to="/workplan"
          className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <FileText className="w-8 h-8 text-orange-500" />
          <div>
            <p className="font-medium text-gray-900">Workplan</p>
            <p className="text-xs text-gray-500">Amendment schedule</p>
          </div>
        </Link>

        <Link
          to="/assessments"
          className="flex items-center gap-3 p-4 bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
        >
          <AlertCircle className="w-8 h-8 text-red-500" />
          <div>
            <p className="font-medium text-gray-900">Stock Status</p>
            <p className="text-xs text-gray-500">SEDAR assessments</p>
          </div>
        </Link>
      </div>

      {/* Top Species */}
      {speciesStats && speciesStats.topSpecies && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Fish className="w-5 h-5 text-gray-400" />
              Most Active Species
            </h2>
            <Link to="/species" className="text-sm text-brand-blue hover:underline">
              View all
            </Link>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {speciesStats.topSpecies.slice(0, 5).map((sp, idx) => (
              <Link
                key={idx}
                to={`/species/${sp.name.toLowerCase().replace(/\s+/g, '-')}`}
                className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-center"
              >
                <p className="font-medium text-gray-900">{sp.name}</p>
                <p className="text-sm text-gray-500">{sp.actionCount} actions</p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DashboardEnhanced;
