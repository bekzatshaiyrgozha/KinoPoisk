import { useState } from 'react';
import { Comment } from '@/types';
import { LikeButton } from '../LikeButton/LikeButton';
import { CommentForm } from '../CommentForm/CommentForm';

interface CommentItemProps {
  comment: Comment;
  movieId: number;
  onReplyAdded: () => void;
}

export const CommentItem = ({ comment, movieId, onReplyAdded }: CommentItemProps) => {
  const [showReplyForm, setShowReplyForm] = useState(false);

  const handleReplySuccess = () => {
    setShowReplyForm(false);
    onReplyAdded();
  };

  return (
    <div className="p-4 bg-white rounded-lg mb-4 shadow-sm">
      <div className="flex justify-between items-center mb-3">
        <span className="font-semibold text-gray-800 text-sm">
          {typeof comment.user === 'string' ? comment.user : comment.user.username}
        </span>
        <span className="text-xs text-gray-400">
          {new Date(comment.created_at).toLocaleDateString('en-US', {
            day: 'numeric',
            month: 'long',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
          })}
        </span>
      </div>

      <div className="text-gray-600 leading-relaxed mb-4 whitespace-pre-wrap">{comment.text}</div>

      <div className="flex gap-4 items-center">
        <LikeButton
          contentType="comment"
          objectId={comment.id}
          initialLikesCount={comment.likes_count}
          initialIsLiked={comment.is_liked}
        />
        <button
          className="px-4 py-2 bg-transparent border-none text-gray-600 text-sm transition-colors hover:text-red-500 cursor-pointer"
          onClick={() => setShowReplyForm(!showReplyForm)}
        >
          {showReplyForm ? 'Cancel' : 'Reply'}
        </button>
      </div>

      {showReplyForm && (
        <div className="mt-4 pl-4 border-l-4 border-gray-200">
          <CommentForm
            movieId={movieId}
            parentId={comment.id}
            onSuccess={handleReplySuccess}
            placeholder="Write a reply..."
          />
        </div>
      )}

      {comment.replies && comment.replies.length > 0 && (
        <div className="mt-4 pl-8 border-l-2 border-gray-200">
          {comment.replies.map((reply: Comment) => (
            <div key={reply.id} className="bg-gray-50 rounded-lg p-4 mb-3">
              <div className="flex justify-between items-center mb-2">
                <span className="font-semibold text-gray-800 text-sm">
                  {typeof reply.user === 'string' ? reply.user : reply.user.username}
                </span>
                <span className="text-xs text-gray-400">
                  {new Date(reply.created_at).toLocaleDateString('en-US', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
              <div className="text-gray-600 leading-relaxed mb-3 whitespace-pre-wrap">{reply.text}</div>
              <LikeButton
                contentType="comment"
                objectId={reply.id}
                initialLikesCount={reply.likes_count}
                initialIsLiked={reply.is_liked}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
};