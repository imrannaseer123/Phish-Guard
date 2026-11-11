import React from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { RiskBadge } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

export function IncidentReportPage() {
  const { state } = useApp();
  const report = state?.props?.report;
  const error = state?.props?.error;

  if (error || !report) {
    return (
      <div className="max-w-3xl mx-auto py-8">
        <div className="p-8 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-3">
          <Icon.FileText size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)]" aria-hidden="true" />
          <h1 className="text-xl font-medium text-[var(--text-primary)]">No incident report</h1>
          <p className="text-[13.5px] text-[var(--text-secondary)] max-w-md mx-auto">
            {error || 'No incident report available for this message.'}
          </p>
          <div className="pt-2">
            <AppLink
              href="/history"
              className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center gap-1.5"
            >
              <Icon.ArrowLeft size={14} strokeWidth={1.5} aria-hidden="true" />
              <span>Back to history</span>
            </AppLink>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-8">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
              Incident report
            </h1>
            <RiskBadge level="High" label={report.severity} />
          </div>
          <div className="font-mono text-[12px] text-[var(--text-muted)] mt-1">
            {report.report_id} · {report.timestamp}
          </div>
        </div>

        <a
          href={`/ascend/incident/${report.email?.message_id}/export`}
          download
          className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-card)] hover:bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5 self-start sm:self-auto"
        >
          <Icon.Download size={14} strokeWidth={1.5} aria-hidden="true" />
          <span>Export as text</span>
        </a>
      </div>

      {/* Executive Summary */}
      <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-2">
        <h2 className="text-[14px] font-medium text-[var(--text-primary)]">Executive summary</h2>
        <p className="text-[13.5px] leading-relaxed text-[var(--text-secondary)]">
          {report.executive_summary}
        </p>
      </div>

      {/* Email Metadata */}
      <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
        <h2 className="text-[14px] font-medium text-[var(--text-primary)]">Email details</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
            <div className="text-[11.5px] text-[var(--text-muted)]">Subject</div>
            <div className="text-[13.5px] font-medium text-[var(--text-primary)] mt-0.5">{report.email?.subject}</div>
          </div>
          <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
            <div className="text-[11.5px] text-[var(--text-muted)]">Sender</div>
            <div className="text-[13.5px] font-medium text-[var(--text-primary)] mt-0.5 break-all">{report.email?.sender}</div>
          </div>
          <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
            <div className="text-[11.5px] text-[var(--text-muted)]">Risk score</div>
            <div className="text-[15px] font-mono font-medium text-red-600 dark:text-red-400 mt-0.5 tabular-nums">
              {Math.round(report.risk_score || 0)} / 100
            </div>
          </div>
          <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
            <div className="text-[11.5px] text-[var(--text-muted)]">Intent classification</div>
            <div className="text-[13.5px] font-medium text-[var(--text-primary)] mt-0.5">{report.intent}</div>
          </div>
        </div>
      </div>

      {/* Evidence Catalogue */}
      <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
        <h2 className="text-[14px] font-medium text-[var(--text-primary)]">
          Evidence catalogue ({(report.evidence || []).length} indicators)
        </h2>
        <div className="space-y-3">
          {(report.evidence || []).map((e, idx) => (
            <div key={idx} className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1.5">
              <div className="flex items-center justify-between gap-2">
                <span className="font-mono text-[12.5px] font-medium text-[var(--text-primary)]">
                  [{e.category}] {(e.indicator || '').replace(/_/g, ' ')}
                </span>
                <span className="font-mono text-[12px] font-medium text-red-600 dark:text-red-400 tabular-nums">
                  +{Number(e.severity_contribution || 0).toFixed(1)} pts
                </span>
              </div>
              {e.evidence && <p className="font-mono text-[12px] text-[var(--text-secondary)] break-all">{e.evidence}</p>}
              {e.description && <p className="text-[12.5px] text-[var(--text-muted)]">{e.description}</p>}
            </div>
          ))}
        </div>
      </div>

      {/* Threat Chains */}
      {report.threat_chains && report.threat_chains.length > 0 && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3">
          <h2 className="text-[14px] font-medium text-[var(--text-primary)]">
            Threat chains ({report.threat_chains.length})
          </h2>
          <div className="space-y-2">
            {report.threat_chains.map((c, idx) => (
              <div
                key={idx}
                className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex flex-wrap items-center gap-2 text-[12.5px]"
              >
                <span className="font-medium text-[var(--accent)]">{(c.evidence || '').replace(/_/g, ' ')}</span>
                <Icon.ArrowRight size={13} strokeWidth={1.5} className="text-[var(--text-muted)]" aria-hidden="true" />
                <span className="font-medium text-amber-600 dark:text-amber-400">{c.intent}</span>
                <Icon.ArrowRight size={13} strokeWidth={1.5} className="text-[var(--text-muted)]" aria-hidden="true" />
                <span className="font-medium text-red-600 dark:text-red-400">{c.impact}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Mitigations */}
      <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3">
        <h2 className="text-[14px] font-medium text-[var(--text-primary)]">Recommended mitigations</h2>
        <ul className="space-y-2 text-[13.5px] text-[var(--text-secondary)]">
          {(report.mitigations || []).map((m, idx) => (
            <li key={idx} className="flex items-start gap-2">
              <Icon.Check size={14} strokeWidth={1.5} className="text-emerald-600 dark:text-emerald-400 mt-1 shrink-0" aria-hidden="true" />
              <span>{m}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Disclaimer */}
      <div className="p-4 rounded-xl bg-amber-50/70 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 text-center space-y-1">
        <p className="text-[12.5px] text-amber-900 dark:text-amber-300">{report.disclaimer}</p>
        <p className="font-mono text-[11px] text-amber-700 dark:text-amber-400">Status: {report.status}</p>
      </div>
    </div>
  );
}

