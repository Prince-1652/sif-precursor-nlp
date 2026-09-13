import type { Metadata } from "next";
import { Newsreader, Outfit } from "next/font/google";
import "./globals.css";
import { TopNav } from "@/components/TopNav";

const newsreader = Newsreader({ 
  subsets: ["latin"],
  variable: "--font-newsreader",
  style: ["normal", "italic"] 
});

const outfit = Outfit({ 
  subsets: ["latin"],
  variable: "--font-outfit"
});

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
      <body className={`${outfit.variable} ${newsreader.variable} font-sans min-h-screen flex flex-col`}>
        <TopNav />
        <main className="flex-1 w-full px-6 py-10 md:px-10 md:py-16">
          {children}
        </main>
      </body>
    </html>
  );
}
