import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Users, CheckCircle, XCircle, RefreshCw } from "lucide-react";
import type { IdentityResponse } from "../types/api";
import { apiGet } from "../lib/api";

const STATUS_STYLES: Record<string, string> = {
  active: "bg-green-500/10 text-green-500 border-green-500/30",
  suspended: "bg-rose-500/10 text-rose-500 border-rose-500/30",
  warming_up: "bg-amber-500/10 text-amber-500 border-amber-500/30",
  cooldown: "bg-blue-500/10 text-blue-500 border-blue-500/30",
};

const formatDate = (iso: string | null): string => {
  if (!iso) return "Never";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export const IdentitiesPage = () => {
  const {
    data: identities,
    isLoading,
    isRefetching,
  } = useQuery<IdentityResponse[]>({
    queryKey: ["identities"],
    queryFn: () => apiGet<IdentityResponse[]>("/api/v1/identities/"),
    refetchInterval: 10000,
  });

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <Users className="w-6 h-6 text-purple-500" />
            Identity Management
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            {identities?.length ?? 0} identities registered
          </p>
        </div>
        {isRefetching && (
          <RefreshCw className="w-4 h-4 text-slate-500 animate-spin" />
        )}
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Username
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Platform
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Status
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Trust Score
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Warm-up
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  User Agent
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Last Used
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {isLoading &&
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j} className="px-6 py-4">
                        <div className="h-4 w-20 bg-slate-800 animate-pulse rounded" />
                      </td>
                    ))}
                  </tr>
                ))}
              {!isLoading && identities?.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-6 py-12 text-center text-slate-500"
                  >
                    No identities found
                  </td>
                </tr>
              )}
              {identities?.map((identity) => (
                <tr
                  key={identity.id}
                  className="hover:bg-slate-800/30 transition-colors"
                >
                  <td className="px-6 py-4 font-medium text-slate-200">
                    {identity.username}
                  </td>
                  <td className="px-6 py-4 text-slate-300 capitalize">
                    {identity.platform}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                        STATUS_STYLES[identity.status] ||
                        "bg-slate-800 text-slate-400 border-slate-700"
                      }`}
                    >
                      {identity.status}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${
                            identity.trust_score >= 80
                              ? "bg-green-500"
                              : identity.trust_score >= 50
                                ? "bg-amber-500"
                                : "bg-rose-500"
                          }`}
                          style={{ width: `${identity.trust_score}%` }}
                        />
                      </div>
                      <span className="text-slate-400 text-xs">
                        {identity.trust_score}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {identity.has_profile ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <XCircle className="w-4 h-4 text-slate-600" />
                    )}
                  </td>
                  <td className="px-6 py-4 max-w-[200px]">
                    <span
                      className="text-slate-500 text-xs truncate block"
                      title={identity.user_agent || undefined}
                    >
                      {identity.user_agent || "-"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {formatDate(identity.last_used_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
