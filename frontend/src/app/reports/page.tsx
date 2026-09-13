"use client";

import { useEffect, useState, useCallback } from "react";
import { ShieldAlert, AlertTriangle, CheckCircle2, FileText, ArrowRight, SlidersHorizontal, Search } from "lucide-react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { Suspense } from "react";

function ReportsContent() {
  const searchParams = useSearchParams();
  const [reports, setReports] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState(searchParams.get("statusFilter") || "ALL");
  const [riskFilter, setRiskFilter] = useState(searchParams.get("riskFilter") || "ALL");
  const [showFilters, setShowFilters] = useState(false);
  const [progress, setProgress] = useState<{active: boolean, total: number, completed: number, pending: number} | null>(null);

  const fetchReports = useCallback(async (showLoading = false) => {
    if (showLoading) setLoading(true);
    try {
      // In a full implementation, we would pass filters as query params
      const [res, progressRes] = await Promise.all([
        fetch("/api/v1/reports?limit=1000"),
        fetch("/api/v1/reports/progress")
      ]);
      
      if (res.ok) {
        setReports(await res.json());
      }
      if (progressRes.ok) {
        setProgress(await progressRes.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports(true);
    const intervalId = setInterval(() => {
      fetchReports(false);
    }, 5000);
    return () => clearInterval(intervalId);
  }, [fetchReports]);

  const filteredReports = reports.filter(r => {
    const matchesSearch = !searchQuery || r.original_text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || r.processing_status === statusFilter || (statusFilter === "PENDING_REVIEW" && ["REVIEW_REQUIRED", "REVIEW_RECOMMENDED"].includes(r.processing_status));
    const matchesRisk = riskFilter === "ALL" || (riskFilter === "SIF" ? r.sif_potential : !r.sif_potential);
    return matchesSearch && matchesStatus && matchesRisk;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-1000">
      <div className="border-b border-[var(--color-claude-border)] pb-6">
        <h1 className="text-4xl md:text-5xl font-serif font-bold text-[var(--color-claude-text)] mb-3 tracking-tight">Intelligence Reports</h1>
        <p className="text-[var(--color-claude-text-secondary)] text-lg">Review and analyze processed safety narratives.</p>
      </div>

      {progress?.active && (
        <div className="bg-white border border-[var(--color-claude-border-strong)] rounded-xl p-6 shadow-sm mb-6 animate-in fade-in slide-in-from-top-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-[var(--color-claude-text)] font-medium flex items-center gap-2">
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-claude-accent)] opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-[var(--color-claude-accent)]"></span>
              </span>
              AI Processing Active
            </h3>
            <span className="text-[var(--color-claude-text-secondary)] text-sm font-medium">
              {progress.completed} / {progress.total}
            </span>
          </div>
          <div className="w-full bg-[var(--color-claude-bg-secondary)] rounded-full h-2.5 overflow-hidden border border-[var(--color-claude-border)]">
            <div 
              className="bg-[var(--color-claude-accent)] h-2.5 rounded-full transition-all duration-1000 ease-out relative"
              style={{ width: `${Math.max(5, (progress.completed / progress.total) * 100)}%` }}
            >
              <div className="absolute top-0 right-0 bottom-0 left-0 bg-white/20 animate-pulse"></div>
            </div>
          </div>
          <p className="text-xs text-[var(--color-claude-text-secondary)] mt-3">
            Analyzing narratives, extracting Life-Saving Rules, and predicting SIF potential...
          </p>
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4">
        <div className="flex-1">
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-claude-text-secondary)] w-5 h-5 transition-colors group-focus-within:text-[var(--color-claude-accent)]" />
            <input 
              type="text" 
              placeholder="Search narratives..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-[var(--color-claude-border-strong)] rounded-lg pl-12 pr-4 py-3 text-base text-[var(--color-claude-text)] placeholder-[var(--color-claude-text-secondary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-claude-accent)]/20 focus:border-[var(--color-claude-accent)] transition-all shadow-sm"
            />
          </div>
        </div>
        {/* Filter Buttons */}
        <button 
          onClick={() => setShowFilters(!showFilters)}
          className={`px-5 py-3 border rounded-lg font-medium transition-colors flex items-center gap-2 ${
            showFilters 
              ? "bg-[var(--color-claude-bg-secondary)] border-[var(--color-claude-border-strong)] text-[var(--color-claude-text)]" 
              : "bg-white border-[var(--color-claude-border-strong)] text-[var(--color-claude-text-secondary)] hover:text-[var(--color-claude-text)] hover:bg-[var(--color-claude-bg-secondary)] shadow-sm"
          }`}
        >
          <SlidersHorizontal size={18} />
          Filters
        </button>
      </div>

      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white border border-[var(--color-claude-border)] p-5 rounded-xl shadow-sm animate-in slide-in-from-top-2">
          <div>
            <label className="block text-sm font-medium text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-2">Processing Status</label>
            <select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border-strong)] rounded-lg p-3 text-[var(--color-claude-text)] text-base focus:outline-none focus:ring-2 focus:ring-[var(--color-claude-accent)]/20 transition-all"
            >
              <option value="ALL">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="PENDING_REVIEW">Pending Review</option>
              <option value="REVIEW_REQUIRED">Review Required</option>
              <option value="REVIEW_RECOMMENDED">Review Recommended</option>
              <option value="COMPLETED_WITH_EDITS">Completed with Edits</option>
              <option value="FAILED">Failed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-[var(--color-claude-text-secondary)] uppercase tracking-wider mb-2">Risk Assessment</label>
            <select 
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border-strong)] rounded-lg p-3 text-[var(--color-claude-text)] text-base focus:outline-none focus:ring-2 focus:ring-[var(--color-claude-accent)]/20 transition-all"
            >
              <option value="ALL">All Risks</option>
              <option value="SIF">SIF Potential</option>
              <option value="NON_SIF">Non-SIF</option>
            </select>
          </div>
        </div>
      )}

      <div className="bg-white border border-[var(--color-claude-border)] rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-[var(--color-claude-text-secondary)] font-serif italic">Loading reports...</div>
        ) : filteredReports.length === 0 ? (
          <div className="p-16 text-center text-[var(--color-claude-text-secondary)]">
            <p className="font-serif text-xl mb-2 text-[var(--color-claude-text)]">No reports found.</p>
            <p>Try adjusting your search or filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-base">
              <thead className="border-b-2 border-[var(--color-claude-border)] text-[var(--color-claude-text-secondary)]">
                <tr>
                  <th className="px-6 py-5 font-medium">Identifier / Date</th>
                  <th className="px-6 py-5 font-medium max-w-md">Narrative Snippet</th>
                  <th className="px-6 py-5 font-medium">Risk Level</th>
                  <th className="px-6 py-5 font-medium">Status</th>
                  <th className="px-6 py-5 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-claude-border)]">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-[var(--color-claude-bg-secondary)] transition-colors group cursor-pointer" onClick={() => window.location.href = `/reports/${report.id}`}>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="font-medium text-[var(--color-claude-text)] font-mono text-sm">{report.source_record_id || report.id.substring(0,8)}</div>
                      <div className="text-sm text-[var(--color-claude-text-secondary)] mt-1">{new Date(report.created_at).toLocaleDateString()}</div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="line-clamp-2 text-[var(--color-claude-text)] italic">"{report.original_text}"</div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      {report.sif_potential ? (
                        <div className="flex items-center gap-2 text-[var(--color-claude-accent)] font-medium">
                          <div className="w-2 h-2 rounded-full bg-[var(--color-claude-accent)]"></div>
                          SIF ({report.risk_band})
                        </div>
                      ) : (
                        <div className="flex items-center gap-2 text-[var(--color-claude-text-secondary)]">
                          <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-claude-text-secondary)]"></div>
                          Standard
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap">
                      <div className="text-sm font-medium bg-[var(--color-claude-bg-secondary)] px-3 py-1.5 rounded-full w-fit border border-[var(--color-claude-border-strong)] text-[var(--color-claude-text-secondary)]">
                        {report.processing_status.replace(/_/g, ' ')}
                      </div>
                    </td>
                    <td className="px-6 py-5 whitespace-nowrap text-right">
                      <span className="inline-flex items-center gap-2 text-[var(--color-claude-accent)] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                        Review <ArrowRight size={16} />
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ReportsPage() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-[var(--color-claude-text-secondary)] font-serif italic">Loading intelligence...</div>}>
      <ReportsContent />
    </Suspense>
  );
}
