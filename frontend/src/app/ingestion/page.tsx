"use client";

import { useState } from "react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { ManualTextInput } from "@/components/ManualTextInput";
import { CheckCircle2, Loader2 } from "lucide-react";

export default function IngestionPage() {
  const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "done">("idle");
  const [jobId, setJobId] = useState<string | null>(null);
  
  // A complete ingestion module with polling would ping a /jobs endpoint.
  // For now we'll simulate the UX flow.
  const handleSuccess = () => {
    setStatus("done");
    setTimeout(() => setStatus("idle"), 3000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in duration-700">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Ingestion</h1>
        <p className="text-gray-400">Upload CSVs or submit manual reports for automated safety analysis.</p>
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl p-8 relative overflow-hidden">
        {status === "done" && (
          <div className="absolute inset-0 bg-green-500/10 backdrop-blur-sm z-10 flex flex-col items-center justify-center animate-in fade-in">
            <CheckCircle2 size={48} className="text-green-500 mb-4" />
            <p className="text-xl font-medium text-white">Upload Complete & Processing Started!</p>
          </div>
        )}
        
        <h2 className="text-xl font-semibold text-white mb-6">Bulk Upload (CSV)</h2>
        <UploadDropzone onUploadSuccess={handleSuccess} />
      </div>

      <div className="bg-white/5 border border-white/10 rounded-2xl p-8">
        <h2 className="text-xl font-semibold text-white mb-6">Manual Entry</h2>
        <ManualTextInput onUploadSuccess={handleSuccess} />
      </div>
    </div>
  );
}
