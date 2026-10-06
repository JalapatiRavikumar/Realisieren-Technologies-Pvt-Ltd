import React from 'react';
import { ExternalLink, Star, ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight, Eye } from 'lucide-react';

export default function DataTable({
  records = [],
  currentPage = 1,
  totalPages = 1,
  totalRecords = 0,
  limit = 20,
  onPageChange,
  onLimitChange,
  onSelectRecord,
}) {
  return (
    <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl overflow-hidden shadow-xl flex flex-col">
      {/* Table Container with Horizontal Scroll */}
      <div className="overflow-x-auto w-full">
        <table className="w-full text-left border-collapse text-xs sm:text-sm">
          <thead>
            <tr className="bg-slate-900/90 text-slate-400 font-semibold uppercase tracking-wider text-[11px] border-b border-slate-700/80">
              <th className="py-3.5 px-4">Source</th>
              <th className="py-3.5 px-4 min-w-[240px]">Title / Quote</th>
              <th className="py-3.5 px-4">Category</th>
              <th className="py-3.5 px-4">Price</th>
              <th className="py-3.5 px-4">Rating</th>
              <th className="py-3.5 px-4">Author</th>
              <th className="py-3.5 px-4 min-w-[180px]">Tags</th>
              <th className="py-3.5 px-4">Availability</th>
              <th className="py-3.5 px-4">Source URL</th>
              <th className="py-3.5 px-4 text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/50">
            {records.length === 0 ? (
              <tr>
                <td colSpan="10" className="py-12 text-center text-slate-400 text-sm">
                  No records match the current filter or search criteria.
                </td>
              </tr>
            ) : (
              records.map((row, idx) => {
                const isBook = row.source?.toLowerCase().includes('book');
                return (
                  <tr
                    key={idx}
                    className="hover:bg-slate-700/40 transition duration-150 group cursor-pointer"
                    onClick={() => onSelectRecord(row)}
                  >
                    {/* Source */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold ${
                          isBook
                            ? 'bg-sky-500/10 text-sky-400 border border-sky-500/20'
                            : 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                        }`}
                      >
                        {row.source}
                      </span>
                    </td>

                    {/* Title / Quote */}
                    <td className="py-3.5 px-4">
                      <div className="font-semibold text-white group-hover:text-emerald-300 transition line-clamp-2 max-w-sm">
                        {row.name_or_title}
                      </div>
                    </td>

                    {/* Category */}
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-300">
                      {row.category ? (
                        <span className="px-2 py-0.5 rounded bg-slate-900/60 border border-slate-700 text-xs">
                          {row.category}
                        </span>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>

                    {/* Price */}
                    <td className="py-3.5 px-4 whitespace-nowrap font-semibold">
                      {row.price !== null && row.price !== undefined ? (
                        <span className="text-emerald-400">£{row.price}</span>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>

                    {/* Rating */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {row.rating ? (
                        <div className="flex items-center gap-0.5">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-3.5 h-3.5 ${
                                i < Number(row.rating)
                                  ? 'text-amber-400 fill-amber-400'
                                  : 'text-slate-700'
                              }`}
                            />
                          ))}
                        </div>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>

                    {/* Author */}
                    <td className="py-3.5 px-4 whitespace-nowrap text-slate-300">
                      {row.author || <span className="text-slate-600">-</span>}
                    </td>

                    {/* Tags */}
                    <td className="py-3.5 px-4">
                      {row.tags ? (
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {row.tags.split(',').slice(0, 3).map((tag, tIdx) => (
                            <span
                              key={tIdx}
                              className="px-1.5 py-0.5 rounded text-[10px] font-medium bg-slate-900/80 text-indigo-300 border border-slate-700 truncate max-w-[100px]"
                            >
                              #{tag.trim()}
                            </span>
                          ))}
                          {row.tags.split(',').length > 3 && (
                            <span className="text-[10px] text-slate-400 self-center">
                              +{row.tags.split(',').length - 3}
                            </span>
                          )}
                        </div>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>

                    {/* Availability */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      {row.availability ? (
                        <span className="text-emerald-400 text-xs font-medium">
                          {row.availability}
                        </span>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>

                    {/* Source URL */}
                    <td className="py-3.5 px-4 whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      {row.source_url ? (
                        <a
                          href={row.source_url}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-sky-400 hover:text-sky-300 hover:underline"
                        >
                          View Source
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-slate-600">-</span>
                      )}
                    </td>

                    {/* Action */}
                    <td className="py-3.5 px-4 text-center whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                      <button
                        onClick={() => onSelectRecord(row)}
                        className="p-1.5 rounded-lg bg-slate-700/60 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                        title="View Full Record Details"
                      >
                        <Eye className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      <div className="p-4 bg-slate-900/90 border-t border-slate-700/80 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-400">
        <div className="flex items-center gap-3">
          <span>
            Showing page <strong className="text-white">{currentPage}</strong> of{' '}
            <strong className="text-white">{totalPages || 1}</strong> ({totalRecords.toLocaleString()} total items)
          </span>

          <div className="flex items-center gap-1.5 ml-2">
            <span>Per page:</span>
            <select
              value={limit}
              onChange={(e) => onLimitChange(Number(e.target.value))}
              className="bg-slate-800 border border-slate-700 rounded-lg px-2 py-1 text-white focus:outline-none focus:ring-1 focus:ring-emerald-500"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
          </div>
        </div>

        {/* Pagination Navigation Buttons */}
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => onPageChange(1)}
            disabled={currentPage <= 1}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-300 transition"
            title="First Page"
          >
            <ChevronsLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => onPageChange(currentPage - 1)}
            disabled={currentPage <= 1}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-300 transition"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>

          <span className="px-3 py-1 font-semibold text-white bg-slate-800 rounded-lg border border-slate-700">
            {currentPage}
          </span>

          <button
            onClick={() => onPageChange(currentPage + 1)}
            disabled={currentPage >= totalPages}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-300 transition"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
          <button
            onClick={() => onPageChange(totalPages)}
            disabled={currentPage >= totalPages}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:hover:bg-slate-800 text-slate-300 transition"
            title="Last Page"
          >
            <ChevronsRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
