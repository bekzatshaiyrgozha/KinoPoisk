import type { CookieOptions } from '../config/cookies.config';

const encode = (v: string) => encodeURIComponent(v);
const decode = (v: string) => {
  try {
    return decodeURIComponent(v);
  } catch {
    return v;
  }
};

const buildCookie = (name: string, value: string, options: CookieOptions = {}) => {
  const parts = [`${encode(name)}=${encode(value)}`];

  if (options.maxAge) {
    parts.push(`expires=${new Date(Date.now() + options.maxAge).toUTCString()}`);
  }
  if (options.path) parts.push(`path=${options.path}`);
  if (options.domain) parts.push(`domain=${options.domain}`);
  if (options.sameSite) parts.push(`SameSite=${options.sameSite}`);
  if (options.secure && window.location.protocol === 'https:') {
    parts.push('secure');
  }

  return parts.join('; ');
};

const parseCookies = () => {
  const cookies = new Map<string, string>();
  
  document.cookie.split(';').forEach((cookie) => {
    const [name, ...rest] = cookie.trim().split('=');
    if (name) {
      cookies.set(decode(name), decode(rest.join('=')));
    }
  });

  return cookies;
};

export const cookieManager = {
  set(name: string, value: string, options?: CookieOptions) {
    document.cookie = buildCookie(name, value, {
      path: '/',
      sameSite: 'Lax',
      secure: true,
      ...options,
    });
  },

  get(name: string): string | null {
    return parseCookies().get(name) ?? null;
  },

  remove(name: string) {
    document.cookie = buildCookie(name, '', { path: '/', maxAge: -1 });
  },

  exists(name: string): boolean {
    return this.get(name) !== null;
  },

  getAll(): Record<string, string> {
    return Object.fromEntries(parseCookies());
  },

  clear() {
    parseCookies().forEach((_, name) => this.remove(name));
  },
};

export type { CookieOptions };
