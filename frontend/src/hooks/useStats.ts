import { useQuery } from "@tanstack/react-query";
import type { StatsResponse } from "../types/api";
import { apiGet } from "../lib/api";

export const useStats = () => {
  return useQuery<StatsResponse>({
    queryKey: ["stats"],
    queryFn: () => apiGet<StatsResponse>("/api/v1/stats/"),
    refetchInterval: 5000,
  });
};
