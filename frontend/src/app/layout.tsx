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
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
                <ShieldCheck size={20} />
              </div>
              <span className="font-semibold text-lg tracking-tight text-gray-100">Safety Intelligence</span>
            </div>
          </div>
        </nav>
        <main className="flex-1 w-full px-8 py-12">
          {children}
        </main>
      </body>
    </html>
  );
}
