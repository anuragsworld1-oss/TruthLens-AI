import React from 'react';
import { CheckCircle2, XCircle, HelpCircle, AlertCircle, ExternalLink, Calendar, Building2 } from 'lucide-react';

export default function ClaimVerificationCards({ claims = [] }) {
  const getStatusBadge = (status) => {
    switch (status) {
      case 'Supported by available evidence':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-xs font-semibold">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Supported by Evidence
          </span>
        );
      case 'Contradicted by available evidence':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 text-xs font-semibold">
            <XCircle className="w-3.5 h-3.5" />
            Contradicted by Evidence
          </span>
        );
      case 'Conflicting evidence':
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 text-xs font-semibold">
            <AlertCircle className="w-3.5 h-3.5" />
            Conflicting Evidence
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-500/10 text-slate-400 border border-slate-500/30 text-xs font-semibold">
            <HelpCircle className="w-3.5 h-3.5" />
            Insufficient Evidence
          </span>
        );
    }
  };

  return (
    <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-white/10">
        <div>
          <h3 className="text-base font-bold text-white">Extracted Factual Claims & Verification</h3>
          <p className="text-xs text-slate-400">Verifiable assertions mapped to certified fact-checkers and primary sources</p>
        </div>
        <span className="text-xs font-bold px-2.5 py-1 rounded bg-purple-500/15 text-purple-300 border border-purple-500/30">
          {claims.length} Claims Identified
        </span>
      </div>

      {claims.length === 0 ? (
        <p className="text-xs text-slate-400 italic">No specific quantitative or entity claims extracted from text.</p>
      ) : (
        <div className="space-y-4">
          {claims.map((claim, idx) => (
            <div key={idx} className="p-4 rounded-xl bg-[#10182A] border border-white/5 space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <span className="text-xs font-bold text-purple-400">Claim #{idx + 1}</span>
                {getStatusBadge(claim.verification_status)}
              </div>

              {/* Claim Body */}
              <p className="text-sm font-semibold text-slate-100 leading-snug">
                "{claim.claim_text}"
              </p>

              {/* Evidence Synthesis */}
              <div className="p-3 rounded-lg bg-[#141F35]/70 border border-white/5 text-xs text-slate-300 leading-relaxed">
                <span className="font-bold text-slate-200 block mb-1">Evidence Summary:</span>
                {claim.evidence_summary}
              </div>

              {/* Sources */}
              {((claim.supporting_sources && claim.supporting_sources.length > 0) ||
                (claim.contradicting_sources && claim.contradicting_sources.length > 0) ||
                (claim.sources && claim.sources.length > 0)) && (
                <div className="pt-2 border-t border-white/5 space-y-2">
                  <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
                    Referenced Sources & Citations
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {(claim.supporting_sources || claim.sources || []).map((src, sIdx) => (
                      <a
                        key={sIdx}
                        href={src.source_url || src.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-start justify-between gap-2 p-2.5 rounded-lg bg-[#080D1B] border border-white/5 hover:border-purple-500/30 hover:bg-[#141F35] transition-all group"
                      >
                        <div className="space-y-1">
                          <span className="text-xs font-medium text-slate-200 group-hover:text-purple-300 block line-clamp-1">
                            {src.source_title || src.title}
                          </span>
                          <div className="flex items-center gap-2 text-[10px] text-slate-400">
                            <span className="flex items-center gap-1">
                              <Building2 className="w-3 h-3 text-slate-500" />
                              {src.publisher}
                            </span>
                            {src.published_at && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3 text-slate-500" />
                                {src.published_at}
                              </span>
                            )}
                          </div>
                        </div>
                        <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-purple-400 flex-shrink-0 mt-0.5" />
                      </a>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
