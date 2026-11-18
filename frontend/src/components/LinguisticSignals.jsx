import React from 'react';
import { AlertCircle, Flame, Type, MessageSquareWarning, Sparkles, CheckCircle } from 'lucide-react';

export default function LinguisticSignals({ linguisticData = {} }) {
  const {
    linguistic_risk_score = 0,
    word_count = 0,
    capitalization_ratio = 0,
    exclamation_count = 0,
    sensational_punctuation_count = 0,
    lexical_diversity_ttr = 0,
    detected_clickbait_terms = [],
    detected_urgency_terms = [],
    detected_credibility_markers = [],
    warning_signals = []
  } = linguisticData;

  return (
    <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Flame className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Linguistic & Behavioral Signal Analysis</h3>
            <p className="text-xs text-slate-400">Stylistic patterns, sensationalism flags, and structural indicators</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs text-slate-400 block mb-0.5">Linguistic Risk</span>
          <span className={`text-base font-black ${linguistic_risk_score > 40 ? 'text-rose-400' : 'text-emerald-400'}`}>
            {linguistic_risk_score} / 100
          </span>
        </div>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
        <div className="p-3 rounded-xl bg-[#10182A] border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Caps Ratio</span>
          <span className="text-base font-bold text-white font-mono">
            {(capitalization_ratio * 100).toFixed(1)}%
          </span>
        </div>
        <div className="p-3 rounded-xl bg-[#10182A] border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Sensational Punct.</span>
          <span className="text-base font-bold text-white font-mono">
            {exclamation_count} marks ({sensational_punctuation_count} clusters)
          </span>
        </div>
        <div className="p-3 rounded-xl bg-[#10182A] border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Lexical Diversity (TTR)</span>
          <span className="text-base font-bold text-white font-mono">
            {lexical_diversity_ttr}
          </span>
        </div>
        <div className="p-3 rounded-xl bg-[#10182A] border border-white/5">
          <span className="text-[11px] text-slate-400 block mb-1">Total Words</span>
          <span className="text-base font-bold text-white font-mono">
            {word_count}
          </span>
        </div>
      </div>

      {/* Warning Signals List */}
      <div className="space-y-3">
        {warning_signals.length > 0 ? (
          warning_signals.map((sig, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-start gap-3">
              <AlertCircle className="w-4 h-4 text-rose-400 mt-0.5 flex-shrink-0" />
              <div>
                <span className="text-xs font-bold text-rose-300 block">{sig.label}</span>
                <p className="text-xs text-rose-200/80 mt-0.5">{sig.description}</p>
              </div>
            </div>
          ))
        ) : (
          <div className="p-3.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center gap-2.5">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="text-xs font-medium text-emerald-300">
              No elevated clickbait, excessive capitalization, or artificial panic patterns detected.
            </span>
          </div>
        )}

        {/* Positive Credibility Markers */}
        {detected_credibility_markers.length > 0 && (
          <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-start gap-3">
            <Sparkles className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
            <div>
              <span className="text-xs font-bold text-purple-300 block">Formal Attributions Identified</span>
              <p className="text-xs text-purple-200/80 mt-0.5">
                Article cites institutional sources: {detected_credibility_markers.join(', ')}.
              </p>
            </div>
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-white/5 text-[11px] text-slate-400 italic">
        * Note: Linguistic features indicate rhetorical style and psychological urgency triggers; they are warning heuristics, not mathematical proof of misinformation.
      </div>
    </div>
  );
}
