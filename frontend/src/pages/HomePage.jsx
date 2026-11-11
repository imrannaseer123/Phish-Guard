import React from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { RiskBadge } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

export function HomePage() {
  const { state } = useApp();
  const authenticated = Boolean(state?.props?.authenticated ?? state?.config?.authenticated);

  const capabilities = [
    {
      icon: Icon.Lock,
      title: 'Read-only Gmail OAuth',
      desc: 'Connects with Google official OAuth 2.0 using gmail.readonly scope. Emails are never modified or stored.',
    },
    {
      icon: Icon.Layers,
      title: '5-point analyzer pipeline',
      desc: 'Evaluates keywords, URLs, sender identity, urgency patterns, and structural cues independently.',
    },
    {
      icon: Icon.BarChart3,
      title: 'Transparent risk breakdown',
      desc: 'Produces a 0 to 100 additive score with per-analyzer point contributions and exact evidence.',
    },
    {
      icon: Icon.Target,
      title: 'Intent classification',
      desc: 'Distinguishes Credential Harvesting, Financial Fraud, Malware Delivery, and Identity Theft.',
    },
    {
      icon: Icon.GraduationCap,
      title: 'Interactive training lab',
      desc: 'Practice identifying realistic phishing samples in an offline sandbox with immediate rule feedback.',
    },
    {
      icon: Icon.FileText,
      title: 'Evidence-backed explanations',
      desc: 'Every flagged indicator carries plain-language reasoning and contextual safety guidance.',
    },
  ];

  const previewAnalyzers = [
    { label: 'Keywords', score: 25, max: 25, color: 'bg-blue-600 dark:bg-blue-500' },
    { label: 'URL inspection', score: 25, max: 25, color: 'bg-sky-600 dark:bg-sky-400' },
    { label: 'Sender identity', score: 12, max: 20, color: 'bg-amber-600 dark:bg-amber-400' },
    { label: 'Urgency cues', score: 15, max: 15, color: 'bg-red-600 dark:bg-red-500' },
    { label: 'Structure', score: 11, max: 15, color: 'bg-slate-600 dark:bg-slate-400' },
  ];

  return (
    <div className="space-y-16 py-4">
      {/* Asymmetric Split Hero */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center pt-4">
        <div className="lg:col-span-6 space-y-6">
          <div className="inline-flex items-center gap-2 text-[12.5px] font-mono text-[var(--text-secondary)]">
            <span
              className={`w-2 h-2 rounded-full ${authenticated ? 'bg-emerald-500' : 'bg-[var(--accent)]'}`}
              aria-hidden="true"
            />
            <span>{authenticated ? 'Gmail session active' : 'Rule-based XAI email inspection'}</span>
          </div>

          <h1 className="text-4xl sm:text-5xl font-medium tracking-[-0.025em] leading-[1.08] text-[var(--text-primary)]">
            Explainable phishing risk analysis for your inbox
          </h1>

          <p className="text-[16px] sm:text-[17px] leading-[1.6] text-[var(--text-secondary)] max-w-xl">
            Inspect Gmail messages with transparent, rule-based scoring. Every risk score breaks down by analyzer,
            extracted evidence, and intent category with no black-box predictions.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-1">
            {authenticated ? (
              <>
                <AppLink
                  href="/inbox"
                  className="h-11 px-5 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[14px] font-medium inline-flex items-center gap-2 transition-colors"
                >
                  <Icon.Inbox size={16} strokeWidth={1.5} aria-hidden="true" />
                  <span>View inbox &amp; analyze</span>
                </AppLink>
                <AppLink
                  href="/history"
                  className="h-11 px-3 text-[14px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] inline-flex items-center gap-1.5 transition-colors"
                >
                  <span>Analysis history</span>
                  <Icon.ArrowRight size={15} strokeWidth={1.5} aria-hidden="true" />
                </AppLink>
              </>
            ) : (
              <>
                <a
                  href="/auth"
                  className="h-11 px-5 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[14px] font-medium inline-flex items-center gap-2 transition-colors"
                >
                  <Icon.Link2 size={16} strokeWidth={1.5} aria-hidden="true" />
                  <span>Connect Gmail</span>
                </a>
                <AppLink
                  href="/training"
                  className="h-11 px-3 text-[14px] font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] inline-flex items-center gap-1.5 transition-colors"
                >
                  <span>Try training simulator</span>
                  <Icon.ArrowRight size={15} strokeWidth={1.5} aria-hidden="true" />
                </AppLink>
              </>
            )}
          </div>

          <div className="pt-2 flex flex-wrap items-center gap-x-6 gap-y-2 text-[12.5px] text-[var(--text-muted)] border-t border-[var(--border-hairline)]">
            <span className="inline-flex items-center gap-1.5">
              <Icon.ShieldCheck size={14} strokeWidth={1.5} aria-hidden="true" />
              Read-only access
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Icon.Database size={14} strokeWidth={1.5} aria-hidden="true" />
              No email bodies stored
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Icon.FileCode2 size={14} strokeWidth={1.5} aria-hidden="true" />
              Deterministic scoring
            </span>
          </div>
        </div>

        {/* Product Moment: Live Forensic Inspection Card Preview */}
        <div className="lg:col-span-6">
          <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] shadow-sm overflow-hidden">
            <div className="px-5 py-3.5 border-b border-[var(--border-hairline)] bg-[var(--bg-raised)] flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 min-w-0">
                <Icon.ScanSearch size={15} strokeWidth={1.5} className="text-[var(--accent)] shrink-0" aria-hidden="true" />
                <span className="text-[12.5px] font-mono text-[var(--text-secondary)] truncate">
                  sample-inspection · paypa1-security-notice
                </span>
              </div>
              <RiskBadge level="High" label="High risk" />
            </div>

            <div className="p-5 space-y-5">
              {/* Top score + intent readout */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                  <div className="text-[12px] text-[var(--text-muted)] mb-1">Aggregate risk score</div>
                  <div className="flex items-baseline gap-1.5">
                    <span className="text-3xl font-medium font-mono tabular-nums text-red-600 dark:text-red-400">
                      88
                    </span>
                    <span className="text-xs font-mono text-[var(--text-muted)]">/ 100</span>
                  </div>
                </div>
                <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                  <div className="text-[12px] text-[var(--text-muted)] mb-1">Detected intent</div>
                  <div className="text-[14px] font-medium text-[var(--text-primary)] leading-snug">
                    Credential Harvesting
                  </div>
                  <div className="text-[11.5px] font-mono text-[var(--text-muted)] mt-0.5">
                    16 evidence rules matched
                  </div>
                </div>
              </div>

              {/* Analyzer breakdown */}
              <div className="space-y-2.5">
                <div className="flex items-center justify-between text-[12px] text-[var(--text-muted)]">
                  <span>Analyzer contribution</span>
                  <span className="font-mono">Points / max</span>
                </div>
                {previewAnalyzers.map((a) => (
                  <div key={a.label} className="grid grid-cols-[112px_1fr_52px] items-center gap-3 text-[12.5px]">
                    <span className="text-[var(--text-secondary)] truncate">{a.label}</span>
                    <div className="h-1.5 rounded-full bg-[var(--bg-raised)] overflow-hidden">
                      <div
                        className={`h-full rounded-full ${a.color}`}
                        style={{ width: `${(a.score / a.max) * 100}%` }}
                      />
                    </div>
                    <span className="font-mono text-right tabular-nums text-[var(--text-primary)]">
                      {a.score}/{a.max}
                    </span>
                  </div>
                ))}
              </div>

              {/* Sample extracted evidence row */}
              <div className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] border-l-2 border-l-red-600 dark:border-l-red-500 text-[12.5px]">
                <div className="flex items-center justify-between mb-1">
                  <span className="font-medium text-[var(--text-primary)]">IP-based destination URL</span>
                  <span className="font-mono text-red-600 dark:text-red-400">+10.0 pts</span>
                </div>
                <div className="font-mono text-[11.5px] text-[var(--text-muted)] truncate">
                  http://192.168.1.100/paypal-verify
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Capabilities Grid */}
      <section className="space-y-6 pt-4 border-t border-[var(--border-hairline)]">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3">
          <div>
            <h2 className="text-2xl font-medium tracking-tight text-[var(--text-primary)]">
              Transparent inspection pipeline
            </h2>
            <p className="text-[14px] text-[var(--text-secondary)] mt-1">
              Six core mechanisms powering every email assessment
            </p>
          </div>
          <AppLink
            href="/about"
            className="text-[13.5px] font-medium text-[var(--accent)] hover:underline inline-flex items-center gap-1"
          >
            <span>Architecture reference</span>
            <Icon.ArrowRight size={14} strokeWidth={1.5} aria-hidden="true" />
          </AppLink>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {capabilities.map((cap) => {
            const CapIcon = cap.icon;
            return (
              <div
                key={cap.title}
                className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col gap-3"
              >
                <div className="flex items-center gap-2.5">
                  <span className="w-8 h-8 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-hairline)] flex items-center justify-center text-[var(--accent)] shrink-0">
                    <CapIcon size={16} strokeWidth={1.5} aria-hidden="true" />
                  </span>
                  <h3 className="text-[15px] font-medium text-[var(--text-primary)]">{cap.title}</h3>
                </div>
                <p className="text-[13.5px] leading-relaxed text-[var(--text-secondary)]">{cap.desc}</p>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}

