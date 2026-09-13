"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { ShieldAlert, CheckCircle2, ChevronLeft, GitMerge, FileCheck, ArrowRight } from "lucide-react";
import Link from "next/link";
import ReactMarkdown from "react-markdown";

export default function ReportDetailPage() {
  const params = useParams();
  const reportId = params.id as string;
  const [report, setReport] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [editComment, setEditComment] = useState("");
  const [riskBand, setRiskBand] = useState("Low");
  const [selectedLsrs, setSelectedLsrs] = useState<string[]>([]);
  const [aiSummary, setAiSummary] = useState<string | null>(null);
  const [loadingSummary, setLoadingSummary] = useState(false);
  const [aiSolution, setAiSolution] = useState<string | null>(null);
  const [loadingSolution, setLoadingSolution] = useState(false);

  const startEditing = () => {
    setIsEditing(true);
    let initialRisk = report.report?.risk_band || report.sif_prediction?.risk_band || "Low";
    if (initialRisk) {
      initialRisk = initialRisk.charAt(0).toUpperCase() + initialRisk.slice(1).toLowerCase();
    }
    setRiskBand(initialRisk);
    setSelectedLsrs(report.lsr_predictions?.map((l: any) => l.rule_id) || []);
  };

  const fetchReport = useCallback(async () => {
    try {
      const res = await fetch(`/api/v1/reports/${reportId}`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
        
        // Load or Fetch AI Summary & Solution sequentially to avoid rate limits
        const fetchSolution = () => {
          if (data.report?.ai_solution) {
            setAiSolution(data.report.ai_solution);
          } else {
            setLoadingSolution(true);
            fetch(`/api/v1/reports/${reportId}/solution`, { method: "POST" })
              .then(r => r.json())
              .then(d => {
                if (d.solution) setAiSolution(d.solution);
                setLoadingSolution(false);
              })
              .catch(e => {
                console.error(e);
                setLoadingSolution(false);
              });
          }
        };

        if (data.report?.ai_summary) {
          setAiSummary(data.report.ai_summary);
          fetchSolution(); // Start solution immediately if summary is already cached
        } else {
          setLoadingSummary(true);
          fetch(`/api/v1/reports/${reportId}/second-opinion`, { method: "POST" })
            .then(r => r.json())
            .then(d => {
              if (d.summary) setAiSummary(d.summary);
              setLoadingSummary(false);
              fetchSolution(); // Chain solution after summary finishes
            })
            .catch(e => {
              console.error(e);
              setLoadingSummary(false);
              fetchSolution(); // Still try to fetch solution if summary failed
            });
        }
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
    return <div className="p-8 text-[var(--color-claude-text-secondary)] font-serif italic">Loading Report details...</div>;
  }

  if (!report) {
    return <div className="p-8 text-red-700 font-medium">Report not found.</div>;
  }

  const handleReview = async (decision: string) => {
    try {
      const payload: any = { decision };
      if (decision === "EDIT") {
        payload.comment = editComment;
        payload.risk_band = riskBand;
        payload.corrected_lsr_ids = selectedLsrs;
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
    let result: React.ReactNode[] = [];

    if (report.evidence && report.evidence.length > 0) {
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

      let lastIndex = 0;
      merged.forEach(([start, end], idx) => {
        if (start > lastIndex) {
          result.push(<span key={`t-${idx}`}>{text.substring(lastIndex, start)}</span>);
        }
        result.push(
          <span key={`h-${idx}`} className="bg-[var(--color-claude-accent)]/20 text-[var(--color-claude-text)] font-medium px-1.5 py-0.5 rounded">
            {text.substring(start, end)}
          </span>
        );
        lastIndex = end;
      });
      if (lastIndex < text.length) {
        result.push(<span key={`end`}>{text.substring(lastIndex)}</span>);
      }
    }

    return (
      <div className="space-y-4">
        
        {report.report?.ai_used ? (
          <>
            <div className="mb-6">
              <h4 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-3 flex items-center gap-2">
                <FileCheck className="text-[var(--color-claude-text-secondary)]" size={16} /> Original Text (Non-English)
              </h4>
              <p className="text-[var(--color-claude-text-secondary)] leading-relaxed text-base bg-[var(--color-claude-bg-secondary)] p-5 rounded-xl border border-[var(--color-claude-border)] italic">
                {report.report?.original_text}
              </p>
            </div>
            <h4 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-3 flex items-center gap-2">
              <ShieldAlert className="text-[var(--color-claude-accent)]" size={16} /> Translated Text (English)
            </h4>
          </>
        ) : (
          <h4 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-3 flex items-center gap-2">
            <ShieldAlert className="text-[var(--color-claude-accent)]" size={16} /> Original Text <span className="text-[var(--color-claude-text-secondary)] text-sm ml-2 font-normal">(No translation needed)</span>
          </h4>
        )}
        <p className="text-[var(--color-claude-text)] leading-relaxed text-lg bg-white p-6 rounded-xl border border-[var(--color-claude-border)] shadow-sm">
          {result.length > 0 ? result : text}
        </p>
        
        {report.evidence && report.evidence.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-3">Evidence Highlights</h4>
            <div className="space-y-2">
              {report.evidence.map((ev: any, idx: number) => (
                <div key={idx} className="bg-blue-50 border border-blue-200 text-blue-900 p-4 rounded-lg text-sm flex gap-3 shadow-sm">
                  <span className="font-mono text-blue-700 bg-blue-100/50 px-2 py-0.5 rounded text-sm shrink-0 border border-blue-200">
                    {ev.start_offset}:{ev.end_offset}
                  </span>
                  <div>
                    <strong className="text-blue-900 block mb-1">"{ev.phrase}"</strong>
                    <span className="text-blue-700/90">Matched Concept: {ev.concept}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex items-center gap-4">
        <Link href="/reports" className="p-2 bg-white border border-[var(--color-claude-border)] rounded-lg hover:bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text-secondary)] hover:text-[var(--color-claude-text)] transition-colors shadow-sm">
          <ChevronLeft size={20} />
        </Link>
        <div>
          <h1 className="text-4xl font-serif font-bold text-[var(--color-claude-text)] mb-1">Report Details</h1>
          <p className="text-[var(--color-claude-text-secondary)] font-mono text-sm">{report.report?.id}</p>
          {report.report?.processing_status && (
            <span className="inline-block mt-2 px-3 py-1.5 bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border-strong)] text-[var(--color-claude-text-secondary)] rounded-full text-sm font-medium">
              Status: {report.report.processing_status}
            </span>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Original Text & Highlights */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
            <h2 className="text-2xl font-serif font-bold text-[var(--color-claude-text)] mb-6 flex items-center gap-2">
              <FileCheck className="text-[var(--color-claude-accent)]" size={24} /> Original Text
            </h2>
            {renderHighlightedText()}
          </div>
          
          {/* Normalization Trace */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
            <h3 className="text-xl font-serif font-bold text-[var(--color-claude-text)] mb-4">Normalization Trace</h3>
            <div className="space-y-3">
              {report.normalizations && report.normalizations.length > 0 && report.normalizations[0].normalization_trace && report.normalizations[0].normalization_trace.length > 0 ? (
                report.normalizations[0].normalization_trace.map((trace: any, idx: number) => (
                  <div key={idx} className="flex items-center gap-3 text-base text-[var(--color-claude-text-secondary)] bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border)] p-3 rounded-lg">
                    <span className="font-mono text-[var(--color-claude-text)] line-through decoration-red-300">"{trace.from || trace.found || trace.rule}"</span>
                    <ArrowRight size={14} className="text-[var(--color-claude-text-secondary)]" />
                    <span className="font-mono text-[var(--color-claude-text)]">"{trace.to || trace.concept || trace.language}"</span>
                    <span className="ml-auto text-sm text-[var(--color-claude-text-secondary)] bg-white border border-[var(--color-claude-border)] px-2 py-1 rounded">Rule: {trace.rule}</span>
                  </div>
                ))
              ) : (
                <div className="text-[var(--color-claude-text-secondary)] text-base p-3 bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border)] rounded-lg italic font-serif">No normalization needed.</div>
              )}
            </div>
          </div>
          
          {/* AI Summary */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm overflow-hidden relative">
            <h3 className="text-xl font-serif font-bold text-[var(--color-claude-text)] mb-4 flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className={`${loadingSummary ? 'animate-ping' : ''} absolute inline-flex h-full w-full rounded-full bg-[var(--color-claude-accent)] opacity-75`}></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--color-claude-accent)]"></span>
              </span>
              AI Summary
            </h3>
            
            {loadingSummary ? (
              <div className="space-y-3 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                <div className="h-4 bg-gray-200 rounded w-4/6"></div>
              </div>
            ) : aiSummary ? (
              <p className="text-[var(--color-claude-text)] text-base leading-relaxed animate-in fade-in">
                {aiSummary}
              </p>
            ) : (
              <p className="text-[var(--color-claude-text-secondary)] italic text-sm">Failed to load summary.</p>
            )}
          </div>
          
          {/* AI Proposed Solution */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm overflow-hidden relative">
            <h3 className="text-xl font-serif font-bold text-[var(--color-claude-text)] mb-4 flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className={`${loadingSolution ? 'animate-ping' : ''} absolute inline-flex h-full w-full rounded-full bg-green-500 opacity-75`}></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </span>
              AI Proposed Solution
            </h3>
            
            {loadingSolution ? (
              <div className="space-y-3 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
              </div>
            ) : aiSolution ? (
              <div className="text-[var(--color-claude-text)] text-base leading-relaxed animate-in fade-in markdown-content">
                <ReactMarkdown
                  components={{
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 my-2 space-y-1" {...props} />,
                    ol: ({node, ...props}) => <ol className="list-decimal pl-5 my-2 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="pl-1" {...props} />,
                    strong: ({node, ...props}) => <strong className="font-bold text-[var(--color-claude-text)]" {...props} />,
                    p: ({node, ...props}) => <p className="mb-2" {...props} />
                  }}
                >
                  {aiSolution}
                </ReactMarkdown>
              </div>
            ) : (
              <p className="text-[var(--color-claude-text-secondary)] italic text-sm">Failed to load solution.</p>
            )}
          </div>
        </div>

        {/* Right Column: AI & Analysis Sidebar */}
        <div className="space-y-6">
          {/* SIF Prediction Box */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">SIF Analysis</h3>
            {report.sif_prediction ? (
              <div className="space-y-4">
                <div className={`p-4 rounded-xl border flex items-center gap-3 ${report.sif_prediction.sif_potential ? 'bg-[#FCF5F3] border-[#F2DCD5] text-[var(--color-claude-accent)]' : 'bg-[#F2F6F3] border-[#DCE4DD] text-[#5C6E53]'}`}>
                  {report.sif_prediction.sif_potential ? <ShieldAlert size={24} /> : <CheckCircle2 size={24} />}
                  <div>
                    <div className="text-xl font-serif font-medium">{report.sif_prediction.sif_potential ? 'SIF Potential' : 'No SIF Potential'}</div>
                    <div className="text-sm opacity-80">Risk Band: <span className="font-bold">{report.sif_prediction.risk_band}</span></div>
                  </div>
                </div>
                <div className="flex justify-between text-sm text-[var(--color-claude-text-secondary)] font-medium">
                  <span>Score: {(report.sif_prediction.score * 100).toFixed(1)}%</span>
                  <span>Confidence: {(report.sif_prediction.confidence * 100).toFixed(1)}%</span>
                </div>
              </div>
            ) : (
              <div className="text-[var(--color-claude-text-secondary)] text-sm italic font-serif">No SIF data available.</div>
            )}
          </div>

          {/* LSR Predictions Box */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Life-Saving Rules</h3>
            {report.lsr_predictions && report.lsr_predictions.length > 0 ? (
              <ul className="space-y-3">
                {report.lsr_predictions.map((lsr: any, idx: number) => (
                  <li key={idx} className="bg-white border border-[var(--color-claude-border-strong)] text-[var(--color-claude-text)] px-4 py-3 rounded-xl text-sm font-medium shadow-sm">
                    <div className="flex justify-between items-center mb-1">
                      <span>{lsr.rule_id}</span>
                      <span className="text-xs text-[var(--color-claude-text-secondary)]">{(lsr.confidence * 100).toFixed(0)}% Conf</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-[var(--color-claude-text-secondary)] text-sm italic font-serif">No LSR matches.</div>
            )}
          </div>

          {/* Extracted Entities */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Extracted Entities</h3>
            {report.entities && report.entities.length > 0 ? (
              <div className="flex flex-wrap gap-2">
                {report.entities.map((ent: any, idx: number) => (
                  <span key={idx} className="bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border)] text-[var(--color-claude-text)] px-3 py-1.5 rounded-md text-sm font-medium">
                    <span className="text-[var(--color-claude-text-secondary)] mr-1">{ent.entity_type}:</span> {ent.value}
                  </span>
                ))}
              </div>
            ) : (
              <div className="text-[var(--color-claude-text-secondary)] text-sm italic font-serif">No entities extracted.</div>
            )}
          </div>

          {/* Review History */}
          {report.reviews && report.reviews.length > 0 && (
            <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
              <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Review History</h3>
              <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {report.reviews.map((rev: any, idx: number) => (
                  <div key={idx} className="bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border)] p-4 rounded-xl space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="font-bold text-[var(--color-claude-text)]">{rev.reviewer_id}</span>
                      <span className="text-[var(--color-claude-text-secondary)]">{new Date(rev.created_at).toLocaleString()}</span>
                    </div>
                    <div className="text-sm">
                      Decision: <span className={`font-bold ${rev.decision === 'CONFIRM' ? 'text-green-700' : rev.decision === 'REJECT' ? 'text-red-700' : 'text-[var(--color-claude-text)]'}`}>{rev.decision}</span>
                    </div>
                    {rev.comment && (
                      <div className="text-sm text-[var(--color-claude-text)] mt-2 p-3 bg-white rounded-lg border border-[var(--color-claude-border)]">
                        {rev.comment}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Review Actions */}
          <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 shadow-sm">
            <h3 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-4">Review Action</h3>
            {!isEditing ? (
              <div className="space-y-3">
                <button onClick={() => handleReview("CONFIRM")} className="w-full bg-[var(--color-claude-text)] hover:bg-[#1a1816] text-white font-medium py-3 rounded-xl transition-colors shadow-sm">
                  Confirm Machine Decision
                </button>
                <button onClick={startEditing} className="w-full bg-white hover:bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border-strong)] text-[var(--color-claude-text)] font-medium py-3 rounded-xl transition-colors shadow-sm">
                  Override / Edit
                </button>
              </div>
            ) : (
              <div className="space-y-5 animate-in fade-in">
                {/* Risk Band Slider */}
                <div className="p-4 bg-[var(--color-claude-bg-secondary)] rounded-lg border border-[var(--color-claude-border)]">
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-bold text-[var(--color-claude-text)]">SIF Risk Level</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-bold ${riskBand === 'High' ? 'bg-red-100 text-red-800' : riskBand === 'Medium' ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>
                      {riskBand}
                    </span>
                  </div>
                  <div className="relative px-2 mt-4 mb-2">
                    <input 
                      type="range" 
                      min="0" 
                      max="2" 
                      step="1"
                      value={riskBand === 'Low' ? 0 : riskBand === 'Medium' ? 1 : 2}
                      onChange={(e) => {
                        const val = parseInt(e.target.value);
                        setRiskBand(val === 0 ? "Low" : val === 1 ? "Medium" : "High");
                      }}
                      className="w-full h-4 bg-gray-300 rounded-lg appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[var(--color-claude-accent)]/20 
                        [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-6 [&::-webkit-slider-thumb]:h-6 [&::-webkit-slider-thumb]:bg-[var(--color-claude-accent)] [&::-webkit-slider-thumb]:rounded-md [&::-webkit-slider-thumb]:shadow-md [&::-webkit-slider-thumb]:transition-transform [&::-webkit-slider-thumb]:hover:scale-110
                        [&::-moz-range-thumb]:appearance-none [&::-moz-range-thumb]:w-6 [&::-moz-range-thumb]:h-6 [&::-moz-range-thumb]:bg-[var(--color-claude-accent)] [&::-moz-range-thumb]:rounded-md [&::-moz-range-thumb]:shadow-md [&::-moz-range-thumb]:border-none [&::-moz-range-thumb]:transition-transform [&::-moz-range-thumb]:hover:scale-110"
                    />
                    <div className="flex justify-between text-xs text-[var(--color-claude-text-secondary)] font-medium mt-3 px-1">
                      <span>Low</span>
                      <span>Medium</span>
                      <span>High</span>
                    </div>
                  </div>
                </div>

                {/* LSR Selector */}
                <div>
                  <label className="block text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-2">Life-Saving Rules</label>
                  <div className="space-y-2 max-h-[150px] overflow-y-auto custom-scrollbar pr-2">
                    {[
                      "BYPASSING_SAFETY_CONTROLS", "CONFINED_SPACE", "DRIVING", "ENERGY_ISOLATION", 
                      "HOT_WORK", "LINE_OF_FIRE", "SAFE_MECHANICAL_LIFTING", "WORKING_AT_HEIGHT", "PERMIT_TO_WORK"
                    ].map(rule => (
                      <label key={rule} className="flex items-center gap-3 p-2 hover:bg-[var(--color-claude-bg-secondary)] rounded-lg cursor-pointer transition-colors border border-transparent hover:border-[var(--color-claude-border)]">
                        <input 
                          type="checkbox" 
                          checked={selectedLsrs.includes(rule)}
                          onChange={(e) => {
                            if (e.target.checked) setSelectedLsrs([...selectedLsrs, rule]);
                            else setSelectedLsrs(selectedLsrs.filter(r => r !== rule));
                          }}
                          className="w-4 h-4 text-[var(--color-claude-accent)] rounded focus:ring-[var(--color-claude-accent)]"
                        />
                        <span className="text-sm font-medium text-[var(--color-claude-text)]">{rule}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <textarea 
                  value={editComment}
                  onChange={(e) => setEditComment(e.target.value)}
                  placeholder="Enter correction notes (optional)..."
                  className="w-full h-24 bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border-strong)] rounded-xl p-3 text-[var(--color-claude-text)] placeholder-[var(--color-claude-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-claude-accent)]/20 focus:border-[var(--color-claude-accent)] resize-none text-base"
                />
                <div className="flex gap-2">
                  <button onClick={() => setIsEditing(false)} className="flex-1 bg-white hover:bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text)] py-2.5 rounded-lg text-sm font-bold transition-colors border border-[var(--color-claude-border-strong)] shadow-sm">
                    Cancel
                  </button>
                  <button 
                    onClick={() => handleReview("EDIT")} 
                    className="flex-1 bg-[var(--color-claude-text)] hover:bg-[#1a1816] text-white py-2.5 rounded-lg text-sm font-bold transition-colors shadow-sm"
                  >
                    Submit Override
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
