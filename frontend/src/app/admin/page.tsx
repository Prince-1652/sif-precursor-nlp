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
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">System Admin</h1>
          <p className="text-gray-400">Monitor platform health, AI providers, and system dependencies.</p>
        </div>
        <button 
          onClick={fetchHealth}
          className="flex items-center gap-2 px-4 py-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 text-white text-sm transition-colors"
        >
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
          Refresh Status
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
           <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
             <Activity className="text-blue-500" /> Platform Status
           </h2>
           {loading ? (
             <div className="text-gray-500">Checking...</div>
           ) : health ? (
             <div className="space-y-4">
               <div className="flex justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                 <span className="text-gray-400">Status</span>
                 <span className={health.status === "ok" ? "text-green-500 font-medium" : "text-red-500 font-medium"}>
                   {health.status.toUpperCase()}
                 </span>
               </div>
               <div className="flex justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                 <span className="text-gray-400">Version</span>
                 <span className="text-white font-mono">{health.version}</span>
               </div>
             </div>
           ) : (
             <div className="text-red-500">Failed to load health status.</div>
           )}
        </div>

        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
           <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
             <Database className="text-indigo-500" /> Dependency Health
           </h2>
           {loading ? (
             <div className="text-gray-500">Checking...</div>
           ) : health ? (
             <div className="space-y-4">
               <div className="flex justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                 <span className="text-gray-300 capitalize">Database</span>
                 <span className={health.database === "ok" ? "text-green-500 font-medium" : "text-red-500 font-medium"}>
                   {health.database ? health.database.toUpperCase() : "UNKNOWN"}
                 </span>
               </div>
               <div className="flex justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                 <span className="text-gray-300 capitalize">AI Provider</span>
                 <span className={health.ai_provider === "ok" ? "text-green-500 font-medium" : "text-red-500 font-medium"}>
                   {health.ai_provider ? health.ai_provider.toUpperCase() : "UNKNOWN"}
                 </span>
               </div>
               <div className="flex justify-between p-3 bg-white/5 rounded-xl border border-white/5">
                 <span className="text-gray-300 capitalize">App Mode</span>
                 <span className="text-white font-medium capitalize">
                   {health.app_mode || "online"}
                 </span>
               </div>
             </div>
           ) : (
             <div className="text-red-500">Failed to load dependencies.</div>
           )}
        </div>
      </div>
    </div>
  );
}
