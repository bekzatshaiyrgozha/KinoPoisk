export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    REGISTER: '/auth/register/',
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    PROFILE: '/auth/profile/',
  },

  // Movies
  MOVIES: {
    LIST: '/movies/',
    DETAIL: (id: number | string) => `/movies/${id}/`,
    COMMENTS: (id: number | string) => `/movies/${id}/comments/`,
    RATE: (id: number | string) => `/movies/${id}/rate/`,
  },

  // Likes
  LIKE: '/like/',
} as const;
