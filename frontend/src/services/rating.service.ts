import { apiClient } from './api/api.client';
import { API_ENDPOINTS } from '@/constants';
import type { Rating, CreateRatingData } from '@/types';

export const ratingService = {
  async rateMovie(data: CreateRatingData): Promise<Rating> {
    const response = await apiClient.post<Rating>(
      API_ENDPOINTS.MOVIES.RATE(data.movie),
      { score: data.score }
    );
    return response.data;
  },

  async updateRating(movieId: number, score: number): Promise<Rating> {
    const response = await apiClient.put<Rating>(
      API_ENDPOINTS.MOVIES.RATE(movieId),
      { score }
    );
    return response.data;
  },
};
