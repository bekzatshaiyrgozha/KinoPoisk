import { apiClient } from './api/api.client';
import { API_ENDPOINTS } from '@/constants';
import type { Like, LikeData } from '@/types';

export const likeService = {
  async toggleLike(data: LikeData): Promise<{ liked: boolean; likes_count: number }> {
    const response = await apiClient.post<{ liked: boolean; likes_count: number }>(
      API_ENDPOINTS.LIKE,
      data
    );
    return response.data;
  },

  async likeMovie(movieId: number): Promise<{ liked: boolean; likes_count: number }> {
    return this.toggleLike({
      content_type: 'movie',
      object_id: movieId,
    });
  },

  async likeComment(commentId: number): Promise<{ liked: boolean; likes_count: number }> {
    return this.toggleLike({
      content_type: 'comment',
      object_id: commentId,
    });
  },
};
