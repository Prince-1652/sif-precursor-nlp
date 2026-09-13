"use client";

import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function PatternsPage() {
  const [patterns, setPatterns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPatterns(showLoading = false) {
      if (showLoading) setLoading(true);
      try {
        const res = await fetch("/api/v1/dashboard/patterns");
        if (res.ok) {
          const data = await res.json();
          setPatterns(data.patterns || []);
        }
      } catch (e) {
        console.error(e);
      } finally {
        if (showLoading) setLoading(false);
      }
    }
    
    fetchPatterns(true);
    
    const intervalId = setInterval(() => {
      fetchPatterns(false);
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div>
        <h1 className="text-4xl font-serif font-bold text-[var(--color-claude-text)] mb-2">Recurring Patterns</h1>
        <p className="text-lg text-[var(--color-claude-text-secondary)]">Discover frequently occurring combinations of activities, hazards, and failed barriers.</p>
      </div>

      <div className="bg-white border border-[var(--color-claude-border)] rounded-xl shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-[var(--color-claude-text-secondary)] italic font-serif">Loading patterns...</div>
        ) : patterns.length === 0 ? (
          <div className="p-12 text-center text-[var(--color-claude-text-secondary)] italic font-serif">No patterns detected for the current period.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-base text-[var(--color-claude-text)]">
              <thead className="bg-[var(--color-claude-bg-secondary)] text-[var(--color-claude-text-secondary)] border-b border-[var(--color-claude-border)]">
                <tr>
                  <th className="px-6 py-4 font-medium">Site</th>
                  <th className="px-6 py-4 font-medium">Activity</th>
                  <th className="px-6 py-4 font-medium">LSR</th>
                  <th className="px-6 py-4 font-medium">Failed Barrier</th>
                  <th className="px-6 py-4 font-medium text-right">Frequency</th>
                  <th className="px-6 py-4 font-medium text-center">Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-claude-border)]">
                {patterns.map((pattern, idx) => (
                  <tr key={idx} className="hover:bg-[var(--color-claude-bg-secondary)] transition-colors">
                    <td className="px-6 py-4 font-bold text-[var(--color-claude-text)]">{pattern.site_id}</td>
                    <td className="px-6 py-4 font-medium">{pattern.activity}</td>
                    <td className="px-6 py-4">
                      <span className="bg-white border border-[var(--color-claude-border-strong)] text-[var(--color-claude-text)] px-3 py-1.5 rounded-md shadow-sm font-bold text-sm">
                        {pattern.lsr_rule}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-red-700 font-bold">{pattern.failed_barrier}</td>
                    <td className="px-6 py-4 text-right font-mono">{pattern.frequency}</td>
                    <td className="px-6 py-4 flex justify-center">
                      {pattern.trend === "RISING" && <TrendingUp className="text-red-600" size={18} />}
                      {pattern.trend === "FALLING" && <TrendingDown className="text-green-700" size={18} />}
                      {pattern.trend === "STABLE" && <Minus className="text-[var(--color-claude-text-secondary)]" size={18} />}
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
