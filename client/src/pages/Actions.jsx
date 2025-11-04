import { useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { RefreshCw } from 'lucide-react';

const Actions = () => {
  const [filterStage, setFilterStage] = useState('all');
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    fetchActions();
  }, []);

  const fetchActions = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/actions`);
      const data = await response.json();

      if (data.success) {
        setActions(data.actions || []);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error fetching actions:', error);
      setLoading(false);
    }
  };

  const syncActions = async () => {
    try {
      setSyncing(true);
      const response = await fetch(`${API_BASE_URL}/api/scrape/amendments`, {
        method: 'POST',
      });
      const data = await response.json();

      if (data.success) {
        alert(`Sync complete! Found ${data.itemsFound} items, ${data.itemsNew} new, ${data.itemsUpdated} updated.`);
        fetchActions();
      } else {
        alert('Failed to sync: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error syncing actions:', error);
      alert('Error syncing actions');
    } finally {
      setSyncing(false);
    }
  };

  const filteredActions = actions.filter(action => {
    if (filterStage === 'all') return true;
    return action.progress_stage && action.progress_stage.toLowerCase().includes(filterStage.toLowerCase());
  });

  const getStageColor = (stage) => {
    if (!stage) return 'bg-gray-100 text-gray-800';

    const stageLower = stage.toLowerCase();
    if (stageLower.includes('scoping')) return 'bg-yellow-100 text-yellow-800';
    if (stageLower.includes('hearing')) return 'bg-blue-100 text-blue-800';
    if (stageLower.includes('approval')) return 'bg-green-100 text-green-800';
    if (stageLower.includes('implementation')) return 'bg-purple-100 text-purple-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div>
      <div className="sm:flex sm:items-center sm:justify-between">
        <div className="sm:flex-auto">
          <h1 className="font-heading text-3xl font-bold text-gray-900">Actions & Amendments</h1>
          <p className="mt-2 text-sm text-gray-700">
            {actions.length} actions total • {filteredActions.length} displayed
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            onClick={syncActions}
            disabled={syncing}
            className="inline-flex items-center gap-2 justify-center rounded-md border border-transparent bg-brand-blue px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-brand-green focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
            {syncing ? 'Syncing...' : 'Sync Actions'}
          </button>
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="mt-6">
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterStage('all')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'all'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            All ({actions.length})
          </button>
          <button
            onClick={() => setFilterStage('scoping')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'scoping'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Scoping ({actions.filter(a => a.progress_stage?.toLowerCase().includes('scoping')).length})
          </button>
          <button
            onClick={() => setFilterStage('hearing')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'hearing'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Public Hearing ({actions.filter(a => a.progress_stage?.toLowerCase().includes('hearing')).length})
          </button>
          <button
            onClick={() => setFilterStage('approval')}
            className={`px-4 py-2 text-sm font-medium rounded-md ${
              filterStage === 'approval'
                ? 'bg-brand-blue text-white'
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            Approval ({actions.filter(a => a.progress_stage?.toLowerCase().includes('approval')).length})
          </button>
        </div>
      </div>

      {/* Actions Table */}
      <div className="mt-6 bg-white shadow overflow-hidden sm:rounded-lg">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                FMP
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progress Stage
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progress
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Last Updated
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-sm text-gray-500">
                  Loading actions...
                </td>
              </tr>
            ) : filteredActions.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-12 text-center text-sm text-gray-500">
                  No actions found
                </td>
              </tr>
            ) : (
              filteredActions.map((action, index) => (
                <tr key={action.id || index} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    {action.source_url ? (
                      <a
                        href={action.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm font-medium text-brand-blue hover:text-brand-green hover:underline"
                      >
                        {action.title}
                      </a>
                    ) : (
                      <div className="text-sm font-medium text-gray-900">{action.title}</div>
                    )}
                    {action.description && (
                      <div className="text-sm text-gray-500 mt-1">{action.description.substring(0, 100)}...</div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{action.fmp || 'N/A'}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(action.progress_stage)}`}>
                      {action.progress_stage || 'Unknown'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-brand-blue h-2 rounded-full"
                          style={{ width: `${action.progress || 0}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-700">{action.progress || 0}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {action.last_updated ? new Date(action.last_updated).toLocaleDateString() : 'N/A'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-4 text-sm text-gray-500">
        Showing {filteredActions.length} of {actions.length} actions
      </div>
    </div>
  );
};

export default Actions;
