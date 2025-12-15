import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { Calendar, MapPin, RefreshCw } from 'lucide-react';

const Meetings = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

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

  const syncMeetings = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/meetings`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchMeetings();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing meetings:', error);
      alert('Error syncing meetings');
    } finally {
      setSyncing(false);
    }
  };

  const getTypeColor = (type) => {
    if (!type) return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';

    const typeLower = type.toLowerCase();
    if (typeLower.includes('council')) return 'bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100';
    if (typeLower.includes('committee')) return 'bg-green-100 text-green-900 dark:bg-green-900 dark:text-green-100';
    if (typeLower.includes('workshop')) return 'bg-purple-100 text-purple-900 dark:bg-purple-900 dark:text-purple-100';
    if (typeLower.includes('webinar')) return 'bg-yellow-100 text-yellow-900 dark:bg-yellow-900 dark:text-yellow-100';
    return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  };

  return (
    <div>
      {/* Description and Action Buttons Row */}
      <div className="page-description-container">
        <p className="page-description-text">
          Schedule of Council meetings, committee sessions, and public hearings.
        </p>
        <div className="page-description-actions">
          <button
            onClick={syncMeetings}
            disabled={syncing}
            className="inline-flex items-center gap-1.5 px-2.5 h-9 justify-center rounded-md border border-transparent bg-brand-blue text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync'}
          </button>
        </div>
      </div>

      {/* Meetings List */}
      <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-4 py-3 sm:px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th scope="col" className="px-4 py-3 sm:px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Council
              </th>
              <th scope="col" className="px-4 py-3 sm:px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th scope="col" className="px-4 py-3 sm:px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th scope="col" className="px-4 py-3 sm:px-6 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-3 py-8 text-center text-sm text-gray-500">
                  Loading meetings...
                </td>
              </tr>
            ) : meetings.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-3 py-8 text-center text-sm text-gray-500">
                  No meetings found
                </td>
              </tr>
            ) : (
              meetings.map((meeting, index) => (
                <tr key={meeting.id || index} className="hover:bg-gray-50">
                  <td className="px-4 py-3 sm:px-6">
                    {meeting.source_url ? (
                      <a
                        href={meeting.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-brand-blue hover:text-brand-green hover:underline"
                      >
                        {meeting.title}
                      </a>
                    ) : (
                      <div className="text-sm font-medium text-gray-900">{meeting.title}</div>
                    )}
                    {meeting.description && (
                      <div className="text-sm text-gray-500 mt-0.5">{meeting.description.substring(0, 100)}...</div>
                    )}
                  </td>
                  <td className="px-4 py-3 sm:px-6 whitespace-nowrap">
                    <div className="text-sm font-semibold text-brand-blue">{meeting.council || 'SAFMC'}</div>
                    {meeting.organization_type && (
                      <div className="text-sm text-gray-500">{meeting.organization_type}</div>
                    )}
                  </td>
                  <td className="px-4 py-3 sm:px-6 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <div>
                        <div className="text-sm text-gray-900">
                          {meeting.start_date ? new Date(meeting.start_date).toLocaleDateString() : 'TBD'}
                        </div>
                        {meeting.end_date && meeting.end_date !== meeting.start_date && (
                          <div className="text-sm text-gray-500">
                            to {new Date(meeting.end_date).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 sm:px-6">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <div className="text-sm text-gray-900">{meeting.location || 'TBD'}</div>
                    </div>
                  </td>
                  <td className="px-4 py-3 sm:px-6 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${getTypeColor(meeting.type)}`}>
                      {meeting.type || 'Meeting'}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default Meetings;
