import React, { useState } from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { useApp } from '../context/AppContext';

export function WhatIfPage() {
  const { state, showToast } = useApp();
  const recentAnalyses = state?.props?.recent_analyses || [];
  const defaultWeights = state?.props?.default_weights || {};

  const [selectedLogId, setSelectedLogId] = useState('');
  const [weights, setWeights] = useState(() => ({ ...defaultWeights }));
  const [simResult, setSimResult] = useState(null);
  const [running, setRunning] = useState(false);

  const handleSelectChange = (e) => {
    setSelectedLogId(e.target.value);
    setSimResult(null);
  };

  const handleSliderChange = (key, val) => {
    setWeights((prev) => ({ ...prev, [key]: Number(val) }));
  };

  const resetWeights = () => {
    setWeights({ ...defaultWeights });
  };

  const runSimulation = async () => {
    if (!selectedLogId) return;
    setRunning(true);
    try {
      const res = await fetch('/ascend/whatif/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ log_id: selectedLogId, weights }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setSimResult(data);
    } catch (err) {
      showToast(`Simulation failed: ${err.message}`, 'error');
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
            What-if learning sandbox
          </h1>
          <p className="text-[14px] text-[var(--text-secondary)] mt-1">
            Experiment with analyzer weight bounds in memory to inspect score sensitivity
          </p>
        </div>
        <AppLink
          href="/ascend/dashboard"
          className="text-[13px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] inline-flex items-center gap-1.5"
        >
          <Icon.ArrowLeft size={14} strokeWidth={1.5} aria-hidden="true" />
          <span>Back to Ascend</span>
        </AppLink>
      </div>

      {/* Advisory Banner */}
      <div className="p-4 rounded-xl bg-amber-50/70 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 flex items-start gap-3">
        <Icon.GraduationCap size={18} strokeWidth={1.5} className="text-amber-700 dark:text-amber-400 mt-0.5 shrink-0" aria-hidden="true" />
        <div>
          <h2 className="text-[13.5px] font-medium text-amber-900 dark:text-amber-300">Educational simulation</h2>
          <p className="text-[12.5px] text-amber-800 dark:text-amber-300/90 mt-0.5 leading-relaxed">
            No changes are saved — all calculations run in memory and never alter the production detection engine.
          </p>
        </div>
      </div>

      {/* Analysis Selector */}
      <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3">
        <label htmlFor="analysis-select" className="block text-[14px] font-medium text-[var(--text-primary)]">
          Select analysis record
        </label>
        {recentAnalyses.length > 0 ? (
          <select
            id="analysis-select"
            value={selectedLogId}
            onChange={handleSelectChange}
            className="w-full h-10 px-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] text-[13.5px] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
          >
            <option value="">Select a past analysis</option>
            {recentAnalyses.map((a) => (
              <option key={a.id} value={a.id}>
                {(a.subject || 'Unknown').slice(0, 60)} (Score: {Math.round(a.risk_score || 0)}, {a.risk_level})
              </option>
            ))}
          </select>
        ) : (
          <p className="text-[13.5px] text-[var(--text-secondary)]">
            No analyses available.{' '}
            <AppLink href="/inbox" className="text-[var(--accent)] hover:underline">
              Analyze some emails
            </AppLink>{' '}
            first.
          </p>
        )}
      </div>

      {/* Sliders */}
      {selectedLogId && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Adjust rule weights</h2>
            <button
              type="button"
              onClick={resetWeights}
              className="h-8 px-3 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] text-[12.5px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] cursor-pointer"
            >
              Reset to defaults
            </button>
          </div>

          <div className="space-y-4">
            {Object.entries(defaultWeights).map(([key, defVal]) => (
              <div key={key} className="space-y-1.5">
                <div className="flex items-center justify-between text-[13px]">
                  <label htmlFor={`weight-${key}`} className="font-medium text-[var(--text-primary)] capitalize">
                    {key.replace(/_/g, ' ')}
                  </label>
                  <span className="font-mono font-medium tabular-nums text-[var(--accent)]">
                    {weights[key] ?? defVal}
                  </span>
                </div>
                <input
                  id={`weight-${key}`}
                  type="range"
                  min={0}
                  max={50}
                  value={weights[key] ?? defVal}
                  onChange={(e) => handleSliderChange(key, e.target.value)}
                  className="w-full accent-[var(--accent)] cursor-pointer"
                />
              </div>
            ))}
          </div>

          <button
            type="button"
            disabled={running}
            onClick={runSimulation}
            className="w-full h-10 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13.5px] font-medium transition-colors cursor-pointer disabled:opacity-50"
          >
            {running ? 'Simulating...' : 'Run simulation'}
          </button>
        </div>
      )}

      {/* Results */}
      {simResult && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-5">
          <div className="flex items-center justify-between gap-2">
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Simulation results</h2>
            <span className="font-mono text-[11.5px] px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 text-amber-800 dark:text-amber-300">
              Educational only
            </span>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] text-center">
              <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {Math.round(simResult.original_score || 0)}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">Original score</div>
            </div>
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--accent)]/40 text-center">
              <div className="text-2xl font-medium font-mono tabular-nums text-[var(--accent)]">
                {Math.round(simResult.simulated_score || 0)}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">Simulated score</div>
            </div>
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] text-center">
              <div
                className={`text-2xl font-medium font-mono tabular-nums ${
                  simResult.delta > 0
                    ? 'text-red-600 dark:text-red-400'
                    : simResult.delta < 0
                    ? 'text-emerald-600 dark:text-emerald-400'
                    : 'text-[var(--text-muted)]'
                }`}
              >
                {(simResult.delta >= 0 ? '+' : '') + Number(simResult.delta || 0).toFixed(1)}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">Difference</div>
            </div>
          </div>

          <p className="text-[13.5px] text-[var(--text-secondary)] leading-relaxed">{simResult.explanation}</p>

          <div className="space-y-2">
            {Object.entries(simResult.analyzer_breakdown || {}).map(([cat, bd]) => {
              const diff = bd.simulated_contribution - bd.original_contribution;
              return (
                <div
                  key={cat}
                  className="px-4 py-2.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex items-center justify-between text-[13px]"
                >
                  <span className="font-medium text-[var(--text-primary)] capitalize">
                    {cat.replace(/_/g, ' ')}
                  </span>
                  <div className="flex items-center gap-4 font-mono tabular-nums text-[12.5px]">
                    <span className="text-[var(--text-secondary)]">
                      {Number(bd.original_contribution).toFixed(1)} → {Number(bd.simulated_contribution).toFixed(1)}
                    </span>
                    <span
                      className={`font-medium w-14 text-right ${
                        diff > 0
                          ? 'text-red-600 dark:text-red-400'
                          : diff < 0
                          ? 'text-emerald-600 dark:text-emerald-400'
                          : 'text-[var(--text-muted)]'
                      }`}
                    >
                      {(diff >= 0 ? '+' : '') + diff.toFixed(1)}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

