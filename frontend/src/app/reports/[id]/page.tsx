"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { ShieldAlert, CheckCircle2, ChevronLeft, GitMerge, FileCheck, ArrowRight } from "lucide-react";
import Link from "next/link";

export default function ReportDetailPage() {
  const params = useParams();
  const reportId = params.id as string;
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editComment, setEditComment] = useState("");

  const fetchReport = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/reports/${reportId}`);
      if (res.ok) {
        setReport(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [reportId]);

  useEffect(() => {
    if (reportId) fetchReport();
  }, [fetchReport, reportId]);

  if (loading) {
    return <div className="p-8 text-gray-400">Loading Report details...</div>;
  }

  if (!report) {
    return <div className="p-8 text-red-400">Report not found.</div>;
  }

  const handleReview = async (decision: string) => {
    try {
      const payload: any = { decision };
      if (decision === "EDIT") {
        payload.comment = editComment;
      }
      const res = await fetch(`/api/v1/reports/${reportId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setIsEditing(false);
        setEditComment("");
        fetchReport();
      }
    } catch (e) {
      console.error("Review failed", e);
    }
  };

  // A helper to highlight text based on evidence items
  const renderHighlightedText = () => {
    const text = report.report?.normalized_text || report.report?.original_text || "";
    if (!report.evidence || report.evidence.length === 0) {
      return (
        <p className="text-gray-300 leading-relaxed text-lg bg-white/5 p-6 rounded-xl border border-white/10">
          {text}
        </p>
      );
    }

    // Handle overlapping offsets by sorting and merging
    let intervals = report.evidence.map((ev: any) => [ev.start_offset, ev.end_offset]);
    intervals.sort((a: any, b: any) => a[0] - b[0]);
    let merged = [];
    if (intervals.length > 0) {
      let current = intervals[0];
      for (let i = 1; i < intervals.length; i++) {
        if (intervals[i][0] <= current[1]) {
          current[1] = Math.max(current[1], intervals[i][1]);
        } else {
          merged.push(current);
          current = intervals[i];
        }
      }
      merged.push(current);
    }

    let result = [];
    let lastIndex = 0;
    merged.forEach(([start, end], idx) => {
      if (start > lastIndex) {
        result.push(<span key={`t-${idx}`}>{text.substring(lastIndex, start)}</span>);
      }
      result.push(
        <span key={`h-${idx}`} className="bg-blue-500/30 text-blue-100 font-medium px-1 rounded">
          {text.substring(start, end)}
        </span>
      );
      lastIndex = end;
    });
    if (lastIndex < text.length) {
      result.push(<span key={`end`}>{text.substring(lastIndex)}</span>);
    }

    return (
      <div className="space-y-4">
        
        {report.report?.ai_used ? (
          <>
            <div className="mb-6">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
                <FileCheck className="text-gray-500" size={16} /> Original Text (Non-English)
              </h4>
              <p className="text-gray-400 leading-relaxed text-md bg-black/20 p-5 rounded-xl border border-white/5 italic">
                {report.report?.original_text}
              </p>
            </div>
            <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <ShieldAlert className="text-blue-500" size={16} /> Translated Text (English)
            </h4>
          </>
        ) : (
          <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3 flex items-center gap-2">
            <ShieldAlert className="text-blue-500" size={16} /> Original Text <span className="text-gray-500 text-xs ml-2 font-normal">(No translation needed)</span>
          </h4>
        )}
        <p className="text-gray-300 leading-relaxed text-lg bg-white/5 p-6 rounded-xl border border-white/10">
          {result.length > 0 ? result : text}
        </p>
        
        <div className="mt-4">
          <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Evidence Highlights</h4>
          <div className="space-y-2">
            {report.evidence.map((ev: any, idx: number) => (
              <div key={idx} className="bg-blue-500/10 border border-blue-500/20 text-blue-300 p-3 rounded-lg text-sm flex gap-3">
                <span className="font-mono text-blue-500 bg-blue-500/20 px-2 py-0.5 rounded text-xs shrink-0">
                  {ev.start_offset}:{ev.end_offset}
                </span>
                <div>
                  <strong className="text-white block mb-1">"{ev.phrase}"</strong>
                  <span className="text-blue-400/80">Matched Concept: {ev.concept}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center gap-4">
        <Link href="/reports" className="p-2 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors">
          <ChevronLeft size={20} />
        </Link>
        <div>
          <h1 className="text-3xl font-bold text-white mb-1">Report Details</h1>
          <p className="text-gray-400 font-mono text-sm">{report.report?.id}</p>
          {report.report?.processing_status && (
            <span className="inline-block mt-2 px-3 py-1 bg-white/10 text-white rounded-full text-xs font-semibold">
              Status: {report.report.processing_status}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Original Text & Highlights */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
            <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
              <FileCheck className="text-blue-500" size={24} /> Original Text
            </h2>
            {renderHighlightedText()}
          </div>
          
          {/* Normalization Trace */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
            <h3 className="text-lg font-semibold text-white mb-4">Normalization Trace</h3>
            <div className="space-y-3">
              {report.normalizations && report.normalizations.length > 0 && report.normalizations[0].normalization_trace && report.normalizations[0].normalization_trace.length > 0 ? (
                report.normalizations[0].normalization_trace.map((trace: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-3 text-sm text-gray-400 bg-black/40 p-3 rounded-lg">
                    <span className="font-mono text-gray-300">"{trace.from || trace.found || trace.rule}"</span>
                    <ArrowRight size={14} className="text-gray-500" />
                    <span className="font-mono text-green-400">"{trace.to || trace.concept || trace.language}"</span>
                    <span className="ml-auto text-xs text-gray-500 bg-white/5 px-2 py-1 rounded">Rule: {trace.rule}</span>
                  </div>
                ))
              ) : (
                <div className="text-gray-500 text-sm p-3 bg-black/20 rounded-lg">No normalization needed.</div>
              )}
            </div>
          </div>
        </div>

        {/* Right Column: AI & Analysis Sidebar */}
        <div className="space-y-6">
          {/* SIF Prediction Box */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">SIF Analysis</h3>
            {report.sif_prediction ? (
              <div className="space-y-4">
                <div className={`p-4 rounded-xl border flex items-center gap-3 ${report.sif_prediction.sif_potential ? 'bg-red-500/10 border-red-500/20 text-red-400' : 'bg-blue-500/10 border-blue-500/20 text-blue-400'}`}>
                  {report.sif_prediction.sif_potential ? <ShieldAlert size={24} /> : <CheckCircle2 size={24} />}
                  <div>
                    <div className="text-lg font-bold">{report.sif_prediction.sif_potential ? 'SIF Potential' : 'No SIF Potential'}</div>
                    <div className="text-xs opacity-80">Risk Band: {report.sif_prediction.risk_band}</div>
                  </div>
                </div>
                <div className="flex justify-between text-sm text-gray-400">
                  <span>Score: {(report.sif_prediction.score * 100).toFixed(1)}%</span>
                  <span>Confidence: {(report.sif_prediction.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No SIF data available.</div>
            )}
          </div>

          {/* LSR Predictions Box */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Life-Saving Rules</h3>
            {report.lsr_predictions && report.lsr_predictions.length > 0 ? (
              <ul className="space-y-3">
                {report.lsr_predictions.map((lsr: any, idx: number) => (
                  <li key={idx} className="bg-orange-500/10 border border-orange-500/20 text-orange-400 px-4 py-3 rounded-xl text-sm font-medium">
                    <div className="flex justify-between items-center mb-1">
                      <span>{lsr.rule_id}</span>
                      <span className="text-xs opacity-70">{(lsr.confidence * 100).toFixed(0)}% Conf</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-gray-500 text-sm">No LSR matches.</div>
            )}
          </div>

          {/* Extracted Entities */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Extracted Entities</h3>
            {report.entities && report.entities.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {report.entities.map((ent: any, idx: number) => (
                  <span key={idx} className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 px-2 py-1 rounded text-xs font-medium">
                    {ent.entity_type}: {ent.value}
                  </span>
                ))}
              </div>
            ) : (
              <div className="text-gray-500 text-sm">No entities extracted.</div>
            )}
          </div>

          {/* Review History */}
          {report.reviews && report.reviews.length > 0 && (
            <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
              <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Review History</h3>
              <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {report.reviews.map((rev: any, idx: number) => (
                  <div key={idx} className="bg-black/40 border border-white/5 p-4 rounded-xl space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="font-semibold text-gray-300">{rev.reviewer_id}</span>
                      <span className="text-gray-500">{new Date(rev.created_at).toLocaleString()}</span>
                    </div>
                    <div className="text-xs">
                      Decision: <span className={`font-semibold ${rev.decision === 'CONFIRM' ? 'text-blue-400' : rev.decision === 'REJECT' ? 'text-red-400' : 'text-gray-300'}`}>{rev.decision}</span>
                    </div>
                    {rev.comment && (
                      <div className="text-sm text-gray-300 mt-2 p-3 bg-white/5 rounded-lg border border-white/5">
                        {rev.comment}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Review Actions */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Review Action</h3>
            {!isEditing ? (
              <div className="space-y-3">
                <button onClick={() => handleReview("CONFIRM")} className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-colors shadow-lg shadow-blue-500/20">
                  Confirm Machine Decision
                </button>
                <button onClick={() => handleReview("REJECT")} className="w-full bg-red-600/20 hover:bg-red-600/40 text-red-400 font-medium py-3 rounded-xl transition-colors shadow-lg shadow-red-500/10">
                  Reject Decision
                </button>
                <button onClick={() => setIsEditing(true)} className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 font-medium py-3 rounded-xl transition-colors">
                  Override / Edit
                </button>
              </div>
            ) : (
              <div className="space-y-3 animate-in fade-in">
                <textarea 
                  value={editComment}
                  onChange={(e) => setEditComment(e.target.value)}
                  placeholder="Enter correction notes..."
                  className="w-full h-24 bg-black/40 border border-white/10 rounded-xl p-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none text-sm"
                />
                <div className="flex gap-2">
                  <button onClick={() => setIsEditing(false)} className="flex-1 bg-white/5 hover:bg-white/10 text-gray-300 py-2 rounded-lg text-sm transition-colors border border-white/10">
                    Cancel
                  </button>
                  <button 
                    onClick={() => handleReview("EDIT")} 
                    disabled={!editComment.trim()}
                    className="flex-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white py-2 rounded-lg text-sm transition-colors shadow-lg shadow-blue-500/20"
                  >
                    Submit Edit
                  </button>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
