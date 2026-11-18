import React from 'react';
import { Bot, AlertTriangle, HelpCircle } from 'lucide-react';

export default function AIStyleBadge({ aiStyleData = {} }) {
  const {
    ai_style_score = 0,
    style_classification = 'Standard Human Writing Patterns',
    sentence_length_uniformity_cv = 0,
    lexical_diversity_ttr = 0,
    formulaic_phrases_detected = [],
    experimental_disclaimer = ''
  } = aiStyleData;

  let badgeColor = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
  if (ai_style_score >= 65) {
    badgeColor = 'text-amber-400 bg-amber-500/10 border-amber-500/20';
  } else if (ai_style_score >= 40) {
    badgeColor = 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20';
  }

  return (
    <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Bot className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-base font-bold text-white">AI-Generated Writing Style Assessment</h3>
              <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                Experimental
              </span>
            </div>
            <p className="text-xs text-slate-400">Statistical stylometry analyzing structural burstiness and formulaic prose</p>
          </div>
        </div>

        <div className="text-right">
          <span className="text-xs text-slate-400 block mb-0.5">Style Index</span>
          <span className="text-base font-black text-purple-400">
            {ai_style_score} / 100
          </span>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-[#10182A] border border-white/5 mb-4">
        <div>
          <span className="text-xs text-slate-400 block mb-1">Stylistic Characterization</span>
          <span className={`inline-block px-2.5 py-1 rounded-full text-xs font-semibold border ${badgeColor}`}>
            {style_classification}
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs text-slate-300 font-mono">
          <div>
            <span className="text-slate-400 block text-[10px]">Burstiness CV</span>
            {sentence_length_uniformity_cv}
          </div>
          <div>
            <span className="text-slate-400 block text-[10px]">Lexical TTR</span>
            {lexical_diversity_ttr}
          </div>
        </div>
      </div>

      {formulaic_phrases_detected.length > 0 && (
        <div className="mb-3 text-xs text-slate-300">
          <span className="text-slate-400 font-medium block mb-1">Formulaic Transition Phrases Detected:</span>
          <div className="flex flex-wrap gap-1.5">
            {formulaic_phrases_detected.map((p, idx) => (
              <span key={idx} className="px-2 py-0.5 rounded bg-white/5 border border-white/10 text-slate-300 font-mono text-[11px]">
                "{p}"
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Strict Ethical Disclaimer */}
      <div className="p-3 rounded-xl bg-purple-950/30 border border-purple-500/20 flex items-start gap-2.5 text-xs text-purple-300/90 leading-relaxed">
        <HelpCircle className="w-4 h-4 text-purple-400 flex-shrink-0 mt-0.5" />
        <p>
          <strong>Ethical Mandate:</strong> {experimental_disclaimer || "AI authorship cannot be reliably established from text alone. AI-assisted writing tools are standard in professional journalism and are NEVER automatically equated with misinformation."}
        </p>
      </div>
    </div>
  );
}
