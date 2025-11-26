import { useState, useEffect } from 'react';
import { MessageSquare, Filter, CheckCircle, Clock, Archive, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../config';
import { useAuth } from '../contexts/AuthContext';

const FeedbackManagement = () => {
  const { user } = useAuth();
  const [feedback, setFeedback] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [updating, setUpdating] = useState(false);

  useEffect(() => {
    fetchFeedback();
    fetchStats();
  }, [statusFilter]);

  const fetchFeedback = async () => {
    try {
      const token = localStorage.getItem('token');
      const url = statusFilter === 'all'
        ? `${API_BASE_URL}/api/feedback/all`
        : `${API_BASE_URL}/api/feedback/all?status=${statusFilter}`;

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();
      if (response.ok) {
        setFeedback(data.feedback);
      } else {
        console.error('Failed to fetch feedback:', data.error);
      }
    } catch (error) {
      console.error('Error fetching feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/feedback/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const data = await response.json();
      if (response.ok) {
        setStats(data.stats);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const updateFeedbackStatus = async (feedbackId, newStatus, adminNotes) => {
    setUpdating(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/feedback/${feedbackId}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status: newStatus,
          admin_notes: adminNotes,
        }),
      });

      const data = await response.json();
      if (response.ok) {
        // Refresh feedback list
        await fetchFeedback();
        await fetchStats();
        setSelectedFeedback(null);
      } else {
        alert(`Failed to update feedback: ${data.error}`);
      }
    } catch (error) {
      console.error('Error updating feedback:', error);
      alert(`Error updating feedback: ${error.message}`);
    } finally {
      setUpdating(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'new':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'in_review':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'resolved':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'archived':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'new':
        return <AlertCircle size={16} />;
      case 'in_review':
        return <Clock size={16} />;
      case 'resolved':
        return <CheckCircle size={16} />;
      case 'archived':
        return <Archive size={16} />;
      default:
        return null;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  if (!user || (user.role !== 'admin' && user.role !== 'super_admin')) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Access Denied</h2>
          <p className="text-gray-600 dark:text-gray-400">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-2 mb-2">
            <MessageSquare size={32} className="text-brand-blue" />
            Feedback Management
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            Review and manage user feedback submissions
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Total Feedback</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">Last 7 Days</div>
              <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.recent}</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">New</div>
              <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.by_status?.new || 0}</div>
            </div>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
              <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">In Review</div>
              <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.by_status?.in_review || 0}</div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4 mb-6">
          <div className="flex items-center gap-2 mb-3">
            <Filter size={20} className="text-gray-600 dark:text-gray-400" />
            <span className="font-medium text-gray-900 dark:text-white">Filter by Status</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {['all', 'new', 'in_review', 'resolved', 'archived'].map((status) => (
              <button
                key={status}
                onClick={() => setStatusFilter(status)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  statusFilter === status
                    ? 'bg-brand-blue text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {/* Feedback List */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
          {loading ? (
            <div className="p-8 text-center text-gray-600 dark:text-gray-400">Loading feedback...</div>
          ) : feedback.length === 0 ? (
            <div className="p-8 text-center text-gray-600 dark:text-gray-400">
              No feedback found for the selected filter.
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {feedback.map((item) => (
                <div
                  key={item.id}
                  className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors"
                  onClick={() => setSelectedFeedback(item)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(item.status)}`}>
                          {getStatusIcon(item.status)}
                          {item.status.replace('_', ' ')}
                        </span>
                        <span className="text-sm text-gray-600 dark:text-gray-400">{item.component}</span>
                      </div>
                      <p className="text-gray-900 dark:text-white line-clamp-2 mb-2">{item.feedback}</p>
                      <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>{item.user_name} ({item.user_email})</span>
                        <span>{formatDate(item.created_at)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Feedback Detail Modal */}
      {selectedFeedback && (
        <div
          className="fixed inset-0 bg-gray-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedFeedback(null)}
        >
          <div
            className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 z-10">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Feedback Details</h3>
                <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${getStatusColor(selectedFeedback.status)}`}>
                  {getStatusIcon(selectedFeedback.status)}
                  {selectedFeedback.status.replace('_', ' ')}
                </span>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-4 space-y-4">
              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">User</label>
                <p className="text-gray-900 dark:text-white">{selectedFeedback.user_name} ({selectedFeedback.user_email})</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Component</label>
                <p className="text-gray-900 dark:text-white">{selectedFeedback.component}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">URL</label>
                <a href={selectedFeedback.url} target="_blank" rel="noopener noreferrer" className="text-brand-blue hover:underline text-sm break-all">
                  {selectedFeedback.url}
                </a>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Feedback</label>
                <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{selectedFeedback.feedback}</p>
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Submitted</label>
                <p className="text-gray-900 dark:text-white">{formatDate(selectedFeedback.created_at)}</p>
              </div>

              {selectedFeedback.reviewed_at && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Reviewed</label>
                  <p className="text-gray-900 dark:text-white">
                    {formatDate(selectedFeedback.reviewed_at)} by {selectedFeedback.reviewed_by}
                  </p>
                </div>
              )}

              {selectedFeedback.admin_notes && (
                <div>
                  <label className="text-sm font-medium text-gray-700 dark:text-gray-300">Admin Notes</label>
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap">{selectedFeedback.admin_notes}</p>
                </div>
              )}

              <div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-2">Update Status</label>
                <div className="space-y-3">
                  <select
                    id="status-select"
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white"
                    defaultValue={selectedFeedback.status}
                  >
                    <option value="new">New</option>
                    <option value="in_review">In Review</option>
                    <option value="resolved">Resolved</option>
                    <option value="archived">Archived</option>
                  </select>

                  <textarea
                    id="admin-notes"
                    placeholder="Add admin notes (optional)..."
                    defaultValue={selectedFeedback.admin_notes || ''}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white placeholder-gray-500 dark:placeholder-gray-300"
                  />

                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        const newStatus = document.getElementById('status-select').value;
                        const adminNotes = document.getElementById('admin-notes').value;
                        updateFeedbackStatus(selectedFeedback.id, newStatus, adminNotes);
                      }}
                      disabled={updating}
                      className="flex-1 px-4 py-2 bg-brand-blue hover:bg-blue-700 text-white rounded-lg font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      {updating ? 'Updating...' : 'Update'}
                    </button>
                    <button
                      onClick={() => setSelectedFeedback(null)}
                      className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 rounded-lg font-medium transition-colors"
                    >
                      Close
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackManagement;
