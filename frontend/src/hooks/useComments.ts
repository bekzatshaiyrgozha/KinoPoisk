import { useState, useEffect } from 'react';
import { commentService } from '@/services';
import type { Comment, CreateCommentData } from '@/types';

interface UseCommentsResult {
  comments: Comment[];
  loading: boolean;
  error: string | null;
  addComment: (data: CreateCommentData) => Promise<void>;
  refetch: () => Promise<void>;
}

export function useComments(movieId: number): UseCommentsResult {
  const [comments, setComments] = useState<Comment[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchComments = async () => {
    if (!movieId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await commentService.getComments(movieId);
      setComments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch comments');
    } finally {
      setLoading(false);
    }
  };

  const addComment = async (data: CreateCommentData) => {
    try {
      const newComment = await commentService.createComment(data);
      setComments((prev) => [newComment, ...prev]);
    } catch (err: any) {
      setError(err.message || 'Failed to add comment');
      throw err;
    }
  };

  useEffect(() => {
    fetchComments();
  }, [movieId]);

  return {
    comments,
    loading,
    error,
    addComment,
    refetch: fetchComments,
  };
}
