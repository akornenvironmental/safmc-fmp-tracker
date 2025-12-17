/**
 * DevLogin Component
 *
 * Development-only page for logging in with a JWT token directly.
 * Usage: http://localhost:5175/dev-login?token=<jwt-token>
 */

import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const DevLogin = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { checkAuth } = useAuth();
  const [status, setStatus] = useState('processing');

  useEffect(() => {
    const token = searchParams.get('token');

    console.log('[DEBUG DevLogin] Token from URL:', token ? `${token.substring(0, 20)}...` : 'NONE');

    if (!token) {
      console.log('[DEBUG DevLogin] No token in URL - showing error');
      setStatus('error');
      return;
    }

    // Store token and redirect immediately
    console.log('[DEBUG DevLogin] Storing token in localStorage');
    localStorage.setItem('authToken', token);
    console.log('[DEBUG DevLogin] Token stored, verifying:', localStorage.getItem('authToken') ? 'SUCCESS' : 'FAILED');
    setStatus('success');

    // Small delay to show success message, then redirect
    setTimeout(() => {
      console.log('[DEBUG DevLogin] Redirecting to dashboard');
      navigate('/', { replace: true });
    }, 800);
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full">
        <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8 border border-gray-200 dark:border-gray-700">
          {status === 'processing' && (
            <div className="text-center">
              <svg
                className="animate-spin mx-auto h-16 w-16 text-blue-500"
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
              <h2 className="mt-6 text-2xl font-heading font-bold text-gray-900 dark:text-gray-100">
                Logging you in...
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Development mode login
              </p>
            </div>
          )}

          {status === 'success' && (
            <div className="text-center">
              <svg
                className="mx-auto h-16 w-16 text-green-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h2 className="mt-6 text-2xl font-heading font-bold text-gray-900 dark:text-gray-100">
                Success!
              </h2>
              <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                Redirecting to dashboard...
              </p>
            </div>
          )}

          {status === 'error' && (
            <div className="text-center">
              <svg
                className="mx-auto h-16 w-16 text-red-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h2 className="mt-6 text-2xl font-heading font-bold text-gray-900 dark:text-gray-100">
                Missing Token
              </h2>
              <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                No token provided in URL
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DevLogin;
