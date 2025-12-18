import { useState } from 'react';
import { commentService } from '@/services';

interface CommentFormProps {
  movieId: number;
  parentId?: number;
  onSuccess: () => void;
  placeholder?: string;
}

export const CommentForm = ({
  movieId,
  parentId,
  onSuccess,
  placeholder = 'Write a comment...'
}: CommentFormProps) => {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();

    if (!text.trim()) {
      setError('Comment cannot be empty');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      if (parentId) {
        await commentService.replyToComment(movieId, parentId, text);
      } else {
        await commentService.createComment({
          movie: movieId,
          text,
        });
      }

      setText('');
      // Используем setTimeout чтобы убедиться, что состояние обновилось перед вызовом onSuccess
      setTimeout(() => {
        onSuccess();
      }, 0);
    } catch (err: any) {
      setError(err.message || 'Failed to post comment');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form className="flex flex-col gap-3" onSubmit={handleSubmit}>
      <textarea
        className="w-full px-3 py-2 border border-gray-300 rounded-lg font-inherit text-sm resize-y min-h-[80px] transition-colors focus:outline-none focus:border-red-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        rows={3}
        disabled={isLoading}
      />
      {error && <div className="text-red-500 text-sm">{error}</div>}
      <div className="flex justify-end">
        <button
          type="submit"
          className="px-8 py-3 bg-red-500 text-white rounded-lg text-sm font-medium transition-colors hover:bg-red-600 disabled:bg-gray-400 disabled:cursor-not-allowed"
          disabled={isLoading || !text.trim()}
        >
          {isLoading ? 'Posting...' : parentId ? 'Reply' : 'Post'}
        </button>
      </div>
    </form>
  );
};