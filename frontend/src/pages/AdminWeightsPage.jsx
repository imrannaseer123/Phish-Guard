import React from 'react';
import { AppLink } from '../components/AppLink';
import { AnalyzerIcon, Icon } from '../components/Icons';
import { useApp } from '../context/AppContext';

export function AdminWeightsPage() {
  const { state } = useApp();
  const suggestions = state?.props?.suggestions || {};
  const feedbackStats = state?.props?.feedback_stats;

  const analyzerLabels = {
    keyword: 'Keywords',
    url: 'URLs',
    sender: 'Sender',
    urgency: 'Urgency',
    structure: 'Structure',
  };

  const hasSuggestions = suggestions && !suggestions.error && suggestions.current_weights;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
          Adaptive weight advisor
        </h1>
        <p className="text-[14px] text-[var(--text-secondary)] mt-1">
          Suggested analyzer weight adjustments from user feedback — read-only and never auto-applied
        </p>
      </div>

      {/* Feedback Statistics */}
      {feedbackStats && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-4">
          {[
            { label: 'Total feedback', val: feedbackStats.total || 0 },
            { label: 'Marked phishing', val: feedbackStats.marked_phishing || 0 },
            { label: 'Marked safe', val: feedbackStats.marked_safe || 0 },
            { label: 'Missed (false neg)', val: feedbackStats.false_negatives || 0 },
            { label: 'Over-flagged (false pos)', val: feedbackStats.false_positives || 0 },
          ].map((item) => (
            <div key={item.label} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {item.val}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">{item.label}</div>
            </div>
          ))}
        </div>
      )}

      {hasSuggestions ? (
        <>
          <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] overflow-hidden">
            <div className="px-6 py-4 border-b border-[var(--border-hairline)] flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Weight comparison</h2>
                <p className="text-[12.5px] text-[var(--text-muted)] mt-0.5">
                  Based on {suggestions.total_feedback || 0} recorded feedback entries
                </p>
              </div>
              <span className="px-2.5 py-1 rounded-md bg-[var(--bg-raised)] border border-[var(--border-hairline)] font-mono text-[12px] text-[var(--text-primary)]">
                Confidence: {(suggestions.confidence || 'low').toUpperCase()}
              </span>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse text-[13px]">
                <thead className="bg-[var(--bg-raised)] text-[12px] text-[var(--text-secondary)]">
                  <tr>
                    <th className="px-6 py-3 font-medium border-b border-[var(--border-hairline)]">Analyzer</th>
                    <th className="px-6 py-3 font-medium border-b border-[var(--border-hairline)] text-right">Current</th>
                    <th className="px-6 py-3 font-medium border-b border-[var(--border-hairline)] text-right">Suggested</th>
                    <th className="px-6 py-3 font-medium border-b border-[var(--border-hairline)] text-right">Change</th>
                    <th className="px-6 py-3 font-medium border-b border-[var(--border-hairline)]">Explanation</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-hairline)]">
                  {Object.entries(suggestions.current_weights || {}).map(([analyzer, current]) => {
                    const suggested = suggestions.suggested_weights?.[analyzer] ?? current;
                    const diff = suggested - current;
                    return (
                      <tr key={analyzer} className="hover:bg-[var(--bg-raised)]/40">
                        <td className="px-6 py-3.5 font-medium text-[var(--text-primary)]">
                          <span className="inline-flex items-center gap-2">
                            <AnalyzerIcon name={analyzer} size={15} className="text-[var(--text-muted)]" />
                            <span>{analyzerLabels[analyzer] || analyzer}</span>
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-right font-mono tabular-nums text-[var(--text-secondary)]">
                          {current}
                        </td>
                        <td className="px-6 py-3.5 text-right font-mono tabular-nums font-medium text-[var(--text-primary)]">
                          {suggested}
                        </td>
                        <td className="px-6 py-3.5 text-right font-mono tabular-nums">
                          {diff > 0 ? (
                            <span className="text-red-600 dark:text-red-400">+{diff}</span>
                          ) : diff < 0 ? (
                            <span className="text-emerald-600 dark:text-emerald-400">{diff}</span>
                          ) : (
                            <span className="text-[var(--text-muted)]">0</span>
                          )}
                        </td>
                        <td className="px-6 py-3.5 text-[var(--text-secondary)]">
                          {suggestions.explanations?.[analyzer] || 'No data'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {suggestions.confidence === 'low' && (
              <div className="px-6 py-3.5 bg-amber-50/70 dark:bg-amber-500/10 border-t border-amber-200 dark:border-amber-500/20 text-[12.5px] text-amber-800 dark:text-amber-300">
                Low confidence: collect at least 5 feedback entries for medium confidence and 20+ for high confidence.
              </div>
            )}
          </div>

          <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">How weight suggestions work</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1">
                <div className="text-[13.5px] font-medium text-[var(--text-primary)]">False negatives</div>
                <p className="text-[12.5px] text-[var(--text-secondary)]">
                  When low-risk messages are marked phishing, relevant analyzers may warrant higher weights.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1">
                <div className="text-[13.5px] font-medium text-[var(--text-primary)]">False positives</div>
                <p className="text-[12.5px] text-[var(--text-secondary)]">
                  When high-risk messages are marked safe, dominant analyzers may warrant lower weights.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1">
                <div className="text-[13.5px] font-medium text-[var(--text-primary)]">Read-only advisory</div>
                <p className="text-[12.5px] text-[var(--text-secondary)]">
                  Suggestions are never auto-applied and serve purely for manual tuning review.
                </p>
              </div>
              <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1">
                <div className="text-[13.5px] font-medium text-[var(--text-primary)]">Transparent rationale</div>
                <p className="text-[12.5px] text-[var(--text-secondary)]">
                  Each suggestion reports mismatch count and average score contribution.
                </p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="py-16 px-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-3">
          <Icon.Scale size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)]" aria-hidden="true" />
          <h2 className="text-[16px] font-medium text-[var(--text-primary)]">No suggestions available</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] max-w-md mx-auto">
            {suggestions?.error || 'Analyze emails and submit accuracy feedback to generate weight suggestions.'}
          </p>
          <div className="pt-2">
            <AppLink
              href="/inbox"
              className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center"
            >
              Go to inbox
            </AppLink>
          </div>
        </div>
      )}
    </div>
  );
}

