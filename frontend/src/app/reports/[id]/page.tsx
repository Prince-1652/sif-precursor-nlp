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
      const res = await fetch(`/api/v1/reports/${reportId}/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ decision })
      });
      if (res.ok) {
        fetchReport();
      }
    } catch (e) {
      console.error("Review failed", e);
    }
  };

  // A helper to highlight text based on evidence items
  const renderHighlightedText = () => {
    const text = report.report?.original_text || "";
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
          {report.normalizations && report.normalizations.length > 0 && report.normalizations[0].normalization_trace && (
             <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
               <h3 className="text-lg font-semibold text-white mb-4">Normalization Trace</h3>
               <div className="space-y-3">
                 {report.normalizations[0].normalization_trace.map((trace: any, idx: number) => (
                   <div key={idx} className="flex items-center gap-3 text-sm text-gray-400 bg-black/40 p-3 rounded-lg">
                     <span className="font-mono text-gray-300">"{trace.from || trace.found || trace.rule}"</span>
                     <ArrowRight size={14} className="text-gray-500" />
                     <span className="font-mono text-green-400">"{trace.to || trace.concept || trace.language}"</span>
                     <span className="ml-auto text-xs text-gray-500 bg-white/5 px-2 py-1 rounded">Rule: {trace.rule}</span>
                   </div>
                 ))}
               </div>
             </div>
          )}
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

          {/* Review Actions */}
          <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Review Action</h3>
            <div className="space-y-3">
              <button onClick={() => handleReview("CONFIRM")} className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-colors shadow-lg shadow-blue-500/20">
                Confirm Machine Decision
              </button>
              <button onClick={() => handleReview("REJECT")} className="w-full bg-red-600/20 hover:bg-red-600/40 text-red-400 font-medium py-3 rounded-xl transition-colors shadow-lg shadow-red-500/10">
                Reject Decision
              </button>
              <button onClick={() => handleReview("EDIT")} className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-gray-300 font-medium py-3 rounded-xl transition-colors">
                Override / Edit
              </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
