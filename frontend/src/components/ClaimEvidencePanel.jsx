import React from 'react';
import {
  Search, CheckCircle2, XCircle, HelpCircle, ExternalLink,
  Tag, Calendar, Building2, MapPin, Hash, Users
} from 'lucide-react';

/**
 * ClaimEvidencePanel - TruthLens 2.0
 * Displays claim-by-claim verification with structured entities, retrieved
 * evidence, source links, and retrieval confidence scores. Shows
 * "Insufficient Evidence" empty state when no match is found (never auto-fake).
 */
export default function ClaimEvidencePanel({ claims = [] }) {
  if (!claims || claims.length === 0) {
    return (
      <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
        <div className="flex items-center gap-2.5 mb-4">
          <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Search className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">Claim-by-Claim Evidence Verification</h3>
            <p className="text-xs text-slate-400">No verifiable claims extracted from this article.</p>
          </div>
        </div>
      </div>
    );
  }

  const getStatusConfig = (status) => {
    if (!status) return { icon: HelpCircle, color: 'text-slate-400', bg: 'bg-slate-500/10', border: 'border-slate-500/20', label: 'Unknown' };
    if (status.startsWith('Supported')) return { icon: CheckCircle2, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/20', label: 'Supported' };
    if (status.startsWith('Contradicted')) return { icon: XCircle, color: 'text-rose-400', bg: 'bg-rose-500/10', border: 'border-rose-500/20', label: 'Contradicted' };
    return { icon: HelpCircle, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/20', label: 'Insufficient Evidence' };
  };

  const EntityChip = ({ icon: Icon, label, values }) => {
    if (!values || values.length === 0) return null;
    return (
      <div className="flex items-center gap-1.5 flex-wrap">
        <Icon className="w-3 h-3 text-slate-500" />
        <span className="text-[10px] text-slate-500 font-semibold uppercase">{label}:</span>
        {values.map((v, i) => (
          <span key={i} className="text-[10px] px-1.5 py-0.5 rounded bg-[#1A2946] text-slate-300 border border-white/5 font-mono">
            {v}
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="bg-[#141F35] rounded-2xl border border-white/10 p-6 shadow-xl">
      <div className="flex items-center gap-2.5 mb-5 pb-4 border-b border-white/10">
        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          <Search className="w-5 h-5" />
        </div>
        <div>
          <h3 className="text-base font-bold text-white">Claim-by-Claim Evidence Verification</h3>
          <p className="text-xs text-slate-400">Structured claim extraction with entity recognition and evidence matching</p>
        </div>
      </div>

      <div className="space-y-4">
        {claims.map((claim) => {
          const sc = getStatusConfig(claim.verification_status);
          const StatusIcon = sc.icon;
          const entities = claim.entities || {};
          const retrievalScores = claim.retrieval_scores || [];

          return (
            <div key={claim.id} className="p-4 rounded-xl bg-[#10182A] border border-white/5">
              {/* Claim header */}
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-mono text-slate-500">{claim.id}</span>
                  {claim.claim_type && (
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                      claim.claim_type === 'opinion'
                        ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
                        : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                    }`}>
                      {claim.claim_type}
                    </span>
                  )}
                </div>
                <span className={`flex items-center gap-1 text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${sc.bg} ${sc.border} ${sc.color} flex-shrink-0`}>
                  <StatusIcon className="w-3 h-3" />
                  {sc.label}
                </span>
              </div>

              {/* Claim text */}
              <p className="text-xs text-slate-200 leading-relaxed mb-2">{claim.claim_text}</p>

              {/* Entities */}
              {claim.has_entities && (
                <div className="flex flex-wrap gap-x-3 gap-y-1 mb-2 pb-2 border-b border-white/5">
                  <EntityChip icon={Calendar} label="Dates" values={entities.dates} />
                  <EntityChip icon={Building2} label="Orgs" values={entities.organizations} />
                  <EntityChip icon={Users} label="People" values={entities.people} />
                  <EntityChip icon={MapPin} label="Locations" values={entities.locations} />
                  <EntityChip icon={Hash} label="Numbers" values={entities.numbers} />
                </div>
              )}

              {/* Evidence summary */}
              {claim.evidence_summary && (
                <p className="text-[11px] text-slate-400 leading-relaxed mb-2">{claim.evidence_summary}</p>
              )}

              {/* Sources */}
              {(claim.supporting_sources?.length > 0 || claim.contradicting_sources?.length > 0) && (
                <div className="space-y-1.5">
                  {claim.supporting_sources?.map((src, i) => (
                    <a key={`s${i}`} href={src.url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-[11px] text-emerald-400 hover:text-emerald-300 transition-colors">
                      <CheckCircle2 className="w-3 h-3 flex-shrink-0" />
                      <span className="truncate">{src.title || src.publisher}</span>
                      <ExternalLink className="w-3 h-3 flex-shrink-0 opacity-50" />
                    </a>
                  ))}
                  {claim.contradicting_sources?.map((src, i) => (
                    <a key={`c${i}`} href={src.url} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-1.5 text-[11px] text-rose-400 hover:text-rose-300 transition-colors">
                      <XCircle className="w-3 h-3 flex-shrink-0" />
                      <span className="truncate">{src.title || src.publisher}</span>
                      <ExternalLink className="w-3 h-3 flex-shrink-0 opacity-50" />
                    </a>
                  ))}
                </div>
              )}

              {/* Retrieval confidence */}
              {retrievalScores.length > 0 && (
                <div className="flex items-center gap-1.5 mt-2 pt-2 border-t border-white/5">
                  <Tag className="w-3 h-3 text-slate-500" />
                  <span className="text-[10px] text-slate-500">
                    Retrieval confidence: {retrievalScores.map(s => (s * 100).toFixed(0) + '%').join(', ')}
                  </span>
                </div>
              )}

              {/* Insufficient evidence notice */}
              {claim.verification_status === 'Insufficient evidence' && (
                <div className="mt-2 p-2 rounded-lg bg-amber-500/5 border border-amber-500/15">
                  <p className="text-[10px] text-amber-300/80">
                    No verified evidence was found to confirm or refute this claim. This does NOT mean the claim is false — manual fact-checking is recommended.
                  </p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
