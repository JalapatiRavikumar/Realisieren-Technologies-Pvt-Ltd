import React from 'react';
import { BookOpen, Quote, ExternalLink } from 'lucide-react';

export default function SourceCard({
  name,
  url,
  type = 'books',
  status = 'Completed',
  collected = 0,
  cleaned = 0,
  rejected = 0,
  duplicates = 0,
}) {
  const isBooks = type === 'books';
  const Icon = isBooks ? BookOpen : Quote;
  const badgeColor = isBooks
    ? 'bg-sky-500/10 text-sky-400 border-sky-500/20'
    : 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';

  return (
    <div className="bg-slate-800/70 border border-slate-700/80 rounded-2xl p-6 shadow-md relative overflow-hidden flex flex-col justify-between">
      {/* Background Subtle Gradient */}
      <div className={`absolute top-0 right-0 w-32 h-32 blur-3xl rounded-full pointer-events-none ${isBooks ? 'bg-sky-500/10' : 'bg-indigo-500/10'}`} />

      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div className={`p-3 rounded-xl border ${badgeColor}`}>
              <Icon className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-1.5">
                {name}
                <a
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  title={`Open ${name} in new tab`}
                  className="text-slate-400 hover:text-white transition"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </h3>
              <p className="text-xs text-slate-400">Dynamic Pagination & Schema Normalization</p>
            </div>
          </div>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            {status}
          </span>
        </div>

        {/* Breakdown Stats */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-700/60">
          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[11px] font-medium text-slate-400 block">Collected</span>
            <span className="text-lg font-bold text-white mt-0.5 block">{collected.toLocaleString()}</span>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[11px] font-medium text-slate-400 block">Cleaned</span>
            <span className="text-lg font-bold text-emerald-400 mt-0.5 block">{cleaned.toLocaleString()}</span>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[11px] font-medium text-slate-400 block">Rejected</span>
            <span className={`text-lg font-bold mt-0.5 block ${rejected > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
              {rejected.toLocaleString()}
            </span>
          </div>

          <div className="bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
            <span className="text-[11px] font-medium text-slate-400 block">Duplicates</span>
            <span className={`text-lg font-bold mt-0.5 block ${duplicates > 0 ? 'text-amber-400' : 'text-slate-400'}`}>
              {duplicates.toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
