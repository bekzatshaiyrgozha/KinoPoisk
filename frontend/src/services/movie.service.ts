import { apiClient } from './api/api.client';
import { API_ENDPOINTS } from '@/constants';
import type { Movie, MovieFilters, PaginatedResponse } from '@/types';

export const movieService = {
  async getMovies(filters?: MovieFilters): Promise<PaginatedResponse<Movie>> {
    const response = await apiClient.get<PaginatedResponse<Movie>>(
      API_ENDPOINTS.MOVIES.LIST,
      { params: filters }
    );
    return response.data;
  },

  async getMovie(id: number): Promise<Movie> {
    const response = await apiClient.get<Movie>(
      API_ENDPOINTS.MOVIES.DETAIL(id)
    );
    return response.data;
  },

  async searchMovies(query: string): Promise<Movie[]> {
    const response = await apiClient.get<PaginatedResponse<Movie>>(
      API_ENDPOINTS.MOVIES.LIST,
      { params: { search: query } }
    );
    return response.data.results;
  },
};
