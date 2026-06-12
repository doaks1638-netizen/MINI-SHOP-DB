/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { api, getTokens, setTokens, clearTokens } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const fetchUser = useCallback(async () => {
    try {
      const { access } = getTokens();
      if (!access) {
        setLoading(false);
        return;
      }
      const userData = await api.get('/users/me');
      setUser(userData);
      setIsAuthenticated(true);
    } catch {
      clearTokens();
      setUser(null);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      fetchUser();
    }, 0);
    return () => clearTimeout(timer);
  }, [fetchUser]);

  const login = useCallback((accessToken, refreshToken) => {
    setTokens(accessToken, refreshToken);
    fetchUser();
  }, [fetchUser]);

  const logout = useCallback(async () => {
    try {
      const { refresh } = getTokens();
      if (refresh) {
        await api.delete('/auth/logout');
      }
    } catch {
      // Ignore
    } finally {
      clearTokens();
      setUser(null);
      setIsAuthenticated(false);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    try {
      const userData = await api.get('/users/me');
      setUser(userData);
    } catch {
      // Ignore
    }
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated,
    login,
    logout,
    refreshUser,
    isAdmin: user?.role === 'admin' || user?.role === 'creator',
    isCreator: user?.role === 'creator',
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}

export default AuthContext;
