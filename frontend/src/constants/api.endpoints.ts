export const API_ENDPOINTS = {
  AUTH: {
    REGISTER: '/auth/register/',
    LOGIN: '/auth/login/',
    LOGOUT: '/auth/logout/',
    PROFILE: '/auth/profile/',
  },
  MOVIES: {
    LIST: '/movies/',
    DETAIL: (id: number | string) => `/movies/${id}/`,
    COMMENTS: (id: number | string) => `/movies/${id}/comments/`,
    RATE: (id: number | string) => `/movies/${id}/rate/`,
    VIDEO_UPLOAD: (id: number | string) => `/movies/${id}/video/`,
    SEARCH: '/movies/search/',
  },

  LIKE: '/movies/like/',
} as const;
