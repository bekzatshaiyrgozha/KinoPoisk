import { useState } from 'react';
import { Loader } from '@/components/ui';
import { MovieList } from '@/components/features/movies';
import { useMovies } from '@/hooks';
import type { MovieFilters } from '@/types';

export const HomePage = () => {
  const [filters, setFilters] = useState<MovieFilters>({});
  const { movies, loading, error } = useMovies(filters);

  if (loading) {
    return (
      <div className="container mx-auto px-4">
        <Loader size="lg" className="py-20" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4">
        <div className="text-center py-12">
          <p className="text-red-600 text-lg">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Фильмы</h1>
        <p className="text-gray-600 mt-2">
          Откройте для себя лучшие фильмы
        </p>
      </div>

      <MovieList movies={movies} />
    </div>
  );
};
