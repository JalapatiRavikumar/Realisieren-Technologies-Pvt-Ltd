import React from 'react';
import { Search, X } from 'lucide-react';

export default function FilterBar({
  search,
  onSearchChange,
  source,
  onSourceChange,
  totalRecords,
}) {
  return (
    <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 shadow-md flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4">
      {/* Search Input */}
      <div className="relative flex-1">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search by title, author, tags, or category (e.g., Einstein, Poetry)..."
          className="w-full pl-10 pr-10 py-2.5 bg-slate-900/90 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition"
        />
        {search && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white p-1"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      {/* Source Filter Tabs / Dropdown */}
      <div className="flex items-center space-x-2 shrink-0">
        <div className="flex items-center bg-slate-900/90 p-1 rounded-xl border border-slate-700">
          <button
            onClick={() => onSourceChange('all')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              source === 'all' || !source
                ? 'bg-emerald-500 text-slate-950 shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            All Sources
          </button>

          <button
            onClick={() => onSourceChange('books')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              source === 'books'
                ? 'bg-sky-500 text-slate-950 shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            Books to Scrape
          </button>

          <button
            onClick={() => onSourceChange('quotes')}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition ${
              source === 'quotes'
                ? 'bg-indigo-500 text-slate-950 shadow-sm'
                : 'text-slate-300 hover:text-white'
            }`}
          >
            Quotes to Scrape
          </button>
        </div>

        {/* Counter Badge */}
        <div className="hidden lg:flex items-center px-3 py-2 rounded-xl bg-slate-900/60 border border-slate-700/60 text-xs text-slate-400 font-medium">
          Matches: <span className="ml-1 text-white font-bold">{totalRecords.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}
