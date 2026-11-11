import React from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { RiskBadge } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

export function AscendDashboardPage() {
  const { state } = useApp();
  const forecast = state?.props?.forecast || {};
  const feedbackSuggestions = state?.props?.feedback_suggestions || {};
  const moduleStatus = state?.props?.module_status || {};

  const modules = [
    { name: 'Counterfactual', active: moduleStatus.counterfactual, desc: 'Score sensitivity reasoning' },
    { name: 'Ontology', active: moduleStatus.threat_ontology, desc: 'Evidence to impact chains' },
    { name: 'Forecast', active: moduleStatus.risk_forecast, desc: 'Human vulnerability trend' },
    { name: 'Psych analyzer', active: moduleStatus.psych_analyzer, desc: 'Manipulation cue detection' },
    { name: 'Rule feedback', active: moduleStatus.rule_feedback, desc: 'Adaptive tuning insights' },
    { name: 'Incident report', active: moduleStatus.incident_reporter, desc: 'Executive report export' },
    { name: 'What-if sandbox', active: moduleStatus.whatif_sandbox, desc: 'In-memory weight simulation' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
              Ascend framework
            </h1>
            <span className="px-2 py-0.5 rounded-md text-[11.5px] font-mono bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-secondary)]">
              Add-on layer
            </span>
          </div>
          <p className="text-[14px] text-[var(--text-secondary)] mt-1">
            Explainable security enhancement modules — read-only and advisory
          </p>
        </div>
      </div>

      {/* Module Status Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {modules.map((m) => (
          <div
            key={m.name}
            className="p-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-1"
          >
            <div className="flex items-center gap-2">
              <span
                className={`w-2 h-2 rounded-full shrink-0 ${
                  m.active ? 'bg-emerald-500' : 'bg-slate-400 dark:bg-slate-600'
                }`}
                aria-hidden="true"
              />
              <span className="text-[13px] font-medium text-[var(--text-primary)] truncate">{m.name}</span>
            </div>
            <div className="text-[11.5px] text-[var(--text-muted)] leading-snug">{m.desc}</div>
          </div>
        ))}
      </div>

      {/* Human Risk Forecast */}
      {forecast && forecast.vulnerability_level && forecast.vulnerability_level !== 'Unknown' ? (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-5">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-[16px] font-medium text-[var(--text-primary)]">Human risk forecast</h2>
            <RiskBadge
              level={forecast.vulnerability_level}
              label={`${forecast.vulnerability_level} vulnerability`}
            />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {forecast.stats?.total_analyses ?? 0}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">Total analyses</div>
            </div>
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {forecast.stats?.avg_risk_score ?? 0}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">Average risk score</div>
            </div>
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-2xl font-medium font-mono tabular-nums text-red-600 dark:text-red-400">
                {forecast.stats?.high_risk_count ?? 0}
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">High-risk emails</div>
            </div>
            <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-2xl font-medium font-mono text-[var(--text-primary)] flex items-center gap-1.5 capitalize">
                {forecast.trend_direction === 'rising' ? (
                  <Icon.TrendingUp size={18} strokeWidth={1.5} className="text-red-500" aria-hidden="true" />
                ) : forecast.trend_direction === 'falling' ? (
                  <Icon.TrendingDown size={18} strokeWidth={1.5} className="text-emerald-500" aria-hidden="true" />
                ) : (
                  <Icon.ArrowRight size={18} strokeWidth={1.5} className="text-[var(--text-muted)]" aria-hidden="true" />
                )}
                <span>{forecast.trend_direction || 'Stable'}</span>
              </div>
              <div className="text-[12px] text-[var(--text-muted)] mt-1">Risk trend</div>
            </div>
          </div>

          <p className="text-[13.5px] text-[var(--text-secondary)] leading-relaxed">
            {forecast.confidence_explanation}
          </p>
          <p className="text-[12px] text-[var(--text-muted)]">
            Advisory note: this forecast is read-only and does not alter core email detection scoring.
          </p>
        </div>
      ) : (
        forecast && (
          <div className="p-8 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-2">
            <Icon.Activity size={28} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)]" aria-hidden="true" />
            <p className="text-[14px] text-[var(--text-secondary)]">{forecast.confidence_explanation}</p>
            <p className="text-[12.5px] text-[var(--text-muted)]">
              Analyze additional emails to generate a human risk forecast.
            </p>
          </div>
        )
      )}

      {/* Adaptive Rule Feedback Suggestions */}
      {feedbackSuggestions && (feedbackSuggestions.total_feedback || 0) > 0 && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
          <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Adaptive rule feedback</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)]">{feedbackSuggestions.summary}</p>

          {feedbackSuggestions.suggestions && feedbackSuggestions.suggestions.length > 0 ? (
            <div className="space-y-2.5">
              {feedbackSuggestions.suggestions.map((s, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[13.5px] font-medium text-[var(--text-primary)] capitalize">
                      {s.analyzer}
                    </span>
                    <span
                      className={`font-mono text-[12px] font-medium px-2 py-0.5 rounded ${
                        s.direction === 'decrease'
                          ? 'bg-red-50 text-red-700 dark:bg-red-500/10 dark:text-red-400'
                          : 'bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400'
                      }`}
                    >
                      {s.current_weight} → {s.suggested_weight}
                    </span>
                  </div>
                  <p className="text-[13px] text-[var(--text-secondary)]">{s.reason}</p>
                  <div className="text-[11.5px] font-mono text-[var(--text-muted)]">
                    Confidence: {s.confidence}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[13px] text-[var(--text-muted)]">
              No adjustment suggestions yet. More feedback data is needed.
            </p>
          )}
        </div>
      )}

      {/* Quick Navigation */}
      <div className="flex flex-wrap gap-3">
        <AppLink
          href="/ascend/whatif"
          className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center gap-1.5"
        >
          <Icon.SlidersHorizontal size={14} strokeWidth={1.5} aria-hidden="true" />
          <span>What-if learning mode</span>
        </AppLink>
        <AppLink
          href="/inbox"
          className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-card)] hover:bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5"
        >
          <Icon.Inbox size={14} strokeWidth={1.5} aria-hidden="true" />
          <span>Analyze emails</span>
        </AppLink>
        <AppLink
          href="/history"
          className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-card)] hover:bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5"
        >
          <Icon.History size={14} strokeWidth={1.5} aria-hidden="true" />
          <span>Analysis history</span>
        </AppLink>
      </div>
    </div>
  );
}

