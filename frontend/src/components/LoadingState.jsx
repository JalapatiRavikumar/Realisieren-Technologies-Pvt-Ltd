import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Loading data...' }) {
  return (
    <div className="w-full flex flex-col items-center justify-center py-16 px-4">
      <div className="relative">
        <div className="w-12 h-12 rounded-full border-2 border-emerald-500/20 border-t-emerald-500 animate-spin" />
        <Loader2 className="w-6 h-6 text-emerald-400 absolute inset-0 m-auto animate-pulse" />
      </div>
      <p className="mt-4 text-sm font-medium text-slate-300">{message}</p>
      <p className="text-xs text-slate-500 mt-1">Please wait while the pipeline processes data</p>
    </div>
  );
}
