import { useState, useEffect } from 'react';
import { movieService } from '@/services';
import type { Movie } from '@/types';

interface UseMovieResult {
  movie: Movie | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

export function useMovie(id: number): UseMovieResult {
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMovie = async () => {
    if (!id) return;

    setLoading(true);
    setError(null);

    try {
      const data = await movieService.getMovie(id);
      setMovie(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch movie');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovie();
  }, [id]);

  return {
    movie,
    loading,
    error,
    refetch: fetchMovie,
  };
}
