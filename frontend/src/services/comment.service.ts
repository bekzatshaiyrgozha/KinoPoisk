import { apiClient } from './api/api.client';
import { API_ENDPOINTS } from '@/constants';
import type { Comment, CreateCommentData, PaginatedResponse } from '@/types';

export const commentService = {
  async getComments(movieId: number): Promise<PaginatedResponse<Comment>> {
    const response = await apiClient.get<PaginatedResponse<Comment>>(
      API_ENDPOINTS.MOVIES.COMMENTS(movieId)
    );
    return response.data;
  },

  async createComment(data: CreateCommentData): Promise<Comment> {
    const response = await apiClient.post<Comment>(
      API_ENDPOINTS.MOVIES.COMMENTS(data.movie),
      data
    );
    return response.data;
  },

  async replyToComment(
    movieId: number,
    parentId: number,
    text: string
  ): Promise<Comment> {
    const response = await apiClient.post<Comment>(
      API_ENDPOINTS.MOVIES.COMMENTS(movieId),
      {
        movie: movieId,
        text,
        parent: parentId,
      }
    );
    return response.data;
  },
};
