import { useState, useEffect, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { API_BASE_URL } from '../config';
import {
  Calendar as CalendarIcon, ChevronLeft, ChevronRight,
  List, Grid, MapPin, Clock, ExternalLink
} from 'lucide-react';

const MeetingCalendar = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState('calendar'); // 'calendar' or 'list'
  const [selectedDate, setSelectedDate] = useState(null);

  useEffect(() => {
    fetchMeetings();
  }, []);

  const fetchMeetings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/meetings`);
      const data = await response.json();
      if (data.success) {
        setMeetings(data.meetings || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching meetings:', error);
      setLoading(false);
    }
  };

  // Get calendar days for current month
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // First day of month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    // Days from previous month to fill first week
    const startPadding = firstDay.getDay();
    const days = [];

    // Previous month padding
    for (let i = startPadding - 1; i >= 0; i--) {
      const date = new Date(year, month, -i);
      days.push({ date, isCurrentMonth: false });
    }

    // Current month days
    for (let i = 1; i <= lastDay.getDate(); i++) {
      const date = new Date(year, month, i);
      days.push({ date, isCurrentMonth: true });
    }

    // Next month padding to complete grid
    const remaining = 42 - days.length; // 6 rows * 7 days
    for (let i = 1; i <= remaining; i++) {
      const date = new Date(year, month + 1, i);
      days.push({ date, isCurrentMonth: false });
    }

    return days;
  }, [currentDate]);

  // Group meetings by date
  const meetingsByDate = useMemo(() => {
    const map = {};
    meetings.forEach(meeting => {
      if (!meeting.start_date) return;
      const dateKey = meeting.start_date.split('T')[0];
      if (!map[dateKey]) map[dateKey] = [];
      map[dateKey].push(meeting);
    });
    return map;
  }, [meetings]);

  // Get meetings for selected date
  const selectedDateMeetings = useMemo(() => {
    if (!selectedDate) return [];
    const dateKey = selectedDate.toISOString().split('T')[0];
    return meetingsByDate[dateKey] || [];
  }, [selectedDate, meetingsByDate]);

  // Navigation
  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
    setSelectedDate(new Date());
  };

  // Format date
  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  // Get meeting type color
  const getMeetingColor = (meeting) => {
    const title = (meeting.title || '').toLowerCase();
    if (title.includes('council')) return 'bg-blue-500';
    if (title.includes('committee')) return 'bg-green-500';
    if (title.includes('public')) return 'bg-purple-500';
    if (title.includes('webinar')) return 'bg-orange-500';
    return 'bg-gray-500';
  };

  // Check if date is today
  const isToday = (date) => {
    const today = new Date();
    return date.toDateString() === today.toDateString();
  };

  // Get upcoming meetings (sorted by date)
  const upcomingMeetings = useMemo(() => {
    const now = new Date();
    return meetings
      .filter(m => m.start_date && new Date(m.start_date) >= now)
      .sort((a, b) => new Date(a.start_date) - new Date(b.start_date))
      .slice(0, 10);
  }, [meetings]);

  return (
    <div>
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="font-heading text-3xl font-bold text-gray-900 flex items-center gap-3">
            <CalendarIcon className="w-8 h-8 text-brand-blue" />
            Meeting Calendar
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            {meetings.length} meetings tracked
          </p>
        </div>
        <div className="mt-4 sm:mt-0 flex gap-2">
          <button
            onClick={() => setView('calendar')}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium ${
              view === 'calendar'
                ? 'bg-brand-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Grid size={16} /> Calendar
          </button>
          <button
            onClick={() => setView('list')}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium ${
              view === 'list'
                ? 'bg-brand-blue text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <List size={16} /> List
          </button>
        </div>
      </div>

      {view === 'calendar' ? (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Calendar */}
          <div className="lg:col-span-3 bg-white rounded-lg shadow-sm border border-gray-200">
            {/* Calendar Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200">
              <button
                onClick={prevMonth}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <ChevronLeft size={20} />
              </button>
              <div className="text-center">
                <h2 className="text-lg font-semibold text-gray-900">
                  {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
                </h2>
                <button
                  onClick={goToToday}
                  className="text-xs text-brand-blue hover:underline"
                >
                  Today
                </button>
              </div>
              <button
                onClick={nextMonth}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <ChevronRight size={20} />
              </button>
            </div>

            {/* Calendar Grid */}
            <div className="p-4">
              {/* Day headers */}
              <div className="grid grid-cols-7 gap-1 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                  <div key={day} className="text-center text-xs font-medium text-gray-500 py-2">
                    {day}
                  </div>
                ))}
              </div>

              {/* Calendar days */}
              <div className="grid grid-cols-7 gap-1">
                {calendarDays.map((day, idx) => {
                  const dateKey = day.date.toISOString().split('T')[0];
                  const dayMeetings = meetingsByDate[dateKey] || [];
                  const isSelected = selectedDate && day.date.toDateString() === selectedDate.toDateString();

                  return (
                    <div
                      key={idx}
                      onClick={() => setSelectedDate(day.date)}
                      className={`min-h-[80px] p-1 border rounded-lg cursor-pointer transition-colors ${
                        day.isCurrentMonth ? 'bg-white' : 'bg-gray-50'
                      } ${
                        isSelected ? 'ring-2 ring-brand-blue' : ''
                      } ${
                        isToday(day.date) ? 'bg-blue-50 border-blue-200' : 'border-gray-100'
                      } hover:border-gray-300`}
                    >
                      <div className={`text-sm font-medium mb-1 ${
                        day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400'
                      } ${
                        isToday(day.date) ? 'text-brand-blue' : ''
                      }`}>
                        {day.date.getDate()}
                      </div>
                      <div className="space-y-0.5">
                        {dayMeetings.slice(0, 3).map((meeting, midx) => (
                          <div
                            key={midx}
                            className={`text-[10px] text-white px-1 py-0.5 rounded truncate ${getMeetingColor(meeting)}`}
                            title={meeting.title}
                          >
                            {meeting.title}
                          </div>
                        ))}
                        {dayMeetings.length > 3 && (
                          <div className="text-[10px] text-gray-500">
                            +{dayMeetings.length - 3} more
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          {/* Selected Date Details / Upcoming */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            {selectedDate ? (
              <>
                <h3 className="font-semibold text-gray-900 mb-3">
                  {formatDate(selectedDate)}
                </h3>
                {selectedDateMeetings.length === 0 ? (
                  <p className="text-sm text-gray-500">No meetings scheduled</p>
                ) : (
                  <div className="space-y-3">
                    {selectedDateMeetings.map((meeting, idx) => (
                      <div key={idx} className="p-3 bg-gray-50 rounded-lg">
                        <h4 className="font-medium text-gray-900 text-sm">{meeting.title}</h4>
                        {meeting.location && (
                          <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                            <MapPin size={12} /> {meeting.location}
                          </p>
                        )}
                        {meeting.start_time && (
                          <p className="text-xs text-gray-500 flex items-center gap-1">
                            <Clock size={12} /> {meeting.start_time}
                          </p>
                        )}
                        {meeting.source_url && (
                          <a
                            href={meeting.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-xs text-brand-blue hover:underline flex items-center gap-1 mt-2"
                          >
                            Details <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </>
            ) : (
              <>
                <h3 className="font-semibold text-gray-900 mb-3">Upcoming Meetings</h3>
                <div className="space-y-2">
                  {upcomingMeetings.slice(0, 5).map((meeting, idx) => (
                    <div
                      key={idx}
                      className="p-2 hover:bg-gray-50 rounded cursor-pointer"
                      onClick={() => setSelectedDate(new Date(meeting.start_date))}
                    >
                      <p className="text-sm font-medium text-gray-900 truncate">{meeting.title}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(meeting.start_date).toLocaleDateString()}
                      </p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        // List View
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="divide-y divide-gray-200">
            {loading ? (
              <div className="p-8 text-center text-gray-500">Loading...</div>
            ) : upcomingMeetings.length === 0 ? (
              <div className="p-8 text-center text-gray-500">No upcoming meetings</div>
            ) : (
              upcomingMeetings.map((meeting, idx) => (
                <div key={idx} className="p-4 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900">{meeting.title}</h3>
                      <div className="mt-1 flex flex-wrap gap-3 text-sm text-gray-500">
                        <span className="flex items-center gap-1">
                          <CalendarIcon size={14} />
                          {new Date(meeting.start_date).toLocaleDateString()}
                        </span>
                        {meeting.location && (
                          <span className="flex items-center gap-1">
                            <MapPin size={14} />
                            {meeting.location}
                          </span>
                        )}
                      </div>
                    </div>
                    {meeting.source_url && (
                      <a
                        href={meeting.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-brand-blue hover:underline text-sm flex items-center gap-1"
                      >
                        View <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-4 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-blue-500 rounded"></span> Council
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-green-500 rounded"></span> Committee
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-purple-500 rounded"></span> Public
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 bg-orange-500 rounded"></span> Webinar
        </span>
      </div>
    </div>
  );
};

export default MeetingCalendar;
