import { createContext, useContext, useState, useEffect } from 'react';
import { API_BASE_URL } from '../config';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  // Check authentication status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('authToken');

      if (!token) {
        setUser(null);
        setAuthenticated(false);
        setLoading(false);
        return;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/check`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      const data = await response.json();

      if (data.authenticated && data.user) {
        setUser(data.user);
        setAuthenticated(true);
      } else {
        setUser(null);
        setAuthenticated(false);
        localStorage.removeItem('authToken');
      }
    } catch (error) {
      console.error('Error checking auth:', error);
      setUser(null);
      setAuthenticated(false);
      localStorage.removeItem('authToken');
    } finally {
      setLoading(false);
    }
  };

  const requestLogin = async (email) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/request-login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to send login link');
      }

      return { success: true, message: data.message, dev_link: data.dev_link };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const verifyLogin = async (token, email) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/auth/verify?token=${encodeURIComponent(token)}&email=${encodeURIComponent(email)}`
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to verify login');
      }

      // Store JWT token in localStorage
      localStorage.setItem('authToken', data.token);

      setUser(data.user);
      setAuthenticated(true);

      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem('authToken');

      if (token) {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      }

      // Remove token from localStorage
      localStorage.removeItem('authToken');

      setUser(null);
      setAuthenticated(false);
    } catch (error) {
      console.error('Error logging out:', error);
      // Still clear local state even if API call fails
      localStorage.removeItem('authToken');
      setUser(null);
      setAuthenticated(false);
    }
  };

  const isAdmin = () => {
    return user?.role === 'admin';
  };

  const isEditor = () => {
    return user?.role === 'admin' || user?.role === 'editor';
  };

  const value = {
    user,
    loading,
    authenticated,
    requestLogin,
    verifyLogin,
    logout,
    checkAuth,
    isAdmin,
    isEditor,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
