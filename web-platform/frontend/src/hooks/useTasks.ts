import useSWR from "swr";

import { api } from "@/src/lib/api";
import type { Task } from "@/src/types";

export function useTasks(tenantId: number | null) {
  const key = tenantId != null ? `/tasks` : null;
  const { data, error, isLoading, mutate } = useSWR<Task[]>(key, api.get);

  return {
    tasks: data,
    isLoading,
    error,
    mutate,
  };
}
