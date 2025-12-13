import { useState, useEffect, useMemo } from 'react';
import { API_BASE_URL } from '../config';
import PageHeader from '../components/PageHeader';
import Button from '../components/Button';
import { GitCompare, Search, Plus, X, Check, AlertCircle, ArrowRight } from 'lucide-react';

const Compare = () => {
  const [actions, setActions] = useState([]);
  const [selectedActions, setSelectedActions] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(true);
  const [comparing, setComparing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterFMP, setFilterFMP] = useState('');
  const [similarActions, setSimilarActions] = useState([]);
  const [showSimilar, setShowSimilar] = useState(false);

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

  // Get unique FMPs
  const uniqueFMPs = useMemo(() => {
    const fmps = new Set(actions.map(a => a.fmp).filter(Boolean));
    return Array.from(fmps).sort();
  }, [actions]);

  // Filter actions
  const filteredActions = useMemo(() => {
    return actions.filter(action => {
      if (filterFMP && action.fmp !== filterFMP) return false;
      if (searchTerm) {
        const search = searchTerm.toLowerCase();
        return (
          action.title?.toLowerCase().includes(search) ||
          action.fmp?.toLowerCase().includes(search) ||
          action.action_id?.toLowerCase().includes(search)
        );
      }
      return true;
    });
  }, [actions, searchTerm, filterFMP]);

  // Add action to comparison
  const addAction = (action) => {
    if (selectedActions.length >= 5) {
      alert('Maximum 5 actions can be compared');
      return;
    }
    if (!selectedActions.find(a => a.id === action.id)) {
      setSelectedActions([...selectedActions, action]);
      setComparison(null); // Reset comparison
    }
  };

  // Remove action from comparison
  const removeAction = (actionId) => {
    setSelectedActions(selectedActions.filter(a => a.id !== actionId));
    setComparison(null);
  };

  // Run comparison
  const runComparison = async () => {
    if (selectedActions.length < 2) return;

    setComparing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/compare`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action_ids: selectedActions.map(a => a.id)
        })
      });
      const data = await response.json();
      if (data.success) {
        setComparison(data.comparison);
      }
    } catch (error) {
      console.error('Error comparing actions:', error);
    }
    setComparing(false);
  };

  // Find similar actions
  const findSimilar = async (actionId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/compare/similar/${actionId}`);
      const data = await response.json();
      if (data.success) {
        setSimilarActions(data.similar);
        setShowSimilar(true);
      }
    } catch (error) {
      console.error('Error finding similar:', error);
    }
  };

  // Get status color
  const getStatusColor = (isDifferent) => {
    return isDifferent ? 'bg-yellow-50 border-yellow-200' : 'bg-green-50 border-green-200';
  };

  return (
    <div>
      {/* Header */}
      <PageHeader
        icon={GitCompare}
        title="Compare Actions"
        subtitle="Side-by-side comparison"
        description="Compare amendment actions and alternatives side-by-side."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Action Selection Panel */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
            <h2 className="font-semibold text-gray-900 mb-4">Select Actions to Compare</h2>

            {/* Search */}
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search actions..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md text-sm"
                />
              </div>
            </div>

            {/* FMP Filter */}
            <div className="mb-4">
              <select
                value={filterFMP}
                onChange={(e) => setFilterFMP(e.target.value)}
                className="w-full border border-gray-300 rounded-md py-2 px-3 text-sm"
              >
                <option value="">All FMPs</option>
                {uniqueFMPs.map(fmp => (
                  <option key={fmp} value={fmp}>{fmp}</option>
                ))}
              </select>
            </div>

            {/* Selected Actions */}
            {selectedActions.length > 0 && (
              <div className="mb-4 p-3 bg-blue-50 rounded-lg">
                <h3 className="text-sm font-medium text-blue-800 mb-2">
                  Selected ({selectedActions.length}/5)
                </h3>
                <div className="space-y-2">
                  {selectedActions.map(action => (
                    <div
                      key={action.id}
                      className="flex items-center justify-between bg-white rounded px-2 py-1 text-xs"
                    >
                      <span className="truncate flex-1 mr-2">{action.title}</span>
                      <button
                        onClick={() => removeAction(action.id)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <X size={14} />
                      </button>
                    </div>
                  ))}
                </div>
                <Button
                  variant="primary"
                  onClick={runComparison}
                  disabled={selectedActions.length < 2 || comparing}
                  className="mt-3 w-full"
                >
                  {comparing ? 'Comparing...' : 'Compare Actions'}
                </Button>
              </div>
            )}

            {/* Action List */}
            <div className="max-h-[400px] overflow-y-auto space-y-2">
              {loading ? (
                <p className="text-gray-500 text-sm text-center py-4">Loading...</p>
              ) : filteredActions.length === 0 ? (
                <p className="text-gray-500 text-sm text-center py-4">No actions found</p>
              ) : (
                filteredActions.slice(0, 50).map(action => (
                  <div
                    key={action.id}
                    className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                      selectedActions.find(a => a.id === action.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                    }`}
                    onClick={() => addAction(action)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <h4 className="text-sm font-medium text-gray-900 truncate">
                          {action.title}
                        </h4>
                        <p className="text-xs text-gray-500 mt-1">{action.fmp}</p>
                      </div>
                      {selectedActions.find(a => a.id === action.id) ? (
                        <Check className="w-5 h-5 text-blue-500 flex-shrink-0" />
                      ) : (
                        <Plus className="w-5 h-5 text-gray-400 flex-shrink-0" />
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Comparison Results */}
        <div className="lg:col-span-2">
          {comparison ? (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="font-semibold text-gray-900">Comparison Results</h2>
                <div className="flex items-center gap-4 text-sm">
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 bg-yellow-200 rounded"></span>
                    Different ({comparison.differences.length})
                  </span>
                  <span className="flex items-center gap-1">
                    <span className="w-3 h-3 bg-green-200 rounded"></span>
                    Same ({comparison.similarities.length})
                  </span>
                </div>
              </div>

              {/* Action Headers */}
              <div className="grid gap-4 mb-6" style={{ gridTemplateColumns: `150px repeat(${comparison.actions.length}, 1fr)` }}>
                <div className="font-medium text-gray-500 text-sm">Field</div>
                {comparison.actions.map((action, idx) => (
                  <div key={idx} className="font-medium text-gray-900 text-sm truncate">
                    {action.title}
                  </div>
                ))}
              </div>

              {/* Comparison Fields */}
              <div className="space-y-2">
                {Object.entries(comparison.fields).map(([key, field]) => (
                  <div
                    key={key}
                    className={`grid gap-4 p-3 rounded-lg border ${getStatusColor(field.isDifferent)}`}
                    style={{ gridTemplateColumns: `150px repeat(${comparison.actions.length}, 1fr)` }}
                  >
                    <div className="font-medium text-gray-700 text-sm flex items-center gap-2">
                      {field.isDifferent ? (
                        <AlertCircle className="w-4 h-4 text-yellow-600" />
                      ) : (
                        <Check className="w-4 h-4 text-green-600" />
                      )}
                      {field.label}
                    </div>
                    {field.values.map((value, idx) => (
                      <div key={idx} className="text-sm text-gray-900">
                        {value || <span className="text-gray-400">N/A</span>}
                      </div>
                    ))}
                  </div>
                ))}
              </div>

              {/* Description Similarity */}
              {comparison.descriptionSimilarity !== undefined && (
                <div className="mt-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-medium text-gray-900 mb-2">Description Similarity</h3>
                  <div className="flex items-center gap-3">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-brand-blue h-2 rounded-full"
                        style={{ width: `${comparison.descriptionSimilarity}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-700">
                      {comparison.descriptionSimilarity}%
                    </span>
                  </div>
                </div>
              )}

              {/* Find Similar Button */}
              {comparison.actions.length === 1 && (
                <button
                  onClick={() => findSimilar(comparison.actions[0].id)}
                  className="mt-4 text-sm text-brand-blue hover:text-brand-blue-light flex items-center gap-1"
                >
                  Find similar actions <ArrowRight size={14} />
                </button>
              )}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
              <GitCompare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Select Actions to Compare
              </h3>
              <p className="text-gray-500 text-sm max-w-md mx-auto">
                Choose 2-5 actions from the list on the left to compare their attributes side-by-side.
                This helps identify differences in status, progress, and other key fields.
              </p>
            </div>
          )}

          {/* Similar Actions Modal */}
          {showSimilar && similarActions.length > 0 && (
            <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-semibold text-gray-900">Similar Actions</h2>
                <button
                  onClick={() => setShowSimilar(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={20} />
                </button>
              </div>
              <div className="space-y-3">
                {similarActions.map((item, idx) => (
                  <div
                    key={idx}
                    className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900">{item.action.title}</h4>
                        <p className="text-sm text-gray-500 mt-1">{item.action.fmp}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {item.matchReasons.map((reason, ridx) => (
                            <span
                              key={ridx}
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-gray-100 text-gray-600"
                            >
                              {reason}
                            </span>
                          ))}
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                          {item.similarityScore}% match
                        </span>
                        <button
                          onClick={() => addAction(item.action)}
                          className="mt-2 block text-xs text-brand-blue hover:underline"
                        >
                          Add to compare
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Compare;
