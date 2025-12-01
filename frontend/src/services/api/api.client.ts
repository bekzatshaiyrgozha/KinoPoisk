import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { API_CONFIG } from './api.config';
import { storage, TOKEN_KEYS } from '@/utils/storage';
import type { ApiError } from '@/types';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: API_CONFIG.TIMEOUT,
      headers: API_CONFIG.HEADERS,
    });

    this.setupInterceptors();
  }

  private setupInterceptors(): void {
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const isAuthEndpoint = config.url?.includes('/auth/login') || 
                              config.url?.includes('/auth/register');
        
        if (!isAuthEndpoint) {
          const token = storage.get<string>(TOKEN_KEYS.ACCESS);
          if (token && config.headers) {
            config.headers.Authorization = `Bearer ${token}`;
          }
        }

        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(error);
      }
    );

    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          const refreshToken = storage.get<string>(TOKEN_KEYS.REFRESH);
          if (refreshToken) {
            try {
              const response = await this.client.post('/auth/token/refresh/', { 
                refresh: refreshToken 
              });
              storage.set(TOKEN_KEYS.ACCESS, response.data.access, 60 * 60 * 1000);
              
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
              }
              return this.client(originalRequest);
            } catch {
              storage.remove(TOKEN_KEYS.ACCESS);
              storage.remove(TOKEN_KEYS.REFRESH);
              window.location.href = '/login';
            }
          } else {
            storage.remove(TOKEN_KEYS.ACCESS);
            storage.remove(TOKEN_KEYS.REFRESH);
            window.location.href = '/login';
          }
        }

        const apiError: ApiError = {
          message: (error.response?.data as any)?.message || error.message || 'Произошла ошибка',
          errors: (error.response?.data as any)?.errors,
          status: error.response?.status,
        };

        return Promise.reject(apiError);
      }
    );
  }

  public getInstance(): AxiosInstance {
    return this.client;
  }

  // Convenience methods
  public get<T>(url: string, config?: any) {
    return this.client.get<T>(url, config);
  }

  public post<T>(url: string, data?: any, config?: any) {
    return this.client.post<T>(url, data, config);
  }

  public put<T>(url: string, data?: any, config?: any) {
    return this.client.put<T>(url, data, config);
  }

  public patch<T>(url: string, data?: any, config?: any) {
    return this.client.patch<T>(url, data, config);
  }

  public delete<T>(url: string, config?: any) {
    return this.client.delete<T>(url, config);
  }
}

export const apiClient = new ApiClient();
export const axiosInstance = apiClient.getInstance();
