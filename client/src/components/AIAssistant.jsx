import { useState, useRef } from 'react';
import { MessageSquare, X, Send } from 'lucide-react';
import { API_BASE_URL } from '../config';
import { useClickOutside } from '../hooks/useClickOutside';

const AIAssistant = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const inputRef = useRef(null);
  const panelRef = useRef(null);

  // Close panel when clicking outside or pressing Escape
  useClickOutside(panelRef, () => setIsExpanded(false), isExpanded);

  const exampleQueries = [
    'What is the FMP development process?',
    'Show me current amendments in review',
    'What are the typical timelines for amendments?',
    'Explain SAFMC\'s jurisdiction',
    'How does the public comment process work?',
    'What are the stages of amendment development?'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      // Get auth token from localStorage
      const authToken = localStorage.getItem('authToken');

      const res = await fetch(`${API_BASE_URL}/api/ai/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({ question: query })
      });

      const data = await res.json();

      if (data.success) {
        setResponse({
          type: 'success',
          title: 'Response',
          message: data.answer
        });
      } else {
        setResponse({
          type: 'error',
          title: 'Error',
          message: data.answer || 'Failed to process query'
        });
      }
    } catch (err) {
      setResponse({
        type: 'error',
        title: 'Error',
        message: 'Failed to connect to AI service. Please try again later.'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleExampleClick = (example) => {
    setQuery(example);
    inputRef.current?.focus();
  };

  return (
    <div className="fixed top-0 right-0 bottom-0 z-40">
      {isExpanded && (
        <div ref={panelRef} className="bg-white dark:bg-gray-800 border-l-4 border-brand-green shadow-2xl h-full" style={{ width: '450px' }}>
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b-2 border-brand-green dark:border-brand-green">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-brand-blue to-blue-600 rounded-lg flex items-center justify-center shadow-md">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">AI Assistant</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Powered by Claude AI</p>
                </div>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
                aria-label="Close AI Assistant"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50 dark:bg-gray-900/50">
              {!response && !loading && (
                <div>
                  <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-4">Try asking:</p>
                  <div className="space-y-2">
                    {exampleQueries.map((example, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleExampleClick(example)}
                        className="w-full text-left px-4 py-3 bg-white dark:bg-gray-800 hover:bg-brand-green/10 dark:hover:bg-brand-green/20 hover:border-brand-green rounded-lg text-sm text-gray-700 dark:text-gray-300 transition-all border-2 border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md"
                      >
                        <span className="text-brand-green font-bold mr-2">→</span>
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-4 border-brand-green mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400 font-medium">Analyzing with Claude AI...</p>
                  </div>
                </div>
              )}

              {response && (
                <div className="space-y-4">
                  <div className="flex justify-between items-start">
                    <h4 className="font-bold text-lg text-gray-900 dark:text-white">{response.title || 'Response'}</h4>
                    <button
                      onClick={() => {
                        setResponse(null);
                        setQuery('');
                      }}
                      className="text-sm text-brand-green hover:text-green-700 dark:hover:text-green-400 font-medium transition-colors"
                    >
                      New Query
                    </button>
                  </div>

                  <div className="p-5 bg-white dark:bg-gray-800 rounded-lg border-2 border-brand-green/30 dark:border-brand-green/50 shadow-sm">
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
                      {response.message}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 italic border-t border-gray-200 dark:border-gray-700 pt-3">
                    <div className="w-5 h-5 bg-gradient-to-br from-brand-blue to-blue-600 rounded flex-shrink-0"></div>
                    <span>Powered by Claude AI • All information should be verified with official SAFMC sources</span>
                  </div>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="border-t-2 border-brand-green/30 dark:border-brand-green/50 p-4 bg-white dark:bg-gray-800">
              <form onSubmit={handleSubmit}>
                <div className="flex gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about FMP development..."
                    className="flex-1 px-4 py-3 border-2 border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-brand-green focus:border-brand-green transition-all"
                  />
                  <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="px-6 py-3 bg-brand-green text-white rounded-lg hover:bg-green-600 disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-medium transition-all shadow-sm hover:shadow-md disabled:shadow-none flex items-center justify-center"
                    aria-label="Send question"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Collapsed Button */}
      {!isExpanded && (
        <button
          onClick={() => setIsExpanded(true)}
          className="absolute top-1/2 right-0 -translate-y-1/2 bg-gradient-to-b from-brand-green to-green-600 text-white shadow-xl hover:from-green-600 hover:to-green-700 transition-all flex items-center justify-center border-l-4 border-brand-blue"
          style={{
            writingMode: 'vertical-rl',
            textOrientation: 'mixed',
            padding: '16px 10px',
            borderTopLeftRadius: '8px',
            borderBottomLeftRadius: '8px',
          }}
          aria-label="Open AI Assistant"
          title="Open AI Assistant"
        >
          <MessageSquare className="w-5 h-5 mb-2" />
          <span className="text-sm font-bold whitespace-nowrap tracking-wide">AI ASSISTANT</span>
        </button>
      )}
    </div>
  );
};

export default AIAssistant;
