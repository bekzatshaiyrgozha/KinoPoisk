export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || '/api',
  TIMEOUT: 10000,
  HEADERS: {
    'Content-Type': 'application/json',
  },
} as const;
