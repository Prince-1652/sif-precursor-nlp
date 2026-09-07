"use client";

import { useEffect, useState, useCallback } from "react";
import { DashboardStats as StatsType, Report } from "@/types";
import { DashboardStats } from "@/components/DashboardStats";
import { UploadDropzone } from "@/components/UploadDropzone";
import { ManualTextInput } from "@/components/ManualTextInput";
import { ReportCard } from "@/components/ReportCard";
import { SearchBar } from "@/components/SearchBar";
import { RefreshCw, XCircle } from "lucide-react";

export default function Home() {
  const [stats, setStats] = useState<StatsType | null>(null);
  const [reports, setReports] = useState<Report[]>([]);
  const [searchResults, setSearchResults] = useState<Report[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchLoading, setSearchLoading] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [statsRes, reportsRes] = await Promise.all([
        fetch("/api/v1/reports/stats"),
        fetch("/api/v1/reports")
      ]);
      
      if (statsRes.ok) setStats(await statsRes.json());
      if (reportsRes.ok) setReports(await reportsRes.json());
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleSearch = async (query: string) => {
    setSearchLoading(true);
    try {
      const res = await fetch(`/api/v1/search?query=${encodeURIComponent(query)}`);
      if (res.ok) {
        setSearchResults(await res.json());
      }
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setSearchLoading(false);
    }
  };

  const clearSearch = () => {
    setSearchResults(null);
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 10 seconds for background job updates (only if not searching)
    const interval = setInterval(() => {
      setSearchResults((prev) => {
        if (!prev) fetchData();
        return prev;
      });
    }, 10000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const displayReports = searchResults || reports;
  const isSearching = searchResults !== null;

  return (
    <div className="space-y-16 animate-in fade-in duration-1000 pt-8 pb-20 w-full max-w-[1600px] mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 mb-4">
        <div className="max-w-3xl">
          <h1 className="text-[56px] leading-[1.05] font-extrabold tracking-[-0.02em] text-white mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Safety Intelligence
          </h1>
          <p className="text-[#A1A1AA] text-[22px] leading-tight font-medium">
            Monitor organizational risk and automatically detect hazards with AI ingestion.
          </p>
        </div>
        <button 
          onClick={() => { setLoading(true); fetchData(); clearSearch(); }}
          className="flex items-center gap-2 px-6 py-3 text-[15px] font-semibold text-white bg-white/5 border border-white/10 rounded-full hover:bg-white/10 transition-colors shadow-lg"
        >
          <RefreshCw size={18} className={loading ? "animate-spin" : ""} />
          Sync Data
        </button>
      </div>

      <DashboardStats stats={stats} />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        <div className="lg:col-span-1">
          <div className="sticky top-24">
            <h2 className="text-xl font-bold text-slate-800 mb-6 drop-shadow-sm">Ingest Data</h2>
            <UploadDropzone onUploadSuccess={fetchData} />
            <ManualTextInput onUploadSuccess={fetchData} />
          </div>
        </div>

        <div className="lg:col-span-2">
          <SearchBar onSearch={handleSearch} isLoading={searchLoading} />

          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-200">
              {isSearching ? "Search Results" : "Recent Reports"}
            </h2>
            {isSearching && (
              <button 
                onClick={clearSearch}
                className="flex items-center gap-1.5 text-sm font-medium text-gray-400 hover:text-gray-200 transition-colors"
              >
                <XCircle size={16} /> Clear Search
              </button>
            )}
          </div>
          
          {loading && displayReports.length === 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="bg-white/5 border border-white/10 rounded-[28px] p-6 h-48 animate-pulse" />
              ))}
            </div>
          ) : displayReports.length === 0 ? (
            <div className="bg-white/5 border border-white/10 rounded-[28px] p-12 text-center text-gray-400">
              {isSearching ? "No matching reports found." : "No reports found. Upload a CSV to get started."}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {displayReports.map(report => (
                <ReportCard key={report.id} report={report} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
