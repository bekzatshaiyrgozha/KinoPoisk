export interface Movie {
  id: number;
  title: string;
  description: string;
  year: number;
  genre: string;
  duration: number;
  poster: string;
  average_rating: number;
  likes_count: number;
  created_at: string;
  updated_at: string;
}

export interface MovieFilters {
  search?: string;
  genre?: string;
  year?: number;
  rating_min?: number;
  rating_max?: number;
  sort_by?: 'title' | 'year' | 'rating' | 'created_at';
  order?: 'asc' | 'desc';
}

export interface MovieCardData {
  id: number;
  title: string;
  poster: string;
  year: number;
  genre: string;
  average_rating: number;
  likes_count: number;
}
