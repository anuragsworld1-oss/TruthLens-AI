import React from 'react';

export default function CircularGauge({ score = 50, prediction = 'Needs Further Verification', size = 200 }) {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  let color = '#F59E0B'; // Yellow warning
  let badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
  let categoryLabel = 'Needs Further Verification';

  if (score >= 70) {
    color = '#22C55E'; // Green
    badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    categoryLabel = 'Likely Genuine';
  } else if (score >= 40) {
    color = '#F59E0B'; // Orange
    badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    categoryLabel = 'Potentially Misleading';
  } else {
    color = '#EF4444'; // Red
    badgeBg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    categoryLabel = 'Needs Further Verification';
  }

  // Override category if specified by backend
  if (prediction) {
    categoryLabel = prediction;
    if (prediction === 'Likely Genuine') {
      color = '#22C55E';
      badgeBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    } else if (prediction === 'Potentially Misleading') {
      color = '#EF4444';
      badgeBg = 'bg-rose-500/10 text-rose-400 border-rose-500/30';
    } else {
      color = '#F59E0B';
      badgeBg = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    }
  }

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-[#141F35] rounded-2xl border border-white/10 shadow-xl">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          {/* Background Track */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#1E293B"
            strokeWidth={strokeWidth}
            fill="transparent"
          />
          {/* Active Colored Arc */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            fill="transparent"
            style={{
              transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)',
            }}
          />
        </svg>

        {/* Center Score Display */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
          <span className="text-4xl font-extrabold tracking-tight text-white">
            {Math.round(score)}
          </span>
          <span className="text-xs font-medium uppercase tracking-wider text-slate-400 mt-1">
            Index / 100
          </span>
        </div>
      </div>

      {/* Main Prediction Badge */}
      <div className={`mt-4 px-4 py-1.5 rounded-full border text-sm font-semibold tracking-wide ${badgeBg}`}>
        {categoryLabel}
      </div>

      <p className="text-xs text-slate-400 text-center max-w-[240px] mt-3 leading-relaxed">
        Model-derived credibility metric synthesizing linguistic patterns, calibrated classifiers, and evidence checks.
      </p>
    </div>
  );
}
