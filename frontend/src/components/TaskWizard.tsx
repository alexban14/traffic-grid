import React, { useState } from "react";
import { Send, Target, CheckCircle, XCircle } from "lucide-react";
import type { DispatchResponse } from "../types/api";
import { apiFetch } from "../lib/api";

export const TaskWizard = () => {
  const [taskType, setTaskType] = useState("tiktok_views");
  const [targetUrl, setTargetUrl] = useState("");
  const [volume, setVolume] = useState(1);
  const [dripMinutes, setDripMinutes] = useState(0);
  const [accountType, setAccountType] = useState("any");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isProfileBoost = taskType === "tiktok_profile_boost";
  const [lastResult, setLastResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleDispatch = async () => {
    setIsSubmitting(true);
    setLastResult(null);
    try {
      const res = await apiFetch("/api/v1/workers/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          task_type: taskType,
          target_url: targetUrl,
          volume: parseInt(volume.toString()),
          drip_minutes: dripMinutes > 0 ? dripMinutes : null,
          account_type: accountType !== "any" ? accountType : null,
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
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-300 focus:border-emerald-500 outline-none transition-colors"
            value={taskType}
            onChange={(e) => setTaskType(e.target.value)}
          >
            <option value="tiktok_views">TikTok: Single Video Views</option>
            <option value="tiktok_profile_boost">TikTok: Profile Boost (All Videos)</option>
            <option value="tiktok_warmup">TikTok: Account Warm-up (Physical)</option>
            <option value="yt_watchtime">YouTube: Watch Time Boost</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
            {isProfileBoost ? "Profile URL" : "Target URL"}
          </label>
          <input
            type="text"
            value={targetUrl}
            onChange={(e) => setTargetUrl(e.target.value)}
            placeholder={isProfileBoost ? "https://www.tiktok.com/@username" : "https://www.tiktok.com/@user/video/... or vm.tiktok.com/..."}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-50 placeholder:text-slate-700 focus:border-emerald-500 outline-none transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
            {isProfileBoost ? "Views per Video" : "Volume"}
          </label>
          <input
            type="number"
            value={volume}
            onChange={(e) => setVolume(parseInt(e.target.value) || 0)}
            placeholder="1,000"
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-50 placeholder:text-slate-700 focus:border-emerald-500 outline-none transition-colors"
          />
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Identity Type</label>
          <select
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-300 focus:border-emerald-500 outline-none transition-colors"
            value={accountType}
            onChange={(e) => setAccountType(e.target.value)}
          >
            <option value="any">Any (prefer authenticated)</option>
            <option value="authenticated">Authenticated only (logged-in accounts)</option>
            <option value="anonymous">Anonymous only (FYP cookies)</option>
          </select>
        </div>

        {isProfileBoost && (
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">
              Drip-Feed (minutes)
            </label>
            <input
              type="number"
              value={dripMinutes}
              onChange={(e) => setDripMinutes(parseInt(e.target.value) || 0)}
              placeholder="0 = all at once"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm text-slate-50 placeholder:text-slate-700 focus:border-emerald-500 outline-none transition-colors"
            />
            <p className="text-xs text-slate-600 mt-1">
              {dripMinutes > 0 ? `Views spread over ${dripMinutes} min with random jitter` : "All views dispatched immediately"}
            </p>
          </div>
        )}

        {lastResult && (
          <div className={`flex items-center gap-2 text-sm ${lastResult.success ? "text-emerald-400" : "text-rose-400"}`}>
            {lastResult.success ? <CheckCircle className="w-4 h-4" /> : <XCircle className="w-4 h-4" />}
            {lastResult.message}
          </div>
        )}

        <button
          onClick={handleDispatch}
          disabled={isSubmitting || !targetUrl}
          className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 disabled:text-slate-600 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-900/20"
        >
          <Send className="w-4 h-4" />
          {isSubmitting ? "Dispatching..." : "Dispatch to Grid"}
        </button>
      </div>
    </div>
  );
};
