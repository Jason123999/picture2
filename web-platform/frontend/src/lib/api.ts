import { authStorage, tenantStorage } from "@/src/lib/auth";
import { getTenantSlugFromLocation } from "@/src/lib/tenant";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8001/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = authStorage.get();
  const tenantSlug = getTenantSlugFromLocation();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token.accessToken}` } : {}),
      ...(tenantSlug ? { "x-tenant-slug": tenantSlug } : {}),
      ...(init?.headers || {}),
    },
    ...init,
  });

  if (response.status === 401) {
    authStorage.clear();
    tenantStorage.clear();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),
  upload: async <T>(path: string, file: File) => {
    const token = authStorage.get();
    const tenantSlug = getTenantSlugFromLocation();
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        ...(token ? { Authorization: `Bearer ${token.accessToken}` } : {}),
        ...(tenantSlug ? { "x-tenant-slug": tenantSlug } : {}),
      },
      body: formData,
    });

    if (response.status === 401) {
      authStorage.clear();
      tenantStorage.clear();
      if (typeof window !== "undefined") {
        window.location.href = "/login";
      }
      throw new Error("Unauthorized");
    }

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed with ${response.status}`);
    }

    return (await response.json()) as T;
  },
};
