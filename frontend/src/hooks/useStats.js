import { useQuery } from "@tanstack/react-query";
export const useStats = () => {
    return useQuery({
        queryKey: ["stats"],
        queryFn: async () => {
            const res = await fetch("/api/v1/stats/");
            if (!res.ok)
                throw new Error("Failed to fetch stats");
            return res.json();
        },
        refetchInterval: 5000,
    });
};
//# sourceMappingURL=useStats.js.map