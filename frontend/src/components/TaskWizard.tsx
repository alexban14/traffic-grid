import React, { useState } from 'react';
import { Send, Clock, Target, Layers } from 'lucide-react';

export const TaskWizard = () => {
  const [taskType, setTaskType] = useState('tiktok_views');
  
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
            <option value="ig_engagement">Instagram: Engagement Loop</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Target URL</label>
          <input 
            type="text" 
            placeholder="https://www.tiktok.com/@user/video/..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Volume</label>
            <input 
              type="number" 
              placeholder="10,000"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Duration (Hours)</label>
            <input 
              type="number" 
              placeholder="48"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-sm focus:border-emerald-500 outline-none transition-colors"
            />
          </div>
        </div>

        <button className="w-full py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-lg flex items-center justify-center gap-2 transition-all shadow-lg shadow-emerald-900/20">
          <Send className="w-4 h-4" />
          Dispatch to Grid
        </button>
      </div>
    </div>
  );
};