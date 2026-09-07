"use client";

import { useEffect, useState } from "react";
import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function PatternsPage() {
  const [patterns, setPatterns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchPatterns() {
      try {
        const res = await fetch("/api/v1/dashboard/patterns");
        if (res.ok) {
          const data = await res.json();
          setPatterns(data.patterns || []);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    fetchPatterns();
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in duration-700 max-w-7xl mx-auto">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Recurring Patterns</h1>
        <p className="text-gray-400">Discover frequently occurring combinations of activities, hazards, and failed barriers.</p>
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-gray-400">Loading patterns...</div>
        ) : patterns.length === 0 ? (
          <div className="p-12 text-center text-gray-400">No patterns detected for the current period.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-gray-300">
              <thead className="bg-white/5 text-gray-400 border-b border-white/10">
                <tr>
                  <th className="px-6 py-4 font-medium">Site</th>
                  <th className="px-6 py-4 font-medium">Activity</th>
                  <th className="px-6 py-4 font-medium">LSR</th>
                  <th className="px-6 py-4 font-medium">Failed Barrier</th>
                  <th className="px-6 py-4 font-medium text-right">Frequency</th>
                  <th className="px-6 py-4 font-medium text-center">Trend</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {patterns.map((pattern, idx) => (
                  <tr key={idx} className="hover:bg-white/[0.02] transition-colors">
                    <td className="px-6 py-4 font-medium text-white">{pattern.site_id}</td>
                    <td className="px-6 py-4">{pattern.activity}</td>
                    <td className="px-6 py-4">
                      <span className="bg-orange-500/10 text-orange-400 px-2.5 py-1 rounded border border-orange-500/20 text-xs">
                        {pattern.rule_id}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-red-400">{pattern.failed_barrier}</td>
                    <td className="px-6 py-4 text-right font-mono">{pattern.frequency}</td>
                    <td className="px-6 py-4 flex justify-center">
                      {pattern.trend === "RISING" && <TrendingUp className="text-red-500" size={18} />}
                      {pattern.trend === "FALLING" && <TrendingDown className="text-green-500" size={18} />}
                      {pattern.trend === "STABLE" && <Minus className="text-gray-500" size={18} />}
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
