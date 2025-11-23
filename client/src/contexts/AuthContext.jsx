import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
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
  const refreshTimeoutRef = useRef(null);

  // Refresh token function - gets new JWT before expiry
  const refreshToken = useCallback(async () => {
    try {
      const storedRefreshToken = localStorage.getItem('refreshToken');

      if (!storedRefreshToken) {
        return false;
      }

      const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refreshToken: storedRefreshToken }),
      });

      const data = await response.json();

      if (response.ok && data.token) {
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('refreshToken', data.refreshToken);
        setUser(data.user);
        setAuthenticated(true);

        // Schedule next refresh 5 minutes before expiry
        scheduleRefresh(data.expiresIn);
        return true;
      } else {
        // Refresh failed - clear tokens
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        setUser(null);
        setAuthenticated(false);
        return false;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      return false;
    }
  }, []);

  // Schedule token refresh before expiry
  const scheduleRefresh = useCallback((expiresInSeconds) => {
    // Clear any existing timeout
    if (refreshTimeoutRef.current) {
      clearTimeout(refreshTimeoutRef.current);
    }

    // Refresh 5 minutes (300s) before expiry, minimum 30 seconds
    const refreshIn = Math.max((expiresInSeconds - 300) * 1000, 30000);

    refreshTimeoutRef.current = setTimeout(() => {
      refreshToken();
    }, refreshIn);
  }, [refreshToken]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }
    };
  }, []);

  // Check authentication status on mount
  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('authToken');
      const storedRefreshToken = localStorage.getItem('refreshToken');

      if (!token) {
        // No JWT - try to get one using refresh token
        if (storedRefreshToken) {
          const refreshed = await refreshToken();
          if (refreshed) {
            setLoading(false);
            return;
          }
        }
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
        // Schedule refresh for the current token (assume 8 hours = 28800 seconds)
        scheduleRefresh(28800);
      } else {
        // JWT invalid - try refresh token
        if (storedRefreshToken) {
          const refreshed = await refreshToken();
          if (refreshed) {
            setLoading(false);
            return;
          }
        }
        setUser(null);
        setAuthenticated(false);
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
      }
    } catch (error) {
      console.error('Error checking auth:', error);
      // Try refresh token before giving up
      const storedRefreshToken = localStorage.getItem('refreshToken');
      if (storedRefreshToken) {
        const refreshed = await refreshToken();
        if (refreshed) {
          setLoading(false);
          return;
        }
      }
      setUser(null);
      setAuthenticated(false);
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
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

      // Store JWT token and refresh token in localStorage
      localStorage.setItem('authToken', data.token);
      if (data.refreshToken) {
        localStorage.setItem('refreshToken', data.refreshToken);
      }

      setUser(data.user);
      setAuthenticated(true);

      // Schedule token refresh before expiry
      if (data.expiresIn) {
        scheduleRefresh(data.expiresIn);
      }

      return { success: true, user: data.user };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = async () => {
    try {
      // Clear refresh timeout
      if (refreshTimeoutRef.current) {
        clearTimeout(refreshTimeoutRef.current);
      }

      const token = localStorage.getItem('authToken');
      const storedRefreshToken = localStorage.getItem('refreshToken');

      if (token || storedRefreshToken) {
        await fetch(`${API_BASE_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': token ? `Bearer ${token}` : '',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refreshToken: storedRefreshToken }),
        });
      }

      // Remove tokens from localStorage
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');

      setUser(null);
      setAuthenticated(false);
    } catch (error) {
      console.error('Error logging out:', error);
      // Still clear local state even if API call fails
      localStorage.removeItem('authToken');
      localStorage.removeItem('refreshToken');
      setUser(null);
      setAuthenticated(false);
    }
  };

  const isSuperAdmin = () => {
    return user?.role === 'super_admin';
  };

  const isAdmin = () => {
    return user?.role === 'super_admin' || user?.role === 'admin';
  };

  const isEditor = () => {
    return user?.role === 'super_admin' || user?.role === 'admin' || user?.role === 'editor';
  };

  const value = {
    user,
    loading,
    authenticated,
    requestLogin,
    verifyLogin,
    logout,
    checkAuth,
    isSuperAdmin,
    isAdmin,
    isEditor,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export default AuthContext;
