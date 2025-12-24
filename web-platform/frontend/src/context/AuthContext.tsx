"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { authStorage, tenantStorage } from "@/src/lib/auth";
import { decodeJwt } from "@/src/lib/jwt";

interface AuthContextValue {
  accessToken: string | null;
  tenantId: number | null;
  email: string | null;
  login: (token: string) => void;
  logout: () => void;
  selectTenant: (id: number | null) => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const initial = useMemo(() => {
    if (typeof window === "undefined") {
      return { token: null as string | null, tenantId: null as number | null, email: null as string | null };
    }

    const stored = authStorage.get();
    const storedTenant = tenantStorage.get();
    if (!stored?.accessToken) {
      return { token: null as string | null, tenantId: null as number | null, email: null as string | null };
    }

    const decoded = decodeJwt<{ tenant_id?: number; email?: string }>(stored.accessToken);
    const resolvedTenantId =
      storedTenant !== null
        ? storedTenant
        : decoded?.tenant_id
          ? Number(decoded.tenant_id)
          : null;

    return {
      token: stored.accessToken,
      tenantId: resolvedTenantId,
      email: decoded?.email ?? null,
    };
  }, []);

  const [token, setToken] = useState<string | null>(() => initial.token);
  const [tenantId, setTenantId] = useState<number | null>(() => initial.tenantId);
  const [email, setEmail] = useState<string | null>(() => initial.email);

  const handleSelectTenant = useCallback((id: number | null) => {
    if (id === null) {
      tenantStorage.clear();
      setTenantId(null);
      return;
    }
    tenantStorage.set(id);
    setTenantId(id);
  }, []);

  useEffect(() => {
    const stored = authStorage.get();
    const storedTenant = tenantStorage.get();
    if (stored?.accessToken) {
      setToken(stored.accessToken);
      const decoded = decodeJwt<{ tenant_id?: number; email?: string }>(stored.accessToken);
      if (storedTenant !== null) {
        handleSelectTenant(storedTenant);
      } else if (decoded?.tenant_id) {
        handleSelectTenant(Number(decoded.tenant_id));
      }
      if (decoded?.email) {
        setEmail(decoded.email);
      }
    }
  }, [handleSelectTenant]);

  const value = useMemo<AuthContextValue>(
    () => ({
      accessToken: token,
      tenantId,
      email,
      login: (newToken: string) => {
        authStorage.set({ accessToken: newToken });
        setToken(newToken);
        const decoded = decodeJwt<{ tenant_id?: number; email?: string }>(newToken);
        if (decoded?.tenant_id) {
          handleSelectTenant(Number(decoded.tenant_id));
        }
        if (decoded?.email) {
          setEmail(decoded.email);
        }
      },
      logout: () => {
        authStorage.clear();
        handleSelectTenant(null);
        setToken(null);
        setEmail(null);
      },
      selectTenant: handleSelectTenant,
    }),
    [token, tenantId, email, handleSelectTenant]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
