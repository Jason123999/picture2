const FIXED_TENANT_SLUG = process.env.NEXT_PUBLIC_TENANT_SLUG;
const ROOT_DOMAIN = process.env.NEXT_PUBLIC_ROOT_DOMAIN;
const APP_SUBDOMAIN = process.env.NEXT_PUBLIC_APP_SUBDOMAIN || "app";
const API_SUBDOMAIN = process.env.NEXT_PUBLIC_API_SUBDOMAIN || "api";

function stripPort(hostname: string): string {
  const idx = hostname.indexOf(":");
  return idx >= 0 ? hostname.slice(0, idx) : hostname;
}

export function getTenantSlugFromHostname(hostname: string): string | null {
  if (FIXED_TENANT_SLUG && FIXED_TENANT_SLUG.trim()) {
    return FIXED_TENANT_SLUG.trim();
  }

  const host = stripPort(hostname).toLowerCase();

  // local dev
  if (host === "localhost" || host === "127.0.0.1") return null;

  if (!ROOT_DOMAIN) return null;
  const root = ROOT_DOMAIN.toLowerCase();

  if (host === root) return null;
  if (host === `${APP_SUBDOMAIN}.${root}`) return null;
  if (host === `${API_SUBDOMAIN}.${root}`) return null;

  const suffix = `.${root}`;
  if (!host.endsWith(suffix)) return null;

  const sub = host.slice(0, -suffix.length);
  // Only accept single-label subdomain as tenant slug
  if (!sub || sub.includes(".")) return null;
  return sub;
}

export function getTenantSlugFromLocation(): string | null {
  if (typeof window === "undefined") return null;
  if (FIXED_TENANT_SLUG && FIXED_TENANT_SLUG.trim()) {
    return FIXED_TENANT_SLUG.trim();
  }
  return getTenantSlugFromHostname(window.location.hostname);
}
