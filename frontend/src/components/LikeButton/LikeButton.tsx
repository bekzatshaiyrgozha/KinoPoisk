import { useState } from 'react';
import { likeService } from '@/services';

interface LikeButtonProps {
  contentType: 'movie' | 'comment';
  objectId: number;
  initialLikesCount: number;
  initialIsLiked?: boolean;
}

export const LikeButton = ({
  contentType,
  objectId,
  initialLikesCount,
  initialIsLiked = false
}: LikeButtonProps) => {
  const [likesCount, setLikesCount] = useState(initialLikesCount);
  const [isLiked, setIsLiked] = useState(initialIsLiked);
  const [isLoading, setIsLoading] = useState(false);

  const handleLike = async () => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      const response = await likeService.toggleLike({
        content_type: contentType,
        object_id: objectId,
      });

      setIsLiked(response.liked);
      setLikesCount(response.likes_count);
    } catch (error) {
      console.error('Failed to toggle like:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      className={`
        flex items-center gap-2 px-4 py-2 rounded-full border transition-all duration-300 text-sm font-medium
        ${isLiked
          ? 'bg-red-50 border-red-500 text-red-500'
          : 'bg-transparent border-gray-300 text-gray-700 hover:bg-gray-50 hover:border-red-500'
        }
        disabled:opacity-60 disabled:cursor-not-allowed
      `}
      onClick={handleLike}
      disabled={isLoading}
    >
      <span className="text-xl leading-none">{isLiked ? '❤️' : '🤍'}</span>
      <span className={isLiked ? 'text-red-500' : 'text-gray-700'}>{likesCount}</span>
    </button>
  );
};