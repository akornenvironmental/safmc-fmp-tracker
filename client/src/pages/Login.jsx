import { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import safmcLogo from '../assets/safmc-logo.jpg';

const Login = () => {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { requestLogin } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await requestLogin(email);

    if (result.success) {
      setSubmitted(true);
    } else {
      setError(result.error || 'Failed to send login link. Please try again.');
    }

    setLoading(false);
  };

  if (submitted) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
        <div className="max-w-md w-full space-y-8">
          <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8 border border-gray-200 dark:border-gray-700">
            <div className="text-center">
              <svg
                className="mx-auto h-16 w-16 text-brand-green"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                />
              </svg>
              <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900 dark:text-gray-100">
                Check your email!
              </h2>
              <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                We've sent a login link to <strong className="text-brand-blue dark:text-blue-400">{email}</strong>
              </p>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Click the link in the email to log in. The link will expire in 15 minutes.
              </p>
              <button
                onClick={() => {
                  setSubmitted(false);
                  setEmail('');
                }}
                className="mt-6 text-sm text-brand-blue dark:text-blue-400 hover:text-brand-green dark:hover:text-blue-300 underline"
              >
                Send to a different email
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <img src={safmcLogo} alt="SAFMC Logo" className="mx-auto h-24 w-auto rounded mb-4" />
          <h2 className="mt-6 text-center text-4xl font-heading font-bold text-gray-900 dark:text-gray-100">
            SAFMC FMP Tracker
          </h2>
          <p className="mt-3 text-center text-sm text-gray-600 dark:text-gray-400">
            Enter your email to receive a secure login link
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8 border border-gray-200 dark:border-gray-700">
          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-700 rounded-md focus:outline-none focus:ring-brand-blue focus:border-brand-blue focus:z-10 sm:text-sm"
                placeholder="your.email@example.com"
              />
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-brand-blue hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-green disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <span className="flex items-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Sending...
                  </span>
                ) : (
                  'Send login link'
                )}
              </button>
              <p className="mt-3 text-xs text-gray-500 dark:text-gray-400 text-center">
                By logging in, you agree to use this system responsibly for tracking FMP data.
              </p>
            </div>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300 dark:border-gray-600" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                  Authorized users only
                </span>
              </div>
            </div>

            <p className="mt-4 text-center text-xs text-gray-500 dark:text-gray-400">
              Don't have access? Contact{' '}
              <a
                href="mailto:aaron.kornbluth@gmail.com"
                className="text-brand-blue dark:text-blue-400 hover:text-brand-green dark:hover:text-blue-300"
              >
                aaron.kornbluth@gmail.com
              </a>
            </p>
          </div>
        </div>

        <footer className="text-center">
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Built by{' '}
            <a
              href="https://akornenvironmental.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-brand-blue dark:text-blue-400 hover:text-brand-green dark:hover:text-blue-300"
            >
              akorn environmental
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
};

export default Login;
