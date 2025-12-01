import { useState, useEffect } from 'react';
import { Input, Button } from '@/components/ui';
import { useDebounce } from '@/hooks';
import type { MovieSearchParams } from '@/types';

interface MovieSearchProps {
  onSearch: (params: MovieSearchParams) => void;
  loading?: boolean;
}

export const MovieSearch = ({ onSearch, loading }: MovieSearchProps) => {
  const [query, setQuery] = useState('');
  const [genre, setGenre] = useState('');
  const [yearFrom, setYearFrom] = useState('');
  const [yearTo, setYearTo] = useState('');
  const [ordering, setOrdering] = useState<MovieSearchParams['ordering']>('-created_at');

  const debouncedQuery = useDebounce(query, 500);

  useEffect(() => {
    handleSearch();
  }, [debouncedQuery]);

  const handleSearch = () => {
    const params: MovieSearchParams = {};

    if (debouncedQuery.trim()) params.query = debouncedQuery.trim();
    if (genre) params.genre = genre;
    if (yearFrom) params.year_from = parseInt(yearFrom);
    if (yearTo) params.year_to = parseInt(yearTo);
    if (ordering) params.ordering = ordering;

    onSearch(params);
  };

  const handleReset = () => {
    setQuery('');
    setGenre('');
    setYearFrom('');
    setYearTo('');
    setOrdering('-created_at');
    onSearch({});
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Поиск фильмов</h2>
      
      <div className="space-y-4">
        {/* Search Query */}
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-1">
            Название или описание
          </label>
          <Input
            id="query"
            type="text"
            placeholder="Введите название фильма..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Genre */}
          <div>
            <label htmlFor="genre" className="block text-sm font-medium text-gray-700 mb-1">
              Жанр
            </label>
            <select
              id="genre"
              value={genre}
              onChange={(e) => setGenre(e.target.value)}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Все жанры</option>
              <option value="Action">Боевик</option>
              <option value="Drama">Драма</option>
              <option value="Comedy">Комедия</option>
              <option value="Sci-Fi">Фантастика</option>
              <option value="Thriller">Триллер</option>
              <option value="Romance">Романтика</option>
            </select>
          </div>

          {/* Year From */}
          <div>
            <label htmlFor="yearFrom" className="block text-sm font-medium text-gray-700 mb-1">
              Год от
            </label>
            <Input
              id="yearFrom"
              type="number"
              placeholder="1980"
              value={yearFrom}
              onChange={(e) => setYearFrom(e.target.value)}
              disabled={loading}
              min="1900"
              max="2100"
            />
          </div>

          {/* Year To */}
          <div>
            <label htmlFor="yearTo" className="block text-sm font-medium text-gray-700 mb-1">
              Год до
            </label>
            <Input
              id="yearTo"
              type="number"
              placeholder="2024"
              value={yearTo}
              onChange={(e) => setYearTo(e.target.value)}
              disabled={loading}
              min="1900"
              max="2100"
            />
          </div>

          {/* Ordering */}
          <div>
            <label htmlFor="ordering" className="block text-sm font-medium text-gray-700 mb-1">
              Сортировка
            </label>
            <select
              id="ordering"
              value={ordering}
              onChange={(e) => setOrdering(e.target.value as MovieSearchParams['ordering'])}
              disabled={loading}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="-created_at">Сначала новые</option>
              <option value="created_at">Сначала старые</option>
              <option value="title">По названию (А-Я)</option>
              <option value="-title">По названию (Я-А)</option>
              <option value="-year">По году (убыв.)</option>
              <option value="year">По году (возр.)</option>
              <option value="-average_rating">По рейтингу (высокий)</option>
              <option value="average_rating">По рейтингу (низкий)</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button
            onClick={handleSearch}
            disabled={loading}
            variant="primary"
          >
            {loading ? 'Поиск...' : 'Найти'}
          </Button>
          <Button
            onClick={handleReset}
            disabled={loading}
            variant="secondary"
          >
            Сбросить
          </Button>
        </div>
      </div>
    </div>
  );
};
