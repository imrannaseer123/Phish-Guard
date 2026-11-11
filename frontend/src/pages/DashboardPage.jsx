import React, { useEffect, useRef } from 'react';
import { Chart, registerables } from 'chart.js';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { RiskBadge, ScoreChip } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

Chart.register(...registerables);

export function DashboardPage() {
  const { state, theme } = useApp();
  const summary = state?.props?.summary || {};
  const profileStats = state?.props?.profile_stats || {};
  const weeklyTrend = state?.props?.weekly_trend || [];

  const isDark = theme === 'dark';
  const gridColor = isDark ? 'rgba(238, 240, 245, 0.08)' : 'rgba(15, 23, 42, 0.08)';
  const labelColor = isDark ? '#a3a9b8' : '#475569';
  const fontMono = "'Fira Code', monospace";
  const fontSans = "'Fira Sans', sans-serif";

  const trendRef = useRef(null);
  const intentRef = useRef(null);
  const dailyRef = useRef(null);
  const brandRef = useRef(null);
  const intentTrendRef = useRef(null);
  const chartsRef = useRef({});

  const destroyChart = (key) => {
    if (chartsRef.current[key]) {
      chartsRef.current[key].destroy();
      delete chartsRef.current[key];
    }
  };

  useEffect(() => {
    const hasData = summary && !summary.error && (summary.total_scanned || 0) > 0;
    if (!hasData) return;

    // 1. Weekly Risk Trend (Line)
    if (weeklyTrend && weeklyTrend.length > 0 && trendRef.current) {
      destroyChart('trend');
      chartsRef.current.trend = new Chart(trendRef.current.getContext('2d'), {
        type: 'line',
        data: {
          labels: weeklyTrend.map((t) => t.date),
          datasets: [
            {
              label: 'Risk Score',
              data: weeklyTrend.map((t) => t.score),
              borderColor: isDark ? '#3b82f6' : '#1e40af',
              backgroundColor: isDark ? 'rgba(59, 130, 246, 0.12)' : 'rgba(30, 64, 175, 0.08)',
              borderWidth: 2,
              tension: 0.25,
              fill: true,
              pointRadius: 2.5,
              pointBackgroundColor: isDark ? '#3b82f6' : '#1e40af',
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              grid: { color: gridColor },
              ticks: { color: labelColor, maxTicksLimit: 8, font: { family: fontMono, size: 11 } },
            },
            y: {
              beginAtZero: true,
              max: 100,
              grid: { color: gridColor },
              ticks: { color: labelColor, font: { family: fontMono, size: 11 } },
            },
          },
          plugins: {
            legend: { display: false },
          },
        },
      });
    }

    // 2. Intent Distribution (Doughnut)
    if (summary.intent_distribution && intentRef.current) {
      destroyChart('intent');
      const labels = Object.keys(summary.intent_distribution);
      const values = Object.values(summary.intent_distribution);
      const colors = labels.map((l) => {
        switch (l) {
          case 'Credential Harvesting':
            return '#dc2626';
          case 'Financial Fraud':
            return '#d97706';
          case 'Malware Delivery':
            return '#2563eb';
          case 'Identity Theft':
            return '#0284c7';
          case 'Legitimate':
            return '#16a34a';
          default:
            return '#64748b';
        }
      });

      chartsRef.current.intent = new Chart(intentRef.current.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels,
          datasets: [{ data: values, backgroundColor: colors, borderWidth: 0, hoverOffset: 6 }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '60%',
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                color: labelColor,
                font: { family: fontSans, size: 12 },
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 14,
              },
            },
          },
        },
      });
    }

    // 3. Daily Activity (Grouped Bar)
    if (dailyRef.current && summary.daily_labels) {
      destroyChart('daily');
      chartsRef.current.daily = new Chart(dailyRef.current.getContext('2d'), {
        type: 'bar',
        data: {
          labels: summary.daily_labels,
          datasets: [
            {
              label: 'Total Scanned',
              data: summary.daily_scan_values,
              backgroundColor: isDark ? 'rgba(59, 130, 246, 0.7)' : 'rgba(30, 64, 175, 0.75)',
              borderRadius: 4,
            },
            {
              label: 'Risky (Med+High)',
              data: summary.daily_risk_values,
              backgroundColor: isDark ? 'rgba(239, 68, 68, 0.75)' : 'rgba(220, 38, 38, 0.8)',
              borderRadius: 4,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              grid: { color: gridColor },
              ticks: { color: labelColor, font: { family: fontMono, size: 11 } },
            },
            y: {
              beginAtZero: true,
              grid: { color: gridColor },
              ticks: { color: labelColor, stepSize: 1, font: { family: fontMono, size: 11 } },
            },
          },
          plugins: {
            legend: {
              labels: { color: labelColor, font: { family: fontSans, size: 12 }, usePointStyle: true },
            },
          },
        },
      });
    }

    // 4. Top Impersonated Brands (Horizontal Bar)
    if (brandRef.current && summary.top_brands && summary.top_brands.length > 0) {
      destroyChart('brand');
      chartsRef.current.brand = new Chart(brandRef.current.getContext('2d'), {
        type: 'bar',
        data: {
          labels: summary.top_brands.map((b) => b[0]),
          datasets: [
            {
              label: 'Impersonation Attempts',
              data: summary.top_brands.map((b) => b[1]),
              backgroundColor: isDark ? 'rgba(245, 158, 11, 0.75)' : 'rgba(217, 119, 6, 0.8)',
              borderRadius: 4,
            },
          ],
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              beginAtZero: true,
              grid: { color: gridColor },
              ticks: { color: labelColor, stepSize: 1, font: { family: fontMono, size: 11 } },
            },
            y: {
              grid: { display: false },
              ticks: { color: labelColor, font: { family: fontSans, size: 12, weight: '500' } },
            },
          },
          plugins: { legend: { display: false } },
        },
      });
    }

    // 5. Daily Intent Trend (Stacked Bar)
    if (intentTrendRef.current && summary.daily_intent_data) {
      destroyChart('intentTrend');
      const d = summary.daily_intent_data;
      const palette = ['#dc2626', '#d97706', '#2563eb', '#0284c7', '#16a34a', '#64748b'];
      chartsRef.current.intentTrend = new Chart(intentTrendRef.current.getContext('2d'), {
        type: 'bar',
        data: {
          labels: d.labels,
          datasets: d.intents.map((intent, idx) => ({
            label: intent,
            data: d.series[intent],
            backgroundColor: palette[idx % palette.length],
            stack: 'Stack 0',
          })),
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              stacked: true,
              grid: { color: gridColor },
              ticks: { color: labelColor, font: { family: fontMono, size: 11 } },
            },
            y: {
              stacked: true,
              beginAtZero: true,
              grid: { color: gridColor },
              ticks: { color: labelColor, stepSize: 1, font: { family: fontMono, size: 11 } },
            },
          },
          plugins: {
            legend: {
              labels: { color: labelColor, font: { family: fontSans, size: 12 }, usePointStyle: true },
            },
          },
        },
      });
    }

    return () => {
      Object.keys(chartsRef.current).forEach(destroyChart);
    };
  }, [summary, weeklyTrend, isDark, gridColor, labelColor, fontMono, fontSans]);

  const hasData = summary && !summary.error && (summary.total_scanned || 0) > 0;
  const total = summary.total_scanned || 0;
  const pct = (count) => (total > 0 ? Math.round((count / total) * 100) : 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
          Weekly security dashboard
        </h1>
        <p className="text-[14px] text-[var(--text-secondary)] mt-1">
          Read-only threat telemetry for the last {summary.period_days || 7} days
        </p>
      </div>

      {hasData ? (
        <>
          {/* Privacy-Safe Risk Profile Summary Bar */}
          {profileStats && profileStats.total_scanned !== undefined && (
            <div className="p-5 sm:p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col lg:flex-row lg:items-center justify-between gap-6">
              <div className="space-y-1 max-w-xl">
                <div className="flex items-center gap-2 text-[14px] font-medium text-[var(--text-primary)]">
                  <Icon.Shield size={16} strokeWidth={1.5} className="text-[var(--accent)]" aria-hidden="true" />
                  <span>Privacy-safe risk profile</span>
                </div>
                <p className="text-[13px] text-[var(--text-secondary)]">
                  Computed from anonymous metadata across your last 50 analyzed emails without storing bodies.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-6 sm:gap-10 shrink-0">
                <div>
                  <div className="text-[12px] text-[var(--text-muted)]">Average score</div>
                  <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)] mt-0.5">
                    {profileStats.average_score}
                  </div>
                </div>
                <div>
                  <div className="text-[12px] text-[var(--text-muted)]">Current risk</div>
                  <div className="mt-1">
                    <RiskBadge level={profileStats.current_risk_level} />
                  </div>
                </div>
                <div>
                  <div className="text-[12px] text-[var(--text-muted)]">Total analyzed</div>
                  <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)] mt-0.5">
                    {profileStats.total_scanned}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 4 Compact Stat Cards (Numbers + Label + Comparison Note) */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">Emails scanned</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-[var(--text-primary)] mt-2">
                {summary.total_scanned}
              </div>
              <div className="text-[12px] font-mono text-[var(--text-muted)] mt-2">
                {summary.total_all_time} all-time
              </div>
            </div>

            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">High risk</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-red-600 dark:text-red-400 mt-2">
                {summary.high_risk_count}
              </div>
              <div className="text-[12px] font-mono text-[var(--text-muted)] mt-2">
                {pct(summary.high_risk_count)}% of period
              </div>
            </div>

            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">Medium risk</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-amber-600 dark:text-amber-400 mt-2">
                {summary.medium_risk_count}
              </div>
              <div className="text-[12px] font-mono text-[var(--text-muted)] mt-2">
                {pct(summary.medium_risk_count)}% of period
              </div>
            </div>

            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
              <div className="text-[12.5px] text-[var(--text-muted)]">Low risk</div>
              <div className="text-3xl font-medium font-mono tabular-nums text-emerald-600 dark:text-emerald-400 mt-2">
                {summary.low_risk_count}
              </div>
              <div className="text-[12px] font-mono text-[var(--text-muted)] mt-2">
                Avg score {summary.avg_score}
              </div>
            </div>
          </div>

          {/* Primary Chart Row (Asymmetric 2/3 Trend + 1/3 Distribution) */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)] mb-4">
                Risk score trend
              </h2>
              <div className="relative h-72 w-full">
                {weeklyTrend && weeklyTrend.length > 0 ? (
                  <canvas ref={trendRef} />
                ) : (
                  <div className="h-full flex items-center justify-center text-[13px] text-[var(--text-muted)]">
                    No trend points available yet
                  </div>
                )}
              </div>
            </div>

            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)] mb-4">
                Intent distribution
              </h2>
              <div className="relative h-72 w-full">
                <canvas ref={intentRef} />
              </div>
            </div>
          </div>

          {/* Secondary Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)] mb-4">
                Daily scan volume
              </h2>
              <div className="relative h-64 w-full">
                <canvas ref={dailyRef} />
              </div>
            </div>

            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)] mb-4">
                Daily intent breakdown
              </h2>
              <div className="relative h-64 w-full">
                {summary.daily_intent_data ? (
                  <canvas ref={intentTrendRef} />
                ) : (
                  <div className="h-full flex items-center justify-center text-[13px] text-[var(--text-muted)]">
                    No daily intent series recorded
                  </div>
                )}
              </div>
            </div>
          </div>

          {summary.top_brands && summary.top_brands.length > 0 && (
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)] mb-4">
                Top impersonated brands
              </h2>
              <div className="relative h-56 w-full">
                <canvas ref={brandRef} />
              </div>
            </div>
          )}

          {/* Alerts & Risky Senders */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {summary.recent_alerts && summary.recent_alerts.length > 0 && (
              <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
                <h2 className="text-[15px] font-medium text-[var(--text-primary)]">
                  Recent high-risk alerts
                </h2>
                <div className="divide-y divide-[var(--border-hairline)]">
                  {summary.recent_alerts.map((alert, i) => (
                    <div key={i} className="py-3 first:pt-0 last:pb-0 space-y-1">
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[13.5px] font-medium text-[var(--text-primary)] truncate">
                          {alert.sender}
                        </span>
                        <ScoreChip score={alert.score} level="High" />
                      </div>
                      <div className="text-[13px] text-[var(--text-secondary)] truncate">{alert.subject}</div>
                      <div className="flex items-center justify-between text-[11.5px] text-[var(--text-muted)]">
                        <span>{alert.intent}</span>
                        <span className="font-mono">{alert.timestamp}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {summary.top_risky_senders && summary.top_risky_senders.length > 0 && (
              <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
                <h2 className="text-[15px] font-medium text-[var(--text-primary)]">
                  Top risky senders
                </h2>
                <div className="divide-y divide-[var(--border-hairline)]">
                  {summary.top_risky_senders.map(([sender, count], i) => (
                    <div key={i} className="py-2.5 first:pt-0 last:pb-0 flex items-center justify-between gap-4">
                      <span className="text-[13px] text-[var(--text-primary)] truncate" title={sender}>
                        {sender}
                      </span>
                      <span className="font-mono text-[12px] text-[var(--text-secondary)] tabular-nums shrink-0">
                        {count} email{count !== 1 ? 's' : ''}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      ) : (
        <div className="py-16 px-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-3">
          <Icon.BarChart3 size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)]" aria-hidden="true" />
          <h2 className="text-[16px] font-medium text-[var(--text-primary)]">No data for this period</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] max-w-md mx-auto">
            {summary.error || 'Analyze emails to see weekly security statistics here.'}
          </p>
          {(summary.total_all_time || 0) > 0 && (
            <p className="text-[12px] font-mono text-[var(--text-muted)]">
              {summary.total_all_time} record(s) exist outside the last {summary.period_days || 7} days.
            </p>
          )}
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

