'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, UserRole, AuthResponse } from '@/lib/types';
import { ApiClient } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  quickSwitchDemoUser: (role: UserRole) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Check localStorage on mount
    const savedToken = localStorage.getItem('smart_canteen_token');
    const savedUser = localStorage.getItem('smart_canteen_user');

    if (savedToken && savedUser) {
      try {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('smart_canteen_token');
        localStorage.removeItem('smart_canteen_user');
      }
    } else {
      // Default to student demo user for instant seamless experience
      quickSwitchDemoUser('STUDENT');
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const data = await ApiClient.post<AuthResponse>('/auth/login', { email, password });
      setToken(data.access_token);
      setUser(data.user);
      localStorage.setItem('smart_canteen_token', data.access_token);
      localStorage.setItem('smart_canteen_user', JSON.stringify(data.user));
    } finally {
      setIsLoading(false);
    }
  };

  const quickSwitchDemoUser = async (role: UserRole) => {
    setIsLoading(true);
    let email = 'student@campus.edu';
    let pass = 'campus123';
    if (role === 'STAFF') {
      email = 'staff@campus.edu';
      pass = 'staff123';
    } else if (role === 'ADMIN') {
      email = 'admin@campus.edu';
      pass = 'admin123';
    }

    try {
      await login(email, pass);
    } catch (e) {
      // If backend is not running yet during SSR/mocking, provide demo user state
      const fallbackUser: User = {
        id: role === 'STUDENT' ? 1 : (role === 'STAFF' ? 3 : 4),
        campus_id: role === 'STUDENT' ? 'STU-2024-001' : (role === 'STAFF' ? 'STF-KITCHEN-01' : 'ADM-DIR-001'),
        full_name: role === 'STUDENT' ? 'Aarav Sharma' : (role === 'STAFF' ? 'Chef Ramesh Kumar' : 'Dr. Sunita Rao'),
        email,
        role,
        is_active: true,
        created_at: new Date().toISOString(),
      };
      setUser(fallbackUser);
      setToken('mock_demo_token');
      localStorage.setItem('smart_canteen_user', JSON.stringify(fallbackUser));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('smart_canteen_token');
    localStorage.removeItem('smart_canteen_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, quickSwitchDemoUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
