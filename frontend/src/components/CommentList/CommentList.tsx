import { useState, useEffect, useCallback } from 'react';
import { commentService } from '@/services';
import { Comment } from '@/types';
import { CommentItem } from '../CommentItem/CommentItem';
import { CommentForm } from '../CommentForm/CommentForm';

interface CommentListProps {
  movieId: number;
}

export const CommentList = ({ movieId }: CommentListProps) => {
  const [comments, setComments] = useState<Comment[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadComments = useCallback(async (showLoader = true) => {
    if (showLoader) {
      setIsLoading(true);
    }
    setError(null);

    try {
      const response = await commentService.getComments(movieId);
      setComments(response.results);
    } catch (err: any) {
      setError(err.message || 'Failed to load comments');
    } finally {
      if (showLoader) {
        setIsLoading(false);
      }
    }
  }, [movieId]);

  useEffect(() => {
    loadComments(true);
  }, [loadComments]);

  const handleCommentAdded = useCallback(async () => {
    // Обновляем список комментариев без показа loader
    // Используем небольшую задержку чтобы дать серверу время обработать запрос
    await new Promise(resolve => setTimeout(resolve, 100));
    await loadComments(false);
  }, [loadComments]);

  if (isLoading) {
    return <div className="text-center py-8 text-gray-600">Loading comments...</div>;
  }

  if (error) {
    return <div className="text-center py-8 text-red-500">{error}</div>;
  }

  return (
    <div className="max-w-3xl mx-auto my-8 px-4">
      <h2 className="text-2xl font-semibold text-gray-800 mb-6">
        Comments {comments.length > 0 && `(${comments.length})`}
      </h2>

      <div className="mb-8 p-6 bg-gray-50 rounded-lg">
        <CommentForm movieId={movieId} onSuccess={handleCommentAdded} />
      </div>

      <div className="flex flex-col gap-4">
        {comments.length === 0 ? (
          <p className="text-center py-12 text-gray-400 text-lg">No comments yet. Be the first to comment!</p>
        ) : (
          comments.map((comment) => (
            <CommentItem
              key={comment.id}
              comment={comment}
              movieId={movieId}
              onReplyAdded={handleCommentAdded}
            />
          ))
        )}
      </div>
    </div>
  );
};