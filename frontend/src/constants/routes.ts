export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  PROFILE: '/profile',
  MOVIE_DETAIL: '/movies/:id',
  FAVORITES: '/favorites',
  WISHLIST: '/wishlist',
  NOT_FOUND: '*',
} as const;

export const getMovieDetailPath = (id: number | string): string => {
  return `/movies/${id}`;
};
