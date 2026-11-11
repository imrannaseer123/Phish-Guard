import React, { useEffect, useRef, useState } from 'react';
import { Chart, registerables } from 'chart.js';
import { AppLink } from '../components/AppLink';
import { AnalyzerIcon, Icon, IntentIcon } from '../components/Icons';
import { RiskBadge, riskStyle } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

Chart.register(...registerables);

export function ReportPage() {
  const { state, theme, showToast } = useApp();
  const props = state?.props || {};
  const email = props.email || {};
  const report = props.report || {};
  const findingsSerialized = props.findings_serialized || [];
  const analyzerMax = props.analyzer_max || {};
  const trustData = props.trust_data;
  const campaignData = props.campaign_data;
  const headerGraphData = props.header_graph_data;
  const psiData = props.psi_data;
  const killchainData = props.killchain_data;
  const linguisticData = props.linguistic_data;
  const domainData = props.domain_data;
  const safeData = props.safe_data;
  const confidenceData = props.confidence_data || {};

  const ascendEnabled = Boolean(state?.config?.ASCEND_ENABLED);
  const mnCounterfactual = props.mn_counterfactual;
  const mnOntology = props.mn_ontology;
  const mnPsych = props.mn_psych;
  const mnIncidentEligible = Boolean(props.mn_incident_eligible);

  const [feedback, setFeedback] = useState(props.existing_feedback?.feedback || null);
  const [feedbackBusy, setFeedbackBusy] = useState(false);

  const [mnFeedback, setMnFeedback] = useState(props.mn_feedback?.feedback_type || null);
  const [mnBusy, setMnBusy] = useState(false);

  const [routeExpanded, setRouteExpanded] = useState(false);

  const radarRef = useRef(null);
  const radarChart = useRef(null);

  const riskScore = Number(report.risk_score || 0);
  const riskLevel = report.risk_level || 'Low';
  const st = riskStyle(riskLevel);

  // Semicircle gauge geometry
  const clampedScore = Math.max(0, Math.min(100, riskScore));
  const arcTotal = 251.2;
  const arcFill = (clampedScore / 100) * arcTotal;
  const angleRad = Math.PI * (1 - clampedScore / 100);
  const needleX = (100 + 68 * Math.cos(angleRad)).toFixed(1);
  const needleY = (100 - 68 * Math.sin(angleRad)).toFixed(1);

  const analyzerLabels = {
    keyword: 'Keywords',
    url: 'URLs',
    sender: 'Sender',
    urgency: 'Urgency',
    structure: 'Structure',
  };

  useEffect(() => {
    setFeedback(props.existing_feedback?.feedback || null);
    setMnFeedback(props.mn_feedback?.feedback_type || null);
  }, [email.id, props.existing_feedback, props.mn_feedback]);

  useEffect(() => {
    if (!radarRef.current) return;
    if (radarChart.current) {
      radarChart.current.destroy();
    }

    const isDark = theme === 'dark';
    const gridColor = isDark ? 'rgba(238, 240, 245, 0.08)' : 'rgba(15, 23, 42, 0.08)';
    const labelColor = isDark ? '#a3a9b8' : '#475569';
    const keys = ['keyword', 'url', 'sender', 'urgency', 'structure'];
    const labels = keys.map((k) => analyzerLabels[k]);
    const scores = report.analyzer_scores || {};
    const actualVals = keys.map((k) => Number((scores[k] || 0).toFixed(1)));
    const maxVals = keys.map((k) => Number(analyzerMax[k] || 0));

    radarChart.current = new Chart(radarRef.current.getContext('2d'), {
      type: 'radar',
      data: {
        labels,
        datasets: [
          {
            label: 'Actual score',
            data: actualVals,
            backgroundColor: isDark ? 'rgba(59, 130, 246, 0.18)' : 'rgba(30, 64, 175, 0.14)',
            borderColor: isDark ? '#3b82f6' : '#1e40af',
            borderWidth: 2,
            pointBackgroundColor: isDark ? '#3b82f6' : '#1e40af',
            pointRadius: 3.5,
          },
          {
            label: 'Maximum weight',
            data: maxVals,
            backgroundColor: 'rgba(148, 163, 184, 0.05)',
            borderColor: isDark ? 'rgba(148, 163, 184, 0.35)' : 'rgba(100, 116, 139, 0.35)',
            borderWidth: 1,
            borderDash: [4, 4],
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            beginAtZero: true,
            max: 25,
            ticks: { display: false },
            grid: { color: gridColor },
            angleLines: { color: gridColor },
            pointLabels: {
              color: labelColor,
              font: { size: 12, family: "'Fira Sans', sans-serif" },
            },
          },
        },
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              color: labelColor,
              font: { size: 12, family: "'Fira Sans', sans-serif" },
              usePointStyle: true,
              pointStyle: 'circle',
            },
          },
        },
      },
    });

    return () => {
      if (radarChart.current) {
        radarChart.current.destroy();
      }
    };
  }, [report.analyzer_scores, analyzerMax, theme]);

  const submitCoreFeedback = async (feedbackType) => {
    setFeedbackBusy(true);
    try {
      const res = await fetch(`/feedback/${email.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback: feedbackType,
          original_score: riskScore,
          original_level: riskLevel,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setFeedback(feedbackType);
      showToast(
        `Feedback submitted: Marked as ${feedbackType.charAt(0).toUpperCase() + feedbackType.slice(1)}`,
        'success'
      );
    } catch (err) {
      showToast(`Feedback failed: ${err.message}`, 'error');
    } finally {
      setFeedbackBusy(false);
    }
  };

  const submitAscendFeedback = async (type) => {
    setMnBusy(true);
    try {
      const categories = findingsSerialized.map((f) => f.analyzer).filter(Boolean);
      const res = await fetch(`/ascend/feedback/${email.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback_type: type,
          risk_score: riskScore,
          risk_level: riskLevel,
          triggered_rules: categories,
        }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setMnFeedback(type);
      showToast('Ascend rule feedback recorded', 'success');
    } catch (err) {
      showToast(`Failed to submit Ascend feedback: ${err.message}`, 'error');
    } finally {
      setMnBusy(false);
    }
  };

  const findings = report.findings || [];

  return (
    <div className="space-y-6 pb-8">
      {/* Top Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
            Forensic analysis report
          </h1>
          <p className="text-[12.5px] font-mono text-[var(--text-muted)] mt-1">
            Message ID: {email.id}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <AppLink
            href="/inbox"
            className="h-9 px-3.5 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-card)] hover:bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5 transition-colors"
          >
            <Icon.ArrowLeft size={14} strokeWidth={1.5} aria-hidden="true" />
            <span>Back to inbox</span>
          </AppLink>
          <a
            href={`/export/${email.id}`}
            download
            className="h-9 px-3.5 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-card)] hover:bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5 transition-colors"
          >
            <Icon.Download size={14} strokeWidth={1.5} aria-hidden="true" />
            <span>Export JSON</span>
          </a>
        </div>
      </div>

      {/* Email Metadata Strip */}
      <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] grid grid-cols-1 md:grid-cols-3 gap-5">
        <div>
          <div className="text-[12px] text-[var(--text-muted)] mb-1">From</div>
          <div className="text-[13.5px] font-medium text-[var(--text-primary)] break-all">{email.sender}</div>
        </div>
        <div>
          <div className="text-[12px] text-[var(--text-muted)] mb-1">Subject</div>
          <div className="text-[13.5px] font-medium text-[var(--text-primary)]">{email.subject}</div>
        </div>
        <div>
          <div className="text-[12px] text-[var(--text-muted)] mb-1">Timestamp</div>
          <div className="text-[13px] font-mono text-[var(--text-secondary)]">{email.date}</div>
        </div>
      </div>

      {/* Trust & Campaign Context Badges */}
      {(trustData || campaignData) && (
        <div className="flex flex-wrap items-center gap-3">
          {trustData && (
            <div
              className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-[12.5px] font-medium border ${
                trustData.level === 'trusted'
                  ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:border-emerald-500/20'
                  : trustData.level === 'neutral'
                  ? 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/20'
                  : 'bg-red-50 text-red-700 border-red-200 dark:bg-red-500/10 dark:text-red-300 dark:border-red-500/20'
              }`}
            >
              <Icon.UserCheck size={14} strokeWidth={1.5} aria-hidden="true" />
              <span>{trustData.label}</span>
              <span className="font-mono text-[11.5px] opacity-80">
                (Score {Math.round(trustData.score || 0)}, {trustData.emails_seen} email
                {trustData.emails_seen !== 1 ? 's' : ''})
              </span>
            </div>
          )}

          {campaignData && (
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-[12.5px] font-medium bg-amber-50 text-amber-800 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/20">
              <Icon.Network size={14} strokeWidth={1.5} aria-hidden="true" />
              <span>Possible campaign detected</span>
              <span className="font-mono text-[11.5px] opacity-80">
                ({campaignData.email_count} similar emails)
              </span>
            </div>
          )}
        </div>
      )}

      {/* Primary Score Gauge + Intent Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Semicircle Gauge */}
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col justify-between min-h-[260px]">
          <div className="flex items-center justify-between">
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Risk score</h2>
            <RiskBadge level={riskLevel} label={`${riskLevel} risk`} />
          </div>

          <div className="flex flex-col items-center justify-center my-4">
            <div className="relative w-60 h-32">
              <svg className="w-full h-full overflow-visible" viewBox="0 0 200 115" aria-hidden="true">
                <path
                  d="M 20 100 A 80 80 0 0 1 180 100"
                  fill="none"
                  stroke="currentColor"
                  className="text-slate-200 dark:text-slate-800"
                  strokeWidth="11"
                  strokeLinecap="round"
                />
                <path
                  d="M 20 100 A 80 80 0 0 1 180 100"
                  fill="none"
                  stroke={riskLevel === 'High' ? '#dc2626' : riskLevel === 'Medium' ? '#d97706' : '#16a34a'}
                  strokeWidth="11"
                  strokeLinecap="round"
                  strokeDasharray={`${arcFill} ${arcTotal}`}
                />
                <line
                  x1="100"
                  y1="100"
                  x2={needleX}
                  y2={needleY}
                  stroke="currentColor"
                  className="text-[var(--text-primary)]"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                />
                <circle cx="100" cy="100" r="4" className="fill-[var(--text-primary)]" />
              </svg>
              <div className="absolute inset-x-0 bottom-0 text-center">
                <div className={`text-4xl font-medium font-mono tabular-nums risk-score-value ${st.text}`}>
                  {Math.round(riskScore)}
                </div>
                <div className="text-[11.5px] font-mono text-[var(--text-muted)]">out of 100</div>
              </div>
            </div>
          </div>
        </div>

        {/* Intent Card */}
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col justify-between gap-4">
          <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Phishing intent</h2>

          <div className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex items-center gap-3.5">
            <span className="w-10 h-10 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] flex items-center justify-center text-[var(--accent)] shrink-0">
              <IntentIcon intent={report.intent} size={20} />
            </span>
            <div>
              <div className="text-[12px] text-[var(--text-muted)]">Classified category</div>
              <div className="text-[17px] font-medium text-[var(--text-primary)]">{report.intent}</div>
            </div>
          </div>

          <p className="text-[13.5px] leading-relaxed text-[var(--text-secondary)]">
            {report.explanation_summary}
          </p>
        </div>
      </div>

      {/* Feature Contribution + Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-5">
          <div>
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Feature contribution</h2>
            <p className="text-[13px] text-[var(--text-muted)] mt-0.5">Score breakdown by analyzer</p>
          </div>
          <div className="space-y-3.5">
            {Object.entries(analyzerMax).map(([name, maxVal]) => {
              const actual = Number((report.analyzer_scores?.[name] || 0).toFixed(1));
              const pct = maxVal > 0 ? Math.min(100, (actual / maxVal) * 100) : 0;
              return (
                <div key={name} className="grid grid-cols-[120px_1fr_56px] items-center gap-3">
                  <div className="flex items-center gap-2 text-[13px] text-[var(--text-secondary)]">
                    <AnalyzerIcon name={name} size={15} className="text-[var(--text-muted)] shrink-0" />
                    <span>{analyzerLabels[name] || name}</span>
                  </div>
                  <div className="h-2 rounded-full bg-[var(--bg-raised)] overflow-hidden">
                    <div
                      className="h-full rounded-full bg-[var(--accent)] transition-[width] duration-500"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <div className="font-mono text-[12.5px] tabular-nums text-right text-[var(--text-primary)]">
                    {actual}/{maxVal}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col">
          <div>
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Risk radar</h2>
            <p className="text-[13px] text-[var(--text-muted)] mt-0.5">Actual score relative to analyzer caps</p>
          </div>
          <div className="relative h-64 w-full mt-4">
            <canvas ref={radarRef} />
          </div>
        </div>
      </div>

      {/* Header Route Visualization */}
      {headerGraphData && (
        <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] overflow-hidden">
          <button
            type="button"
            onClick={() => setRouteExpanded((v) => !v)}
            aria-expanded={routeExpanded}
            className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-[var(--bg-raised)]/50 transition-colors cursor-pointer"
          >
            <div>
              <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Mail route visualization</h2>
              <p className="text-[12.5px] font-mono text-[var(--text-muted)] mt-0.5">
                {headerGraphData.hop_count} server hop{headerGraphData.hop_count !== 1 ? 's' : ''} detected
              </p>
            </div>
            <Icon.ChevronRight
              size={16}
              strokeWidth={1.5}
              className={`text-[var(--text-muted)] transition-transform ${routeExpanded ? 'rotate-90' : ''}`}
            />
          </button>

          {routeExpanded && (
            <div className="p-6 pt-4 border-t border-[var(--border-hairline)] overflow-x-auto">
              {headerGraphData.nodes && headerGraphData.nodes.length > 0 ? (
                <div className="flex items-center gap-3 min-w-max py-2">
                  {headerGraphData.nodes.map((node, idx) => {
                    const edge = headerGraphData.edges?.find((e) => e.from === node.id);
                    return (
                      <React.Fragment key={node.id}>
                        <div className="px-4 py-2.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] min-w-[160px]">
                          <div className="text-[12.5px] font-medium text-[var(--text-primary)]">{node.label}</div>
                          {node.ip && (
                            <div className="text-[11px] font-mono text-[var(--text-muted)] mt-0.5">{node.ip}</div>
                          )}
                        </div>
                        {idx < headerGraphData.nodes.length - 1 && (
                          <div className="flex flex-col items-center px-1 shrink-0">
                            {edge?.protocol && (
                              <span className="text-[10px] font-mono text-[var(--accent)] mb-0.5">
                                {edge.protocol}
                              </span>
                            )}
                            <Icon.ArrowRight size={15} strokeWidth={1.5} className="text-[var(--text-muted)]" />
                          </div>
                        )}
                      </React.Fragment>
                    );
                  })}
                </div>
              ) : (
                <p className="text-[13px] text-[var(--text-muted)]">No route data available.</p>
              )}
            </div>
          )}
        </div>
      )}

      {/* PSI Breakdown */}
      {psiData && psiData.psi_label && psiData.psi_label !== 'Unknown' && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
          <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Phishing Severity Index (PSI)</h2>
          <div className="flex flex-col md:flex-row md:items-center gap-6">
            <div className="flex items-baseline gap-2 shrink-0">
              <span className="text-4xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {psiData.psi_score}
              </span>
              <span className="text-[14px] font-mono text-[var(--text-muted)]">/ 10</span>
              <span className="ml-2 px-2.5 py-0.5 rounded-md text-[12px] font-medium bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-primary)]">
                {psiData.psi_label}
              </span>
            </div>
            <div className="flex-1 space-y-3">
              <p className="text-[13.5px] text-[var(--text-secondary)]">{psiData.explanation}</p>
              {psiData.components && (
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {Object.entries(psiData.components).map(([key, comp]) => (
                    <div key={key} className="space-y-1">
                      <div className="flex justify-between text-[12px] text-[var(--text-muted)]">
                        <span>{comp.label || key}</span>
                        <span className="font-mono tabular-nums">{comp.score}/10</span>
                      </div>
                      <div className="h-1.5 rounded-full bg-[var(--bg-raised)] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-[var(--accent)]"
                          style={{ width: `${Math.min(100, Math.round((comp.score / 10) * 100))}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Safe Classification Reasoning (when Low risk) */}
      {safeData && safeData.is_applicable && (safeData.trust_signals?.length > 0 || safeData.absent_risks?.length > 0) && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
          <div className="flex items-center gap-2">
            <Icon.ShieldCheck size={16} strokeWidth={1.5} className="text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
            <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Why this email appears safe</h2>
          </div>
          {safeData.summary && (
            <p className="text-[13.5px] text-[var(--text-secondary)]">{safeData.summary}</p>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...(safeData.trust_signals || []), ...(safeData.absent_risks || [])].map((item, i) => (
              <div key={i} className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex items-start gap-2.5">
                <Icon.Check size={14} strokeWidth={1.5} className="text-emerald-600 dark:text-emerald-400 mt-0.5 shrink-0" aria-hidden="true" />
                <div>
                  <div className="text-[13px] font-medium text-[var(--text-primary)]">{item.title}</div>
                  <p className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">{item.explanation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Findings */}
      <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
        <div>
          <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Detailed findings</h2>
          <p className="text-[13px] text-[var(--text-muted)] mt-0.5">
            Detected indicators with extracted evidence and rule explanations
          </p>
        </div>

        {findings.length > 0 ? (
          <div className="space-y-3">
            {findings.map((finding, idx) => {
              const conf = confidenceData[finding.indicator];
              return (
                <div
                  key={idx}
                  className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] border-l-2 border-l-[var(--accent)] space-y-2"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <AnalyzerIcon name={finding.analyzer} size={15} className="text-[var(--text-muted)]" />
                      <span className="text-[14px] font-medium text-[var(--text-primary)]">
                        {(finding.indicator || '').replace(/_/g, ' ')}
                      </span>
                      <span className="text-[11.5px] font-mono px-1.5 py-0.5 rounded bg-[var(--bg-raised)] text-[var(--text-muted)]">
                        {finding.analyzer}
                      </span>
                      {conf && (
                        <span className="text-[11.5px] font-mono text-[var(--text-muted)]">
                          Confidence {Math.round(conf.confidence_pct || 0)}%
                        </span>
                      )}
                    </div>
                    <span className="font-mono text-[12.5px] font-medium px-2 py-0.5 rounded bg-red-50 text-red-700 border border-red-200 dark:bg-red-500/10 dark:text-red-400 dark:border-red-500/20 tabular-nums">
                      +{(finding.score || 0).toFixed(1)} pts
                    </span>
                  </div>
                  <div className="text-[13px] text-[var(--text-primary)]">
                    <span className="text-[var(--text-muted)]">Evidence: </span>
                    <span className="font-mono text-[12.5px] break-all">{finding.evidence}</span>
                  </div>
                  <p className="text-[13px] text-[var(--text-secondary)]">{finding.explanation}</p>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-10 text-center rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] text-[13.5px] text-[var(--text-secondary)]">
            No suspicious indicators detected in this email.
          </div>
        )}
      </div>

      {/* Awareness Tips */}
      {report.awareness_tips && report.awareness_tips.length > 0 && (
        <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3">
          <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Recommended precautions</h2>
          <ul className="space-y-2 text-[13.5px] text-[var(--text-secondary)]">
            {report.awareness_tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <Icon.Info size={15} strokeWidth={1.5} className="text-[var(--accent)] mt-0.5 shrink-0" aria-hidden="true" />
                <span>{tip.replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\s]+/u, '')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* v2 Domain & Kill-Chain & Linguistic Supplemental Panels */}
      {(domainData?.findings?.length > 0 || (killchainData?.active_count || 0) > 0 || (linguisticData?.deception_signals_count || 0) > 0) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {(killchainData?.active_count || 0) > 0 && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3">
              <div className="flex items-center justify-between gap-2">
                <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Phishing kill-chain stages</h2>
                <span className="font-mono text-[11.5px] text-[var(--text-muted)]">
                  {killchainData.active_count} active
                </span>
              </div>
              {killchainData.phase_summary && (
                <p className="text-[13px] text-[var(--text-secondary)]">
                  {String(killchainData.phase_summary).replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\s]+/u, '')}
                </p>
              )}
              <div className="space-y-2">
                {(killchainData.stages || []).filter((s) => s.active).map((stItem, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">
                        {String(stItem.label || stItem.id).replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\s]+/u, '')}
                      </span>
                      <span className="font-mono text-[11px] text-[var(--text-muted)] capitalize">
                        {stItem.confidence}
                      </span>
                    </div>
                    <p className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">{stItem.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {domainData?.findings?.length > 0 && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Domain infrastructure heuristics</h2>
              <div className="space-y-2">
                {domainData.findings.map((flag, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">{flag.title || flag.type}</span>
                      {flag.severity && (
                        <span className="font-mono text-[11px] text-[var(--text-muted)] capitalize">{flag.severity}</span>
                      )}
                    </div>
                    <p className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">{flag.description}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {(linguisticData?.deception_signals_count || 0) > 0 && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-3 lg:col-span-2">
              <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Linguistic deception signals</h2>
              {linguisticData.summary && (
                <p className="text-[13px] text-[var(--text-secondary)]">
                  {String(linguisticData.summary).replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\s]+/u, '')}
                </p>
              )}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {(linguisticData.emotional_manipulation || []).map((em, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-[13px] font-medium text-[var(--text-primary)]">
                        {String(em.label || em.category).replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}\s]+/u, '')}
                      </span>
                      <span className="font-mono text-[11px] text-[var(--text-muted)] capitalize">{em.intensity}</span>
                    </div>
                    <p className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">{em.description}</p>
                  </div>
                ))}
                {linguisticData.pronoun_analysis?.inconsistency_detected && (
                  <div className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                    <div className="text-[13px] font-medium text-[var(--text-primary)]">Pronoun inconsistency</div>
                    <p className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">
                      {linguisticData.pronoun_analysis.explanation}
                    </p>
                  </div>
                )}
                {linguisticData.tone_mismatch?.detected && (
                  <div className="p-3 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
                    <div className="text-[13px] font-medium text-[var(--text-primary)]">Tone mismatch</div>
                    <p className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">
                      {linguisticData.tone_mismatch.explanation}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* ASCEND Framework Layer */}
      {ascendEnabled && (
        <div className="space-y-6 pt-2">
          {/* Counterfactual Reasoning */}
          {mnCounterfactual && mnCounterfactual.length > 0 && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Counterfactual reasoning</h2>
                  <p className="text-[13px] text-[var(--text-muted)] mt-0.5">
                    Score sensitivity when individual indicator categories are removed
                  </p>
                </div>
                <span className="font-mono text-[11.5px] px-2 py-0.5 rounded bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-secondary)]">
                  Ascend
                </span>
              </div>
              <div className="space-y-2.5">
                {mnCounterfactual.map((cf, i) => (
                  <div
                    key={i}
                    className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] flex items-center gap-4"
                  >
                    <div className="w-24 shrink-0 font-mono text-[13px] tabular-nums">
                      <span className="font-medium text-[var(--text-primary)]">{Math.round(cf.original_score)}</span>
                      <span className="text-[var(--text-muted)]"> → {Math.round(cf.hypothetical_score)}</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-[13.5px] font-medium text-[var(--text-primary)]">{cf.category_label}</div>
                      <div className="text-[12.5px] text-[var(--text-secondary)] mt-0.5">{cf.narrative}</div>
                    </div>
                    <span className="font-mono text-[12.5px] font-medium text-red-600 dark:text-red-400 shrink-0 tabular-nums">
                      -{cf.delta} pts
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Threat Intent Ontology */}
          {mnOntology && mnOntology.length > 0 && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
              <div className="flex items-center justify-between gap-2">
                <div>
                  <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Threat intent ontology</h2>
                  <p className="text-[13px] text-[var(--text-muted)] mt-0.5">Evidence → Intent → Impact chain mapping</p>
                </div>
                <span className="font-mono text-[11.5px] px-2 py-0.5 rounded bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-secondary)]">
                  Ascend
                </span>
              </div>
              <div className="space-y-3">
                {mnOntology.map((entry, idx) =>
                  (entry.chains || []).map((chain, cIdx) => (
                    <div
                      key={`${idx}-${cIdx}`}
                      className="p-3.5 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-1.5"
                    >
                      <div className="flex flex-wrap items-center gap-2 text-[12.5px]">
                        <span className="px-2 py-0.5 rounded bg-[var(--bg-raised)] border border-[var(--border-hairline)] font-medium text-[var(--text-primary)]">
                          {(entry.evidence || '').replace(/_/g, ' ')}
                        </span>
                        <Icon.ArrowRight size={13} strokeWidth={1.5} className="text-[var(--text-muted)]" aria-hidden="true" />
                        <span className="px-2 py-0.5 rounded bg-amber-50 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20 font-medium text-amber-800 dark:text-amber-300">
                          {chain.intent}
                        </span>
                        <Icon.ArrowRight size={13} strokeWidth={1.5} className="text-[var(--text-muted)]" aria-hidden="true" />
                        <span className="px-2 py-0.5 rounded bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 font-medium text-red-700 dark:text-red-300">
                          {chain.impact}
                        </span>
                      </div>
                      {chain.description && (
                        <p className="text-[12.5px] text-[var(--text-secondary)]">{chain.description}</p>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Psychological Manipulation Analysis */}
          {mnPsych && mnPsych.enabled && mnPsych.overall_level && mnPsych.overall_level !== 'None' && (
            <div className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-4">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <h2 className="text-[15px] font-medium text-[var(--text-primary)]">Psychological manipulation</h2>
                  <RiskBadge level={mnPsych.overall_level} />
                </div>
                <span className="font-mono text-[11.5px] px-2 py-0.5 rounded bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-secondary)]">
                  Ascend
                </span>
              </div>
              <p className="text-[13.5px] text-[var(--text-secondary)]">{mnPsych.narrative}</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Object.entries(mnPsych.categories || {})
                  .filter(([, cat]) => (cat.intensity || 0) > 0)
                  .map(([catKey, cat]) => (
                    <div
                      key={catKey}
                      className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)] space-y-2.5"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-[13.5px] font-medium text-[var(--text-primary)]">{cat.label}</span>
                        <RiskBadge level={cat.level} />
                      </div>
                      <div className="h-1.5 rounded-full bg-[var(--bg-raised)] overflow-hidden">
                        <div
                          className="h-full rounded-full bg-[var(--accent)]"
                          style={{ width: `${Math.min(100, (cat.intensity || 0) * 8)}%` }}
                        />
                      </div>
                      <div className="flex flex-wrap gap-1.5">
                        {(cat.matches || []).slice(0, 4).map((m, idx) => (
                          <span
                            key={idx}
                            className="font-mono text-[11px] px-1.5 py-0.5 rounded bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-secondary)]"
                          >
                            {m}
                          </span>
                        ))}
                        {(cat.matches || []).length > 4 && (
                          <span className="font-mono text-[11px] text-[var(--text-muted)]">
                            +{cat.matches.length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Incident Report & Ascend Rule Feedback Bar */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)]">
            <div>
              {mnIncidentEligible ? (
                <AppLink
                  href={`/ascend/incident/${email.id}`}
                  className="h-9 px-4 rounded-lg bg-red-600 hover:bg-red-700 text-white text-[13px] font-medium inline-flex items-center gap-1.5 transition-colors"
                >
                  <Icon.FileText size={14} strokeWidth={1.5} aria-hidden="true" />
                  <span>Generate incident report</span>
                </AppLink>
              ) : (
                <span className="text-[12.5px] text-[var(--text-muted)]">
                  Score below autonomous incident report threshold
                </span>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <span className="text-[12.5px] text-[var(--text-secondary)]">Ascend rule feedback:</span>
              {mnFeedback ? (
                <span className="text-[12.5px] font-medium text-[var(--text-primary)]">
                  Recorded: {mnFeedback.replace(/_/g, ' ')}
                </span>
              ) : (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    disabled={mnBusy}
                    onClick={() => submitAscendFeedback('helpful')}
                    className="h-8 px-3 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] hover:border-emerald-400 text-[12.5px] font-medium text-[var(--text-primary)] cursor-pointer disabled:opacity-40"
                  >
                    Helpful
                  </button>
                  <button
                    type="button"
                    disabled={mnBusy}
                    onClick={() => submitAscendFeedback('false_alarm')}
                    className="h-8 px-3 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] hover:border-amber-400 text-[12.5px] font-medium text-[var(--text-primary)] cursor-pointer disabled:opacity-40"
                  >
                    False alarm
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Footer Accuracy Feedback & Navigation */}
      <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="text-[13.5px] font-medium text-[var(--text-primary)]">Is this assessment accurate?</span>
          {feedback ? (
            <span className="text-[13px] text-[var(--text-secondary)]">
              You marked this as <strong className="font-medium text-[var(--text-primary)]">{feedback}</strong>
            </span>
          ) : (
            <div className="flex items-center gap-2">
              <button
                type="button"
                disabled={feedbackBusy}
                onClick={() => submitCoreFeedback('phishing')}
                className="h-8 px-3 rounded-lg border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-500/20 text-[12.5px] font-medium cursor-pointer disabled:opacity-40"
              >
                Mark phishing
              </button>
              <button
                type="button"
                disabled={feedbackBusy}
                onClick={() => submitCoreFeedback('safe')}
                className="h-8 px-3 rounded-lg border border-emerald-200 dark:border-emerald-500/30 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-500/20 text-[12.5px] font-medium cursor-pointer disabled:opacity-40"
              >
                Mark safe
              </button>
            </div>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-2.5">
          <AppLink
            href="/inbox"
            className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center"
          >
            Analyze another email
          </AppLink>
          <AppLink
            href="/history"
            className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center"
          >
            View history
          </AppLink>
        </div>
      </div>
    </div>
  );
}

