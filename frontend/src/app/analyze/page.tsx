"use client";

import { useState } from "react";
import { ShieldAlert, CheckCircle2, ChevronRight, Loader2, ArrowRight } from "lucide-react";

export default function AnalyzePage() {
  const [text, setText] = useState("");
  const [reportType, setReportType] = useState("INCIDENT");
  const [sourceId, setSourceId] = useState("");
  const [reportDate, setReportDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setResult(null);
    setError(null);

    try {
      let res: Response | null = null;
      let attempt = 0;
      
      // Auto-retry up to 3 times for 500/502 errors to handle Uvicorn --reload downtime
      while (attempt < 3) {
        res = await fetch("/api/v1/reports/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            original_text: text,
            report_type: reportType,
            site_id: undefined,
            source_record_id: sourceId || undefined,
            reported_at: reportDate ? new Date(reportDate).toISOString() : undefined
          })
        });
        
        if (res.ok || res.status < 500) break;
        
        // Wait 1 second before retrying to let the backend finish restarting
        await new Promise(r => setTimeout(r, 1000));
        attempt++;
      }
      
      if (!res) throw new Error("Network error occurred");
      if (res.ok) {
        setResult(await res.json());
      } else {
        const errorData = await res.json().catch(() => null);
        let errorMsg = "Analysis failed due to a server error.";
        
        if (res.status >= 500) {
          errorMsg = "Backend server is down or restarting due to a code change. Wait a few seconds and try again, or check your terminal for syntax errors.";
        } else if (errorData?.detail) {
          if (Array.isArray(errorData.detail)) {
            errorMsg = errorData.detail.map((e: any) => `${e.loc?.join('.')}: ${e.msg}`).join(', ');
          } else if (typeof errorData.detail === 'string') {
            errorMsg = errorData.detail;
          } else {
            errorMsg = JSON.stringify(errorData.detail);
          }
        }
        setError(errorMsg);
        console.error("Analysis failed:", errorData || `HTTP ${res.status}`);
      }
    } catch (e: any) {
      setError(e.message || "Network error occurred");
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in duration-700">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Live Analysis</h1>
        <p className="text-gray-400">Test the processing pipeline synchronously without writing to the database.</p>
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
        {/* Unused metadata fields removed for clarity */}
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste an incident report here..."
          className="w-full h-40 bg-black/40 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none mb-4"
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !text.trim()}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-blue-500/20"
        >
          {loading ? <Loader2 size={18} className="animate-spin" /> : <ChevronRight size={18} />}
          Run Analysis
        </button>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl animate-in fade-in flex items-center gap-3">
          <ShieldAlert size={20} />
          <span>{error}</span>
        </div>
      )}

      {result && (
        <div className="space-y-6 animate-in slide-in-from-bottom-4 duration-500">
          <h2 className="text-xl font-semibold text-white">Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Left Column */}
            <div className="space-y-6">
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Pipeline Metrics</h3>
                <div className="space-y-2 text-sm text-gray-300">
                  <div className="flex justify-between p-2 bg-white/5 rounded">
                    <span>Processing Path:</span>
                    <span className="font-medium text-white">{result.processing_path || "N/A"}</span>
                  </div>
                  <div className="flex justify-between p-2 bg-white/5 rounded">
                    <span>Review State:</span>
                    <span className="font-medium text-white">{result.review_state || "N/A"}</span>
                  </div>
                  <div className="flex justify-between p-2 bg-white/5 rounded">
                    <span>AI Used:</span>
                    <span className="font-medium text-white">{result.ai_used ? "Yes" : "No"}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                 <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Normalization Trace</h3>
                 {result.normalization && result.normalization.normalization_trace && result.normalization.normalization_trace.length > 0 ? (
                   <div className="space-y-2">
                     {result.normalization.normalization_trace.map((trace: any, idx: number) => (
                       <div key={idx} className="flex items-center gap-2 text-xs text-gray-400">
                         <span className="font-mono text-gray-300 truncate max-w-[100px]">"{trace.from}"</span>
                         <ArrowRight size={12} />
                         <span className="font-mono text-green-400 truncate max-w-[100px]">"{trace.to}"</span>
                       </div>
                     ))}
                   </div>
                 ) : (
                   <div className="text-gray-500 text-sm">No normalization needed.</div>
                 )}
              </div>
            </div>

            {/* Right Column */}
            <div className="space-y-6">
              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Predictions</h3>
                {result.sif_prediction && (
                  <div className={`p-4 rounded-xl border flex items-center gap-3 mb-4 ${result.sif_prediction.sif_potential ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-blue-500/10 border-blue-500/20 text-blue-400'}`}>
                    {result.sif_prediction.sif_potential ? <ShieldAlert size={24} /> : <CheckCircle2 size={24} />}
                    <div>
                      <div className="text-lg font-bold">{result.sif_prediction.sif_potential ? 'SIF Potential' : 'No SIF Potential'}</div>
                      <div className="text-xs opacity-80">Risk Band: {result.sif_prediction.risk_band}</div>
                    </div>
                  </div>
                )}
                
                {result.lsr_predictions && result.lsr_predictions.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-xs text-gray-500 mb-2">Life-Saving Rules</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.lsr_predictions.map((lsr: any, idx: number) => (
                        <span key={idx} className="bg-orange-500/10 border border-orange-500/20 text-orange-400 px-3 py-1 rounded-md text-xs font-medium">
                          {lsr.rule_id}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-white/5 border border-white/10 rounded-xl p-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Extracted Entities</h3>
                {result.entities && result.entities.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.entities.map((ent: any, idx: number) => (
                      <span key={idx} className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2 py-1 rounded text-xs font-medium">
                        {ent.entity_type}: {ent.value}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500 text-sm">No entities found.</div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
