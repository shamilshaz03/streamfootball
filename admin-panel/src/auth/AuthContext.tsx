import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';
import { authApi } from '../api';
import type { AdminUser } from '../types';

interface AuthCtx {
  admin: AdminUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthCtx | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [admin, setAdmin] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchMe = useCallback(async () => {
    try {
      const res = await authApi.me();
      setAdmin(res.data);
    } catch {
      setAdmin(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) fetchMe(); else setLoading(false);
  }, [fetchMe]);

  const login = async (username: string, password: string) => {
    const res = await authApi.login(username, password);
    localStorage.setItem('access_token', res.data.access_token);
    await fetchMe();
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setAdmin(null);
  };

  return (
    <AuthContext.Provider value={{ admin, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthCtx => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be inside AuthProvider');
  return ctx;
};
