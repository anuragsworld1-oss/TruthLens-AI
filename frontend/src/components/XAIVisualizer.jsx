import React, { useState } from 'react';
import { Eye, ShieldAlert, CheckCircle2, Info } from 'lucide-react';

export default function XAIVisualizer({ xaiData = {} }) {
  const [activeTab, setActiveTab] = useState('features'); // 'features' | 'tokens' | 'sentences'

  const {
    top_misleading_features = [],
    top_genuine_features = [],
    token_highlights = [],
    sentence_explanations = []
  } = xaiData;

  const renderTokenHighlight = (tok, idx) => {
    let classes = 'text-slate-300';
    if (tok.category === 'misleading_strong') {
      classes = 'bg-rose-500/30 text-rose-300 border-b border-rose-400 font-semibold px-1 rounded-sm';
    } else if (tok.category === 'misleading_moderate') {
      classes = 'bg-rose-500/15 text-rose-200 px-0.5 rounded-sm';
    } else if (tok.category === 'genuine_strong') {
      classes = 'bg-emerald-500/30 text-emerald-300 border-b border-emerald-400 font-semibold px-1 rounded-sm';
    } else if (tok.category === 'genuine_moderate') {
      classes = 'bg-emerald-500/15 text-emerald-200 px-0.5 rounded-sm';
    }

    return (
      <span key={idx} className={`${classes} inline-block mr-1 my-0.5`} title={`Impact: ${tok.score}`}>
        {tok.token}
      </span>
    );
  };

  return (
    <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-5 pb-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
            <Eye className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Explainable AI (XAI) Attribution</h3>
            <p className="text-xs text-slate-400">Word-level importance and sentence saliency based on model feature weights</p>
          </div>
        </div>

        {/* Tab Controls */}
        <div className="flex items-center gap-1 bg-[#10182A] p-1 rounded-xl border border-white/5">
          <button
            onClick={() => setActiveTab('features')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'features' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Key Terms
          </button>
          <button
            onClick={() => setActiveTab('tokens')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'tokens' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Text Saliency
          </button>
          <button
            onClick={() => setActiveTab('sentences')}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeTab === 'sentences' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-white'
            }`}
          >
            Sentences
          </button>
        </div>
        {xaiData.explanation_disclaimer && (
          <p className="text-[10px] text-slate-500 italic mt-2 leading-relaxed">
            {xaiData.explanation_disclaimer}
          </p>
        )}
      </div>

      {/* Tab 1: Key Terms */}
      {activeTab === 'features' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Misleading Features */}
          <div className="p-4 rounded-xl bg-rose-500/5 border border-rose-500/15">
            <div className="flex items-center gap-2 mb-3 text-rose-400">
              <ShieldAlert className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">Features Increasing Risk</h4>
            </div>
            {top_misleading_features.length > 0 ? (
              <div className="space-y-2">
                {top_misleading_features.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-[#10182A]/80 border border-white/5">
                    <span className="font-semibold text-rose-300 font-mono">"{item.term}"</span>
                    <span className="text-rose-400 font-bold">+{item.score}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No high-risk terms identified.</p>
            )}
          </div>

          {/* Genuine Features */}
          <div className="p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/15">
            <div className="flex items-center gap-2 mb-3 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
              <h4 className="text-xs font-bold uppercase tracking-wider">Features Increasing Credibility</h4>
            </div>
            {top_genuine_features.length > 0 ? (
              <div className="space-y-2">
                {top_genuine_features.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs p-2 rounded-lg bg-[#10182A]/80 border border-white/5">
                    <span className="font-semibold text-emerald-300 font-mono">"{item.term}"</span>
                    <span className="text-emerald-400 font-bold">+{item.score}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400">No strong institutional markers matched.</p>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Text Saliency Highlight Map */}
      {activeTab === 'tokens' && (
        <div className="p-4 rounded-xl bg-[#10182A] border border-white/10 max-h-72 overflow-y-auto leading-relaxed text-sm">
          <div className="flex items-center gap-4 mb-3 text-xs text-slate-400 pb-2 border-b border-white/5">
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-emerald-500/40 border border-emerald-400 inline-block"></span>
              <span>Credible Evidence</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-rose-500/40 border border-rose-400 inline-block"></span>
              <span>Sensational / Misleading</span>
            </div>
          </div>
          <div>{token_highlights.map(renderTokenHighlight)}</div>
        </div>
      )}

      {/* Tab 3: Sentence Breakdown */}
      {activeTab === 'sentences' && (
        <div className="space-y-2.5 max-h-72 overflow-y-auto">
          {sentence_explanations.map((sent) => {
            let badge = 'bg-slate-500/10 text-slate-400 border-slate-500/20';
            if (sent.assessment === 'high_risk') badge = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
            if (sent.assessment === 'moderate_risk') badge = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
            if (sent.assessment.includes('credibility')) badge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';

            return (
              <div key={sent.sentence_index} className="p-3 rounded-xl bg-[#10182A] border border-white/5">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-semibold text-slate-400">Sentence #{sent.sentence_index}</span>
                  <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badge}`}>
                    {sent.assessment.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-xs text-slate-200 leading-relaxed font-sans">{sent.text}</p>
                {sent.reason && (
                  <div className="mt-1.5 p-2 rounded-lg bg-[#0D1424] border border-white/5">
                    <p className="text-[10px] text-slate-400 leading-relaxed">
                      <span className="font-semibold text-slate-300">Why: </span>{sent.reason}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
