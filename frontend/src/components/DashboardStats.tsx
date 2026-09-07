import { DashboardStats as StatsType } from "@/types";
import { FileText, CheckCircle, AlertOctagon } from "lucide-react";

interface StatsProps {
  stats: StatsType | null;
}

export function DashboardStats({ stats }: StatsProps) {
  if (!stats) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-16">
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-[28px] p-8 flex flex-col hover:-translate-y-1 transition-transform duration-400">
        <div className="w-12 h-12 bg-blue-500/10 text-blue-400 rounded-2xl flex items-center justify-center mb-6">
          <FileText size={24} />
        </div>
        <p className="text-[13px] font-bold uppercase tracking-widest text-gray-400 mb-1">Total Reports</p>
        <h3 className="text-[40px] font-extrabold tracking-tight text-white leading-none">{stats?.total_reports || 0}</h3>
      </div>
      
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-[28px] p-8 flex flex-col hover:-translate-y-1 transition-transform duration-400">
        <div className="w-12 h-12 bg-emerald-500/10 text-emerald-400 rounded-2xl flex items-center justify-center mb-6">
          <CheckCircle size={24} />
        </div>
        <p className="text-[13px] font-bold uppercase tracking-widest text-gray-400 mb-1">Analyzed by AI</p>
        <h3 className="text-[40px] font-extrabold tracking-tight text-white leading-none">{stats?.processed_reports || 0}</h3>
      </div>
      
      <div className="bg-white/5 backdrop-blur-md border border-white/10 rounded-[28px] p-8 flex flex-col hover:-translate-y-1 transition-transform duration-400">
        <div className="w-12 h-12 bg-red-500/10 text-red-400 rounded-2xl flex items-center justify-center mb-6">
          <AlertOctagon size={24} />
        </div>
        <p className="text-[13px] font-bold uppercase tracking-widest text-gray-400 mb-1">High Severity</p>
        <h3 className="text-[40px] font-extrabold tracking-tight text-white leading-none">{stats?.high_severity_reports || 0}</h3>
      </div>
    </div>
  );
}
