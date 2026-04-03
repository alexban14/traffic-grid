import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React from "react";
import { Monitor, Smartphone, Activity } from "lucide-react";
import { useWorkers } from "../hooks/useGridData";
const WorkerNode = ({ id, type, status, load }) => {
    const statusColors = {
        idle: "bg-slate-800 border-slate-700",
        busy: "bg-emerald-500/10 border-emerald-500/50",
        error: "bg-rose-500/10 border-rose-500/50",
        warming_up: "bg-amber-500/10 border-amber-500/50",
    };
    const Indicator = type === "physical" ? Smartphone : Monitor;
    return (_jsxs("div", { className: `p-3 rounded-lg border ${statusColors[status] || statusColors.idle} transition-all hover:scale-105 group relative overflow-hidden`, children: [_jsxs("div", { className: "flex justify-between items-start mb-2", children: [_jsx(Indicator, { className: `w-4 h-4 ${status === "busy" ? "text-emerald-500" : "text-slate-500"}` }), _jsx("div", { className: `w-1.5 h-1.5 rounded-full ${status === "idle" ? "bg-slate-600" : "bg-emerald-500 animate-pulse"}` })] }), _jsx("div", { className: "text-[10px] font-bold text-slate-400 truncate", children: id })] }));
};
export const WorkerGrid = () => {
    const { data: workers, isLoading } = useWorkers();
    return (_jsxs("div", { className: "bg-slate-900 border border-slate-800 rounded-xl p-6", children: [_jsx("div", { className: "flex justify-between items-center mb-6", children: _jsxs("h3", { className: "text-lg font-bold flex items-center gap-2", children: [_jsx(Activity, { className: "w-5 h-5 text-blue-500" }), "Worker Plane Cluster"] }) }), isLoading ? (_jsx("div", { className: "grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3", children: Array.from({ length: 8 }).map((_, i) => (_jsx("div", { className: "h-16 bg-slate-800 animate-pulse rounded-lg" }, i))) })) : (_jsxs("div", { className: "grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-3", children: [workers?.map((worker) => (_jsx(WorkerNode, { ...worker }, worker.id))), (!workers || workers.length === 0) && (_jsx("div", { className: "col-span-full text-center py-8 text-slate-500 text-sm", children: "No active workers detected. Start a heartbeat script." }))] }))] }));
};
//# sourceMappingURL=WorkerGrid.js.map