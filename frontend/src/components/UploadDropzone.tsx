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
      setMessage("Data successfully ingested. Pipeline processing started.");
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
        "bg-white border rounded-xl relative flex flex-col items-center justify-center p-10 transition-all duration-300 border-dashed border-2 cursor-pointer shadow-sm",
        isDragging 
          ? "border-[var(--color-claude-accent)] bg-[var(--color-claude-bg-secondary)] scale-[1.01]" 
          : "border-[var(--color-claude-border-strong)] hover:border-[var(--color-claude-text-secondary)] hover:bg-[var(--color-claude-bg-secondary)]"
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
          <div className="w-16 h-16 bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border)] text-[var(--color-claude-text)] rounded-full flex items-center justify-center mb-6 shadow-sm">
            <UploadCloud size={28} strokeWidth={2} />
          </div>
          <h3 className="text-xl font-serif font-medium text-[var(--color-claude-text)] mb-3 tracking-tight">Upload Dataset</h3>
          <p className="text-sm text-[var(--color-claude-text-secondary)] text-center max-w-sm">
            Drag and drop your CSV dataset here, or click to browse. The intelligence pipeline will automatically begin processing.
          </p>
        </>
      )}

      {status === "uploading" && (
        <div className="flex flex-col items-center text-[var(--color-claude-text)]">
          <Loader2 size={36} className="animate-spin mb-5 text-[var(--color-claude-accent)]" />
          <p className="text-sm font-medium">Ingesting dataset & scheduling pipeline...</p>
        </div>
      )}

      {status === "success" && (
        <div className="flex flex-col items-center text-[#5C6E53]">
          <CheckCircle2 size={40} className="mb-5" />
          <p className="text-sm font-medium">{message}</p>
        </div>
      )}

      {status === "error" && (
        <div className="flex flex-col items-center text-red-700">
          <AlertCircle size={40} className="mb-5" />
          <p className="text-sm font-medium">{message}</p>
        </div>
      )}
    </div>
  );
}
