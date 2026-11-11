import React, { useState } from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { useApp } from '../context/AppContext';

export function TrainingPage() {
  const { state, submitForm } = useApp();
  const props = state?.props || {};
  const scenarios = props.scenarios || [];
  const stats = props.stats;
  const scenario = props.scenario;
  const result = props.result;

  const [submitting, setSubmitting] = useState(false);

  const handleGuess = async (guessValue) => {
    if (!scenario || submitting) return;
    setSubmitting(true);
    const fd = new FormData();
    fd.append('guess', guessValue);
    await submitForm(`/training/${scenario.id}`, fd);
    setSubmitting(false);
  };

  const diffBadgeClass = (diff) => {
    if (diff === 'Easy') {
      return 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20';
    }
    if (diff === 'Medium') {
      return 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-400 dark:border-amber-500/20';
    }
    return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20';
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
          Security training simulation
        </h1>
        <p className="text-[14px] text-[var(--text-secondary)] mt-1">
          Practice identifying phishing indicators in an offline environment without sending or receiving live emails
        </p>
      </div>

      {/* Evaluation Result */}
      {result && (
        <div
          className={`p-6 rounded-xl border space-y-5 ${
            result.correct
              ? 'bg-emerald-50/70 border-emerald-200 dark:bg-emerald-500/10 dark:border-emerald-500/20'
              : 'bg-red-50/70 border-red-200 dark:bg-red-500/10 dark:border-red-500/20'
          }`}
        >
          <div className="flex items-start gap-3">
            {result.correct ? (
              <Icon.CheckCircle2 size={22} strokeWidth={1.5} className="text-emerald-600 dark:text-emerald-400 mt-0.5 shrink-0" aria-hidden="true" />
            ) : (
              <Icon.XCircle size={22} strokeWidth={1.5} className="text-red-600 dark:text-red-400 mt-0.5 shrink-0" aria-hidden="true" />
            )}
            <div>
              <h2
                className={`text-xl font-medium ${
                  result.correct ? 'text-emerald-900 dark:text-emerald-200' : 'text-red-900 dark:text-red-200'
                }`}
              >
                {result.feedback}
              </h2>
              <div className="flex flex-wrap gap-3 mt-2 text-[12.5px] font-mono text-[var(--text-secondary)]">
                <span>Scenario: {result.scenario_title}</span>
                <span>Category: {result.category}</span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.red_flags && result.red_flags.length > 0 && (
              <div className="p-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-2">
                <h3 className="text-[14px] font-medium text-[var(--text-primary)]">Red flags</h3>
                <ul className="space-y-1.5 text-[13px] text-[var(--text-secondary)]">
                  {result.red_flags.map((flag, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-[var(--text-muted)]">-</span>
                      <span>{flag}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {result.learning_points && result.learning_points.length > 0 && (
              <div className="p-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-2">
                <h3 className="text-[14px] font-medium text-[var(--text-primary)]">Key takeaways</h3>
                <ul className="space-y-1.5 text-[13px] text-[var(--text-secondary)]">
                  {result.learning_points.map((pt, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <Icon.Check size={14} strokeWidth={1.5} className="text-[var(--accent)] mt-0.5 shrink-0" aria-hidden="true" />
                      <span>{pt}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div>
            <AppLink
              href="/training"
              className="h-9 px-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] hover:bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5 transition-colors"
            >
              <Icon.ArrowLeft size={14} strokeWidth={1.5} aria-hidden="true" />
              <span>Back to scenarios</span>
            </AppLink>
          </div>
        </div>
      )}

      {/* Active Scenario Viewer */}
      {scenario && !result && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-[11.5px] font-medium border ${diffBadgeClass(scenario.difficulty)}`}>
                  {scenario.difficulty}
                </span>
                <span className="px-2 py-0.5 rounded bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[11.5px] font-mono text-[var(--text-secondary)]">
                  {scenario.category}
                </span>
              </div>
              <h2 className="text-xl font-medium text-[var(--text-primary)]">{scenario.title}</h2>
            </div>

            <AppLink
              href="/training"
              className="text-[13px] text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            >
              Cancel
            </AppLink>
          </div>

          {/* Email Viewer */}
          <div className="rounded-lg border border-[var(--border-hairline)] overflow-hidden bg-[var(--bg-app)]">
            <div className="px-4 py-3 border-b border-[var(--border-hairline)] bg-[var(--bg-raised)] space-y-1.5 text-[13px]">
              <div className="flex items-baseline gap-3">
                <span className="w-16 text-[var(--text-muted)] shrink-0">From</span>
                <span className="font-mono text-[12.5px] text-[var(--text-primary)] break-all">
                  {scenario.sender}
                </span>
              </div>
              <div className="flex items-baseline gap-3">
                <span className="w-16 text-[var(--text-muted)] shrink-0">Subject</span>
                <span className="font-medium text-[var(--text-primary)]">{scenario.subject}</span>
              </div>
            </div>
            <div className="p-5 sm:p-6 text-[14px] leading-relaxed text-[var(--text-primary)] whitespace-pre-wrap">
              {scenario.body_text}
            </div>
          </div>

          {/* Guess Selection */}
          <div className="p-5 rounded-xl bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-4">
            <h3 className="text-[14px] font-medium text-[var(--text-primary)] text-center">
              What risk level would you assign to this message?
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-2xl mx-auto">
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleGuess('Low')}
                className="p-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] hover:border-emerald-500 text-center space-y-1 transition-colors cursor-pointer disabled:opacity-50"
              >
                <div className="text-[14px] font-medium text-emerald-700 dark:text-emerald-400">Low risk</div>
                <div className="text-[12px] text-[var(--text-muted)]">Safe / legitimate</div>
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleGuess('Medium')}
                className="p-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] hover:border-amber-500 text-center space-y-1 transition-colors cursor-pointer disabled:opacity-50"
              >
                <div className="text-[14px] font-medium text-amber-700 dark:text-amber-400">Medium risk</div>
                <div className="text-[12px] text-[var(--text-muted)]">Suspicious cues</div>
              </button>
              <button
                type="button"
                disabled={submitting}
                onClick={() => handleGuess('High')}
                className="p-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] hover:border-red-500 text-center space-y-1 transition-colors cursor-pointer disabled:opacity-50"
              >
                <div className="text-[14px] font-medium text-red-700 dark:text-red-400">High risk</div>
                <div className="text-[12px] text-[var(--text-muted)]">Clear phishing attack</div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Scenario Catalog */}
      {!scenario && !result && (
        <>
          {stats && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
                <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                  {stats.total_scenarios}
                </div>
                <div className="text-[12px] text-[var(--text-muted)] mt-1">Total scenarios</div>
              </div>
              {Object.entries(stats.by_difficulty || {}).map(([diff, count]) => (
                <div key={diff} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
                  <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                    {count}
                  </div>
                  <div className="text-[12px] text-[var(--text-muted)] mt-1">{diff}</div>
                </div>
              ))}
            </div>
          )}

          {scenarios.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {scenarios.map((s) => (
                <AppLink
                  key={s.id}
                  href={`/training/${s.id}`}
                  className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] hover:border-[var(--accent)] flex flex-col justify-between gap-4 transition-colors group"
                >
                  <div className="space-y-2.5">
                    <div className="flex items-center justify-between gap-2">
                      <span className={`px-2 py-0.5 rounded text-[11px] font-medium border ${diffBadgeClass(s.difficulty)}`}>
                        {s.difficulty}
                      </span>
                      <span className="text-[11px] font-mono text-[var(--text-muted)]">{s.category}</span>
                    </div>
                    <h3 className="text-[15px] font-medium text-[var(--text-primary)] group-hover:text-[var(--accent)] transition-colors">
                      {s.title}
                    </h3>
                  </div>

                  <div className="space-y-2">
                    <div className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1 text-[12px]">
                      <div className="flex gap-2">
                        <span className="text-[var(--text-muted)] shrink-0">From:</span>
                        <span className="font-mono text-[var(--text-secondary)] truncate">{s.sender}</span>
                      </div>
                      <div className="flex gap-2">
                        <span className="text-[var(--text-muted)] shrink-0">Subj:</span>
                        <span className="text-[var(--text-secondary)] truncate">{s.subject}</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-end gap-1 text-[12.5px] font-medium text-[var(--accent)]">
                      <span>Start scenario</span>
                      <Icon.ArrowRight size={13} strokeWidth={1.5} aria-hidden="true" />
                    </div>
                  </div>
                </AppLink>
              ))}
            </div>
          ) : (
            <div className="py-16 px-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center">
              <Icon.GraduationCap size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)] mb-3" aria-hidden="true" />
              <h2 className="text-[16px] font-medium text-[var(--text-primary)]">Training module unavailable</h2>
              <p className="text-[13.5px] text-[var(--text-secondary)] max-w-md mx-auto mt-1">
                Training simulation scenarios could not be loaded.
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}

