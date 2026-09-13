import { useState } from "react";
import { Send, Loader2 } from "lucide-react";

interface ManualTextInputProps {
  onUploadSuccess: () => void;
}

export function ManualTextInput({ onUploadSuccess }: ManualTextInputProps) {
  const [text, setText] = useState("");
  const [reportType, setReportType] = useState("Incident");
  const [status, setStatus] = useState<"idle" | "submitting" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;

    setStatus("submitting");
    try {
      const res = await fetch("/api/v1/reports/manual", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          source: "manual",
          report_type: reportType,
          original_text: text,
        }),
      });

      if (!res.ok) {
        if (res.status === 429) throw new Error("Too many requests. Please slow down.");
        throw new Error("Failed to submit report");
      }

      setStatus("success");
      setMessage("Report submitted successfully.");
      setText("");
      onUploadSuccess();

      setTimeout(() => {
        setStatus("idle");
        setMessage("");
      }, 3000);
    } catch (err: any) {
      setStatus("error");
      setMessage(err.message || "Failed to submit the report.");
      
      setTimeout(() => {
        setStatus("idle");
        setMessage("");
      }, 3000);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white border border-[var(--color-claude-border)] rounded-xl p-6 flex flex-col shadow-sm focus-within:border-[var(--color-claude-border-strong)] transition-colors">
      <h3 className="text-xl font-serif font-medium text-[var(--color-claude-text)] mb-6 tracking-tight">Direct Entry</h3>
      
      <select 
        value={reportType}
        onChange={(e) => setReportType(e.target.value)}
        className="mb-5 bg-[var(--color-claude-bg-secondary)] border border-[var(--color-claude-border-strong)] rounded-lg px-4 py-3 text-sm text-[var(--color-claude-text)] outline-none focus:ring-2 focus:ring-[var(--color-claude-accent)]/20 transition-all"
      >
        <option value="Incident">Incident</option>
        <option value="Near Miss">Near Miss</option>
        <option value="Unsafe Act">Unsafe Act</option>
        <option value="Unsafe Condition">Unsafe Condition</option>
        <option value="Spill">Spill</option>
        <option value="Observation">Observation</option>
      </select>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type or paste a safety narrative here..."
        className="w-full h-40 p-4 bg-transparent border border-[var(--color-claude-border)] rounded-lg outline-none focus:border-[var(--color-claude-accent)] resize-none text-[var(--color-claude-text)] placeholder:text-[var(--color-claude-text-secondary)] font-serif italic text-lg leading-relaxed mb-6 transition-all"
      />

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={status === "submitting" || !text.trim()}
          className="flex items-center justify-center gap-2 px-8 py-3 bg-[var(--color-claude-text)] hover:bg-[#1a1816] disabled:bg-[var(--color-claude-border-strong)] disabled:text-white/50 text-white rounded-md transition-all shadow-sm font-medium"
        >
          {status === "submitting" ? (
            <><Loader2 size={18} className="animate-spin" /> Ingesting...</>
          ) : (
            <><Send size={18} /> Submit to Pipeline</>
          )}
        </button>
      </div>

      {message && (
        <p className={`mt-5 text-sm font-medium text-center ${status === "success" ? "text-green-700 bg-green-50 p-2 rounded" : "text-red-700 bg-red-50 p-2 rounded"}`}>
          {message}
        </p>
      )}
    </form>
  );
}
