import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { User, Building2, RefreshCw } from 'lucide-react';

const Comments = () => {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterPosition, setFilterPosition] = useState('all');
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchComments();
  }, []);

  const fetchComments = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/comments`);
      const data = await response.json();

      if (data.success) {
        setComments(data.comments || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching comments:', error);
      setLoading(false);
    }
  };

  const syncComments = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/comments`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchComments();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing comments:', error);
      alert('Error syncing comments');
    } finally {
      setSyncing(false);
    }
  };

  const filteredComments = comments.filter(comment => {
    if (filterPosition === 'all') return true;
    return comment.position && comment.position.toLowerCase() === filterPosition.toLowerCase();
  });

  const getPositionColor = (position) => {
    if (!position) return 'bg-gray-100 text-gray-800';

    const positionLower = position.toLowerCase();
    if (positionLower.includes('support')) return 'bg-green-100 text-green-800';
    if (positionLower.includes('oppose')) return 'bg-red-100 text-red-800';
    if (positionLower.includes('neutral')) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Public Comments</h1>
          <p className="mt-2 text-sm text-gray-700">
            {comments.length} comments total • {filteredComments.length} displayed
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={syncComments}
            disabled={syncing}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Comments'}
          </button>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="mt-6">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterPosition('all')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'all'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            All ({comments.length})
          </button>
          <button
            onClick={() => setFilterPosition('support')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'support'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Support ({comments.filter(c => c.position?.toLowerCase().includes('support')).length})
          </button>
          <button
            onClick={() => setFilterPosition('oppose')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'oppose'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Oppose ({comments.filter(c => c.position?.toLowerCase().includes('oppose')).length})
          </button>
          <button
            onClick={() => setFilterPosition('neutral')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterPosition === 'neutral'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Neutral ({comments.filter(c => c.position?.toLowerCase().includes('neutral')).length})
          </button>
        </div>
      </div>

      {/* Comments List */}
      <div className="mt-6 space-y-4">
        {loading ? (
          <div className="bg-white shadow sm:rounded-lg p-12 text-center text-sm text-gray-500">
            Loading comments...
          </div>
        ) : filteredComments.length === 0 ? (
          <div className="bg-white shadow sm:rounded-lg p-12 text-center text-sm text-gray-500">
            No comments found
          </div>
        ) : (
          filteredComments.map((comment, index) => (
            <div key={comment.id || index} className="bg-white shadow sm:rounded-lg p-6 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-4 mb-2">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-gray-400" />
                      <h3 className="text-lg font-medium text-gray-900">
                        {comment.name || 'Anonymous'}
                      </h3>
                    </div>
                    {comment.state && (
                      <span className="text-sm text-gray-500">• {comment.state}</span>
                    )}
                  </div>
                  {comment.organization && (
                    <div className="flex items-center gap-2 mb-3">
                      <Building2 className="w-4 h-4 text-gray-400" />
                      <p className="text-sm text-gray-600">{comment.organization}</p>
                    </div>
                  )}
                  <p className="text-sm text-gray-900 mb-3">{comment.comment_text}</p>
                  {comment.submitted_date && (
                    <p className="text-xs text-gray-500">
                      Submitted: {new Date(comment.submitted_date).toLocaleDateString()}
                    </p>
                  )}
                </div>
                <div className="ml-4">
                  <span className={`inline-flex px-3 py-1 text-xs font-semibold rounded-full ${getPositionColor(comment.position)}`}>
                    {comment.position || 'No Position'}
                  </span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Showing {filteredComments.length} of {comments.length} comments
      </div>
    </div>
  );
};

export default Comments;
