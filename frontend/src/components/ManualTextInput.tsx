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
    <form onSubmit={handleSubmit} className="bg-white/5 border border-white/10 rounded-[28px] p-8 flex flex-col mt-8">
      <h3 className="text-lg font-bold text-white mb-4">Paste Single Report</h3>
      
      <select 
        value={reportType}
        onChange={(e) => setReportType(e.target.value)}
        className="mb-4 bg-white/5 border border-white/10 rounded-xl px-4 py-2 text-sm font-medium text-white outline-none focus:ring-2 focus:ring-blue-500/50"
      >
        <option value="Incident" className="bg-gray-900 text-white">Incident</option>
        <option value="Near Miss" className="bg-gray-900 text-white">Near Miss</option>
        <option value="Unsafe Act" className="bg-gray-900 text-white">Unsafe Act</option>
        <option value="Unsafe Condition" className="bg-gray-900 text-white">Unsafe Condition</option>
        <option value="Spill" className="bg-gray-900 text-white">Spill</option>
        <option value="Observation" className="bg-gray-900 text-white">Observation</option>
      </select>

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Paste your safety report here for live analysis..."
        className="w-full h-32 p-4 bg-white/5 border border-white/10 rounded-2xl outline-none focus:ring-2 focus:ring-blue-500/50 resize-none text-white placeholder:text-gray-500 font-medium mb-4"
      />

      <button
        type="submit"
        disabled={status === "submitting" || !text.trim()}
        className="flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 disabled:from-white/10 disabled:to-white/10 disabled:text-white/30 text-white font-bold rounded-xl transition-all shadow-md active:translate-y-0 hover:-translate-y-0.5"
      >
        {status === "submitting" ? (
          <><Loader2 size={18} className="animate-spin" /> Processing...</>
        ) : (
          <><Send size={18} /> Analyze Report</>
        )}
      </button>

      {message && (
        <p className={`mt-4 text-sm font-bold text-center ${status === "success" ? "text-emerald-600" : "text-red-500"}`}>
          {message}
        </p>
      )}
    </form>
  );
}
