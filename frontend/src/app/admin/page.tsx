"use client";

import { useEffect, useState } from "react";
import { Server, Database, Activity, RefreshCw } from "lucide-react";

export default function AdminPage() {
  const [health, setHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchHealth = async () => {
    setLoading(true);
    try {
      const [res1, res2] = await Promise.all([
        fetch("/api/v1/health"),
        fetch("/api/v1/health/dependencies")
      ]);
      if (res1.ok && res2.ok) {
        const data1 = await res1.json();
        const data2 = await res2.json();
        setHealth({ ...data1, ...data2 });
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-1000">
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-6 border-b border-[var(--color-claude-border)] pb-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-[var(--color-claude-text)] mb-3 tracking-tight">System Status</h1>
          <p className="text-[var(--color-claude-text-secondary)] text-lg">Monitor platform health, API dependencies, and versioning.</p>
        </div>
        <button 
          onClick={fetchHealth}
          className="flex items-center gap-2 px-5 py-2.5 bg-white border border-[var(--color-claude-border-strong)] rounded-lg hover:bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text)] text-sm font-medium transition-colors shadow-sm"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          Refresh Diagnostics
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
           <h2 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-6 flex items-center gap-2 border-b border-[var(--color-claude-border)] pb-3">
             <Activity size={18} className="text-[var(--color-claude-accent)]" /> Platform Health
           </h2>
           {loading ? (
             <div className="text-[var(--color-claude-text-secondary)] font-serif italic py-4">Running diagnostics...</div>
           ) : health ? (
             <div className="space-y-3">
               <div className="flex justify-between p-4 bg-[var(--color-claude-bg-secondary)] rounded-lg border border-[var(--color-claude-border)]">
                 <span className="text-[var(--color-claude-text-secondary)] font-medium">Status</span>
                 <span className={health.status === "ok" ? "text-green-700 font-bold" : "text-red-700 font-bold"}>
                   {health.status.toUpperCase()}
                 </span>
               </div>
               <div className="flex justify-between p-4 bg-[var(--color-claude-bg-secondary)] rounded-lg border border-[var(--color-claude-border)]">
                 <span className="text-[var(--color-claude-text-secondary)] font-medium">Version Release</span>
                 <span className="text-[var(--color-claude-text)] font-mono text-base">{health.version}</span>
               </div>
             </div>
           ) : (
             <div className="text-red-700 font-medium py-4">Failed to connect to health endpoints.</div>
           )}
        </div>

        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
           <h2 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-6 flex items-center gap-2 border-b border-[var(--color-claude-border)] pb-3">
             <Database size={18} className="text-[#8B9A84]" /> Dependency Health
           </h2>
           {loading ? (
             <div className="text-[var(--color-claude-text-secondary)] font-serif italic py-4">Running diagnostics...</div>
           ) : health ? (
             <div className="space-y-3">
               <div className="flex justify-between p-4 bg-[var(--color-claude-bg-secondary)] rounded-lg border border-[var(--color-claude-border)]">
                 <span className="text-[var(--color-claude-text-secondary)] font-medium">PostgreSQL Database</span>
                 <span className={health.database === "ok" ? "text-green-700 font-bold flex items-center gap-2" : "text-red-700 font-bold flex items-center gap-2"}>
                   {health.database === "ok" && <span className="w-2 h-2 rounded-full bg-green-500"></span>}
                   {health.database ? health.database.toUpperCase() : "UNKNOWN"}
                 </span>
               </div>
               <div className="flex justify-between p-4 bg-[var(--color-claude-bg-secondary)] rounded-lg border border-[var(--color-claude-border)]">
                 <span className="text-[var(--color-claude-text-secondary)] font-medium">LLM Provider</span>
                 <span className={health.ai_provider === "ok" ? "text-green-700 font-bold flex items-center gap-2" : "text-red-700 font-bold flex items-center gap-2"}>
                   {health.ai_provider === "ok" && <span className="w-2 h-2 rounded-full bg-green-500"></span>}
                   {health.ai_provider ? health.ai_provider.toUpperCase() : "UNKNOWN"}
                 </span>
               </div>
               <div className="flex justify-between p-4 bg-[var(--color-claude-bg-secondary)] rounded-lg border border-[var(--color-claude-border)]">
                 <span className="text-[var(--color-claude-text-secondary)] font-medium">Application Mode</span>
                 <span className="text-[var(--color-claude-text)] font-medium capitalize">
                   {health.app_mode || "online"}
                 </span>
               </div>
             </div>
           ) : (
             <div className="text-red-700 font-medium py-4">Failed to load dependencies.</div>
           )}
        </div>
      </div>
    </div>
  );
}
