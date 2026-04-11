import React from "react";
import type { LucideIcon } from "lucide-react";
import { Activity, Shield, Users, Server } from "lucide-react";
import type { StatsResponse } from "../types/api";

import { TaskWizard } from "./TaskWizard";
import { WorkerGrid } from "./WorkerGrid";
import { LiveConsole } from "./LiveConsole";
import { useStats } from "../hooks/useStats";

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  loading: boolean;
}

const StatCard = ({ title, value, icon: Icon, color, loading }: StatCardProps) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
    <div className="flex items-center justify-between mb-4">
      <span className="text-slate-400 text-sm font-medium">{title}</span>
      <Icon className={`w-5 h-5 ${color}`} />
    </div>
    <div className="text-2xl font-bold">
      {loading ? <div className="h-8 w-16 bg-slate-800 animate-pulse rounded" /> : value}
    </div>
  </div>
);

export const Dashboard = () => {
  const { data: stats, isLoading } = useStats();

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 p-8">
      <header className="flex justify-between items-center mb-12">
        <div>
          <h1 className="text-3xl font-bold">TrafficGrid Control</h1>
          <p className="text-slate-500">Real-time Bot Farm Orchestration</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-emerald-950/30 border border-emerald-500/30 rounded-lg">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            <span className="text-xs text-emerald-500 font-bold uppercase tracking-wider">Gateway Online</span>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <StatCard
          title="Active Workers"
          value={stats?.active_workers ?? 0}
          icon={Server}
          color="text-blue-500"
          loading={isLoading}
        />
        <StatCard
          title="Tasks Pending"
          value={stats?.tasks_pending ?? 0}
          icon={Activity}
          color="text-emerald-500"
          loading={isLoading}
        />
        <StatCard
          title="Identities"
          value={stats?.total_identities ?? 0}
          icon={Users}
          color="text-purple-500"
          loading={isLoading}
        />
        <StatCard
          title="Success Rate"
          value={stats?.success_rate != null ? `${stats.success_rate}%` : "N/A"}
          icon={Shield}
          color="text-amber-500"
          loading={isLoading}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-8">
          <TaskWizard />
          <LiveConsole workerId="S24-ULTRA-01" />
        </div>
        <div className="lg:col-span-2">
          <WorkerGrid />
        </div>
      </div>
    </div>
  );
};
