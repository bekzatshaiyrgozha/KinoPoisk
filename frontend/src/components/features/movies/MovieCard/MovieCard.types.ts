import type { Movie } from '@/types';

export interface MovieCardProps {
  movie: Movie;
  onClick?: (movie: Movie) => void;
}
