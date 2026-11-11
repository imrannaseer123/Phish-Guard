import React from 'react';

export function riskStyle(level) {
  switch (level) {
    case 'High':
      return {
        badge:
          'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20',
        text: 'text-red-600 dark:text-red-400',
        dot: 'bg-red-600 dark:bg-red-400',
        bar: 'bg-red-600 dark:bg-red-500',
      };
    case 'Medium':
      return {
        badge:
          'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20',
        text: 'text-amber-600 dark:text-amber-400',
        dot: 'bg-amber-500 dark:bg-amber-400',
        bar: 'bg-amber-500 dark:bg-amber-400',
      };
    case 'Low':
    default:
      return {
        badge:
          'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20',
        text: 'text-emerald-600 dark:text-emerald-400',
        dot: 'bg-emerald-600 dark:bg-emerald-400',
        bar: 'bg-emerald-600 dark:bg-emerald-500',
      };
  }
}

export function RiskBadge({ level, label }) {
  const st = riskStyle(level);
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-md text-xs font-medium border ${st.badge}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${st.dot}`} aria-hidden="true" />
      {label || level}
    </span>
  );
}

export function ScoreChip({ score, level }) {
  const st = riskStyle(level);
  return (
    <span
      className={`inline-flex items-center justify-center min-w-[2.5rem] px-2 py-0.5 rounded-md font-mono text-xs font-medium tabular-nums border ${st.badge}`}
    >
      {Math.round(score || 0)}
    </span>
  );
}

