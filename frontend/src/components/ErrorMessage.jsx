import React from 'react';
import { AlertOctagon, RefreshCw, ServerCrash } from 'lucide-react';

export default function ErrorMessage({
  message = 'An unexpected error occurred.',
  isBackendError = false,
  onRetry,
}) {
  return (
    <div className="bg-rose-500/10 border border-rose-500/30 rounded-2xl p-6 text-slate-200 my-4 shadow-lg shadow-rose-950/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
      <div className="flex items-start space-x-4">
        <div className="p-3 rounded-xl bg-rose-500/20 text-rose-400 border border-rose-500/30 shrink-0">
          {isBackendError ? <ServerCrash className="w-6 h-6" /> : <AlertOctagon className="w-6 h-6" />}
        </div>
        <div>
          <h4 className="text-base font-semibold text-rose-300">
            {isBackendError ? 'Backend Server Unavailable' : 'Error Notice'}
          </h4>
          <p className="text-sm text-slate-300 mt-1 max-w-2xl">{message}</p>
          {isBackendError && (
            <p className="text-xs text-slate-400 mt-2">
              Ensure FastAPI backend is running on <code className="bg-slate-900 px-1.5 py-0.5 rounded text-rose-300">http://localhost:8000</code> via <code className="bg-slate-900 px-1.5 py-0.5 rounded text-emerald-300">uvicorn backend.main:app --reload</code>.
            </p>
          )}
        </div>
      </div>

      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-medium text-sm transition shrink-0 shadow-md"
        >
          <RefreshCw className="w-4 h-4" />
          Retry Connection
        </button>
      )}
    </div>
  );
}
