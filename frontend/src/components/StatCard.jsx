import React from 'react';

export default function StatCard({ title, value, subtitle, icon: Icon, color = 'emerald' }) {
  const colorMap = {
    emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20 group-hover:border-emerald-500/40',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20 group-hover:border-blue-500/40',
    purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20 group-hover:border-purple-500/40',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20 group-hover:border-amber-500/40',
    rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20 group-hover:border-rose-500/40',
    slate: 'bg-slate-500/10 text-slate-300 border-slate-500/20 group-hover:border-slate-500/40',
  };

  const selectedColor = colorMap[color] || colorMap.emerald;

  return (
    <div className="group relative overflow-hidden bg-slate-800/60 hover:bg-slate-800/90 transition duration-200 rounded-2xl p-5 border border-slate-700/60 hover:border-slate-600 shadow-md">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2.5 rounded-xl border transition ${selectedColor}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      <div className="mt-4 flex items-baseline justify-between">
        <span className="text-3xl font-extrabold text-white tracking-tight">
          {typeof value === 'number' ? value.toLocaleString() : value ?? 0}
        </span>
      </div>
      {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
    </div>
  );
}
