import React from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { RiskBadge } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

export function CampaignsPage() {
  const { state } = useApp();
  const campaigns = state?.props?.campaigns || [];

  const totalEmails = campaigns.reduce((sum, c) => sum + (c.email_count || 0), 0);
  const uniqueDomains = new Set(
    campaigns.flatMap((c) => (c.sender_domains || []).filter(Boolean))
  ).size;

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
            Campaign detection
          </h1>
          <p className="text-[14px] text-[var(--text-secondary)] mt-1 max-w-2xl">
            Clusters coordinated phishing messages using SimHash subject fingerprinting, Jaccard body similarity, and sender domain grouping.
          </p>
        </div>

        {campaigns.length > 0 && (
          <div className="grid grid-cols-3 gap-3 shrink-0">
            <div className="px-4 py-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {campaigns.length}
              </div>
              <div className="text-[11.5px] text-[var(--text-muted)]">Campaigns</div>
            </div>
            <div className="px-4 py-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {totalEmails}
              </div>
              <div className="text-[11.5px] text-[var(--text-muted)]">Emails</div>
            </div>
            <div className="px-4 py-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {uniqueDomains}
              </div>
              <div className="text-[11.5px] text-[var(--text-muted)]">Domains</div>
            </div>
          </div>
        )}
      </div>

      {campaigns.length > 0 ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {campaigns.map((camp, idx) => (
            <div
              key={camp.campaign_id || idx}
              className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] overflow-hidden"
            >
              <div className="px-5 py-4 border-b border-[var(--border-hairline)] flex items-center justify-between gap-3 bg-[var(--bg-raised)]">
                <div className="flex items-center gap-3 min-w-0">
                  <span className="w-7 h-7 rounded-md bg-[var(--bg-card)] border border-[var(--border-hairline)] font-mono text-[12px] font-medium flex items-center justify-center text-[var(--text-secondary)]">
                    #{idx + 1}
                  </span>
                  <div className="min-w-0">
                    <div className="text-[11px] text-[var(--text-muted)]">Cluster ID</div>
                    <div className="font-mono text-[13px] text-[var(--text-primary)] truncate">
                      {(camp.campaign_id || '').slice(0, 14)}
                    </div>
                  </div>
                </div>
                <span className="px-2.5 py-1 rounded-md bg-[var(--bg-card)] border border-[var(--border-hairline)] font-mono text-[12px] text-[var(--text-primary)] tabular-nums">
                  {camp.email_count} emails
                </span>
              </div>

              <div className="p-5 space-y-4">
                <div>
                  <div className="text-[12px] text-[var(--text-muted)] mb-2">Sender domains</div>
                  <div className="flex flex-wrap gap-1.5">
                    {(camp.sender_domains || []).filter(Boolean).map((d, dIdx) => (
                      <span
                        key={dIdx}
                        className="px-2 py-0.5 rounded bg-[var(--bg-app)] border border-[var(--border-hairline)] font-mono text-[12px] text-[var(--text-secondary)]"
                      >
                        {d}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-[12px] text-[var(--text-muted)] mb-2">Intents</div>
                    <div className="flex flex-wrap gap-1.5">
                      {(camp.intents || []).filter(Boolean).map((intent, iIdx) => (
                        <span
                          key={iIdx}
                          className="px-2 py-0.5 rounded text-[12px] bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-primary)]"
                        >
                          {intent}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <div className="text-[12px] text-[var(--text-muted)] mb-2">Risk levels</div>
                    <div className="flex flex-wrap gap-1.5">
                      {(camp.risk_levels || []).filter(Boolean).map((rl, rIdx) => (
                        <RiskBadge key={rIdx} level={rl} />
                      ))}
                    </div>
                  </div>
                </div>

                <div className="pt-3 border-t border-[var(--border-hairline)] flex items-center justify-between text-[12px] font-mono text-[var(--text-muted)]">
                  <span>First: {camp.first_seen ? camp.first_seen.slice(0, 10) : 'N/A'}</span>
                  <span>Last: {camp.last_seen ? camp.last_seen.slice(0, 10) : 'N/A'}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="p-10 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-6">
          <div className="max-w-lg mx-auto space-y-2">
            <Icon.Network size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)]" aria-hidden="true" />
            <h2 className="text-[17px] font-medium text-[var(--text-primary)]">No campaigns detected yet</h2>
            <p className="text-[13.5px] text-[var(--text-secondary)] leading-relaxed">
              Analyze more messages to detect coordinated waves via SimHash subject similarity and Jaccard token overlap.
            </p>
          </div>

          <div className="flex justify-center gap-3">
            <AppLink
              href="/inbox"
              className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center"
            >
              Analyze emails
            </AppLink>
            <AppLink
              href="/history"
              className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center"
            >
              View history
            </AppLink>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 max-w-2xl mx-auto pt-4 border-t border-[var(--border-hairline)] text-left">
            <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-[13px] font-medium text-[var(--text-primary)]">SimHash fingerprinting</div>
              <p className="text-[12px] text-[var(--text-muted)] mt-1">
                Locality-sensitive hashing detects similar subjects across minor edits.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-[13px] font-medium text-[var(--text-primary)]">Jaccard body overlap</div>
              <p className="text-[12px] text-[var(--text-muted)] mt-1">
                Token overlap ≥ 0.4 groups messages sharing common phishing copy.
              </p>
            </div>
            <div className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-[13px] font-medium text-[var(--text-primary)]">Domain clustering</div>
              <p className="text-[12px] text-[var(--text-muted)] mt-1">
                Shared sender infrastructure boosts cluster confidence.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

