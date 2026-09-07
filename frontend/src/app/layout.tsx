import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { ShieldCheck } from "lucide-react";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Safety Intelligence",
  description: "AI-Powered Safety Analysis Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} min-h-screen flex flex-col`}>
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
                <a href="/" className="hover:text-white transition-colors">Dashboard</a>
                <a href="/analyze" className="hover:text-white transition-colors">Analyze</a>
                <a href="/reports" className="hover:text-white transition-colors">Reports</a>
                <a href="/patterns" className="hover:text-white transition-colors">Patterns</a>
                <a href="/admin" className="hover:text-white transition-colors">Admin</a>
              </div>
            </div>
            <div>
              <a href="/ingestion" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-md text-sm font-medium transition-colors">
                Upload CSV
              </a>
            </div>
          </div>
        </nav>
        <main className="flex-1 w-full px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
