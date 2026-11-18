import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { 
  LayoutDashboard, CheckCircle2, AlertTriangle, HelpCircle, 
  TrendingUp, Globe2, Sparkles, ArrowRight, Activity, Flame, RefreshCw
} from 'lucide-react';
import { 
  ResponsiveContainer, PieChart, Pie, Cell, Tooltip as RechartsTooltip, 
  AreaChart, Area, XAxis, YAxis, BarChart, Bar 
} from 'recharts';
import api from '../services/api';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await api.getDashboardStats();
      setStats(res.data);
      setError(null);
    } catch (err) {
      console.error("Failed to load dashboard statistics:", err);
      setError("Unable to load latest statistics. Please ensure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
        <span className="text-sm font-medium text-slate-400">Loading intelligence dashboard...</span>
      </div>
    );
  }

  const s = stats || {};
  const isSample = s.is_sample_data;

  const pieColors = ['#22C55E', '#EF4444', '#F59E0B'];

  return (
    <div className="space-y-8 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-white/10">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">Executive Intelligence Dashboard</h1>
            {isSample && (
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
                Preview Data
              </span>
            )}
          </div>
          <p className="text-xs text-slate-400">
            Real-time telemetry, credibility distributions, trending narratives, and model performance.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchStats}
            className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-[#141F35] hover:bg-[#1A2946] border border-white/10 text-xs font-semibold text-slate-200 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5 text-cyan-400" />
            <span>Refresh</span>
          </button>

          <Link
            to="/studio"
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-bold text-white shadow-lg shadow-purple-600/30 transition-all hover:scale-[1.02]"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Analyze News</span>
          </Link>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Analyzed */}
        <div className="p-5 rounded-2xl bg-[#141F35] border border-white/10 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Analyzed</span>
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <LayoutDashboard className="w-4 h-4" />
            </div>
          </div>
          <span className="text-3xl font-black text-white block mb-1">
            {s.total_articles_analyzed || 0}
          </span>
          <span className="text-[11px] text-slate-400">Across web, text, and documents</span>
        </div>

        {/* Likely Genuine */}
        <div className="p-5 rounded-2xl bg-[#141F35] border border-white/10 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">Likely Genuine</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <span className="text-3xl font-black text-emerald-400 block mb-1">
            {s.likely_genuine_count || 0}
          </span>
          <span className="text-[11px] text-slate-400">
            {s.total_articles_analyzed ? Math.round((s.likely_genuine_count / s.total_articles_analyzed) * 100) : 0}% of all records
          </span>
        </div>

        {/* Potentially Misleading */}
        <div className="p-5 rounded-2xl bg-[#141F35] border border-white/10 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider">Misleading Flags</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <span className="text-3xl font-black text-rose-400 block mb-1">
            {s.potentially_misleading_count || 0}
          </span>
          <span className="text-[11px] text-slate-400">
            {s.total_articles_analyzed ? Math.round((s.potentially_misleading_count / s.total_articles_analyzed) * 100) : 0}% clickbait/hoax rate
          </span>
        </div>

        {/* Needs Verification */}
        <div className="p-5 rounded-2xl bg-[#141F35] border border-white/10 shadow-lg relative overflow-hidden">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Needs Verification</span>
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <HelpCircle className="w-4 h-4" />
            </div>
          </div>
          <span className="text-3xl font-black text-amber-400 block mb-1">
            {s.needs_verification_count || 0}
          </span>
          <span className="text-[11px] text-slate-400">Disagreements & preprints</span>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Credibility Distribution Donut Chart */}
        <div className="p-6 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl flex flex-col justify-between">
          <div className="mb-4">
            <h3 className="text-base font-bold text-white mb-1">Credibility Breakdown</h3>
            <p className="text-xs text-slate-400">Distribution across the three core assessment tiers</p>
          </div>

          <div className="w-full h-56 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={s.credibility_distribution || []}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {(s.credibility_distribution || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={pieColors[index % pieColors.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#10182A', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#F8FAFC', fontSize: '12px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex items-center justify-around pt-3 border-t border-white/5 text-xs text-slate-300">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>Genuine</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span>Misleading</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span>Unverified</span>
          </div>
        </div>

        {/* Verification Trends Area Chart */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-base font-bold text-white mb-1">Analysis Volume & Velocity</h3>
              <p className="text-xs text-slate-400">7-day verification activity across newsrooms</p>
            </div>
            <div className="flex items-center gap-1 text-xs text-cyan-400 font-semibold">
              <TrendingUp className="w-4 h-4" />
              <span>Active Telemetry</span>
            </div>
          </div>

          <div className="w-full h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={s.analysis_trends || []}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8B5CF6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8B5CF6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#10182A', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#F8FAFC', fontSize: '12px' }}
                />
                <Area type="monotone" dataKey="analyses" stroke="#8B5CF6" strokeWidth={2.5} fillOpacity={1} fill="url(#areaGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Language Breakdown & Trending Topics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Language Breakdown */}
        <div className="p-6 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Globe2 className="w-4 h-4 text-purple-400" />
            <h3 className="text-base font-bold text-white">Language Distribution</h3>
          </div>
          <div className="w-full h-48">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={s.language_distribution || []}>
                <XAxis dataKey="language" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} />
                <RechartsTooltip
                  contentStyle={{ backgroundColor: '#10182A', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#F8FAFC', fontSize: '12px' }}
                />
                <Bar dataKey="count" fill="#06B6D4" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Trending Misinformation Narratives */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl">
          <div className="flex items-center gap-2 mb-4">
            <Flame className="w-4 h-4 text-amber-400" />
            <h3 className="text-base font-bold text-white">Trending Narratives & Narrative Clustered Risk</h3>
          </div>

          <div className="space-y-3">
            {(s.trending_topics || []).map((t, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-[#10182A] border border-white/5">
                <div>
                  <span className="text-xs font-bold text-slate-200 block">{t.topic}</span>
                  <span className="text-[11px] text-slate-400">{t.mentions} submissions tracked</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-[11px] px-2 py-0.5 rounded bg-white/5 text-slate-300 font-mono">
                    {t.dominant_sentiment}
                  </span>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${
                    t.risk === 'High' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                  }`}>
                    {t.risk} Risk
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="p-6 rounded-2xl bg-[#141F35] border border-white/10 shadow-xl">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-base font-bold text-white">Recent Analysis Telemetry</h3>
            <p className="text-xs text-slate-400">Latest submitted news articles and automated assessments</p>
          </div>
          <Link to="/history" className="text-xs text-purple-400 hover:text-purple-300 font-semibold flex items-center gap-1">
            <span>View Full History</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 uppercase tracking-wider font-semibold">
                <th className="pb-3">Headline</th>
                <th className="pb-3">Determination</th>
                <th className="pb-3">Credibility Score</th>
                <th className="pb-3 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 text-slate-300">
              {(s.recent_activity || []).map((act) => (
                <tr key={act.id} className="hover:bg-white/5 transition-colors">
                  <td className="py-3.5 pr-4 font-medium text-white max-w-md truncate">
                    {act.title}
                  </td>
                  <td className="py-3.5">
                    <span className={`px-2 py-0.5 rounded-full text-[11px] font-semibold border ${
                      act.predicted_class === 'Likely Genuine'
                        ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                        : act.predicted_class === 'Potentially Misleading'
                        ? 'bg-rose-500/10 text-rose-400 border-rose-500/20'
                        : 'bg-amber-500/10 text-amber-400 border-amber-500/20'
                    }`}>
                      {act.predicted_class}
                    </span>
                  </td>
                  <td className="py-3.5 font-bold font-mono">
                    {Math.round(act.credibility_score)} / 100
                  </td>
                  <td className="py-3.5 text-right">
                    <Link
                      to={`/report/${act.id}`}
                      className="px-2.5 py-1 rounded-lg bg-white/5 hover:bg-purple-600 hover:text-white text-slate-300 transition-all text-xs font-medium"
                    >
                      View Report
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
