/**
 * SSC Meetings Page
 * Displays SSC meetings with calendar view, agendas, briefing books, and reports
 */

import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../../config';
import Breadcrumb from '../../components/Breadcrumb';
import {
  Calendar,
  MapPin,
  FileText,
  BookOpen,
  Download,
  Video,
  Clock,
  Filter,
  ChevronDown,
  AlertCircle,
  ExternalLink,
  Users,
  ArrowUpDown
} from 'lucide-react';

const SSCMeetings = () => {
  const [meetings, setMeetings] = useState([]);
  const [filteredMeetings, setFilteredMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [statusFilter, setStatusFilter] = useState('all');
  const [yearFilter, setYearFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [sortOrder, setSortOrder] = useState('desc'); // desc = newest first

  // Fetch SSC meetings
  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('authToken');
      const response = await fetch(`${API_BASE_URL}/api/ssc/meetings?per_page=100`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to fetch SSC meetings');
      }

      setMeetings(data.meetings || []);
      setFilteredMeetings(data.meetings || []);
    } catch (err) {
      console.error('Error fetching SSC meetings:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Apply filters
  useEffect(() => {
    let filtered = [...meetings];

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(meeting => meeting.status === statusFilter);
    }

    // Year filter
    if (yearFilter !== 'all') {
      filtered = filtered.filter(meeting => {
        const year = new Date(meeting.meeting_date_start).getFullYear();
        return year === parseInt(yearFilter);
      });
    }

    // Sort by date
    filtered.sort((a, b) => {
      const dateA = new Date(a.meeting_date_start);
      const dateB = new Date(b.meeting_date_start);
      return sortOrder === 'desc' ? dateB - dateA : dateA - dateB;
    });

    setFilteredMeetings(filtered);
  }, [statusFilter, yearFilter, sortOrder, meetings]);

  // Get unique years
  const years = [...new Set(meetings.map(m => new Date(m.meeting_date_start).getFullYear()))]
    .filter(Boolean)
    .sort((a, b) => b - a);

  // Format date range
  const formatDateRange = (start, end) => {
    const startDate = new Date(start);
    const endDate = end ? new Date(end) : null;

    const options = { month: 'short', day: 'numeric', year: 'numeric' };
    const startStr = startDate.toLocaleDateString('en-US', options);

    if (!endDate || startDate.toDateString() === endDate.toDateString()) {
      return startStr;
    }

    const endStr = endDate.toLocaleDateString('en-US', options);
    return `${startStr} - ${endStr}`;
  };

  // Get status badge
  const getStatusBadge = (status) => {
    const badges = {
      'scheduled': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      'completed': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      'in-progress': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
    };
    return badges[status] || 'bg-gray-100 text-gray-800';
  };

  // Check if meeting is upcoming
  const isUpcoming = (dateStart) => {
    return new Date(dateStart) > new Date();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading SSC meetings...</p>
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
          <Calendar className="w-8 h-8 text-brand-blue" />
          <div>
            <h1 className="font-heading text-3xl font-bold text-gray-900 dark:text-white">
              SSC Meetings
            </h1>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
              Scientific and Statistical Committee Meeting Schedule
            </p>
          </div>
        </div>
        <p className="text-gray-700 dark:text-gray-300">
          The SSC generally meets twice a year to review stock assessments and provide scientific advice to the Council.
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="mb-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 px-4 py-3 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error loading SSC meetings</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Filters Bar */}
      <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Filters & Sorting
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
                <option value="scheduled">Scheduled</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            {/* Year Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Year
              </label>
              <select
                value={yearFilter}
                onChange={(e) => setYearFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-brand-blue focus:border-brand-blue bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">All Years</option>
                {years.map(year => (
                  <option key={year} value={year}>{year}</option>
                ))}
              </select>
            </div>

            {/* Sort Order */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Sort Order
              </label>
              <button
                onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 bg-white dark:bg-gray-700 text-gray-900 dark:text-white flex items-center justify-between"
              >
                <span>{sortOrder === 'desc' ? 'Newest First' : 'Oldest First'}</span>
                <ArrowUpDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Results Count */}
        <div className="mt-3 text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredMeetings.length} of {meetings.length} meetings
        </div>
      </div>

      {/* Meetings List */}
      <div className="space-y-4">
        {filteredMeetings.map((meeting) => (
          <div
            key={meeting.id}
            className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm hover:shadow-md transition-shadow border ${
              isUpcoming(meeting.meeting_date_start)
                ? 'border-brand-blue border-2'
                : 'border-gray-200 dark:border-gray-700'
            }`}
          >
            {/* Meeting Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {meeting.title}
                    </h3>
                    {isUpcoming(meeting.meeting_date_start) && (
                      <span className="px-2 py-1 rounded-full text-xs font-semibold bg-brand-blue text-white">
                        Upcoming
                      </span>
                    )}
                  </div>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
                    <div className="flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      {formatDateRange(meeting.meeting_date_start, meeting.meeting_date_end)}
                    </div>
                    {meeting.location && (
                      <div className="flex items-center gap-1">
                        <MapPin className="w-4 h-4" />
                        {meeting.location}
                      </div>
                    )}
                    {meeting.is_virtual && (
                      <div className="flex items-center gap-1 text-brand-blue">
                        <Video className="w-4 h-4" />
                        Virtual
                      </div>
                    )}
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(meeting.status)}`}>
                  {meeting.status}
                </span>
              </div>
            </div>

            {/* Meeting Body */}
            <div className="p-4">
              {/* Description */}
              {meeting.description && (
                <p className="text-gray-700 dark:text-gray-300 text-sm mb-4">
                  {meeting.description}
                </p>
              )}

              {/* Topics & Species */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                {meeting.topics && meeting.topics.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                      Topics
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {meeting.topics.map((topic, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 rounded-md text-xs bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {meeting.species_discussed && meeting.species_discussed.length > 0 && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-2">
                      Species Discussed
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {meeting.species_discussed.map((species, idx) => (
                        <span
                          key={idx}
                          className="px-2 py-1 rounded-md text-xs bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300"
                        >
                          {species}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Meeting Materials */}
              <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase mb-3">
                  Meeting Materials
                </h4>
                <div className="flex flex-wrap gap-3">
                  {meeting.agenda_url && (
                    <a
                      href={meeting.agenda_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/30 transition-colors text-sm font-medium"
                    >
                      <FileText className="w-4 h-4" />
                      Agenda
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {meeting.briefing_book_url && (
                    <a
                      href={meeting.briefing_book_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-purple-50 text-purple-700 hover:bg-purple-100 dark:bg-purple-900/20 dark:text-purple-300 dark:hover:bg-purple-900/30 transition-colors text-sm font-medium"
                    >
                      <BookOpen className="w-4 h-4" />
                      Briefing Book
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {meeting.report_url && (
                    <a
                      href={meeting.report_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-green-50 text-green-700 hover:bg-green-100 dark:bg-green-900/20 dark:text-green-300 dark:hover:bg-green-900/30 transition-colors text-sm font-medium"
                    >
                      <Download className="w-4 h-4" />
                      Final Report
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                  {meeting.webinar_link && (
                    <a
                      href={meeting.webinar_link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 rounded-md bg-red-50 text-red-700 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-300 dark:hover:bg-red-900/30 transition-colors text-sm font-medium"
                    >
                      <Video className="w-4 h-4" />
                      Join Webinar
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>

              {/* Attendance */}
              {meeting.attendance_count && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400">
                    <Users className="w-4 h-4" />
                    {meeting.attendance_count} members attended
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* No Results */}
      {filteredMeetings.length === 0 && !loading && (
        <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-lg">
          <Calendar className="w-16 h-16 text-gray-300 dark:text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            No meetings found
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {meetings.length === 0
              ? 'SSC meetings will appear here once they are scheduled.'
              : 'Try adjusting your filters to see more meetings.'}
          </p>
        </div>
      )}
    </div>
  );
};

export default SSCMeetings;
