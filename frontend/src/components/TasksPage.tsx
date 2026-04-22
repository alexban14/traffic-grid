import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { ListTodo, RefreshCw } from "lucide-react";
import type { TaskResponse } from "../types/api";
import { apiGet } from "../lib/api";

const STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-amber-500/10 text-amber-500 border-amber-500/30",
  QUEUED: "bg-blue-500/10 text-blue-500 border-blue-500/30",
  RUNNING: "bg-emerald-500/10 text-emerald-400 border-emerald-500/30",
  SUCCESS: "bg-green-500/10 text-green-500 border-green-500/30",
  FAILED: "bg-rose-500/10 text-rose-500 border-rose-500/30",
};

const StatusBadge = ({ status }: { status: string }) => (
  <span
    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${
      STATUS_STYLES[status] || "bg-slate-800 text-slate-400 border-slate-700"
    }`}
  >
    {status}
  </span>
);

const formatDuration = (seconds: number | null | undefined): string => {
  if (seconds == null) return "-";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  const mins = Math.floor(seconds / 60);
  const secs = Math.round(seconds % 60);
  return `${mins}m ${secs}s`;
};

const formatDate = (iso: string | null): string => {
  if (!iso) return "-";
  const d = new Date(iso);
  return d.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
};

type StatusFilter = "ALL" | TaskResponse["status"];

export const TasksPage = () => {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("ALL");

  const { data: tasks, isLoading, isRefetching } = useQuery<TaskResponse[]>({
    queryKey: ["tasks"],
    queryFn: () => apiGet<TaskResponse[]>("/api/v1/tasks/"),
    refetchInterval: 5000,
  });

  const filtered =
    statusFilter === "ALL"
      ? tasks
      : tasks?.filter((t) => t.status === statusFilter);

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-3">
            <ListTodo className="w-6 h-6 text-emerald-500" />
            Task History
          </h2>
          <p className="text-slate-500 text-sm mt-1">
            {tasks?.length ?? 0} total tasks
          </p>
        </div>
        <div className="flex items-center gap-3">
          {isRefetching && (
            <RefreshCw className="w-4 h-4 text-slate-500 animate-spin" />
          )}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-300 focus:border-emerald-500 outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="PENDING">Pending</option>
            <option value="QUEUED">Queued</option>
            <option value="RUNNING">Running</option>
            <option value="SUCCESS">Success</option>
            <option value="FAILED">Failed</option>
          </select>
        </div>
      </div>

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  ID
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Type
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Target URL
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Status
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Identity
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Duration
                </th>
                <th className="text-left text-xs font-bold text-slate-500 uppercase tracking-wider px-6 py-4">
                  Created
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
              {!isLoading && filtered?.length === 0 && (
                <tr>
                  <td
                    colSpan={7}
                    className="px-6 py-12 text-center text-slate-500"
                  >
                    No tasks found
                  </td>
                </tr>
              )}
              {filtered?.map((task) => (
                <tr
                  key={task.id}
                  className="hover:bg-slate-800/30 transition-colors"
                >
                  <td className="px-6 py-4 font-mono text-slate-400">
                    #{task.id}
                  </td>
                  <td className="px-6 py-4 text-slate-300">{task.type}</td>
                  <td className="px-6 py-4 max-w-[250px]">
                    <span
                      className="text-slate-300 truncate block"
                      title={task.target_url}
                    >
                      {task.target_url}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={task.status} />
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {task.identity_username || "-"}
                  </td>
                  <td className="px-6 py-4 text-slate-400">
                    {formatDuration(task.duration_seconds)}
                  </td>
                  <td className="px-6 py-4 text-slate-500">
                    {formatDate(task.created_at)}
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
