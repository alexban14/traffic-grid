import { useState, useEffect } from 'react';
import { Activity, Shield, Users, Server } from 'lucide-react';

import { TaskWizard } from './TaskWizard';
import { WorkerGrid } from './WorkerGrid';
import { LiveConsole } from './LiveConsole';

const StatCard = ({ title, value, icon: Icon, color }: any) => (
  <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl">
    <div className="flex items-center justify-between mb-4">
      <span className="text-slate-400 text-sm font-medium">{title}</span>
      <Icon className={`w-5 h-5 ${color}`} />
    </div>
    <div className="text-2xl font-bold">{value}</div>
  </div>
);

export const Dashboard = () => {
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
        <StatCard title="Active Workers" value="142" icon={Server} color="text-blue-500" />
        <StatCard title="Proxy Latency" value="124ms" icon={Activity} color="text-emerald-500" />
        <StatCard title="Identities" value="1,024" icon={Users} color="text-purple-500" />
        <StatCard title="Success Rate" value="98.2%" icon={Shield} color="text-amber-500" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1 space-y-8">
          <TaskWizard />
          <LiveConsole workerId="S24-ULTRA-01" />
        </div>
        <div className="lg:col-span-2">
          <WorkerGrid />
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-bold mb-6">Active Tasks</h3>
          <div className="space-y-4">
            {[1, 2, 3].map(i => (
              <div key={i} className="p-4 bg-slate-950 rounded-lg border border-slate-800">
                <div className="flex justify-between text-sm mb-2">
                  <span>TikTok Views #0{i}</span>
                  <span className="text-emerald-500">75%</span>
                </div>
                <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                  <div className="bg-emerald-500 h-full w-3/4" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};