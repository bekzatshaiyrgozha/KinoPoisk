import { useParams } from 'react-router-dom';
import { FaClock, FaCalendar } from 'react-icons/fa';
import { Loader, Card, Badge } from '@/components/ui';
import { LikeButton } from '@/components/LikeButton';
import { MovieRating } from '@/components/MovieRating';
import { CommentList } from '@/components/CommentList';
import { useMovie } from '@/hooks';
import { useAuth } from '@/contexts';
import { VideoPlayer, VideoUploadForm } from '@/components/features/movies';
import { formatDuration } from '@/utils';

export const MovieDetailPage = () => {
  const { id } = useParams<{ id: string }>();
  const { movie, loading, error, refetch } = useMovie(Number(id));
  const { isAuthenticated, user } = useAuth();

  if (loading) {
    return (
      <div className="container mx-auto px-4">
        <Loader size="lg" className="py-20" />
      </div>
    );
  }

  if (error || !movie) {
    return (
      <div className="container mx-auto px-4">
        <div className="text-center py-12">
          <p className="text-red-600 text-lg">{error || 'Movie not found'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4">
      <Card padding="lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-1">
            <div className="aspect-[2/3] bg-gray-200 rounded-lg overflow-hidden">
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
            </div>
          </div>

          <div className="md:col-span-2 space-y-6">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                {movie.title}
              </h1>
              <div className="flex items-center gap-4 text-gray-600">
                <div className="flex items-center gap-2">
                  <FaCalendar />
                  <span>{movie.year}</span>
                </div>
                <div className="flex items-center gap-2">
                  <FaClock />
                  <span>{formatDuration(movie.duration)}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <Badge variant="default" size="md">
                {movie.genre}
              </Badge>
            </div>

            {/* Rating Section */}
            <div className="p-6 bg-gray-50 rounded-lg">
              <MovieRating
                movieId={movie.id}
                averageRating={movie.average_rating}
                userRating={movie.user_rating}
                onRatingChange={refetch}
              />
            </div>

            {/* Like Button */}
            <div className="flex justify-end">
              <LikeButton
                contentType="movie"
                objectId={movie.id}
                initialLikesCount={movie.likes_count}
                initialIsLiked={movie.is_liked}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Description
              </h2>
              <p className="text-gray-700 leading-relaxed">{movie.description}</p>
            </div>

            <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Video
              </h2>
              <VideoPlayer src={movie.video_url || movie.video} title={movie.title} />
              {isAuthenticated && user?.is_staff && (
                <div className="mt-4">
                  <VideoUploadForm movieId={movie.id} onUploaded={refetch} />
                </div>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Comments Section */}
      {id && (
        <div className="mt-8">
          <CommentList movieId={Number(id)} />
        </div>
      )}
    </div>
  );
};
