import React from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { RiskBadge, ScoreChip } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

export function RiskProfilePage() {
  const { state } = useApp();
  const profile = state?.props?.profile || {};
  const hasProfile = profile && profile.total_emails_analyzed !== undefined;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
          User risk profile
        </h1>
        <p className="text-[14px] text-[var(--text-secondary)] mt-1">
          Personal email threat exposure over the past {profile.period_days || 30} days — read-only metadata analytics
        </p>
      </div>

      {hasProfile ? (
        <>
          {/* Exposure Score Hero Card */}
          <div className="p-6 sm:p-8 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col sm:flex-row items-center justify-between gap-6">
            <div className="space-y-2 max-w-xl">
              <div className="flex items-center gap-2.5">
                <h2 className="text-[16px] font-medium text-[var(--text-primary)]">Exposure score</h2>
                <RiskBadge level={profile.exposure_label} label={`${profile.exposure_label} exposure`} />
              </div>
              <p className="text-[13.5px] leading-relaxed text-[var(--text-secondary)]">{profile.summary}</p>
            </div>

            <div className="flex items-baseline gap-2 shrink-0 p-5 rounded-xl bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <span className="text-5xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {profile.exposure_score}
              </span>
              <span className="text-[14px] font-mono text-[var(--text-muted)]">/ 100</span>
            </div>
          </div>

          {/* Stats Row */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">Emails analyzed</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-[var(--text-primary)] mt-2">
                {profile.total_emails_analyzed}
              </div>
            </div>
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">High risk</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-red-600 dark:text-red-400 mt-2">
                {profile.risk_distribution?.High || 0}
              </div>
            </div>
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">Medium risk</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-amber-600 dark:text-amber-400 mt-2">
                {profile.risk_distribution?.Medium || 0}
              </div>
            </div>
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">Low risk</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-emerald-600 dark:text-emerald-400 mt-2">
                {profile.risk_distribution?.Low || 0}
              </div>
            </div>
          </div>

          {/* Weekly Frequency */}
          {profile.risk_frequency && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Weekly risk frequency</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex items-center justify-between">
                  <span className="text-[13.5px] text-[var(--text-secondary)]">High-risk emails per week</span>
                  <span className="font-mono text-xl font-medium tabular-nums text-red-600 dark:text-red-400">
                    {profile.risk_frequency.high_per_week}
                  </span>
                </div>
                <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex items-center justify-between">
                  <span className="text-[13.5px] text-[var(--text-secondary)]">Medium-risk emails per week</span>
                  <span className="font-mono text-xl font-medium tabular-nums text-amber-600 dark:text-amber-400">
                    {profile.risk_frequency.medium_per_week}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Intents & Risky Senders */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {profile.top_intents && profile.top_intents.length > 0 && (
              <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
                <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Most common attack types</h2>
                <div className="space-y-3.5">
                  {profile.top_intents.map((item, i) => (
                    <div key={i} className="space-y-1.5">
                      <div className="flex justify-between text-[13px]">
                        <span className="text-[var(--text-primary)]">{item.intent}</span>
                        <span className="font-mono text-[var(--text-muted)] tabular-nums">{item.pct}%</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-[var(--bg-raised)] overflow-hidden">
                        <div className="h-full rounded-full bg-[var(--accent)]" style={{ width: `${item.pct}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {profile.top_risky_senders && profile.top_risky_senders.length > 0 && (
              <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
                <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Top risky senders</h2>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-[13px]">
                    <thead>
                      <tr className="border-b border-[var(--border-hairline)] text-[12px] text-[var(--text-muted)]">
                        <th className="pb-2 font-medium">Sender</th>
                        <th className="pb-2 font-medium text-center">Count</th>
                        <th className="pb-2 font-medium text-right">Avg score</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[var(--border-hairline)]">
                      {profile.top_risky_senders.map((s, i) => (
                        <tr key={i}>
                          <td className="py-2.5 pr-4 text-[var(--text-primary)] max-w-[180px] truncate" title={s.sender}>
                            {s.sender}
                          </td>
                          <td className="py-2.5 text-center font-mono text-[var(--text-secondary)] tabular-nums">
                            {s.count}
                          </td>
                          <td className="py-2.5 text-right">
                            <ScoreChip
                              score={s.avg_score}
                              level={s.avg_score >= 67 ? 'High' : s.avg_score >= 34 ? 'Medium' : 'Low'}
                            />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* Common Indicators */}
          {profile.most_common_indicators && profile.most_common_indicators.length > 0 && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Most triggered detection rules</h2>
              <div className="flex flex-wrap gap-2">
                {profile.most_common_indicators.map((ind, i) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] text-[12.5px] text-[var(--text-primary)]"
                  >
                    <span>{(ind.indicator || '').replace(/_/g, ' ')}</span>
                    <span className="font-mono text-[11.5px] text-[var(--text-muted)] tabular-nums">×{ind.count}</span>
                  </span>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="py-16 px-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-3">
          <Icon.UserCheck size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)]" aria-hidden="true" />
          <h2 className="text-[16px] font-medium text-[var(--text-primary)]">No analysis data available</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] max-w-md mx-auto">
            Analyze emails from your inbox to build your personal exposure profile.
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

