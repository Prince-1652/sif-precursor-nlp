import { useState } from "react";
import { Search, Loader2 } from "lucide-react";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export function SearchBar({ onSearch, isLoading }: SearchBarProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-2xl mb-8 group">
      <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-500 transition-colors">
        {isLoading ? <Loader2 size={20} className="animate-spin" /> : <Search size={20} />}
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for similar incidents, hazards, or root causes..."
        className="w-full h-14 pl-12 pr-4 bg-white/5 border border-white/10 rounded-[24px] outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all text-white placeholder:text-gray-500"
      />
      <button 
        type="submit" 
        disabled={isLoading || !query.trim()}
        className="absolute inset-y-2 right-2 px-5 bg-white text-black hover:bg-gray-200 disabled:bg-white/10 disabled:text-gray-500 text-sm font-semibold rounded-[16px] transition-colors shadow-md"
      >
        Search
      </button>
    </form>
  );
}
