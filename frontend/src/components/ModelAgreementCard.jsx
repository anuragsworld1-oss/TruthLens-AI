import React from 'react';
import { Cpu, CheckCircle2, AlertTriangle, HelpCircle } from 'lucide-react';

export default function ModelAgreementCard({ modelPredictions = {}, agreementRate = 100 }) {
  const modelsList = Object.entries(modelPredictions);

  const getBadge = (prediction) => {
    if (prediction === 'Likely Genuine') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Likely Genuine
        </span>
      );
    }
    if (prediction === 'Potentially Misleading') {
      return (
        <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20 text-xs font-semibold">
          <AlertTriangle className="w-3.5 h-3.5" />
          Misleading
        </span>
      );
    }
    return (
      <span className="flex items-center gap-1 px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold">
        <HelpCircle className="w-3.5 h-3.5" />
        Needs Verification
      </span>
    );
  };

  return (
    <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-white/10">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Multi-Model Ensemble Consensus</h3>
            <p className="text-xs text-slate-400">Classical ML · BiLSTM{modelPredictions['DistilBERT'] ? ' · DistilBERT' : ''} ensemble · model confidence ≠ factual truth</p>
          </div>
        </div>

        {/* Agreement Meter */}
        <div className="text-right">
          <span className="text-xs text-slate-400 block mb-0.5">Model Agreement</span>
          <span className={`text-base font-black ${agreementRate >= 70 ? 'text-emerald-400' : 'text-amber-400'}`}>
            {agreementRate}%
          </span>
        </div>
      </div>

      <div className="space-y-3.5">
        {modelsList.map(([name, data]) => {
          const probs = data.probabilities || {};
          const genuineProb = probs['Likely Genuine'] || 0;
          const misleadingProb = probs['Potentially Misleading'] || 0;
          const verifyProb = probs['Needs Further Verification'] || 0;

          return (
            <div key={name} className="p-3.5 rounded-xl bg-[#10182A] border border-white/5 hover:border-white/10 transition-colors">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-slate-200">{name}</span>
                {getBadge(data.prediction)}
              </div>

              {/* Probability distribution bar */}
              <div className="w-full h-2 rounded-full bg-[#1E293B] overflow-hidden flex">
                <div
                  className="bg-emerald-500 transition-all duration-700"
                  style={{ width: `${genuineProb}%` }}
                  title={`Likely Genuine: ${genuineProb}%`}
                />
                <div
                  className="bg-rose-500 transition-all duration-700"
                  style={{ width: `${misleadingProb}%` }}
                  title={`Potentially Misleading: ${misleadingProb}%`}
                />
                <div
                  className="bg-amber-500 transition-all duration-700"
                  style={{ width: `${verifyProb}%` }}
                  title={`Needs Verification: ${verifyProb}%`}
                />
              </div>

              <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1.5 font-mono">
                <span>Genuine: {genuineProb}%</span>
                <span>Misleading: {misleadingProb}%</span>
                <span>Verify: {verifyProb}%</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
