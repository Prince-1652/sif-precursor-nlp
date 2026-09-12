"use client";

import { useState, useCallback } from "react";
import { UploadCloud, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import clsx from "clsx";

interface UploadDropzoneProps {
  onUploadSuccess: () => void;
}

export function UploadDropzone({ onUploadSuccess }: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragging(true);
    } else if (e.type === "dragleave") {
      setIsDragging(false);
    }
  }, []);

  const uploadFile = async (file: File) => {
    if (!file.name.endsWith(".csv")) {
      setStatus("error");
      setMessage("Please upload a valid CSV file.");
      return;
    }

    setStatus("uploading");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/api/v1/reports/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        if (res.status === 429) throw new Error("Too many requests. Please slow down.");
        throw new Error("Upload failed");
      }
      
      setStatus("success");
      setMessage("CSV uploaded successfully. Processing started.");
      onUploadSuccess();
      
      setTimeout(() => {
        setStatus("idle");
        setMessage("");
      }, 3000);
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Failed to upload the file. Ensure the backend is running.");
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  return (
    <div
      className={clsx(
        "bg-white/5 backdrop-blur-xl border shadow-lg rounded-[28px] relative flex flex-col items-center justify-center p-12 transition-all duration-300 border-dashed border-[1.5px]",
        isDragging ? "border-blue-400 bg-blue-500/10 scale-[1.02]" : "border-white/20 hover:border-white/40 hover:bg-white/10"
      )}
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
    >
      <input
        type="file"
        accept=".csv"
        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        onChange={handleChange}
        disabled={status === "uploading"}
      />
      
      {status === "idle" && (
        <>
          <div className="w-16 h-16 bg-white/60 backdrop-blur-md shadow-sm border border-white/80 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
            <UploadCloud size={28} strokeWidth={2.5} />
          </div>
          <h3 className="text-lg font-bold text-white mb-2">Upload Safety Reports</h3>
          <p className="text-sm text-gray-400 text-center max-w-sm font-medium">
            Drag and drop your CSV file here, or click to browse. AI will automatically analyze the contents.
          </p>
        </>
      )}

      {status === "uploading" && (
        <div className="flex flex-col items-center text-blue-600">
          <Loader2 size={32} className="animate-spin mb-4" />
          <p className="text-sm font-medium">Uploading and scheduling processing...</p>
        </div>
      )}

      {status === "success" && (
        <div className="flex flex-col items-center text-emerald-600">
          <CheckCircle2 size={32} className="mb-4" />
          <p className="text-sm font-medium">{message}</p>
        </div>
      )}

      {status === "error" && (
        <div className="flex flex-col items-center text-red-600">
          <AlertCircle size={32} className="mb-4" />
          <p className="text-sm font-medium">{message}</p>
        </div>
      )}
    </div>
  );
}
