"use client";

import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { DashboardSummary, SiteDensity, Pattern } from "@/types";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [sites, setSites] = useState<{sites: SiteDensity[]} | null>(null);
  const [patterns, setPatterns] = useState<{patterns: Pattern[]} | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const [sumRes, sitesRes, patternsRes] = await Promise.all([
          fetch("/api/v1/dashboard/summary"),
          fetch("/api/v1/dashboard/sites"),
          fetch("/api/v1/dashboard/patterns")
        ]);
        if (sumRes.ok) setSummary(await sumRes.json());
        if (sitesRes.ok) setSites(await sitesRes.json());
        if (patternsRes.ok) setPatterns(await patternsRes.json());
      } catch (e: any) {
        console.error(e);
        setError("Failed to load dashboard data. Please make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) {
    return <div className="p-8 text-gray-400">Loading Dashboard...</div>;
  }

  if (error) {
    return (
      <div className="p-8 animate-in fade-in">
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-4 rounded-xl">
          {error}
        </div>
      </div>
    );
  }

  if (!summary) return null;

  const sifData = [
    { name: 'SIF Potential', value: summary.sif_count, color: '#ef4444' },
    { name: 'Non-SIF', value: summary.total_reports - summary.sif_count, color: '#3b82f6' }
  ];

  const lsrData = Object.entries(summary.lsr_distribution || {}).map(([key, val]) => ({
    name: key.replace(/_/g, ' '),
    count: val
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-gray-400">High-level metrics and safety trends.</p>
        </div>
        <div className="text-sm text-gray-500">
          Last updated: {new Date(summary.generated_at).toLocaleString()}
        </div>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <MetricCard title="Total Reports" value={summary.total_reports} trend={summary.volume_trend} />
        <MetricCard title="SIF Potential" value={summary.sif_count} subtext={`${(summary.sif_percentage * 100).toFixed(1)}% of total`} color="text-red-500" trend={summary.sif_trend} />
        <MetricCard title="High Risk" value={summary.high_risk_count} color="text-orange-500" />
        <MetricCard title="Pending Review" value={summary.review_count} color="text-yellow-500" />
      </div>

      {/* Trending Terms */}
      {summary.trending_terms && summary.trending_terms.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Trending Terms (Last 30 Days)</h2>
          <div className="flex flex-wrap gap-2">
            {summary.trending_terms.map((term: string, idx: number) => (
              <span key={idx} className="bg-blue-500/10 border border-blue-500/20 text-blue-400 px-3 py-1.5 rounded-full text-sm font-medium">
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* SIF Donut */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">SIF Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sifData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                  {sifData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* LSR Bar */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-semibold text-white mb-6">LSR Matches</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lsrData} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                <XAxis dataKey="name" stroke="#888" interval={0} tick={{fontSize: 10, angle: -45, textAnchor: 'end'}} height={80} />
                <YAxis type="number" stroke="#888" allowDecimals={false} />
                <RechartsTooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none' }} cursor={{fill: '#ffffff0a'}} />
                <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Sites Density Table */}
      {sites && sites.sites && sites.sites.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 overflow-hidden">
          <h2 className="text-xl font-semibold text-white mb-6">Site Density</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-white/5 text-gray-400">
                <tr>
                  <th className="px-4 py-3 font-medium rounded-tl-lg">Site ID</th>
                  <th className="px-4 py-3 font-medium">Valid Reports</th>
                  <th className="px-4 py-3 font-medium">SIF Reports</th>
                  <th className="px-4 py-3 font-medium">Density</th>
                  <th className="px-4 py-3 font-medium rounded-tr-lg">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {sites.sites.map((site: any) => (
                  <tr key={site.site_id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-4 py-3 font-medium text-white">{site.site_id}</td>
                    <td className="px-4 py-3">{site.valid_reports}</td>
                    <td className="px-4 py-3">{site.sif_reports}</td>
                    <td className="px-4 py-3">{(site.density * 100).toFixed(1)}%</td>
                    <td className="px-4 py-3">
                      {site.low_sample ? (
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-500 rounded text-xs">Low Sample</span>
                      ) : (
                        <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-xs">High</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Patterns Table */}
      {patterns && patterns.patterns && patterns.patterns.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-6 overflow-hidden">
          <h2 className="text-xl font-semibold text-white mb-6">Emerging Patterns</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-white/5 text-gray-400">
                <tr>
                  <th className="px-4 py-3 font-medium rounded-tl-lg">Site</th>
                  <th className="px-4 py-3 font-medium">Activity</th>
                  <th className="px-4 py-3 font-medium">LSR Rule</th>
                  <th className="px-4 py-3 font-medium">Failed Barrier</th>
                  <th className="px-4 py-3 font-medium rounded-tr-lg" title="Number of times this specific barrier failed">Frequency (Failed Barrier)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {patterns.patterns.map((pattern: any, idx: number) => (
                  <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-4 py-3 font-medium text-white">{pattern.site_id}</td>
                    <td className="px-4 py-3">{pattern.activity || "ANY"}</td>
                    <td className="px-4 py-3 text-orange-400">{pattern.lsr_rule}</td>
                    <td className="px-4 py-3 text-red-400">{pattern.failed_barrier}</td>
                    <td className="px-4 py-3 font-medium">{pattern.frequency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ title, value, subtext, color = "text-white", trend }: { title: string, value: number, subtext?: string, color?: string, trend?: string }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-colors relative overflow-hidden">
      <h3 className="text-gray-400 text-sm font-medium mb-2">{title}</h3>
      <div className={`text-4xl font-bold ${color}`}>{value}</div>
      {subtext && <p className="text-xs text-gray-500 mt-2">{subtext}</p>}
      
      {trend && (
        <div className={`absolute top-6 right-6 px-2 py-1 rounded text-xs font-bold ${trend === 'RISING' ? 'bg-red-500/20 text-red-400' : trend === 'FALLING' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
          {trend}
        </div>
      )}
    </div>
  );
}
