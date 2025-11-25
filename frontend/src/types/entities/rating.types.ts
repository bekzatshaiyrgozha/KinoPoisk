export interface Rating {
  id: number;
  user: number;
  movie: number;
  score: number;
  created_at: string;
  updated_at?: string;
}

export interface CreateRatingData {
  movie: number;
  score: number;
}
