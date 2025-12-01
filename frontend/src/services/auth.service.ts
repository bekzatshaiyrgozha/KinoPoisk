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
    const response = await apiClient.post<AuthTokens>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials
    );

    storage.set(TOKEN_KEYS.ACCESS, response.data.access, 60 * 60 * 1000);
    storage.set(TOKEN_KEYS.REFRESH, response.data.refresh, 7 * 24 * 60 * 60 * 1000); 

    return response.data;
  },

  async register(data: RegisterData): Promise<User> {
    const response = await apiClient.post<User>(
      API_ENDPOINTS.AUTH.REGISTER,
      data
    );
    return response.data;
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
    const response = await apiClient.get<UserProfile>(
      API_ENDPOINTS.AUTH.PROFILE
    );
    return response.data;
  },

  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await apiClient.put<UserProfile>(
      API_ENDPOINTS.AUTH.PROFILE,
      data
    );
    return response.data;
  },

  isAuthenticated(): boolean {
    return !!storage.get<string>(TOKEN_KEYS.ACCESS);
  },

  getAccessToken(): string | null {
    return storage.get<string>(TOKEN_KEYS.ACCESS);
  },
};
