import useSWR from "swr";

import { api } from "@/src/lib/api";
import type { Tenant } from "@/src/types";

export function useTenants() {
  const { data, error, isLoading, mutate } = useSWR<Tenant[]>("/tenants", api.get);

  return {
    tenants: data,
    isLoading,
    error,
    mutate,
  };
}
