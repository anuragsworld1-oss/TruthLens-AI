import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { 
  ShieldCheck, Printer, ArrowLeft, Building2, UserCheck, 
  Calendar, Globe2, Sparkles, CheckSquare, MessageSquare, AlertCircle
} from 'lucide-react';
import api from '../services/api';
import CircularGauge from '../components/CircularGauge';
import ModelAgreementCard from '../components/ModelAgreementCard';
import LinguisticSignals from '../components/LinguisticSignals';
import XAIVisualizer from '../components/XAIVisualizer';
import ClaimVerificationCards from '../components/ClaimVerificationCards';
import AIStyleBadge from '../components/AIStyleBadge';
import UncertaintyBadge from '../components/UncertaintyBadge';
import ClaimEvidencePanel from '../components/ClaimEvidencePanel';

export default function ReportDetailPage() {
  const { id } = useParams();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Review states
  const [reviewStatus, setReviewStatus] = useState('Verified');
  const [reviewNotes, setReviewNotes] = useState('');
  const [reviewSubmitted, setReviewSubmitted] = useState(false);

  useEffect(() => {
    const fetchReport = async () => {
      setLoading(true);
      try {
        // Try to fetch from sessionStorage first for instant render
        const cached = sessionStorage.getItem(`truthlens_report_${id}`);
        if (cached) {
          setReport(JSON.parse(cached));
          setLoading(false);
          return;
        }

        const res = await api.getAnalysisDetail(id);
        setReport(res.data);
      } catch (err) {
        console.error('Failed to load analysis report:', err);
        setError('Analysis dossier could not be retrieved from the database.');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.submitReview({
        analysis_id: id,
        status: reviewStatus,
        notes: reviewNotes
      });
      setReviewSubmitted(true);
    } catch (err) {
      console.error('Review submit failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <div className="w-10 h-10 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
        <span className="text-sm font-medium text-slate-400">Assembling verification report...</span>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto p-8 rounded-2xl bg-[#141F35] border border-white/10 text-center space-y-4">
        <AlertCircle className="w-12 h-12 text-rose-400 mx-auto" />
        <h2 className="text-xl font-bold text-white">Report Not Found</h2>
        <p className="text-xs text-slate-400">{error || 'The requested analysis record does not exist.'}</p>
        <Link to="/studio" className="inline-block px-4 py-2 rounded-xl bg-purple-600 text-white text-xs font-semibold">
          Perform New Analysis
        </Link>
      </div>
    );
  }

  const articleTitle = report.article_title || 'Analyzed News Article';
  const articleContent = report.article_content || '';
  const score = report.credibility_score || 50;
  const prediction = report.predicted_class || 'Needs Further Verification';
  const pubIntel = report.publisher_intelligence || {};

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20 print:p-0 print:space-y-4">
      {/* Action Navigation Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10 print:hidden">
        <Link
          to="/history"
          className="flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to History</span>
        </Link>

        <div className="flex items-center gap-3">
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#141F35] hover:bg-[#1A2946] border border-white/10 text-xs font-semibold text-slate-200 transition-colors shadow-md"
          >
            <Printer className="w-4 h-4 text-cyan-400" />
            <span>Export / Print PDF</span>
          </button>

          <Link
            to="/studio"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs font-bold text-white shadow-lg shadow-purple-600/30 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>

      {/* Main Dossier Header Card */}
      <div className="p-6 sm:p-8 rounded-2xl bg-[#141F35] border border-white/10 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-8">
          <div className="space-y-3 max-w-3xl">
            <div className="flex flex-wrap items-center gap-2 text-xs">
              <span className="px-2.5 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30 font-semibold font-mono">
                DOSSIER #{report.id || id}
              </span>
              <span className="text-slate-400 flex items-center gap-1 font-mono">
                <Calendar className="w-3.5 h-3.5" />
                {report.created_at ? report.created_at.slice(0, 10) : 'Recent'}
              </span>
              <span className="text-slate-400 flex items-center gap-1 font-mono">
                <Globe2 className="w-3.5 h-3.5" />
                Lang: {(report.language || 'en').toUpperCase()}
              </span>
            </div>

            <h1 className="text-xl sm:text-2xl lg:text-3xl font-extrabold text-white tracking-tight leading-snug">
              {articleTitle}
            </h1>

            {report.source_url && (
              <p className="text-xs text-cyan-400 font-mono truncate max-w-xl">
                Source: {report.source_url}
              </p>
            )}

            {/* Publisher Intelligence Snippet */}
            {pubIntel.name && (
              <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#10182A] border border-white/5 text-xs text-slate-300">
                <Building2 className="w-3.5 h-3.5 text-purple-400" />
                <span>Publisher: <strong>{pubIntel.name}</strong> ({pubIntel.type || 'Wire/Media'})</span>
                <span className="text-slate-500">|</span>
                <span className="text-cyan-400 font-medium">{pubIntel.rating}</span>
              </div>
            )}
          </div>

          {/* Circular Gauge Component */}
          <div className="flex-shrink-0 mx-auto lg:mx-0">
            <CircularGauge
              score={score}
              prediction={prediction}
              size={180}
            />
          </div>
        </div>
      </div>

      {/* TruthLens 2.0 Assessment Banner: outcome + uncertainty */}
      {(report.outcome || report.uncertainty_level) && (
        <div className="p-4 rounded-2xl bg-[#141F35] border border-white/10 shadow-lg flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            {report.outcome === 'Likely Reliable' && <ShieldCheck className="w-6 h-6 text-emerald-400" />}
            {report.outcome === 'Potentially Misleading' && <AlertCircle className="w-6 h-6 text-rose-400" />}
            {report.outcome === 'Unverified' && <AlertCircle className="w-6 h-6 text-amber-400" />}
            <div>
              <h3 className="text-sm font-bold text-white">
                Overall Assessment: <span className={
                  report.outcome === 'Likely Reliable' ? 'text-emerald-400' :
                  report.outcome === 'Potentially Misleading' ? 'text-rose-400' : 'text-amber-400'
                }>{report.outcome || prediction}</span>
              </h3>
              <p className="text-[11px] text-slate-400">Model confidence is a probabilistic signal, not a measure of factual truth.</p>
            </div>
          </div>
          {report.uncertainty_level && <UncertaintyBadge level={report.uncertainty_level} />}
        </div>
      )}

      {/* Credibility Reasoning (TruthLens 2.0) */}
      {report.credibility_reasoning && report.credibility_reasoning.length > 0 && (
        <div className="p-5 rounded-2xl bg-[#141F35] border border-white/10 shadow-lg">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-purple-400" />
            Assessment Reasoning
          </h3>
          <ul className="space-y-1.5">
            {report.credibility_reasoning.map((reason, i) => (
              <li key={i} className="text-xs text-slate-300 flex items-start gap-2">
                <span className="text-purple-400 mt-0.5">•</span>
                <span>{reason}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Grid: Multi-Model Ensemble & Linguistic Warning Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ModelAgreementCard
          modelPredictions={report.model_predictions || {}}
          agreementRate={report.model_agreement_percentage || 80}
        />

        <LinguisticSignals
          linguisticData={report.linguistic_analysis || {}}
        />
      </div>

      {/* Explainable AI Visualizer (SHAP/LIME Feature Attribution) */}
      <XAIVisualizer
        xaiData={report.explainable_ai || report.explanation || {}}
      />

      {/* Claim Extraction & Evidence-Based Verification (legacy cards) */}
      <ClaimVerificationCards
        claims={report.claims || report.extracted_claims || []}
      />

      {/* TruthLens 2.0: Structured Claim Evidence Panel with entities + RAG */}
      <ClaimEvidencePanel
        claims={report.claims || report.extracted_claims || []}
      />

      {/* Grid: AI Writing Style & Recommended Next Steps */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AIStyleBadge
          aiStyleData={report.ai_writing_style || {}}
        />

        {/* Recommended Actions Card */}
        <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-white/10">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                <UserCheck className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-bold text-white">Recommended Fact-Checking Steps</h3>
                <p className="text-xs text-slate-400">Actionable guidance for editors and readers</p>
              </div>
            </div>

            <div className="space-y-2.5">
              {(report.recommended_actions || [
                "Verify statistical claims with original regulatory briefings.",
                "Seek independent confirmation from accredited international wires.",
                "Inspect referenced citations and publication timestamps."
              ]).map((act, idx) => (
                <div key={idx} className="flex items-start gap-2.5 text-xs text-slate-200">
                  <span className="w-5 h-5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">
                    {idx + 1}
                  </span>
                  <span className="mt-0.5">{act}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-3 border-t border-white/5 text-[11px] text-slate-400">
            {report.limitations_disclaimer || "TruthLens AI produces probabilistic assessments. It does not replace independent journalistic investigation."}
          </div>
        </div>
      </div>

      {/* Human Review & Editorial Workflow */}
      <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl print:hidden">
        <div className="flex items-center gap-2.5 mb-4 pb-3 border-b border-white/10">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <CheckSquare className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Human Verification Workflow</h3>
            <p className="text-xs text-slate-400">Human-in-the-loop review mechanism to record verified editorial determinations</p>
          </div>
        </div>

        {reviewSubmitted ? (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 flex-shrink-0" />
            <span>Review decision has been permanently recorded in the audit trail.</span>
          </div>
        ) : (
          <form onSubmit={handleReviewSubmit} className="space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="text-xs text-slate-400 block mb-1">Editorial Determination</label>
                <select
                  value={reviewStatus}
                  onChange={(e) => setReviewStatus(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#10182A] border border-white/10 text-xs text-white focus:outline-none focus:border-purple-500"
                >
                  <option value="Verified Authentic">Verified Authentic</option>
                  <option value="Confirmed Misleading">Confirmed Misleading</option>
                  <option value="Inconclusive Evidence">Inconclusive Evidence</option>
                  <option value="Editorial Correction Needed">Editorial Correction Needed</option>
                </select>
              </div>

              <div className="sm:col-span-2">
                <label className="text-xs text-slate-400 block mb-1">Reviewer Audit Notes</label>
                <input
                  type="text"
                  placeholder="e.g. Cross-checked with official PIB statement and corroborated with press briefing..."
                  value={reviewNotes}
                  onChange={(e) => setReviewNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-[#10182A] border border-white/10 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-purple-500 font-sans"
                />
              </div>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold transition-all shadow-md"
              >
                Record Editorial Review
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
