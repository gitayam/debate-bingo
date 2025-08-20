import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1/auth',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface LoginResponse {
  user: {
    id: number;
    email: string;
    username: string;
    display_name?: string;
    avatar_url?: string;
    bio?: string;
    is_verified: boolean;
    created_at: string;
  };
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await api.post('/login', { email, password });
    return response.data;
  },
  
  register: async (
    email: string,
    username: string,
    password: string,
    displayName?: string
  ): Promise<LoginResponse> => {
    const response = await api.post('/register', {
      email,
      username,
      password,
      display_name: displayName,
    });
    return response.data;
  },
  
  logout: async (accessToken: string): Promise<void> => {
    await api.post('/logout', null, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
  },
  
  refreshToken: async (refreshToken: string): Promise<TokenResponse> => {
    const response = await api.post('/refresh', { refresh_token: refreshToken });
    return response.data;
  },
  
  getCurrentUser: async (accessToken: string) => {
    const response = await api.get('/me', {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  },
  
  updateProfile: async (accessToken: string, updates: any) => {
    const response = await api.patch('/me', updates, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });
    return response.data;
  },
  
  changePassword: async (
    accessToken: string,
    currentPassword: string,
    newPassword: string
  ) => {
    const response = await api.post(
      '/change-password',
      {
        current_password: currentPassword,
        new_password: newPassword,
      },
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
    return response.data;
  },
};