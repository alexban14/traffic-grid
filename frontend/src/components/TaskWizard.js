import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import React, { useState } from "react";
import { Send, Target } from "lucide-react";
export const TaskWizard = () => {
    const [taskType, setTaskType] = useState("tiktok_views");
    const [targetUrl, setTargetUrl] = useState("");
    const [volume, setVolume] = useState(1000);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const handleDispatch = async () => {
        setIsSubmitting(true);
        try {
            const res = await fetch("/api/v1/workers/dispatch", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    task_type: taskType,
                    target_url: targetUrl,
                    volume: parseInt(volume.toString()),
                }),
            });
            if (!res.ok)
                throw new Error("Failed to dispatch task");
            alert("Task dispatched successfully!");
        }
        catch (err) {
            console.error(err);
            alert("Error dispatching task.");
        }
        finally {
            setIsSubmitting(false);
        }
    };
    return (_jsxs("div", { className: "bg-slate-900 border border-slate-800 rounded-xl p-6", children: [_jsxs("h3", { className: "text-lg font-bold mb-6 flex items-center gap-2", children: [_jsx(Target, { className: "w-5 h-5 text-emerald-500" }), "New Task Orchestration"] }), _jsxs("div", { className: "space-y-6", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-xs font-bold text-slate-500 uppercase mb-2", children: "Platform & Action" }), _jsxs("select", { className: "w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors", value: taskType, onChange: (e) => setTaskType(e.target.value), children: [_jsx("option", { value: "tiktok_views", children: "TikTok: Mass Views" }), _jsx("option", { value: "tiktok_warmup", children: "TikTok: Account Warm-up (Physical)" }), _jsx("option", { value: "yt_watchtime", children: "YouTube: Watch Time Boost" })] })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-xs font-bold text-slate-500 uppercase mb-2", children: "Target URL" }), _jsx("input", { type: "text", value: targetUrl, onChange: (e) => setTargetUrl(e.target.value), placeholder: "https://www.tiktok.com/@user/video/...", className: "w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors" })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-xs font-bold text-slate-500 uppercase mb-2", children: "Volume" }), _jsx("input", { type: "number", value: volume, onChange: (e) => setVolume(parseInt(e.target.value)), placeholder: "1,000", className: "w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors" })] }), _jsxs("button", { onClick: handleDispatch, disabled: isSubmitting, className: "w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-900/20", children: [_jsx(Send, { className: "w-4 h-4" }), isSubmitting ? "Dispatching..." : "Dispatch to Grid"] })] })] }));
};
//# sourceMappingURL=TaskWizard.js.map