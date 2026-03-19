import { useQuery } from '@tanstack/react-query';

export const useWorkers = () => {
  return useQuery({
    queryKey: ['workers'],
    queryFn: async () => {
      const res = await fetch('/api/v1/workers/status');
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    },
    refetchInterval: 5000,
  });
};

export const useProxies = () => {
  return useQuery({
    queryKey: ['proxies'],
    queryFn: async () => {
      const res = await fetch('/api/v1/proxies/health');
      if (!res.ok) throw new Error('Network response was not ok');
      return res.json();
    },
    refetchInterval: 10000,
  });
};