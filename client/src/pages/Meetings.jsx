import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { Calendar, MapPin } from 'lucide-react';

const Meetings = () => {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);

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

  const getTypeColor = (type) => {
    if (!type) return 'bg-gray-100 text-gray-800';

    const typeLower = type.toLowerCase();
    if (typeLower.includes('council')) return 'bg-blue-100 text-blue-800';
    if (typeLower.includes('committee')) return 'bg-green-100 text-green-800';
    if (typeLower.includes('workshop')) return 'bg-purple-100 text-purple-800';
    if (typeLower.includes('webinar')) return 'bg-yellow-100 text-yellow-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Meeting Calendar</h1>
          <p className="mt-2 text-sm text-gray-700">
            {meetings.length} meetings scheduled
          </p>
        </div>
      </div>

      {/* Meetings List */}
      <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Location
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Type
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="4" className="px-6 py-12 text-center text-sm text-gray-500">
                  Loading meetings...
                </td>
              </tr>
            ) : meetings.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-12 text-center text-sm text-gray-500">
                  No meetings found
                </td>
              </tr>
            ) : (
              meetings.map((meeting, index) => (
                <tr key={meeting.id || index} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{meeting.title}</div>
                    {meeting.description && (
                      <div className="text-sm text-gray-500 mt-1">{meeting.description.substring(0, 100)}...</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-400" />
                      <div>
                        <div className="text-sm text-gray-900">
                          {meeting.start_date ? new Date(meeting.start_date).toLocaleDateString() : 'TBD'}
                        </div>
                        {meeting.end_date && meeting.end_date !== meeting.start_date && (
                          <div className="text-xs text-gray-500">
                            to {new Date(meeting.end_date).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      <div className="text-sm text-gray-900">{meeting.location || 'TBD'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getTypeColor(meeting.type)}`}>
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
