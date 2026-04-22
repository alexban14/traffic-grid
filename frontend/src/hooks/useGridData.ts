import { useQuery } from "@tanstack/react-query";
import type { WorkerStatus, ProxyHealth } from "../types/api";
import { apiGet } from "../lib/api";

export const useWorkers = () => {
  return useQuery<WorkerStatus[]>({
    queryKey: ["workers"],
    queryFn: () => apiGet<WorkerStatus[]>("/api/v1/workers/status"),
    refetchInterval: 5000,
  });
};

export const useProxies = () => {
  return useQuery<ProxyHealth[]>({
    queryKey: ["proxies"],
    queryFn: () => apiGet<ProxyHealth[]>("/api/v1/proxies/health"),
    refetchInterval: 10000,
  });
};
