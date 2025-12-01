import { cookieManager } from './cookie.utils';
import { COOKIE_EXPIRATION } from '../config/cookies.config';

const PREFIX = 'kinopoisk_';

export const storage = {
  get<T>(key: string): T | null {
    try {
      const item = cookieManager.get(`${PREFIX}${key}`);
      return item ? JSON.parse(item) : null;
    } catch {
      return null;
    }
  },

  set<T>(key: string, value: T, maxAge = COOKIE_EXPIRATION.WEEK): void {
    try {
      cookieManager.set(`${PREFIX}${key}`, JSON.stringify(value), {
        maxAge,
        path: '/',
        sameSite: 'Lax',
        secure: true,
      });
    } catch {}
  },

  remove(key: string): void {
    cookieManager.remove(`${PREFIX}${key}`);
  },

  clear(): void {
    Object.keys(cookieManager.getAll()).forEach((key) => {
      if (key.startsWith(PREFIX)) cookieManager.remove(key);
    });
  },
};

export const TOKEN_KEYS = {
  ACCESS: 'access_token',
  REFRESH: 'refresh_token',
} as const;
