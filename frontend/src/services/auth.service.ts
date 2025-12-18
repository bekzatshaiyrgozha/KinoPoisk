import { apiClient } from './api/api.client';
import { API_ENDPOINTS } from '@/constants';
import { storage, TOKEN_KEYS } from '@/utils/storage';
import type {
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  UserProfile,
} from '@/types';

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await apiClient.post<{
      success: boolean;
      data: User;
      access: string;
      refresh: string;
      message?: string;
    }>(API_ENDPOINTS.AUTH.LOGIN, credentials);

    storage.set(TOKEN_KEYS.ACCESS, response.data.access, 60 * 60 * 1000);
    storage.set(TOKEN_KEYS.REFRESH, response.data.refresh, 7 * 24 * 60 * 60 * 1000);

    return {
      access: response.data.access,
      refresh: response.data.refresh,
    };
  },

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<{
      success: boolean;
      data: User;
      access: string;
      refresh: string;
      message?: string;
    }>(API_ENDPOINTS.AUTH.REGISTER, data);

    // Сохраняем токены после регистрации
    storage.set(TOKEN_KEYS.ACCESS, response.data.access, 60 * 60 * 1000);
    storage.set(TOKEN_KEYS.REFRESH, response.data.refresh, 7 * 24 * 60 * 60 * 1000);

    return response.data.data;
  },

  async logout(): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.LOGOUT);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Always clear tokens
      storage.remove(TOKEN_KEYS.ACCESS);
      storage.remove(TOKEN_KEYS.REFRESH);
    }
  },

  async getProfile(): Promise<UserProfile> {
    const response = await apiClient.get<{
      success: boolean;
      data: UserProfile;
    }>(API_ENDPOINTS.AUTH.PROFILE);
    return response.data.data;
  },

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await apiClient.put<{
      success: boolean;
      data: UserProfile;
      message?: string;
    }>(API_ENDPOINTS.AUTH.PROFILE, data);
    return response.data.data;
  },

  isAuthenticated(): boolean {
    return !!storage.get<string>(TOKEN_KEYS.ACCESS);
  },

  getAccessToken(): string | null {
    return storage.get<string>(TOKEN_KEYS.ACCESS);
  },
};
