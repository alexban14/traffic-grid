import React, { useState } from "react";
import { Send, Target, CheckCircle, XCircle } from "lucide-react";
import type { DispatchResponse } from "../types/api";

export const TaskWizard = () => {
  const [taskType, setTaskType] = useState("tiktok_views");
  const [targetUrl, setTargetUrl] = useState("");
  const [volume, setVolume] = useState(1000);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleDispatch = async () => {
    setIsSubmitting(true);
    setLastResult(null);
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
      if (!res.ok) throw new Error("Failed to dispatch task");
      const data: DispatchResponse = await res.json();
      setLastResult({ success: true, message: `Task #${data.task_id} queued` });
    } catch (err) {
      console.error(err);
      setLastResult({ success: false, message: "Failed to dispatch task" });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
      <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
        <Target className="w-5 h-5 text-emerald-500" />
        New Task Orchestration
      </h3>

      <div className="space-y-6">
        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Platform & Action</label>
          <select
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors"
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
          >
            <option value="tiktok_views">TikTok: Mass Views</option>
            <option value="tiktok_warmup">TikTok: Account Warm-up (Physical)</option>
            <option value="yt_watchtime">YouTube: Watch Time Boost</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Target URL</label>
          <input
            type="text"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder="https://www.tiktok.com/@user/video/..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Volume</label>
          <input
            type="number"
            value={volume}
            onChange={(e) => setVolume(parseInt(e.target.value) || 0)}
            placeholder="1,000"
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors"
          />
        </div>

        {lastResult && (
          <div className={`flex items-center gap-2 text-sm ${lastResult.success ? "text-emerald-400" : "text-rose-400"}`}>
            {lastResult.success ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
            {lastResult.message}
          </div>
        )}

        <button
          onClick={handleDispatch}
          disabled={isSubmitting || !targetUrl}
          className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-900/20"
        >
          <Send className="w-4 h-4" />
          {isSubmitting ? "Dispatching..." : "Dispatch to Grid"}
        </button>
      </div>
    </div>
  );
};
