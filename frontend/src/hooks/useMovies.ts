import { useState, useEffect } from 'react';
import { movieService } from '@/services';
import type { Movie, MovieFilters } from '@/types';

interface UseMoviesResult {
  movies: Movie[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  hasMore: boolean;
  refetch: () => Promise<void>;
}

export function useMovies(initialFilters?: MovieFilters): UseMoviesResult {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [hasMore, setHasMore] = useState(false);

  const fetchMovies = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await movieService.getMovies(initialFilters);
      setMovies(response.results);
      setTotalCount(response.count);
      setHasMore(!!response.next);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch movies');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovies();
  }, [JSON.stringify(initialFilters)]);

  return {
    movies,
    loading,
    error,
    totalCount,
    hasMore,
    refetch: fetchMovies,
  };
}
