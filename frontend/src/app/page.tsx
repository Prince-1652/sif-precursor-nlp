"use client";

import { useEffect, useState } from "react";
import { PieChart, Pie, Cell, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts';
import { DashboardSummary, SiteDensity, Pattern } from "@/types";
import Link from "next/link";

export default function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [sites, setSites] = useState<{sites: SiteDensity[]} | null>(null);
  const [patterns, setPatterns] = useState<{patterns: Pattern[]} | null>(null);
  const [recentReports, setRecentReports] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;
    
    async function fetchData(showLoading = false) {
      if (showLoading) setLoading(true);
      try {
        const [sumRes, sitesRes, patternsRes, reportsRes] = await Promise.all([
          fetch("/api/v1/dashboard/summary"),
          fetch("/api/v1/dashboard/sites"),
          fetch("/api/v1/dashboard/patterns"),
          fetch("/api/v1/reports?limit=5")
        ]);
        if (sumRes.ok) setSummary(await sumRes.json());
        if (sitesRes.ok) setSites(await sitesRes.json());
        if (patternsRes.ok) setPatterns(await patternsRes.json());
        if (reportsRes.ok) setRecentReports(await reportsRes.json());
        setError(null);
      } catch (e: any) {
        console.error(e);
        setError("Failed to load dashboard data. Please make sure the backend is running.");
      } finally {
        if (showLoading) setLoading(false);
      }
    }
    
    // Initial fetch
    fetchData(true);
    
    // Setup polling
    intervalId = setInterval(() => {
      fetchData(false); // Silent fetch in background
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, []);

  if (loading) {
    return <div className="p-8 text-[var(--color-claude-text-secondary)] font-serif italic">Loading intelligence...</div>;
  }

  if (error) {
    return (
      <div className="p-8 animate-in fade-in">
        <div className="bg-red-50 border border-red-200 text-red-800 p-4 rounded-md font-medium">
          {error}
        </div>
      </div>
    );
  }

  if (!summary) return null;

  const sifData = [
    { name: 'SIF Potential', value: summary.sif_count, color: '#DA7756' }, // Terracotta
    { name: 'Non-SIF', value: summary.total_reports - summary.sif_count, color: '#8B9A84' } // Sage
  ];

  const lsrData = Object.entries(summary.lsr_distribution || {}).map(([key, val]) => ({
    name: key.replace(/_/g, ' '),
    count: val
  }));

  return (
    <div className="space-y-8 animate-in fade-in duration-1000">
      <div className="flex flex-col md:flex-row md:justify-between md:items-end gap-4 border-b border-[var(--color-claude-border)] pb-6">
        <div>
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-[var(--color-claude-text)] mb-3 tracking-tight">Intelligence Overview</h1>
          <p className="text-[var(--color-claude-text-secondary)] text-lg">High-level metrics and emerging safety trends across all sites.</p>
        </div>
        <div className="text-base text-[var(--color-claude-text-secondary)] font-mono bg-[var(--color-claude-bg-secondary)] px-3 py-1.5 rounded-md">
          Updated: {new Date(summary.generated_at).toLocaleString()}
        </div>
      </div>

      {/* Top Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Total Reports" value={summary.total_reports} href="/reports" />
        <MetricCard title="SIF Potential" value={summary.sif_count} subtext={`${(summary.sif_percentage * 100).toFixed(1)}% of total`} color="text-[var(--color-claude-accent)]" trend={summary.sif_trend} href="/reports?riskFilter=SIF" />
        <MetricCard title="Pending Review" value={summary.review_count} href="/reports?statusFilter=PENDING_REVIEW" />
      </div>

      {/* Trending Terms */}
      {summary.trending_terms && summary.trending_terms.length > 0 && (
        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
          <h2 className="text-2xl font-serif font-bold text-[var(--color-claude-text)] mb-4">Trending Subjects (30 Days)</h2>
          <div className="flex flex-wrap gap-3">
            {summary.trending_terms.map((term: string, idx: number) => (
              <span key={idx} className="bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text)] px-4 py-2 rounded-full text-base font-medium border border-[var(--color-claude-border-strong)]">
                {term}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* SIF Donut */}
        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
          <h2 className="text-2xl font-serif font-bold text-[var(--color-claude-text)] mb-4">Risk Distribution</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={sifData} innerRadius={80} outerRadius={110} paddingAngle={2} dataKey="value" stroke="none">
                  {sifData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #EAE6DF', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }} 
                  itemStyle={{ color: '#2D2926' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* LSR Bar */}
        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm">
          <h2 className="text-2xl font-serif font-bold text-[var(--color-claude-text)] mb-4">Life Saving Rules</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={lsrData} margin={{ top: 10, right: 10, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#CBD5E1" vertical={false} />
                <XAxis dataKey="name" stroke="#736F6A" tick={{fontSize: 13}} tickLine={false} axisLine={false} interval={0} angle={-45} textAnchor="end" height={60} />
                <YAxis type="number" stroke="#736F6A" tick={{fontSize: 13}} tickLine={false} axisLine={false} allowDecimals={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#ffffff', borderRadius: '8px', border: '1px solid #EAE6DF', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)' }}
                  cursor={{fill: '#F4F1EC'}} 
                />
                <Bar dataKey="count" fill="#7A8B99" radius={[4, 4, 0, 0]} maxBarSize={40} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Sites Density Table */}
      {sites && sites.sites && sites.sites.length > 0 && (
        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm overflow-hidden">
          <h2 className="text-2xl font-serif font-bold text-[var(--color-claude-text)] mb-4">Site Density Analysis</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-base">
              <thead>
                <tr className="border-b-2 border-[var(--color-claude-border)] text-[var(--color-claude-text-secondary)]">
                  <th className="px-4 py-4 font-medium">Site ID</th>
                  <th className="px-4 py-4 font-medium">Valid Reports</th>
                  <th className="px-4 py-4 font-medium">SIF Reports</th>
                  <th className="px-4 py-4 font-medium">Density</th>
                  <th className="px-4 py-4 font-medium">Confidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-claude-border)]">
                {sites.sites.map((site: any) => (
                  <tr key={site.site_id} className="hover:bg-[var(--color-claude-bg-secondary)] transition-colors">
                    <td className="px-4 py-4 font-medium text-[var(--color-claude-text)]">{site.site_id}</td>
                    <td className="px-4 py-4 text-[var(--color-claude-text-secondary)]">{site.valid_reports}</td>
                    <td className="px-4 py-4 text-[var(--color-claude-text-secondary)]">{site.sif_reports}</td>
                    <td className="px-4 py-4 font-medium text-[var(--color-claude-text)]">{(site.density * 100).toFixed(1)}%</td>
                    <td className="px-4 py-4">
                      {site.low_sample ? (
                        <span className="px-3 py-1.5 bg-amber-50 text-amber-700 border border-amber-200 rounded-full text-sm font-medium">Low Sample</span>
                      ) : (
                        <span className="px-3 py-1.5 bg-green-50 text-green-700 border border-green-200 rounded-full text-sm font-medium">High</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Recent Reports Table */}
      {recentReports && recentReports.length > 0 && (
        <div className="bg-white border border-[var(--color-claude-border)] rounded-xl p-5 shadow-sm overflow-hidden">
          <h2 className="text-2xl font-serif font-bold text-[var(--color-claude-text)] mb-4">Recent Additions</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-base">
              <thead>
                <tr className="border-b-2 border-[var(--color-claude-border)] text-[var(--color-claude-text-secondary)]">
                  <th className="px-4 py-4 font-medium">Identifier</th>
                  <th className="px-4 py-4 font-medium">Excerpt</th>
                  <th className="px-4 py-4 font-medium">Status</th>
                  <th className="px-4 py-4 font-medium">Assessment</th>
                  <th className="px-4 py-4 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-claude-border)]">
                {recentReports.map((r: any) => (
                  <tr key={r.id} className="hover:bg-[var(--color-claude-bg-secondary)] transition-colors group cursor-pointer" onClick={() => window.location.href = `/reports/${r.id}`}>
                    <td className="px-4 py-4 font-mono text-sm text-[var(--color-claude-text-secondary)]">{r.id.substring(0, 8)}</td>
                    <td className="px-4 py-4 text-[var(--color-claude-text)] truncate max-w-sm italic">"{r.original_text.substring(0, 60)}..."</td>
                    <td className="px-4 py-4">
                      <span className="px-3 py-1.5 bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text-secondary)] rounded-full text-sm border border-[var(--color-claude-border)]">
                        {r.processing_status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-4 py-4">
                      {r.sif_potential 
                        ? <span className="text-[var(--color-claude-accent)] font-medium flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-[var(--color-claude-accent)]"></div> SIF Potential</span> 
                        : <span className="text-[var(--color-claude-text-secondary)]">Standard</span>}
                    </td>
                    <td className="px-4 py-4 text-right">
                      <span className="text-[var(--color-claude-accent)] font-medium opacity-0 group-hover:opacity-100 transition-opacity">
                        Review &rarr;
                      </span>
                    </td>
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

function MetricCard({ title, value, subtext, color = "text-[var(--color-claude-text)]", trend, href }: { title: string, value: number, subtext?: string, color?: string, trend?: string, href?: string }) {
  const content = (
    <div className={`bg-white border border-[var(--color-claude-border)] rounded-xl p-6 hover:shadow-md hover:border-[var(--color-claude-border-strong)] transition-all relative h-40 flex flex-col justify-between ${href ? 'cursor-pointer' : ''}`}>
      <h3 className="text-[var(--color-claude-text-secondary)] text-base font-medium tracking-wide uppercase">{title}</h3>
      <div>
        <div className={`text-6xl font-serif ${color} tracking-tight`}>{value.toLocaleString()}</div>
        {subtext && <p className="text-base text-[var(--color-claude-text-secondary)] mt-1">{subtext}</p>}
      </div>
      
      {trend && (
        <div className={`absolute top-5 right-5 px-3 py-1.5 rounded-full text-sm font-medium border ${
          trend === 'RISING' ? 'bg-red-50 text-red-700 border-red-200' 
          : trend === 'FALLING' ? 'bg-green-50 text-green-700 border-green-200' 
          : 'bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text-secondary)] border-[var(--color-claude-border-strong)]'
        }`}>
          {trend === 'RISING' ? '↑ Rising' : trend === 'FALLING' ? '↓ Falling' : 'Stable'}
        </div>
      )}
    </div>
  );

  if (href) {
    return <Link href={href} className="block group h-full">{content}</Link>;
  }
  return content;
}
