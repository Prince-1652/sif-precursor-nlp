import { Report } from "@/types";
import { AlertTriangle, Clock, RefreshCw } from "lucide-react";
import clsx from "clsx";

interface ReportCardProps {
  report: Report;
}

export function ReportCard({ report }: ReportCardProps) {
  const isProcessing = report.processing_status === "PROCESSING";
  const isReady = report.processing_status === "READY";
  const isCompleted = report.processing_status === "COMPLETED";

  const getSeverityColor = (score?: number) => {
    if (!score) return "bg-gray-100 text-gray-600";
    if (!score) return "bg-gray-800 text-gray-400 border-gray-700";
    if (score >= 4) return "bg-red-500/10 text-red-400 border-red-500/20";
    if (score === 3) return "bg-orange-500/10 text-orange-400 border-orange-500/20";
    return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-[28px] p-8 flex flex-col hover:-translate-y-1 transition-all duration-400 ease-out shadow-lg">
      <div className="flex justify-between items-start mb-6">
        <div className="flex flex-col gap-1.5">
          <span className="text-[10px] font-bold uppercase tracking-[0.2em] text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full w-fit">
            {report.report_type}
          </span>
          <span className="text-[11px] text-gray-400 font-medium tracking-wide mt-1">ID: {report.source_record_id || report.id.split('-')[0]}</span>
        </div>
        
        {isCompleted && report.severity_score ? (
          <div className={clsx("px-3 py-1 rounded-full text-xs font-bold border", getSeverityColor(report.severity_score))}>
            Severity {report.severity_score}
          </div>
        ) : (
          <div className="px-3 py-1 rounded-full bg-white/5 text-gray-400 text-xs font-medium flex items-center gap-1.5 border border-white/5">
            {isProcessing ? <RefreshCw size={12} className="animate-spin" /> : <Clock size={12} />}
            {report.processing_status}
          </div>
        )}
      </div>

      <p className="text-gray-200 text-[15px] leading-relaxed font-medium mb-8">
        {report.original_text}
      </p>

      {isCompleted && (
        <div className="mt-auto space-y-5 border-t border-white/10 pt-6">
          {report.extracted_hazards && report.extracted_hazards.length > 0 && (
            <div>
              <h4 className="text-[11px] font-bold uppercase tracking-[0.1em] text-gray-500 mb-2 flex items-center gap-1.5">
                <AlertTriangle size={12} /> Hazards
              </h4>
              <ul className="flex flex-wrap gap-2">
                {report.extracted_hazards.map((h, i) => (
                  <li key={i} className="text-[13px] bg-red-500/10 text-red-400 px-3 py-1.5 rounded-xl font-medium border border-red-500/20">
                    {h}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {report.root_causes && report.root_causes.length > 0 && (
            <div className="pt-3 border-t border-slate-200/50">
              <h4 className="text-[11px] font-bold uppercase tracking-[0.1em] text-slate-400 mb-2">Root Causes</h4>
              <ul className="list-disc pl-4 text-xs text-slate-600 space-y-1 font-medium">
                {report.root_causes.map((cause, idx) => (
                  <li key={idx}>{cause}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
