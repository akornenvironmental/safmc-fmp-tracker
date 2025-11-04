import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const VerifyLogin = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { verifyLogin } = useAuth();
  const [status, setStatus] = useState('verifying'); // verifying, success, error
  const [error, setError] = useState('');

  useEffect(() => {
    const verify = async () => {
      const token = searchParams.get('token');
      const email = searchParams.get('email');

      if (!token || !email) {
        setStatus('error');
        setError('Invalid login link. Please request a new one.');
        return;
      }

      const result = await verifyLogin(token, email);

      if (result.success) {
        setStatus('success');
        // Redirect to dashboard after brief delay
        setTimeout(() => {
          navigate('/');
        }, 1500);
      } else {
        setStatus('error');
        setError(result.error || 'Failed to verify login. Please try again.');
      }
    };

    verify();
  }, [searchParams, verifyLogin, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white dark:bg-gray-800 shadow-xl rounded-lg p-8 border border-gray-200 dark:border-gray-700">
          <div className="text-center">
            {status === 'verifying' && (
              <>
                <svg
                  className="animate-spin mx-auto h-16 w-16 text-brand-blue"
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
                <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900 dark:text-gray-100">
                  Verifying...
                </h2>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Please wait while we log you in.
                </p>
              </>
            )}

            {status === 'success' && (
              <>
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
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900 dark:text-gray-100">
                  Success!
                </h2>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  You're logged in. Redirecting to dashboard...
                </p>
              </>
            )}

            {status === 'error' && (
              <>
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
                <h2 className="mt-6 text-3xl font-heading font-bold text-gray-900 dark:text-gray-100">
                  Login Failed
                </h2>
                <p className="mt-2 text-sm text-red-600 dark:text-red-400">
                  {error}
                </p>
                <button
                  onClick={() => navigate('/login')}
                  className="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-brand-blue hover:bg-brand-blue-light focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-green transition-colors"
                >
                  Back to Login
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VerifyLogin;
