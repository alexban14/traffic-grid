import React from "react";
import { Monitor, Smartphone, Activity } from "lucide-react";
import { useWorkers } from "../hooks/useGridData";

const WorkerNode = ({ id, type, status, load }: any) => {
  const statusColors: any = {
    idle: "bg-slate-800 border-slate-700",
    busy: "bg-emerald-500/10 border-emerald-500/50",
    error: "bg-rose-500/10 border-rose-500/50",
    warming_up: "bg-amber-500/10 border-amber-500/50",
  };

  const Indicator = type === "physical" ? Smartphone : Monitor;

  return (
    <div className={`p-3 rounded-lg border ${statusColors[status] || statusColors.idle} transition-all hover:scale-105 group relative overflow-hidden`}>
      <div className="flex justify-between items-start mb-2">
        <Indicator className={`w-4 h-4 ${status === "busy" ? "text-emerald-500" : "text-slate-500"}`} />
        <div className={`w-1.5 h-1.5 rounded-full ${status === "idle" ? "bg-slate-600" : "bg-emerald-500 animate-pulse"}`} />
      </div>
      <div className="text-[10px] font-bold text-slate-400 truncate">{id}</div>
    </div>
  );
};

export const WorkerGrid = () => {
  const { data: workers, isLoading } = useWorkers();

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-bold flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-500" />
          Worker Plane Cluster
        </h3>
      </div>
      
      {isLoading ? (
        <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3">
           {Array.from({ length: 8 }).map((_, i) => (
             <div key={i} className="h-16 bg-slate-800 animate-pulse rounded-lg" />
           ))}
        </div>
      ) : (
        <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3">
          {workers?.map((worker: any) => (
            <WorkerNode key={worker.id} {...worker} />
          ))}
          {(!workers || workers.length === 0) && (
            <div className="col-span-full text-center py-8 text-slate-500 text-sm">
              No active workers detected. Start a heartbeat script.
            </div>
          )}
        </div>
      )}
    </div>
  );
};
