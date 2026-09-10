"use client";

import { useEffect, useState, useCallback } from "react";
import { ShieldAlert, AlertTriangle, CheckCircle2, FileText, ArrowRight } from "lucide-react";
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

  const fetchReports = useCallback(async () => {
    setLoading(true);
    try {
      // In a full implementation, we would pass filters as query params
      const res = await fetch("/api/v1/reports");
      if (res.ok) {
        setReports(await res.json());
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  const filteredReports = reports.filter(r => {
    const matchesSearch = !searchQuery || r.original_text.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "ALL" || r.processing_status === statusFilter || (statusFilter === "PENDING_REVIEW" && ["REVIEW_REQUIRED", "REVIEW_RECOMMENDED"].includes(r.processing_status));
    const matchesRisk = riskFilter === "ALL" || (riskFilter === "SIF" ? r.sif_potential : !r.sif_potential);
    return matchesSearch && matchesStatus && matchesRisk;
  });

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Reports</h1>
        <p className="text-gray-400">View and review processed safety reports.</p>
      </div>

      <div className="flex gap-4">
        <div className="flex-1">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search text..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        {/* Filter Buttons */}
        <button 
          onClick={() => setShowFilters(!showFilters)}
          className="px-4 py-2 bg-white/5 border border-white/10 rounded-xl text-gray-300 hover:bg-white/10 transition-colors"
        >
          Filters
        </button>
      </div>

      {showFilters && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 bg-white/5 border border-white/10 p-4 rounded-xl">
          <div>
            <label className="block text-xs text-gray-400 font-medium uppercase mb-1">Status</label>
            <select 
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white text-sm focus:outline-none"
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
            <label className="block text-xs text-gray-400 font-medium uppercase mb-1">Risk</label>
            <select 
              value={riskFilter}
              onChange={(e) => setRiskFilter(e.target.value)}
              className="w-full bg-black/40 border border-white/10 rounded-lg p-2 text-white text-sm focus:outline-none"
            >
              <option value="ALL">All Risks</option>
              <option value="SIF">SIF Potential</option>
              <option value="NON_SIF">Non-SIF</option>
            </select>
          </div>
        </div>
      )}

      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading reports...</div>
        ) : filteredReports.length === 0 ? (
          <div className="p-12 text-center text-gray-400">No reports found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-white/5 text-gray-400 border-b border-white/10">
                <tr>
                  <th className="px-6 py-4 font-medium">ID / Date</th>
                  <th className="px-6 py-4 font-medium max-w-md">Report Text</th>
                  <th className="px-6 py-4 font-medium">Risk</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filteredReports.map((report) => (
                  <tr key={report.id} className="hover:bg-white/[0.02] transition-colors group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="font-medium text-white">{report.source_record_id || report.id.substring(0,8)}</div>
                      <div className="text-xs text-gray-500 mt-1">{new Date(report.created_at).toLocaleDateString()}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="line-clamp-2 text-gray-300">{report.original_text}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {report.sif_potential ? (
                        <div className="flex items-center gap-1.5 text-red-400 bg-red-500/10 px-2.5 py-1 rounded-md w-fit text-xs font-medium border border-red-500/20">
                          <ShieldAlert size={14} /> SIF ({report.risk_band})
                        </div>
                      ) : (
                        <div className="flex items-center gap-1.5 text-blue-400 bg-blue-500/10 px-2.5 py-1 rounded-md w-fit text-xs font-medium border border-blue-500/20">
                          <CheckCircle2 size={14} /> NON-SIF
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-xs font-medium bg-white/5 px-2.5 py-1 rounded-md w-fit border border-white/10 text-gray-300">
                        {report.processing_status.replace(/_/g, ' ')}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Link href={`/reports/${report.id}`} className="flex items-center gap-2 text-blue-400 hover:text-blue-300 font-medium transition-colors">
                        Review <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
                      </Link>
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
    <Suspense fallback={<div className="p-8 text-center text-gray-400">Loading reports...</div>}>
      <ReportsContent />
    </Suspense>
  );
}
