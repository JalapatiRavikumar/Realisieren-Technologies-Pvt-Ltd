import React from 'react';
import { RefreshCw, Layers } from 'lucide-react';

export default function Navbar({ isScraping, onRefresh, backendStatus }) {
  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-teal-400 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Layers className="w-5 h-5 text-slate-950 font-bold" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
              Multi-Source Web Scraping Dashboard
              <span className="hidden sm:inline-block text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                v1.0
              </span>
            </h1>
            <p className="text-xs text-slate-400">Books & Quotes Data Consolidation Pipeline</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* Backend Status Indicator */}
          <div className="hidden md:flex items-center space-x-2 text-xs font-medium px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60">
            <span
              className={`w-2 h-2 rounded-full ${
                backendStatus === 'online'
                  ? 'bg-emerald-400 animate-pulse'
                  : backendStatus === 'offline'
                  ? 'bg-rose-500'
                  : 'bg-amber-400'
              }`}
            />
            <span className="text-slate-300">
              API {backendStatus === 'online' ? 'Connected' : backendStatus === 'offline' ? 'Offline' : 'Connecting...'}
            </span>
          </div>

          {/* Refresh Button */}
          <button
            onClick={onRefresh}
            disabled={isScraping}
            title="Refresh dashboard data"
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition border border-slate-700 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isScraping ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>
    </header>
  );
}
