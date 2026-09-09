"use client";

import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export function TopNav() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 w-full bg-[#050505]/80 backdrop-blur-xl border-b border-white/5">
      <div className="w-full px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-8">
          <div className="flex items-center gap-3 mr-4">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
              <ShieldCheck size={20} />
            </div>
            <span className="font-semibold text-lg tracking-tight text-gray-100">Safety Intelligence</span>
          </div>
          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-gray-400">
            <Link href="/" className={`${pathname === "/" ? "text-white" : "hover:text-white transition-colors"}`}>Dashboard</Link>
            <Link href="/analyze" className={`${pathname === "/analyze" ? "text-white" : "hover:text-white transition-colors"}`}>Analyze</Link>
            <Link href="/reports" className={`${pathname === "/reports" ? "text-white" : "hover:text-white transition-colors"}`}>Reports</Link>
            <Link href="/patterns" className={`${pathname === "/patterns" ? "text-white" : "hover:text-white transition-colors"}`}>Patterns</Link>
            <Link href="/admin" className={`${pathname === "/admin" ? "text-white" : "hover:text-white transition-colors"}`}>Admin</Link>
          </div>
        </div>
        <div>
          {pathname !== "/ingestion" && (
            <Link href="/ingestion" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md text-sm font-medium transition-colors">
              Upload CSV
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}
