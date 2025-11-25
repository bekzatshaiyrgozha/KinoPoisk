export interface Like {
  id: number;
  user: number;
  content_type: number;
  object_id: number;
  created_at: string;
}

export interface LikeData {
  content_type: 'movie' | 'comment';
  object_id: number;
}
