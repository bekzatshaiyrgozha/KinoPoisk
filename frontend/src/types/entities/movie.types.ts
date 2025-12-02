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
  is_liked: boolean;
  user_rating: number | null;
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

export interface MovieSearchParams {
  query?: string;
  genre?: string;
  year_from?: number;
  year_to?: number;
  ordering?: 
    | 'title' 
    | '-title' 
    | 'year' 
    | '-year' 
    | 'average_rating' 
    | '-average_rating' 
    | 'created_at' 
    | '-created_at';
  page?: number;
  page_size?: number;
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
