import React from "react";
import { Server, RefreshCw, Wifi, WifiOff } from "lucide-react";
import { useWorkers } from "../hooks/useGridData";
import type { WorkerStatus } from "../types/api";

const HEARTBEAT_TIMEOUT_MS = 60_000;

const isOnline = (worker: WorkerStatus): boolean => {
  if (!worker.last_seen) return false;
  return Date.now() - new Date(worker.last_seen).getTime() < HEARTBEAT_TIMEOUT_MS;
};

const formatHeartbeat = (iso: string | null): string => {
  if (!iso) return "Never";
  const d = new Date(iso);
  const diff = Date.now() - d.getTime();
  if (diff < 5000) return "Just now";
  if (diff < 60_000) return `${Math.floor(diff / 1000)}s ago`;
  if (diff < 3600_000) return `${Math.floor(diff / 60_000)}m ago`;
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const STATUS_STYLES: Record<string, string> = {
  idle: "bg-slate-700/30 text-slate-400 border-slate-700",
  busy: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  error: "bg-rose-500/10 text-rose-500 border-rose-500/30",
  warming_up: "bg-amber-500/10 text-amber-500 border-amber-500/30",
};

export const WorkersPage = () => {
  const { data: workers, isLoading, isRefetching } = useWorkers();

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <Server className="w-6 h-6 text-blue-500" />
            Worker Fleet
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            {workers?.length ?? 0} workers registered
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
                  Status
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Name
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Type
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  IP
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  State
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Load
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Last Heartbeat
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
              {!isLoading && workers?.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-6 py-12 text-center text-slate-500"
                  >
                    No workers registered. Start a heartbeat script on a worker
                    node.
                  </td>
                </tr>
              )}
              {workers?.map((worker) => {
                const online = isOnline(worker);
                return (
                  <tr
                    key={worker.id}
                    className="hover:bg-slate-800/30 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {online ? (
                          <Wifi className="w-4 h-4 text-emerald-500" />
                        ) : (
                          <WifiOff className="w-4 h-4 text-slate-600" />
                        )}
                        <span
                          className={`text-xs font-semibold ${
                            online ? "text-emerald-500" : "text-slate-600"
                          }`}
                        >
                          {online ? "Online" : "Offline"}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 font-medium text-slate-200">
                      {worker.name || worker.id}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                          worker.type === "physical"
                            ? "bg-purple-500/10 text-purple-400 border-purple-500/30"
                            : "bg-blue-500/10 text-blue-400 border-blue-500/30"
                        }`}
                      >
                        {worker.type}
                      </span>
                    </td>
                    <td className="px-6 py-4 font-mono text-slate-400 text-xs">
                      {worker.ip || "-"}
                    </td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
                          STATUS_STYLES[worker.status] || STATUS_STYLES.idle
                        }`}
                      >
                        {worker.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        <div className="w-16 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${
                              worker.load > 80
                                ? "bg-rose-500"
                                : worker.load > 50
                                  ? "bg-amber-500"
                                  : "bg-emerald-500"
                            }`}
                            style={{ width: `${Math.min(worker.load, 100)}%` }}
                          />
                        </div>
                        <span className="text-slate-400 text-xs">
                          {worker.load}%
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-slate-500">
                      {formatHeartbeat(worker.last_seen)}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
