import React from 'react';
import { ShieldQuestion, ShieldAlert, ShieldCheck } from 'lucide-react';

/**
 * UncertaintyBadge - displays the model+evidence uncertainty level
 * (Low / Medium / High) with the explicit note that model confidence
 * is NOT a measure of factual truth.
 */
export default function UncertaintyBadge({ level = 'Low' }) {
  const config = {
    Low: {
      icon: ShieldCheck,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
      border: 'border-emerald-500/20',
      label: 'Low Uncertainty',
    },
    Medium: {
      icon: ShieldAlert,
      color: 'text-amber-400',
      bg: 'bg-amber-500/10',
      border: 'border-amber-500/20',
      label: 'Medium Uncertainty',
    },
    High: {
      icon: ShieldQuestion,
      color: 'text-rose-400',
      bg: 'bg-rose-500/10',
      border: 'border-rose-500/20',
      label: 'High Uncertainty',
    },
  };

  const c = config[level] || config.Low;
  const Icon = c.icon;

  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-xl ${c.bg} ${c.border} border`}>
      <Icon className={`w-4 h-4 ${c.color}`} />
      <span className={`text-xs font-bold ${c.color}`}>{c.label}</span>
    </div>
  );
}
