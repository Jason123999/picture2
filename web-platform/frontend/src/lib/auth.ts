export type AuthTokens = {
  accessToken: string;
};

const ACCESS_TOKEN_KEY = "photo-platform.access_token";
const TENANT_KEY = "photo-platform.tenant_id";

export const authStorage = {
  set(tokens: AuthTokens) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
  },
  get(): AuthTokens | null {
    if (typeof window === "undefined") return null;
    const token = window.localStorage.getItem(ACCESS_TOKEN_KEY);
    if (!token) return null;
    return { accessToken: token };
  },
  clear() {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(TENANT_KEY);
  },
};

export const tenantStorage = {
  set(id: number) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(TENANT_KEY, String(id));
  },
  get(): number | null {
    if (typeof window === "undefined") return null;
    const value = window.localStorage.getItem(TENANT_KEY);
    if (!value) return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : null;
  },
  clear() {
    if (typeof window === "undefined") return;
    window.localStorage.removeItem(TENANT_KEY);
  },
};
