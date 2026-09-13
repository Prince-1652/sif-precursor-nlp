"use client";

import { useState, useEffect } from "react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { ManualTextInput } from "@/components/ManualTextInput";
import { CheckCircle2 } from "lucide-react";
import { useRouter } from "next/navigation";

export default function IngestionPage() {
  const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "done">("idle");
  const router = useRouter();
  
  useEffect(() => {
    if (status === "done") {
      const t = setTimeout(() => {
        router.push("/reports");
      }, 1500);
      return () => clearTimeout(t);
    }
  }, [status, router]);

  const handleSuccess = () => {
    setStatus("done");
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-1000 relative">
      {status === "done" && (
        <div className="fixed inset-0 bg-white/80 backdrop-blur-sm z-50 flex flex-col items-center justify-center animate-in fade-in">
          <CheckCircle2 size={64} className="text-[#5C6E53] mb-6" />
          <p className="text-2xl font-serif font-medium text-[var(--color-claude-text)]">Ingestion Successful</p>
          <p className="text-[var(--color-claude-text-secondary)] mt-2">The pipeline is now analyzing the data.</p>
        </div>
      )}
      
      <div className="border-b border-[var(--color-claude-border)] pb-5">
        <h1 className="text-4xl md:text-5xl font-serif font-bold text-[var(--color-claude-text)] mb-3 tracking-tight">Data Ingestion</h1>
        <p className="text-[var(--color-claude-text-secondary)] text-lg">Upload datasets or submit individual narratives for intelligence processing.</p>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <section>
          <h2 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-6">Bulk Upload (CSV)</h2>
          <UploadDropzone onUploadSuccess={handleSuccess} />
        </section>

        <section>
          <h2 className="text-sm font-bold text-[var(--color-claude-text-secondary)] uppercase tracking-widest mb-6">Manual Entry</h2>
          <ManualTextInput onUploadSuccess={handleSuccess} />
        </section>
      </div>
    </div>
  );
}
