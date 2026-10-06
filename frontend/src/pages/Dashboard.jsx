import React, { useState, useEffect, useCallback } from 'react';
import {
  Play,
  FileSpreadsheet,
  FileCode,
  Clock,
  CheckCircle,
  AlertCircle,
  Database,
  Layers,
  Sparkles,
  BookOpen,
  Quote,
  ShieldCheck,
  ShieldAlert,
  CopyX,
} from 'lucide-react';

import StatCard from '../components/StatCard';
import SourceCard from '../components/SourceCard';
import FilterBar from '../components/FilterBar';
import DataTable from '../components/DataTable';
import RecordDetails from '../components/RecordDetails';
import LoadingState from '../components/LoadingState';
import ErrorMessage from '../components/ErrorMessage';

import {
  getDashboard,
  getRecords,
  runScraper,
  getDownloadCsvUrl,
  getDownloadSummaryUrl,
} from '../services/api';

export default function Dashboard({ onBackendStatusChange }) {
  // State for Dashboard Stats
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [backendError, setBackendError] = useState(null);

  // State for Records Table
  const [records, setRecords] = useState([]);
  const [loadingRecords, setLoadingRecords] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalMatching, setTotalMatching] = useState(0);
  const [limit, setLimit] = useState(20);
  const [search, setSearch] = useState('');
  const [source, setSource] = useState('all');

  // Scraping Execution State
  const [isScraping, setIsScraping] = useState(false);
  const [scrapeNotification, setScrapeNotification] = useState(null);

  // Selected Record for Modal
  const [selectedRecord, setSelectedRecord] = useState(null);

  // 1. Fetch Dashboard Stats
  const fetchDashboardStats = useCallback(async () => {
    try {
      setBackendError(null);
      const data = await getDashboard();
      setStats(data);
      if (onBackendStatusChange) onBackendStatusChange('online');
    } catch (err) {
      console.error('Failed to load dashboard stats:', err);
      setBackendError('Unable to connect to the backend. Please make sure the FastAPI server is running on http://localhost:8000.');
      if (onBackendStatusChange) onBackendStatusChange('offline');
    } finally {
      setLoadingStats(false);
    }
  }, [onBackendStatusChange]);

  // 2. Fetch Paginated Records
  const fetchRecords = useCallback(async () => {
    setLoadingRecords(true);
    try {
      const data = await getRecords({
        page: currentPage,
        limit,
        source,
        search,
      });
      setRecords(data.records || []);
      setTotalPages(data.total_pages || 1);
      setTotalMatching(data.total || 0);
    } catch (err) {
      console.error('Failed to load records:', err);
    } finally {
      setLoadingRecords(false);
    }
  }, [currentPage, limit, source, search]);

  // Initial Load
  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  useEffect(() => {
    fetchRecords();
  }, [fetchRecords]);

  // Trigger Scraper
  const handleRunScraper = async () => {
    setIsScraping(true);
    setScrapeNotification({ type: 'info', message: 'Scraping in progress... Executing Python pipeline.' });

    try {
      const res = await runScraper({ source: 'all' });
      if (res.status === 'completed') {
        setScrapeNotification({
          type: 'success',
          message: `Scraping completed successfully in ${res.data?.execution_time_seconds || 0}s! Found ${res.data?.final_record_count || 0} items.`,
        });
        await fetchDashboardStats();
        await fetchRecords();
      } else if (res.status === 'running') {
        setScrapeNotification({ type: 'warning', message: res.message || 'Scraper is already running.' });
      } else {
        setScrapeNotification({ type: 'error', message: res.message || 'Failed to complete scraping.' });
      }
    } catch (err) {
      console.error('Scrape execution failed:', err);
      const errMsg = err.response?.data?.detail || 'An error occurred during scraper execution. Please verify backend logs.';
      setScrapeNotification({ type: 'error', message: errMsg });
    } finally {
      setIsScraping(false);
    }
  };

  // Reset page to 1 when filters change
  const handleSearchChange = (newSearch) => {
    setSearch(newSearch);
    setCurrentPage(1);
  };

  const handleSourceChange = (newSource) => {
    setSource(newSource);
    setCurrentPage(1);
  };

  // Format date helper
  const formatDateTime = (isoString) => {
    if (!isoString) return 'Not yet executed';
    try {
      const d = new Date(isoString);
      return d.toLocaleString('en-US', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Hero Banner with Run Button */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-700/80 rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="space-y-2 z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            Live Consolidated Data Engine
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Multi-Source Web Scraping Dashboard
          </h2>
          <p className="text-slate-400 text-sm max-w-xl leading-relaxed">
            Consolidating structured books and quote repositories via Python scraping, resilient cleaning, schema validation, and deterministic deduplication.
          </p>
        </div>

        {/* Action Buttons: Run Scraper & Downloads */}
        <div className="flex flex-wrap items-center gap-3 z-10 w-full md:w-auto">
          <button
            onClick={handleRunScraper}
            disabled={isScraping || backendError}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-emerald-500/25 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            <Play className={`w-4 h-4 ${isScraping ? 'animate-spin' : 'fill-slate-950'}`} />
            {isScraping ? 'Scraping in progress...' : 'Run Scraper'}
          </button>

          <a
            href={getDownloadCsvUrl()}
            download
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-4 py-3.5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs transition"
          >
            <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
            Download CSV
          </a>

          <a
            href={getDownloadSummaryUrl()}
            download
            className="flex-1 sm:flex-initial inline-flex items-center justify-center gap-2 px-4 py-3.5 rounded-2xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs transition"
          >
            <FileCode className="w-4 h-4 text-indigo-400" />
            Download Summary JSON
          </a>
        </div>
      </div>

      {/* Backend Error State Banner */}
      {backendError && (
        <ErrorMessage
          message={backendError}
          isBackendError={true}
          onRetry={fetchDashboardStats}
        />
      )}

      {/* Scrape Execution Alert Banner */}
      {scrapeNotification && (
        <div
          className={`p-4 rounded-2xl border flex items-center justify-between text-sm transition ${
            scrapeNotification.type === 'success'
              ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
              : scrapeNotification.type === 'warning'
              ? 'bg-amber-500/10 border-amber-500/30 text-amber-300'
              : scrapeNotification.type === 'error'
              ? 'bg-rose-500/10 border-rose-500/30 text-rose-300'
              : 'bg-blue-500/10 border-blue-500/30 text-blue-300'
          }`}
        >
          <div className="flex items-center gap-3">
            {scrapeNotification.type === 'success' ? (
              <CheckCircle className="w-5 h-5 shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 shrink-0" />
            )}
            <span>{scrapeNotification.message}</span>
          </div>
          <button
            onClick={() => setScrapeNotification(null)}
            className="text-xs underline hover:opacity-80 ml-4 font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Last Run Information Bar */}
      {stats && (
        <div className="bg-slate-800/40 border border-slate-700/60 rounded-2xl px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-emerald-400" />
            <span>Last scraper run: <strong className="text-slate-200">{formatDateTime(stats.last_run)}</strong></span>
          </div>

          <div className="flex items-center gap-4">
            <span>Status: <strong className="text-emerald-400">{stats.is_running ? 'Scraping Active' : 'Completed'}</strong></span>
            <span>Execution time: <strong className="text-slate-200">{stats.execution_time_seconds}s</strong></span>
          </div>
        </div>
      )}

      {/* Stats Cards Grid (7 Cards) */}
      <section>
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <Database className="w-4 h-4 text-emerald-400" /> Pipeline Metrics Overview
        </h3>

        {loadingStats ? (
          <LoadingState message="Loading pipeline metrics..." />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
            <StatCard
              title="Total Raw"
              value={stats?.total_records}
              subtitle="All sources"
              icon={Database}
              color="slate"
            />
            <StatCard
              title="Books"
              value={stats?.books}
              subtitle="Books to Scrape"
              icon={BookOpen}
              color="blue"
            />
            <StatCard
              title="Quotes"
              value={stats?.quotes}
              subtitle="Quotes to Scrape"
              icon={Quote}
              color="purple"
            />
            <StatCard
              title="Valid Records"
              value={stats?.valid_records}
              subtitle="Passed quality gate"
              icon={ShieldCheck}
              color="emerald"
            />
            <StatCard
              title="Rejected"
              value={stats?.rejected_records}
              subtitle="Validation errors"
              icon={ShieldAlert}
              color="rose"
            />
            <StatCard
              title="Duplicates"
              value={stats?.duplicates}
              subtitle="Deduplicated"
              icon={CopyX}
              color="amber"
            />
            <StatCard
              title="Final Dataset"
              value={stats?.final_records}
              subtitle="Exported records"
              icon={CheckCircle}
              color="emerald"
            />
          </div>
        )}
      </section>

      {/* Target Source Detail Cards (2 Columns) */}
      <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <SourceCard
          name="Books to Scrape"
          url="https://books.toscrape.com/"
          type="books"
          status={stats?.sources_detail?.books?.status || 'Completed'}
          collected={stats?.sources_detail?.books?.records_collected || 0}
          cleaned={stats?.sources_detail?.books?.cleaned_records || 0}
          rejected={stats?.sources_detail?.books?.rejected_records || 0}
          duplicates={stats?.sources_detail?.books?.duplicates || 0}
        />

        <SourceCard
          name="Quotes to Scrape"
          url="https://quotes.toscrape.com/"
          type="quotes"
          status={stats?.sources_detail?.quotes?.status || 'Completed'}
          collected={stats?.sources_detail?.quotes?.records_collected || 0}
          cleaned={stats?.sources_detail?.quotes?.cleaned_records || 0}
          rejected={stats?.sources_detail?.quotes?.rejected_records || 0}
          duplicates={stats?.sources_detail?.quotes?.duplicates || 0}
        />
      </section>

      {/* Filter and Consolidated Records Table */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            Consolidated Records Dataset
          </h3>
          <span className="text-xs text-slate-400">
            Source of truth: <code className="bg-slate-800 px-2 py-0.5 rounded text-emerald-300 font-mono">output/final_dataset.csv</code>
          </span>
        </div>

        {/* Filter & Search Bar */}
        <FilterBar
          search={search}
          onSearchChange={handleSearchChange}
          source={source}
          onSourceChange={handleSourceChange}
          totalRecords={totalMatching}
        />

        {/* Table View */}
        {loadingRecords ? (
          <div className="bg-slate-800/80 rounded-2xl border border-slate-700/80 p-8">
            <LoadingState message="Fetching filtered dataset records..." />
          </div>
        ) : (
          <DataTable
            records={records}
            currentPage={currentPage}
            totalPages={totalPages}
            totalRecords={totalMatching}
            limit={limit}
            onPageChange={setCurrentPage}
            onLimitChange={(newLimit) => {
              setLimit(newLimit);
              setCurrentPage(1);
            }}
            onSelectRecord={(rec) => setSelectedRecord(rec)}
          />
        )}
      </section>

      {/* Record Details Modal */}
      {selectedRecord && (
        <RecordDetails
          record={selectedRecord}
          onClose={() => setSelectedRecord(null)}
        />
      )}
    </div>
  );
}
