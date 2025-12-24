export function decodeJwt<T = Record<string, unknown>>(token: string): T | null {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => {
          const code = c.charCodeAt(0).toString(16).padStart(2, "0");
          return `%${code}`;
        })
        .join("")
    );

    return JSON.parse(jsonPayload) as T;
  } catch {
    return null;
  }
}
