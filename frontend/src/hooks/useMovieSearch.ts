import { useState, useCallback } from 'react';
import { movieService } from '@/services';
import type { Movie, MovieSearchParams, PaginatedResponse } from '@/types';

interface UseMovieSearchReturn {
  movies: Movie[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  nextPage: string | null;
  previousPage: string | null;
  searchMovies: (params: MovieSearchParams) => Promise<void>;
  clearResults: () => void;
}

export const useMovieSearch = (): UseMovieSearchReturn => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [nextPage, setNextPage] = useState<string | null>(null);
  const [previousPage, setPreviousPage] = useState<string | null>(null);

  const searchMovies = useCallback(async (params: MovieSearchParams) => {
    setLoading(true);
    setError(null);
    
    try {
      const response: PaginatedResponse<Movie> = await movieService.searchMovies(params);
      
      setMovies(response.results);
      setTotalCount(response.count);
      setNextPage(response.next);
      setPreviousPage(response.previous);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Ошибка при поиске фильмов';
      setError(errorMessage);
      setMovies([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const clearResults = useCallback(() => {
    setMovies([]);
    setError(null);
    setTotalCount(0);
    setNextPage(null);
    setPreviousPage(null);
  }, []);

  return {
    movies,
    loading,
    error,
    totalCount,
    nextPage,
    previousPage,
    searchMovies,
    clearResults,
  };
};
