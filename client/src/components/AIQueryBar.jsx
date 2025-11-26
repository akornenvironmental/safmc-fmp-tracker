/**
 * AI Query Bar - Sliding Panel Assistant
 *
 * Right-side sliding panel for querying SAFMC FMP tracker data using AI.
 * Provides natural language interface for amendments, FMPs, comments, and meetings.
 */

import { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../config';
import { X } from 'lucide-react';

const AIQueryBar = () => {
  // State
  const [query, setQuery] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const inputRef = useRef(null);

  // Example queries tailored for SAFMC FMP Tracker
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

  // Toggle expanded state
  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
    if (!isExpanded) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  };

  // Clear response and start new query
  const clearResponse = () => {
    setResponse(null);
    setQuery('');
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  // Handle example query click
  const handleExampleClick = (example) => {
    setQuery(example);
    setTimeout(() => inputRef.current?.focus(), 100);
  };

  // Submit query to AI backend
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;

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

      if (!res.ok) {
        throw new Error(data.error || 'Failed to process query');
      }

      setResponse(data.response || data);
    } catch (error) {
      console.error('AI Query Error:', error);
      setResponse({
        type: 'error',
        title: 'Error',
        message: error.message || 'Failed to process your query. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle ESC key to close panel
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isExpanded) {
        setIsExpanded(false);
      }
    };

    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isExpanded]);

  // Render response content based on type
  const renderResponse = () => {
    if (!response) return null;

    // Error response
    if (response.type === 'error') {
      return (
        <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p className="text-sm text-red-900 dark:text-red-200">{response.message}</p>
        </div>
      );
    }

    // Success/Info response
    return (
      <div className="space-y-4">
        {response.title && (
          <div className="flex items-center justify-between">
            <h3 className="font-heading text-xl font-bold text-gray-900 dark:text-white">
              {response.title}
            </h3>
            <button
              onClick={clearResponse}
              className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 transition-colors"
            >
              New Query
            </button>
          </div>
        )}

        {response.message && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
            <p className="text-sm text-blue-900 dark:text-blue-200 whitespace-pre-wrap">{response.message}</p>
          </div>
        )}

        {response.insight && (
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
            <p className="text-sm text-purple-900 dark:text-purple-200">
              <span className="mr-2">💡</span>
              <strong>Insight:</strong> {response.insight}
            </p>
          </div>
        )}

        {response.data && Array.isArray(response.data) && response.data.length > 0 && (
          <div className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  {Object.keys(response.data[0]).map((key) => (
                    <th
                      key={key}
                      className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {response.data.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    {Object.values(row).map((value, vidx) => (
                      <td
                        key={vidx}
                        className="px-4 py-3 text-sm text-gray-900 dark:text-white"
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

        {response.note && (
          <div className="p-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              <span className="mr-2">📝</span>
              {response.note}
            </p>
          </div>
        )}
      </div>
    );
  };

  return (
    <>
      {/* Collapsed Tab Button */}
      {!isExpanded && (
        <button
          onClick={toggleExpanded}
          className="fixed top-1/2 right-0 -translate-y-1/2 z-50 px-3 py-5 bg-gradient-to-b from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg transition-all duration-300 rounded-l-lg flex items-center gap-2"
          style={{ writingMode: 'vertical-rl', textOrientation: 'mixed' }}
          aria-label="Open AI Assistant"
          aria-expanded="false"
        >
          <span className="text-xl">🤖</span>
          <span className="font-medium whitespace-nowrap">AI Assistant</span>
        </button>
      )}

      {/* Expanded Panel */}
      {isExpanded && (
        <div
          className="fixed top-0 right-0 bottom-0 z-50 bg-white dark:bg-gray-800 border-l-2 border-blue-500 dark:border-blue-600 shadow-2xl flex flex-col"
          style={{ width: '450px' }}
          role="dialog"
          aria-label="AI Assistant Panel"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h2 className="font-heading text-lg font-bold text-gray-900 dark:text-white">
                  AI Query Assistant
                </h2>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Ask questions about amendments, FMPs, and meetings
                </p>
              </div>
            </div>
            <button
              onClick={toggleExpanded}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              aria-label="Close AI Assistant"
            >
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto px-6 py-4">
            {isLoading ? (
              // Loading State
              <div className="flex flex-col items-center justify-center py-12">
                <div className="w-12 h-12 border-2 border-transparent border-b-blue-600 dark:border-b-blue-400 rounded-full animate-spin mb-4"></div>
                <p className="text-base text-gray-600 dark:text-gray-400">Analyzing your data...</p>
              </div>
            ) : response ? (
              // Response Display
              renderResponse()
            ) : (
              // Default State - Example Queries
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Try asking questions like:
                </p>
                <div className="space-y-2">
                  {exampleQueries.map((example, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleExampleClick(example)}
                      className="w-full text-left px-4 py-3 bg-gray-50 dark:bg-gray-900 hover:bg-blue-50 dark:hover:bg-blue-900/20 border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600 rounded-lg text-sm text-gray-700 dark:text-gray-300 hover:text-blue-700 dark:hover:text-blue-400 transition-all duration-200"
                    >
                      <span className="text-blue-500 dark:text-blue-400 mr-2">→</span>
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Input Area (Footer) */}
          <div className="sticky bottom-0 px-4 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
            <form onSubmit={handleSubmit} className="flex gap-2">
              <input
                ref={inputRef}
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask a question about amendments, FMPs, comments, or meetings..."
                className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg text-sm placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white rounded-lg text-sm font-medium transition-all duration-200 disabled:cursor-not-allowed"
                aria-label="Submit query"
                aria-busy={isLoading}
              >
                {isLoading ? 'Analyzing...' : 'Ask'}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

export default AIQueryBar;
