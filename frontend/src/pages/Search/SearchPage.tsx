import { useState } from 'react';
import { Loader, Button } from '@/components/ui';
import { MovieList, MovieSearch } from '@/components/features/movies';
import { useMovieSearch } from '@/hooks';
import type { MovieSearchParams } from '@/types';

export const SearchPage = () => {
  const { movies, loading, error, totalCount, nextPage, searchMovies } = useMovieSearch();
  const [hasSearched, setHasSearched] = useState(false);
  const [currentParams, setCurrentParams] = useState<MovieSearchParams>({});
  const [currentPage, setCurrentPage] = useState(1);

  const handleSearch = async (params: MovieSearchParams) => {
    setHasSearched(true);
    setCurrentParams(params);
    setCurrentPage(1);
    await searchMovies({ ...params, page: 1 }, false);
  };

  const handleLoadMore = async () => {
    const nextPageNum = currentPage + 1;
    setCurrentPage(nextPageNum);
    await searchMovies({ ...currentParams, page: nextPageNum }, true);
  };

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Поиск фильмов</h1>
        <p className="text-gray-600 mt-2">
          Найдите фильмы по названию, жанру или году выпуска
        </p>
      </div>

      <MovieSearch onSearch={handleSearch} loading={loading} />

      {loading && currentPage === 1 && (
        <div className="py-12">
          <Loader size="lg" />
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {!loading && hasSearched && (
        <>
          <div className="mb-4">
            <p className="text-gray-600">
              Найдено фильмов: <span className="font-semibold">{totalCount}</span>
            </p>
          </div>

          <MovieList movies={movies} />

          {nextPage && (
            <div className="flex justify-center mt-8">
              <Button
                onClick={handleLoadMore}
                disabled={loading}
                variant="primary"
              >
                {loading ? 'Загрузка...' : 'Загрузить еще'}
              </Button>
            </div>
          )}
        </>
      )}

      {!loading && !hasSearched && (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg">Используйте фильтры для поиска фильмов</p>
        </div>
      )}
    </div>
  );
};
