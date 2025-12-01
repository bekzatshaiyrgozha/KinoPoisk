import { Movie } from '@/types';
import { MovieCard } from '../MovieCard/MovieCard';

interface MovieListProps {
  movies: Movie[];
  onMovieClick?: (movie: Movie) => void;
}

export const MovieList = ({ movies, onMovieClick }: MovieListProps) => {
  if (!movies || movies.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p className="text-lg">Фильмы не найдены</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
      {movies.map((movie) => (
        <MovieCard key={movie.id} movie={movie} onClick={onMovieClick} />
      ))}
    </div>
  );
};
