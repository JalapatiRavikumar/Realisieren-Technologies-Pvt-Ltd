import React from 'react';
import { X, ExternalLink, Star, Tag, CheckCircle2 } from 'lucide-react';

export default function RecordDetails({ record, onClose }) {
  if (!record) return null;

  const isBook = record.source?.toLowerCase().includes('book');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl p-6 sm:p-8 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Source Badge */}
        <div className="flex items-center gap-2 mb-3">
          <span
            className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${
              isBook
                ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
            }`}
          >
            {record.source}
          </span>
          {record.availability && (
            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              {record.availability}
            </span>
          )}
        </div>

        {/* Title or Quote text */}
        <h3 className="text-xl font-bold text-white leading-snug mb-4">
          {record.name_or_title}
        </h3>

        {/* Key Attributes Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 my-6 bg-slate-800/60 p-4 rounded-2xl border border-slate-700/60">
          {record.author && (
            <div>
              <span className="text-xs font-medium text-slate-400 block">Author</span>
              <span className="text-sm font-semibold text-white mt-0.5 block">{record.author}</span>
            </div>
          )}

          {record.category && (
            <div>
              <span className="text-xs font-medium text-slate-400 block">Category</span>
              <span className="text-sm font-semibold text-white mt-0.5 block">{record.category}</span>
            </div>
          )}

          {record.price !== null && record.price !== undefined && (
            <div>
              <span className="text-xs font-medium text-slate-400 block">Price</span>
              <span className="text-sm font-bold text-emerald-400 mt-0.5 block">£{record.price}</span>
            </div>
          )}

          {record.rating && (
            <div>
              <span className="text-xs font-medium text-slate-400 block">Rating</span>
              <div className="flex items-center gap-1 mt-0.5">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-4 h-4 ${
                      i < Number(record.rating)
                        ? 'text-amber-400 fill-amber-400'
                        : 'text-slate-600'
                    }`}
                  />
                ))}
                <span className="text-xs font-semibold text-slate-300 ml-1">({record.rating}/5)</span>
              </div>
            </div>
          )}

          {record.scraped_at && (
            <div className="sm:col-span-2">
              <span className="text-xs font-medium text-slate-400 block">Scraped Timestamp</span>
              <span className="text-xs font-mono text-slate-300 mt-0.5 block">{record.scraped_at}</span>
            </div>
          )}
        </div>

        {/* Tags */}
        {record.tags && (
          <div className="mb-6">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-2 flex items-center gap-1.5">
              <Tag className="w-3.5 h-3.5 text-indigo-400" /> Tags
            </span>
            <div className="flex flex-wrap gap-1.5">
              {record.tags.split(',').map((tag, idx) => (
                <span
                  key={idx}
                  className="px-2.5 py-1 rounded-lg text-xs font-medium bg-slate-800 text-indigo-300 border border-slate-700"
                >
                  #{tag.trim()}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Description */}
        {record.description && (
          <div className="mb-6">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 block mb-1">
              Description
            </span>
            <p className="text-sm text-slate-300 leading-relaxed bg-slate-800/40 p-4 rounded-xl border border-slate-700/40">
              {record.description}
            </p>
          </div>
        )}

        {/* Source URL Action */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800 mt-6">
          <span className="text-xs text-slate-500">Origin: {record.source}</span>
          {record.source_url && (
            <a
              href={record.source_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-xs transition shadow-md"
            >
              Visit Source Webpage
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
