import React from 'react';
import { Monitor, Smartphone, Cpu, Activity } from 'lucide-react';

interface WorkerProps {
  id: string;
  type: 'lxc' | 'physical';
  status: 'idle' | 'busy' | 'error' | 'warming_up';
  load: number;
}

const WorkerNode = ({ id, type, status, load }: WorkerProps) => {
  const statusColors = {
    idle: 'bg-slate-800 border-slate-700',
    busy: 'bg-emerald-500/10 border-emerald-500/50',
    error: 'bg-rose-500/10 border-rose-500/50',
    warming_up: 'bg-amber-500/10 border-amber-500/50',
  };

  const Indicator = type === 'physical' ? Smartphone : Monitor;

  return (
    <div className={`p-3 rounded-lg border ${statusColors[status]} transition-all hover:scale-105 group relative overflow-hidden`}>
      <div className="flex justify-between items-start mb-2">
        <Indicator className={`w-4 h-4 ${status === 'busy' ? 'text-emerald-500' : 'text-slate-500'}`} />
        <div className={`w-1.5 h-1.5 rounded-full ${status === 'idle' ? 'bg-slate-600' : 'bg-emerald-500 animate-pulse'}`} />
      </div>
      <div className="text-[10px] font-bold text-slate-400 truncate">{id}</div>
      <div className="mt-2 flex items-center gap-1">
        <Cpu className="w-3 h-3 text-slate-600" />
        <div className="w-full bg-slate-950 h-1 rounded-full overflow-hidden">
          <div className="bg-blue-500 h-full" style={{ width: `${load}%` }} />
        </div>
      </div>
      
      {/* Tooltip on hover */}
      <div className="absolute inset-0 bg-slate-900/90 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
        <button className="text-[10px] font-bold text-emerald-500 uppercase tracking-tighter">View Stream</button>
      </div>
    </div>
  );
};

export const WorkerGrid = () => {
  // Mock data for 32 workers
  const workers: WorkerProps[] = [
    { id: 'S24-ULTRA-01', type: 'physical', status: 'warming_up', load: 45 },
    { id: 'MOTO-G40-01', type: 'physical', status: 'idle', load: 12 },
    ...Array.from({ length: 30 }).map((_, i) => ({
      id: `LXC-WORKER-${String(i + 1).padStart(2, '0')}`,
      type: 'lxc' as const,
      status: (i % 5 === 0 ? 'busy' : 'idle') as any,
      load: Math.floor(Math.random() * 80),
    })),
  ];

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-500" />
          Worker Plane Cluster
        </h3>
        <div className="flex gap-4 text-[10px] font-bold text-slate-500">
          <div className="flex items-center gap-1"><span className="w-2 h-2 bg-emerald-500 rounded-full" /> BUSY</div>
          <div className="flex items-center gap-1"><span className="w-2 h-2 bg-slate-600 rounded-full" /> IDLE</div>
        </div>
      </div>
      
      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3">
        {workers.map((worker) => (
          <WorkerNode key={worker.id} {...worker} />
        ))}
      </div>
    </div>
  );
};