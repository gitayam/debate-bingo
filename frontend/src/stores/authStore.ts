import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import Cookies from 'js-cookie';
import { authApi } from '@/services/authApi';

export interface User {
  id: number;
  email: string;
  username: string;
  display_name?: string;
  avatar_url?: string;
  bio?: string;
  is_verified: boolean;
  created_at: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, displayName?: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshAccessToken: () => Promise<void>;
  updateProfile: (updates: Partial<User>) => Promise<void>;
  setUser: (user: User | null) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.login(email, password);
          const { user, access_token, refresh_token } = response;
          
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
          
          // Set cookies for SSR
          Cookies.set('accessToken', access_token, { expires: 1 }); // 1 day
          Cookies.set('refreshToken', refresh_token, { expires: 7 }); // 7 days
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || 'Login failed'
          });
          throw error;
        }
      },
      
      register: async (email: string, username: string, password: string, displayName?: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await authApi.register(email, username, password, displayName);
          const { user, access_token, refresh_token } = response;
          
          set({
            user,
            accessToken: access_token,
            refreshToken: refresh_token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          });
          
          // Set cookies for SSR
          Cookies.set('accessToken', access_token, { expires: 1 });
          Cookies.set('refreshToken', refresh_token, { expires: 7 });
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.detail || 'Registration failed'
          });
          throw error;
        }
      },
      
      logout: async () => {
        const { accessToken } = get();
        
        try {
          if (accessToken) {
            await authApi.logout(accessToken);
          }
        } catch (error) {
          console.error('Logout error:', error);
        } finally {
          // Clear auth state regardless
          get().clearAuth();
        }
      },
      
      refreshAccessToken: async () => {
        const { refreshToken } = get();
        
        if (!refreshToken) {
          get().clearAuth();
          throw new Error('No refresh token available');
        }
        
        try {
          const response = await authApi.refreshToken(refreshToken);
          const { access_token, refresh_token } = response;
          
          set({
            accessToken: access_token,
            refreshToken: refresh_token
          });
          
          Cookies.set('accessToken', access_token, { expires: 1 });
          Cookies.set('refreshToken', refresh_token, { expires: 7 });
        } catch (error) {
          get().clearAuth();
          throw error;
        }
      },
      
      updateProfile: async (updates: Partial<User>) => {
        const { accessToken, user } = get();
        
        if (!accessToken || !user) {
          throw new Error('Not authenticated');
        }
        
        try {
          const updatedUser = await authApi.updateProfile(accessToken, updates);
          set({ user: updatedUser });
        } catch (error: any) {
          set({ error: error.response?.data?.detail || 'Profile update failed' });
          throw error;
        }
      },
      
      setUser: (user: User | null) => {
        set({ user, isAuthenticated: !!user });
      },
      
      setTokens: (accessToken: string, refreshToken: string) => {
        set({ accessToken, refreshToken });
        Cookies.set('accessToken', accessToken, { expires: 1 });
        Cookies.set('refreshToken', refreshToken, { expires: 7 });
      },
      
      clearAuth: () => {
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null
        });
        
        Cookies.remove('accessToken');
        Cookies.remove('refreshToken');
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);