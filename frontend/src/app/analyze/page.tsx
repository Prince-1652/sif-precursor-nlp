"use client";

import { useState } from "react";
import { ShieldAlert, CheckCircle2, ChevronRight, Loader2, ArrowRight } from "lucide-react";
import ReactMarkdown from "react-markdown";

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
        
        if (res.status === 429) {
          errorMsg = "Too many requests. Please slow down.";
        } else if (res.status >= 500) {
          errorMsg = "Backend server is down or restarting due to a code change. Wait a few seconds and try again.";
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
      }
    } catch (e: any) {
      setError(e.message || "Network error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-1000">
      <div className="border-b border-[var(--color-claude-border)] pb-5">
        <h1 className="text-4xl md:text-5xl font-serif font-bold text-[var(--color-claude-text)] mb-3 tracking-tight">Live Analysis</h1>
        <p className="text-[var(--color-claude-text-secondary)] text-lg">Test the intelligence pipeline synchronously without database persistence.</p>
      </div>

      <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm transition-all focus-within:border-[var(--color-claude-border-strong)] focus-within:shadow-md">
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste a narrative or incident report here..."
          className="w-full h-48 bg-transparent text-[var(--color-claude-text)] placeholder-[var(--color-claude-text-secondary)] focus:outline-none resize-none mb-6 text-lg leading-relaxed italic font-serif"
        />
        <div className="flex justify-end border-t border-[var(--color-claude-border)] pt-6">
          <button
            onClick={handleAnalyze}
            disabled={loading || !text.trim()}
            className="px-8 py-3 bg-[var(--color-claude-accent)] hover:bg-[var(--color-claude-accent-hover)] text-white rounded-md font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 shadow-sm"
          >
            {loading ? <Loader2 size={18} className="animate-spin" /> : <span>Run Pipeline</span>}
            {!loading && <ChevronRight size={18} />}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 border border-red-200 p-5 rounded-xl animate-in fade-in flex items-start gap-4">
          <ShieldAlert size={20} className="mt-0.5 shrink-0" />
          <span className="font-medium">{error}</span>
        </div>
      )}

      {result && (
        <div className="space-y-8 animate-in slide-in-from-bottom-4 duration-700 pt-4">
          <h2 className="text-2xl font-serif font-medium text-[var(--color-claude-text)] border-b border-[var(--color-claude-border)] pb-3">Analysis Results</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Left Column */}
            <div className="space-y-8">
              <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Pipeline Metrics</h3>
                <div className="space-y-3 text-base">
                  <div className="flex justify-between items-center py-2 border-b border-[var(--color-claude-border)]">
                    <span className="text-[var(--color-claude-text-secondary)]">Processing Path:</span>
                    <span className="font-medium text-[var(--color-claude-text)] bg-[var(--color-claude-bg-secondary)] px-2 py-1 rounded text-sm">{result.processing_path || "N/A"}</span>
                  </div>
                  <div className="flex justify-between items-center py-2 border-b border-[var(--color-claude-border)]">
                    <span className="text-[var(--color-claude-text-secondary)]">Review State:</span>
                    <span className="font-medium text-[var(--color-claude-text)]">{result.review_state || "N/A"}</span>
                  </div>
                  <div className="flex justify-between items-center py-2">
                    <span className="text-[var(--color-claude-text-secondary)]">AI Used:</span>
                    <span className="font-medium text-[var(--color-claude-text)]">{result.ai_used ? "Yes" : "No"}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
                 <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Normalization Trace</h3>
                 {result.normalization && result.normalization.normalization_trace && result.normalization.normalization_trace.length > 0 ? (
                   <div className="space-y-3">
                     {result.normalization.normalization_trace.map((trace: any, idx: number) => (
                       <div key={idx} className="flex flex-col gap-1 text-base bg-[var(--color-claude-bg-secondary)] p-3 rounded-lg border border-[var(--color-claude-border)]">
                         <span className="font-mono text-[var(--color-claude-text-secondary)] line-through decoration-red-300">"{trace.from}"</span>
                         <span className="font-mono text-[var(--color-claude-text)]">"{trace.to}"</span>
                       </div>
                     ))}
                   </div>
                 ) : (
                   <div className="text-[var(--color-claude-text-secondary)] text-base italic font-serif">No text normalization was required.</div>
                 )}
              </div>

              {/* AI Summary in Left Column */}
              {result.ai_summary && (
                <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
                  <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-3 flex items-center gap-2">
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[var(--color-claude-accent)]"></span>
                    </span>
                    AI Summary
                  </h3>
                  <p className="text-[var(--color-claude-text)] text-base leading-relaxed">
                    {result.ai_summary}
                  </p>
                </div>
              )}
            </div>

            {/* Right Column */}
            <div className="space-y-8">
              <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Predictions</h3>
                {result.sif_prediction && (
                  <div className={`p-5 rounded-lg border mb-5 ${result.sif_prediction.sif_potential ? 'bg-[#FCF5F3] border-[#F2DCD5] text-[var(--color-claude-accent)]' : 'bg-[#F2F6F3] border-[#DCE4DD] text-[#5C6E53]'}`}>
                    <div className="flex items-start gap-4">
                      {result.sif_prediction.sif_potential ? <ShieldAlert size={28} className="shrink-0 mt-1" /> : <CheckCircle2 size={28} className="shrink-0 mt-1" />}
                      <div>
                        <div className="text-xl font-serif font-medium">{result.sif_prediction.sif_potential ? 'SIF Potential Identified' : 'No SIF Potential'}</div>
                        <div className="text-base mt-1 opacity-80">Risk Band: <span className="font-bold">{result.sif_prediction.risk_band}</span></div>
                      </div>
                    </div>
                  </div>
                )}
                
                {result.lsr_predictions && result.lsr_predictions.length > 0 && (
                  <div>
                    <h4 className="text-sm text-[var(--color-claude-text-secondary)] mb-3">Life-Saving Rules Triggered</h4>
                    <div className="flex flex-wrap gap-2">
                      {result.lsr_predictions.map((lsr: any, idx: number) => (
                        <span key={idx} className="bg-white border border-[var(--color-claude-border-strong)] text-[var(--color-claude-text)] px-3 py-1.5 rounded-md text-sm font-medium shadow-sm">
                          {lsr.rule_id}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
                <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Extracted Entities</h3>
                {result.entities && result.entities.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {result.entities.map((ent: any, idx: number) => (
                      <span key={idx} className="bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border)] text-[var(--color-claude-text)] px-3 py-1.5 rounded-md text-sm font-medium">
                        <span className="text-[var(--color-claude-text-secondary)] mr-1">{ent.entity_type}:</span> {ent.value}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="text-[var(--color-claude-text-secondary)] text-base italic font-serif">No entities identified in text.</div>
                )}
              </div>
              {/* AI Solution in Right Column */}
              {result.ai_solution && (
                <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
                  <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-3 flex items-center gap-2">
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-green-500"></span>
                    </span>
                    AI Proposed Solution
                  </h3>
                  <div className="text-[var(--color-claude-text)] text-base leading-relaxed markdown-content">
                    <ReactMarkdown
                      components={{
                        ul: ({node, ...props}) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                        ol: ({node, ...props}) => <ol className="list-decimal pl-5 my-2 space-y-1" {...props} />,
                        li: ({node, ...props}) => <li className="pl-1" {...props} />,
                        strong: ({node, ...props}) => <strong className="font-bold text-[var(--color-claude-text)]" {...props} />,
                        p: ({node, ...props}) => <p className="mb-2" {...props} />
                      }}
                    >
                      {result.ai_solution}
                    </ReactMarkdown>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
