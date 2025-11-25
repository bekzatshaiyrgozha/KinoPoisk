import { User } from './user.types';

export interface CommentUser {
  id: number;
  username: string;
}

export interface Comment {
  id: number;
  movie: number;
  user: CommentUser;
  text: string;
  parent: number | null;
  likes_count: number;
  created_at: string;
  updated_at?: string;
  replies?: Comment[];
}

export interface CreateCommentData {
  movie: number;
  text: string;
  parent?: number | null;
}
