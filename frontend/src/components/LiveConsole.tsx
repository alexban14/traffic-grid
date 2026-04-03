import React, { useState, useEffect, useRef } from "react";
import { Terminal } from "lucide-react";

export const LiveConsole = ({ workerId }: { workerId: string }) => {
  const [logs, setLogs] = useState<string[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const host = window.location.hostname;
    const port = "18420"; // Backend port
    const ws = new WebSocket(`${protocol}//${host}:${port}/api/v1/workers/${workerId}/ws`);
    
    ws.onmessage = (event) => {
      setLogs((prev) => [...prev.slice(-49), `[${new Date().toLocaleTimeString()}] ${event.data}`]);
    };

    ws.onerror = (err) => {
      console.error("WebSocket error:", err);
    };

    return () => ws.close();
  }, [workerId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-xl overflow-hidden flex flex-col h-[300px]">
      <div className="bg-slate-900 px-4 py-2 border-b border-slate-800 flex items-center gap-2">
        <Terminal className="w-4 h-4 text-slate-500" />
        <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Live Console: {workerId}</span>
      </div>
      <div ref={scrollRef} className="p-4 font-mono text-[10px] space-y-1 overflow-y-auto flex-1 scrollbar-hide">
        {logs.length === 0 && <div className="text-slate-700">Waiting for worker stream...</div>}
        {logs.map((log, i) => (
          <div key={i} className="text-emerald-400/90 font-medium">
            <span className="text-emerald-600">$</span> {log}
          </div>
        ))}
      </div>
    </div>
  );
};
