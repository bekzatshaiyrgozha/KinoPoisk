import { useNavigate } from 'react-router-dom';
import { FaHeart, FaClock } from 'react-icons/fa';
import { Card, Badge } from '@/components/ui';
import { RatingStars } from '../RatingStars/RatingStars';
import { formatDuration, formatLikesCount } from '@/utils';
import { getMovieDetailPath } from '@/constants';
import type { MovieCardProps } from './MovieCard.types';

export const MovieCard = ({ movie, onClick }: MovieCardProps) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick(movie);
    } else {
      navigate(getMovieDetailPath(movie.id));
    }
  };

  return (
    <Card
      padding="none"
      hover
      className="cursor-pointer overflow-hidden"
      onClick={handleClick}
    >
      <div className="relative aspect-[2/3] bg-gray-200">
        {movie.poster ? (
          <img
            src={movie.poster}
            alt={movie.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            No Poster
          </div>
        )}
        <div className="absolute top-2 right-2">
          <Badge variant="default">{movie.year}</Badge>
        </div>
      </div>

      <div className="p-4 space-y-2">
        <h3 className="font-semibold text-lg line-clamp-1">{movie.title}</h3>

        <div className="flex items-center justify-between">
          <Badge variant="default">{movie.genre}</Badge>
          <div className="flex items-center gap-1 text-sm text-gray-600">
            <FaClock className="text-xs" />
            <span>{formatDuration(movie.duration)}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <RatingStars rating={movie.average_rating} readonly size="sm" />
          <div className="flex items-center gap-1 text-sm text-gray-600">
            <FaHeart className="text-xs text-red-500" />
            <span>{formatLikesCount(movie.likes_count)}</span>
          </div>
        </div>
      </div>
    </Card>
  );
};
