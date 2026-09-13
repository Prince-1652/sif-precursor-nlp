"use client";

import { usePathname } from "next/navigation";
import { ShieldCheck } from "lucide-react";
import Link from "next/link";

export function TopNav() {
  const pathname = usePathname();

  return (
    <nav className="sticky top-0 z-50 w-full bg-[var(--color-claude-bg)]/80 backdrop-blur-xl border-b border-[var(--color-claude-border)]">
      <div className="w-full px-6 md:px-10 h-16 flex items-center justify-between">
        <div className="flex items-center gap-10">
          <Link href="/" className="flex items-center gap-3 mr-4 group">
            <div className="w-8 h-8 rounded-md bg-[var(--color-claude-accent)] flex items-center justify-center text-white shadow-sm transition-transform group-hover:scale-105">
              <ShieldCheck size={18} strokeWidth={2.5} />
            </div>
            <span className="font-serif font-bold text-2xl tracking-tight text-[var(--color-claude-text)]">
              Safety Intelligence
            </span>
          </Link>
          <div className="hidden md:flex items-center gap-8 text-base font-bold">
            <NavLink href="/" active={pathname === "/"}>Dashboard</NavLink>
            <NavLink href="/analyze" active={pathname === "/analyze"}>Analyze</NavLink>
            <NavLink href="/reports" active={pathname === "/reports"}>Reports</NavLink>
            <NavLink href="/patterns" active={pathname === "/patterns"}>Patterns</NavLink>
            <NavLink href="/admin" active={pathname === "/admin"}>Admin</NavLink>
          </div>
        </div>
        <div>
          {pathname !== "/ingestion" && (
            <Link 
              href="/ingestion" 
              className="px-6 py-2.5 bg-[var(--color-claude-accent)] hover:bg-[var(--color-claude-accent-hover)] text-white rounded-md text-base font-bold transition-colors shadow-sm"
            >
              Upload Data
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}

function NavLink({ href, active, children }: { href: string, active: boolean, children: React.ReactNode }) {
  return (
    <Link 
      href={href} 
      className={`transition-colors ${
        active 
          ? "text-[var(--color-claude-text)] border-b-2 border-[var(--color-claude-accent)] pb-1 -mb-[3px]" 
          : "text-[var(--color-claude-text-secondary)] hover:text-[var(--color-claude-text)]"
      }`}
    >
      {children}
    </Link>
  );
}
