import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      <Navbar
        onRefresh={handleRefresh}
        backendStatus={backendStatus}
      />
      <main className="flex-1">
        <Dashboard
          key={refreshKey}
          onBackendStatusChange={setBackendStatus}
        />
      </main>
      <footer className="border-t border-slate-800/80 bg-slate-900/60 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>Python Web Scraping & Data Consolidation Pipeline</span>
          <span className="font-mono text-slate-400">FastAPI Backend + React Frontend + BeautifulSoup Scrapers</span>
        </div>
      </footer>
    </div>
  );
}
