import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  History, Search, Filter, Trash2, ExternalLink, 
  Download, RefreshCw, Calendar, AlertCircle
} from 'lucide-react';
import api from '../services/api';

export default function HistoryPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [sortOrder, setSortOrder] = useState('newest');

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = {};
      if (category) params.category = category;
      if (search) params.search = search;
      const res = await api.getHistory(params);
      setItems(res.data.items || []);
    } catch (err) {
      console.error('Failed to fetch history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [category]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete analysis record #${id}?`)) return;
    try {
      await api.deleteAnalysis(id);
      setItems(items.filter((item) => item.id !== id));
    } catch (err) {
      console.error('Failed to delete analysis:', err);
    }
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(items, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `truthlens_analysis_history_${new Date().toISOString().slice(0,10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Sort items
  const sortedItems = [...items].sort((a, b) => {
    if (sortOrder === 'newest') {
      return new Date(b.created_at) - new Date(a.created_at);
    }
    return new Date(a.created_at) - new Date(b.created_at);
  });

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Audit & Article History</h1>
          <p className="text-xs text-slate-400">Search, filter, and inspect previously analyzed news stories</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleExportJSON}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#141F35] hover:bg-[#1A2946] border border-white/10 text-xs font-semibold text-slate-200 transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Export JSON</span>
          </button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="p-4 rounded-2xl bg-[#141F35] border border-white/10 flex flex-col md:flex-row items-center justify-between gap-3 shadow-lg">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-96">
          <input
            type="text"
            placeholder="Search by headline or topic..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-xl bg-[#10182A] border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 font-sans"
          />
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
        </form>

        <div className="flex items-center gap-3 w-full md:w-auto">
          {/* Category Filter */}
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#10182A] border border-white/10 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
          >
            <option value="">All Categories</option>
            <option value="Likely Genuine">Likely Genuine</option>
            <option value="Potentially Misleading">Potentially Misleading</option>
            <option value="Needs Further Verification">Needs Verification</option>
          </select>

          {/* Sort Order */}
          <select
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value)}
            className="px-3 py-2 rounded-xl bg-[#10182A] border border-white/10 text-xs text-slate-200 focus:outline-none focus:border-purple-500"
          >
            <option value="newest">Sort: Newest First</option>
            <option value="oldest">Sort: Oldest First</option>
          </select>

          <button
            onClick={fetchHistory}
            className="p-2 rounded-xl bg-[#10182A] hover:bg-white/5 border border-white/10 text-slate-400 hover:text-white transition-colors"
            title="Refresh list"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* History List */}
      {loading ? (
        <div className="flex flex-col items-center justify-center py-20 space-y-3">
          <div className="w-8 h-8 border-3 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
          <span className="text-xs text-slate-400">Loading analysis archive...</span>
        </div>
      ) : sortedItems.length === 0 ? (
        <div className="p-12 rounded-2xl bg-[#141F35] border border-white/10 text-center space-y-3">
          <AlertCircle className="w-10 h-10 text-slate-500 mx-auto" />
          <h3 className="text-base font-bold text-white">No Analysis Records Found</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            {search || category ? 'No records matched your search filters.' : 'You have not analyzed any news articles yet. Head over to the News Analysis Studio to get started.'}
          </p>
          <Link
            to="/studio"
            className="inline-block px-4 py-2 rounded-xl bg-purple-600 text-white text-xs font-semibold shadow-md"
          >
            Analyze First Article
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {sortedItems.map((item) => (
            <div
              key={item.id}
              className="p-5 rounded-2xl bg-[#141F35] border border-white/5 hover:border-white/15 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group"
            >
              <div className="space-y-1.5 max-w-2xl">
                <div className="flex items-center gap-2 text-xs">
                  <span className={`px-2.5 py-0.5 rounded-full font-semibold border text-[11px] ${
                    item.predicted_class === 'Likely Genuine'
                      ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      : item.predicted_class === 'Potentially Misleading'
                      ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                      : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                  }`}>
                    {item.predicted_class}
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1">
                    <Calendar className="w-3 h-3 text-slate-500" />
                    {item.created_at ? item.created_at.slice(0, 10) : ''}
                  </span>
                  <span className="text-slate-500">•</span>
                  <span className="text-purple-400 font-mono text-[11px]">
                    Lang: {(item.language || 'en').toUpperCase()}
                  </span>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-purple-300 transition-colors">
                  {item.article_title || 'Untitled Article'}
                </h3>

                <p className="text-xs text-slate-400 line-clamp-2">
                  {item.article_content || ''}
                </p>
              </div>

              {/* Actions & Score */}
              <div className="flex items-center gap-4 justify-between md:justify-end pt-3 md:pt-0 border-t md:border-t-0 border-white/5">
                <div className="text-right">
                  <span className="text-[10px] text-slate-500 block uppercase font-mono">Credibility</span>
                  <span className="text-lg font-black text-white font-mono">
                    {Math.round(item.credibility_score)} / 100
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <Link
                    to={`/report/${item.id}`}
                    className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-purple-600/20 hover:bg-purple-600 text-purple-300 hover:text-white border border-purple-500/30 text-xs font-semibold transition-all"
                  >
                    <span>View Dossier</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </Link>

                  <button
                    onClick={() => handleDelete(item.id)}
                    className="p-2 rounded-xl bg-white/5 hover:bg-rose-500/20 text-slate-400 hover:text-rose-400 transition-colors"
                    title="Delete record"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
