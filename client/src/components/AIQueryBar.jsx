import { useState, useRef } from 'react';
import { API_BASE_URL } from '../config';

const AIQueryBar = () => {
  const [query, setQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const inputRef = useRef(null);

  // Example queries for SAFMC FMP Tracker
  const exampleQueries = [
    "Show me all amendments currently under development",
    "What amendments are in the public comment phase?",
    "How many FMP actions are planned for Snapper-Grouper?",
    "List all upcoming council meetings this month",
    "Which amendments have missed their target dates?",
    "Show me public comments submitted in the last 30 days",
    "What's the progress on Dolphin Wahoo amendments?",
    "Which FMPs have the most active amendments?",
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);

    try {
      const token = localStorage.getItem('authToken');
      const res = await fetch(`${API_BASE_URL}/api/claude/query`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query.trim() })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        setResponse(data.response);
      } else {
        setResponse({
          type: 'error',
          title: 'Query Failed',
          message: data.error || 'Failed to process query. Please try again.'
        });
      }
    } catch (error) {
      console.error('AI query error:', error);
      setResponse({
        type: 'error',
        title: 'Error',
        message: error.message || 'Failed to process query. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleExampleClick = (example) => {
    setQuery(example);
    inputRef.current?.focus();
  };

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  const clearResponse = () => {
    setResponse(null);
    setQuery('');
    inputRef.current?.focus();
  };

  return (
    <div className="fixed top-0 right-0 bottom-0 z-50">
      {/* Expanded Panel */}
      {isExpanded && (
        <div className="bg-white border-l-2 border-blue-500 shadow-2xl h-full" style={{ width: '450px' }}>
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white text-xl">🤖</span>
                </div>
                <div>
                  <h3 className="font-heading text-lg font-bold text-gray-900">AI Query Assistant</h3>
                  <p className="text-xs text-gray-500">Ask questions about amendments, FMPs, and meetings</p>
                </div>
              </div>
              <button
                onClick={toggleExpanded}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-y-auto p-6">
              {!response && !isLoading && (
                <div>
                  <p className="text-sm text-gray-600 mb-4">Try asking questions like:</p>
                  <div className="space-y-2">
                    {exampleQueries.map((example, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleExampleClick(example)}
                        className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-blue-50 rounded-lg text-sm text-gray-700 hover:text-blue-700 transition-colors border border-gray-200 hover:border-blue-300"
                      >
                        <span className="text-blue-500 mr-2">→</span>
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {isLoading && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
                    <p className="text-gray-600">Analyzing your data...</p>
                  </div>
                </div>
              )}

              {response && (
                <div className="space-y-4">
                  <div className="flex items-start justify-between">
                    <h4 className="font-heading text-xl font-bold text-gray-900">{response.title}</h4>
                    <button
                      onClick={clearResponse}
                      className="text-sm text-blue-600 hover:text-blue-800"
                    >
                      New Query
                    </button>
                  </div>

                  {/* Content */}
                  {response.content && (
                    <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-sm text-blue-900 whitespace-pre-wrap">{response.content}</p>
                    </div>
                  )}

                  {/* Message */}
                  {response.message && (
                    <div className={`p-4 rounded-lg border ${
                      response.type === 'error'
                        ? 'bg-red-50 border-red-200'
                        : 'bg-blue-50 border-blue-200'
                    }`}>
                      <p className={`text-sm ${
                        response.type === 'error' ? 'text-red-900' : 'text-blue-900'
                      } whitespace-pre-wrap`}>{response.message}</p>
                    </div>
                  )}

                  {/* Data Table */}
                  {response.data && Array.isArray(response.data) && response.data.length > 0 && (
                    <div className="bg-white border rounded-lg overflow-hidden">
                      <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                          <tr>
                            {Object.keys(response.data[0]).map((key) => (
                              <th
                                key={key}
                                className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase"
                              >
                                {key}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                          {response.data.map((row, idx) => (
                            <tr key={idx} className="hover:bg-gray-50">
                              {Object.values(row).map((value, vidx) => (
                                <td
                                  key={vidx}
                                  className="px-4 py-3 text-sm text-gray-900"
                                >
                                  {String(value)}
                                </td>
                              ))}
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}

                  {/* Insight */}
                  {response.insight && (
                    <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                      <p className="text-sm text-purple-900">
                        <span className="mr-2">💡</span>
                        <strong>Insight:</strong> {response.insight}
                      </p>
                    </div>
                  )}

                  {/* Note */}
                  {response.note && (
                    <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <p className="text-xs text-gray-600">
                        <span className="mr-2">📝</span>
                        {response.note}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Input Area */}
            <div className="border-t p-4">
              <form onSubmit={handleSubmit}>
                <div className="flex gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask a question about amendments, FMPs, comments, or meetings..."
                    className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  />
                  <button
                    type="submit"
                    disabled={isLoading || !query.trim()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed font-medium text-sm transition-colors"
                  >
                    {isLoading ? 'Analyzing...' : 'Ask'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Collapsed Tab */}
      {!isExpanded && (
        <button
          onClick={toggleExpanded}
          className="absolute top-1/2 right-0 -translate-y-1/2 bg-gradient-to-b from-blue-600 to-purple-600 text-white shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all"
          style={{
            writingMode: 'vertical-rl',
            textOrientation: 'mixed',
            padding: '20px 12px',
            borderTopLeftRadius: '8px',
            borderBottomLeftRadius: '8px',
          }}
        >
          <div className="flex items-center gap-2">
            <span className="text-xl">🤖</span>
            <span className="font-medium whitespace-nowrap">AI Assistant</span>
          </div>
        </button>
      )}
    </div>
  );
};

export default AIQueryBar;
