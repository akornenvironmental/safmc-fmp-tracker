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
      const res = await fetch(`${API_BASE_URL}/api/ai/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    <div className="fixed top-0 right-0 bottom-0 z-50">
      {isExpanded && (
        <div ref={panelRef} className="bg-white dark:bg-gray-800 border-l-2 border-brand-blue shadow-2xl h-full" style={{ width: '450px' }}>
          <div className="h-full flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-brand-blue to-brand-green rounded-lg flex items-center justify-center">
                  <MessageSquare className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-gray-900 dark:text-white">AI Assistant</h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Ask questions about FMP development</p>
                </div>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto p-6">
              {!response && !loading && (
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Try asking:</p>
                  <div className="space-y-2">
                    {exampleQueries.map((example, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleExampleClick(example)}
                        className="w-full text-left px-4 py-3 bg-gray-50 dark:bg-gray-700 hover:bg-brand-blue/10 dark:hover:bg-brand-blue/20 rounded-lg text-sm text-gray-700 dark:text-gray-300 transition-colors border border-gray-200 dark:border-gray-600"
                      >
                        <span className="text-brand-blue mr-2">→</span>
                        {example}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {loading && (
                <div className="flex items-center justify-center py-12">
                  <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-brand-blue mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">Analyzing...</p>
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
                      className="text-sm text-brand-blue hover:text-brand-blue-dark"
                    >
                      New Query
                    </button>
                  </div>

                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                    <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                      {response.message}
                    </p>
                  </div>

                  <p className="text-xs text-gray-500 dark:text-gray-400 italic">
                    Powered by Claude • All information should be verified with official SAFMC sources
                  </p>
                </div>
              )}
            </div>

            {/* Input */}
            <div className="border-t border-gray-200 dark:border-gray-700 p-4">
              <form onSubmit={handleSubmit}>
                <div className="flex gap-2">
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Ask about FMP development..."
                    className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:ring-2 focus:ring-brand-blue focus:border-transparent"
                  />
                  <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="px-6 py-3 bg-brand-blue text-white rounded-lg hover:bg-brand-blue-dark disabled:bg-gray-300 dark:disabled:bg-gray-600 disabled:cursor-not-allowed font-medium transition-colors"
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
          className="absolute top-1/2 right-0 -translate-y-1/2 bg-gradient-to-b from-brand-blue to-brand-green text-white shadow-lg hover:from-brand-blue-dark hover:to-brand-green-dark transition-all"
          style={{
            writingMode: 'vertical-rl',
            textOrientation: 'mixed',
            padding: '20px 12px',
            borderTopLeftRadius: '8px',
            borderBottomLeftRadius: '8px',
          }}
        >
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            <span className="font-medium whitespace-nowrap">AI Assistant</span>
          </div>
        </button>
      )}
    </div>
  );
};

export default AIAssistant;
