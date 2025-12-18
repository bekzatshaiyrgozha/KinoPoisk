import { apiClient } from './api/api.client';
import { API_ENDPOINTS } from '@/constants';
import type { Movie, MovieFilters, MovieSearchParams, PaginatedResponse } from '@/types';

export const movieService = {
  async getMovies(filters?: MovieFilters): Promise<PaginatedResponse<Movie>> {
    const response = await apiClient.get<PaginatedResponse<Movie> | Movie[]>(
      API_ENDPOINTS.MOVIES.LIST,
      { params: filters }
    );

    const data = response.data as PaginatedResponse<Movie> | Movie[];

    if (Array.isArray(data)) {
      return {
        count: data.length,
        next: null,
        previous: null,
        results: data,
      };
    }

    return {
      count: data?.count ?? data?.results?.length ?? 0,
      next: data?.next ?? null,
      previous: data?.previous ?? null,
      results: Array.isArray(data?.results) ? data.results : [],
    };
  },

  async getMovie(id: number): Promise<Movie> {
    const response = await apiClient.get<{ success: boolean; data: Movie }>(
      API_ENDPOINTS.MOVIES.DETAIL(id)
    );
    return response.data.data;
  },

  async uploadVideo(movieId: number, file: File): Promise<Movie> {
    const formData = new FormData();
    formData.append('video', file);

    const response = await apiClient.put<Movie>(
      API_ENDPOINTS.MOVIES.VIDEO_UPLOAD(movieId),
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  async searchMovies(
    params: MovieSearchParams
  ): Promise<PaginatedResponse<Movie>> {
    const response = await apiClient.get<PaginatedResponse<Movie>>(
      API_ENDPOINTS.MOVIES.SEARCH,
      { params }
    );
    return response.data;
  },
};
