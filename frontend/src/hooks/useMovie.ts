import { useState, useEffect } from 'react';
import { movieService } from '@/services';
import type { Movie } from '@/types';

interface UseMovieResult {
  movie: Movie | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  refetchSilent: () => Promise<void>;
}

export function useMovie(id: number): UseMovieResult {
  const [movie, setMovie] = useState<Movie | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchMovie = async (showLoader = true) => {
    if (!id) return;

    if (showLoader) {
      setLoading(true);
    }
    setError(null);

    try {
      const data = await movieService.getMovie(id);
      console.log('=== MOVIE DATA FROM SERVER ===');
      console.log('Movie ID:', data.id);
      console.log('User Rating:', data.user_rating);
      console.log('Full movie data:', data);
      console.log('=== END MOVIE DATA ===');
      setMovie(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch movie');
    } finally {
      if (showLoader) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchMovie(true);
  }, [id]);

  const refetch = async () => {
    await fetchMovie(true);
  };

  const refetchSilent = async () => {
    await fetchMovie(false);
  };

  return {
    movie,
    loading,
    error,
    refetch,
    refetchSilent,
  };
}
