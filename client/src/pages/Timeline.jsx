import { useState, useEffect, useMemo } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import PageHeader from '../components/PageHeader';
import { API_BASE_URL } from '../config';
import {
  Calendar, Filter, Search, ChevronDown, ChevronRight,
  FileText, Users, MessageSquare, TrendingUp, Clock, ExternalLink, GitBranch
} from 'lucide-react';

const Timeline = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [actions, setActions] = useState([]);
  const [meetings, setMeetings] = useState([]);
  const [comments, setComments] = useState([]);
  const [sscMeetings, setSSCMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState(searchParams.get('search') || '');
  const [selectedFMP, setSelectedFMP] = useState(searchParams.get('fmp') || '');
  const [selectedAction, setSelectedAction] = useState(searchParams.get('action') || '');
  const [expandedActions, setExpandedActions] = useState(new Set());
  const [viewMode, setViewMode] = useState('grouped'); // 'grouped' or 'chronological'

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [actionsRes, meetingsRes, commentsRes, sscRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/actions`),
        fetch(`${API_BASE_URL}/api/meetings`),
        fetch(`${API_BASE_URL}/api/comments`),
        fetch(`${API_BASE_URL}/api/ssc/meetings`)
      ]);

      const [actionsData, meetingsData, commentsData, sscData] = await Promise.all([
        actionsRes.json(),
        meetingsRes.json(),
        commentsRes.json(),
        sscRes.json()
      ]);

      if (actionsData.success) setActions(actionsData.actions || []);
      if (meetingsData.success) setMeetings(meetingsData.meetings || []);
      if (commentsData.success) setComments(commentsData.comments || []);
      if (sscData.success) setSSCMeetings(sscData.meetings || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching timeline data:', error);
      setLoading(false);
    }
  };

  // Get unique FMPs for filter
  const uniqueFMPs = useMemo(() => {
    const fmps = new Set();
    actions.forEach(action => {
      if (action.fmp) fmps.add(action.fmp);
    });
    return Array.from(fmps).sort();
  }, [actions]);

  // Filter actions based on search and FMP
  const filteredActions = useMemo(() => {
    return actions.filter(action => {
      const matchesSearch = !searchTerm ||
        action.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        action.action_id?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        action.description?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesFMP = !selectedFMP || action.fmp === selectedFMP;

      return matchesSearch && matchesFMP;
    });
  }, [actions, searchTerm, selectedFMP]);

  // Build timeline events for each action
  const buildActionTimeline = (action) => {
    const events = [];
    const actionId = action.action_id;

    // Add action phases as events
    if (action.start_date) {
      events.push({
        type: 'action_start',
        date: action.start_date,
        title: 'Action Started',
        description: action.title,
        icon: FileText,
        color: 'blue',
        link: null
      });
    }

    // Find related meetings
    const relatedMeetings = meetings.filter(meeting =>
      meeting.title?.includes(actionId) ||
      meeting.title?.includes(action.title?.split(' ')[0]) ||
      meeting.description?.includes(actionId)
    );

    relatedMeetings.forEach(meeting => {
      if (meeting.start_date) {
        events.push({
          type: 'meeting',
          date: meeting.start_date,
          title: meeting.title || 'Council Meeting',
          description: meeting.location || 'Location TBD',
          icon: Users,
          color: 'purple',
          link: meeting.source_url
        });
      }
    });

    // Find related comments
    const relatedComments = comments.filter(comment =>
      comment.action_id === actionId
    );

    if (relatedComments.length > 0) {
      // Group comments by date
      const commentsByDate = {};
      relatedComments.forEach(comment => {
        if (comment.submit_date) {
          const date = comment.submit_date.split('T')[0];
          if (!commentsByDate[date]) commentsByDate[date] = [];
          commentsByDate[date].push(comment);
        }
      });

      Object.entries(commentsByDate).forEach(([date, dateComments]) => {
        events.push({
          type: 'comments',
          date: date,
          title: `${dateComments.length} Public Comment${dateComments.length > 1 ? 's' : ''}`,
          description: `Comments received during comment period`,
          icon: MessageSquare,
          color: 'green',
          count: dateComments.length,
          link: null
        });
      });
    }

    // Find related SSC meetings
    const relatedSSC = sscMeetings.filter(ssc =>
      ssc.title?.includes(action.fmp) ||
      ssc.topics?.some(topic => action.title?.includes(topic))
    );

    relatedSSC.forEach(ssc => {
      if (ssc.meeting_date_start) {
        events.push({
          type: 'ssc',
          date: ssc.meeting_date_start,
          title: ssc.title || 'SSC Meeting',
          description: ssc.location || 'SSC Review',
          icon: TrendingUp,
          color: 'orange',
          link: ssc.agenda_url || ssc.report_url
        });
      }
    });

    // Add completion/approval
    if (action.status?.toLowerCase().includes('approved') && action.end_date) {
      events.push({
        type: 'action_complete',
        date: action.end_date,
        title: 'Action Approved',
        description: `Status: ${action.status}`,
        icon: FileText,
        color: 'green',
        link: action.source_url
      });
    }

    // Sort events by date
    return events.sort((a, b) => new Date(a.date) - new Date(b.date));
  };

  // Build chronological timeline (all events from all actions)
  const chronologicalTimeline = useMemo(() => {
    const allEvents = [];

    filteredActions.forEach(action => {
      const events = buildActionTimeline(action);
      events.forEach(event => {
        allEvents.push({
          ...event,
          actionId: action.action_id,
          actionTitle: action.title,
          fmp: action.fmp
        });
      });
    });

    return allEvents.sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [filteredActions, meetings, comments, sscMeetings]);

  const toggleActionExpand = (actionId) => {
    const newExpanded = new Set(expandedActions);
    if (newExpanded.has(actionId)) {
      newExpanded.delete(actionId);
    } else {
      newExpanded.add(actionId);
    }
    setExpandedActions(newExpanded);
  };

  const getEventColor = (color) => {
    const colors = {
      blue: 'bg-blue-500',
      purple: 'bg-purple-500',
      green: 'bg-green-500',
      orange: 'bg-orange-500',
      red: 'bg-red-500'
    };
    return colors[color] || 'bg-gray-500';
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Date TBD';
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto"></div>
          <p className="mt-4 text-gray-500 dark:text-gray-400">Loading timeline...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* Page Header */}
      <PageHeader
        icon={GitBranch}
        title="Timeline"
        subtitle="Chronological view"
        description="Chronological view of fishery management actions and milestones."
      />

      {/* Filters and Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4">
          {/* Search */}
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Search actions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-brand-blue focus:border-transparent"
              />
            </div>
          </div>

          {/* FMP Filter */}
          <select
            value={selectedFMP}
            onChange={(e) => setSelectedFMP(e.target.value)}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-brand-blue"
          >
            <option value="">All FMPs</option>
            {uniqueFMPs.map(fmp => (
              <option key={fmp} value={fmp}>{fmp}</option>
            ))}
          </select>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 border border-gray-300 dark:border-gray-600 rounded-md">
            <button
              onClick={() => setViewMode('grouped')}
              className={`px-4 py-2 text-sm font-medium rounded-l-md transition-colors ${
                viewMode === 'grouped'
                  ? 'bg-brand-blue text-white'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              By Action
            </button>
            <button
              onClick={() => setViewMode('chronological')}
              className={`px-4 py-2 text-sm font-medium rounded-r-md transition-colors ${
                viewMode === 'chronological'
                  ? 'bg-brand-blue text-white'
                  : 'bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
              }`}
            >
              Chronological
            </button>
          </div>
        </div>
      </div>

      {/* Timeline Content */}
      {viewMode === 'grouped' ? (
        // Grouped by Action View
        <div className="space-y-4">
          {filteredActions.length === 0 ? (
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              No actions found matching your filters
            </div>
          ) : (
            filteredActions.map(action => {
              const timeline = buildActionTimeline(action);
              const isExpanded = expandedActions.has(action.action_id);

              return (
                <div
                  key={action.action_id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700"
                >
                  {/* Action Header */}
                  <div
                    className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                    onClick={() => toggleActionExpand(action.action_id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
                          <div>
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {action.title || action.action_id}
                            </h3>
                            <div className="flex items-center gap-3 mt-1">
                              <span className="text-xs px-2 py-1 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 rounded">
                                {action.action_id}
                              </span>
                              {action.fmp && (
                                <span className="text-xs px-2 py-1 bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200 rounded">
                                  {action.fmp}
                                </span>
                              )}
                              <span className="text-xs text-gray-500 dark:text-gray-400">
                                {timeline.length} event{timeline.length !== 1 ? 's' : ''}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        {action.start_date && (
                          <div className="text-sm text-gray-600 dark:text-gray-400">
                            {formatDate(action.start_date)}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Timeline Events */}
                  {isExpanded && (
                    <div className="border-t border-gray-200 dark:border-gray-700 p-6">
                      <div className="relative">
                        {/* Timeline line */}
                        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

                        {/* Events */}
                        <div className="space-y-6">
                          {timeline.map((event, idx) => {
                            const Icon = event.icon;
                            return (
                              <div key={idx} className="relative pl-14">
                                {/* Timeline dot */}
                                <div className={`absolute left-4 w-5 h-5 rounded-full ${getEventColor(event.color)} flex items-center justify-center`}>
                                  <Icon size={12} className="text-white" />
                                </div>

                                {/* Event content */}
                                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                                  <div className="flex items-start justify-between gap-4">
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2">
                                        <h4 className="font-medium text-gray-900 dark:text-white">
                                          {event.title}
                                        </h4>
                                        {event.link && (
                                          <a
                                            href={event.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-brand-blue hover:text-blue-700"
                                          >
                                            <ExternalLink size={14} />
                                          </a>
                                        )}
                                      </div>
                                      <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                        {event.description}
                                      </p>
                                      {event.count && (
                                        <div className="mt-2 text-xs text-gray-500 dark:text-gray-500">
                                          {event.count} items
                                        </div>
                                      )}
                                    </div>
                                    <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                                      <Clock size={14} />
                                      {formatDate(event.date)}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      ) : (
        // Chronological View
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200 dark:bg-gray-700"></div>

            {/* Events */}
            <div className="space-y-6">
              {chronologicalTimeline.length === 0 ? (
                <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                  No events found matching your filters
                </div>
              ) : (
                chronologicalTimeline.map((event, idx) => {
                  const Icon = event.icon;
                  return (
                    <div key={idx} className="relative pl-14">
                      {/* Timeline dot */}
                      <div className={`absolute left-4 w-5 h-5 rounded-full ${getEventColor(event.color)} flex items-center justify-center`}>
                        <Icon size={12} className="text-white" />
                      </div>

                      {/* Event content */}
                      <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-xs px-2 py-0.5 bg-blue-100 dark:bg-blue-900/50 text-blue-800 dark:text-blue-200 rounded">
                                {event.actionId}
                              </span>
                              {event.fmp && (
                                <span className="text-xs px-2 py-0.5 bg-purple-100 dark:bg-purple-900/50 text-purple-800 dark:text-purple-200 rounded">
                                  {event.fmp}
                                </span>
                              )}
                            </div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium text-gray-900 dark:text-white">
                                {event.title}
                              </h4>
                              {event.link && (
                                <a
                                  href={event.link}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-brand-blue hover:text-blue-700"
                                >
                                  <ExternalLink size={14} />
                                </a>
                              )}
                            </div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {event.description}
                            </p>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                              {event.actionTitle}
                            </p>
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                            <Clock size={14} />
                            {formatDate(event.date)}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Timeline;
