import useSWR from "swr";

import { api } from "@/src/lib/api";
import type { ImageAsset } from "@/src/types";

export function useAssets(tenantId: number | null) {
  const key = tenantId != null ? `/assets` : null;
  const { data, error, isLoading, mutate } = useSWR<ImageAsset[]>(key, api.get);

  return {
    assets: data,
    isLoading,
    error,
    mutate,
  };
}
