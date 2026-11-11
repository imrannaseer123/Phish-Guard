import React, { useMemo, useState } from 'react';
import { AppLink } from '../components/AppLink';
import { Icon, IntentIcon } from '../components/Icons';
import { RiskBadge, ScoreChip } from '../components/RiskBadge';
import { useApp } from '../context/AppContext';

export function HistoryPage() {
  const { state, showToast, navigate } = useApp();
  const initialLogs = state?.props?.logs || [];

  const [logs, setLogs] = useState(initialLogs);
  const [search, setSearch] = useState('');
  const [levelFilter, setLevelFilter] = useState('All');
  const [sortCol, setSortCol] = useState('id');
  const [sortDir, setSortDir] = useState('desc');
  const [feedbackMap, setFeedbackMap] = useState({});
  const [submittingId, setSubmittingId] = useState(null);
  const [confirmClear, setConfirmClear] = useState(false);
  const [clearing, setClearing] = useState(false);

  const toggleSort = (col) => {
    if (sortCol === col) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortCol(col);
      setSortDir(col === 'risk_score' || col === 'id' ? 'desc' : 'asc');
    }
  };

  const processedLogs = useMemo(() => {
    const q = search.trim().toLowerCase();
    return [...logs]
      .filter((row) => {
        if (levelFilter !== 'All' && row.risk_level !== levelFilter) return false;
        if (!q) return true;
        return (
          (row.sender || '').toLowerCase().includes(q) ||
          (row.subject || '').toLowerCase().includes(q) ||
          (row.intent || '').toLowerCase().includes(q)
        );
      })
      .sort((a, b) => {
        let av = a[sortCol];
        let bv = b[sortCol];
        if (sortCol === 'id' || sortCol === 'risk_score') {
          av = Number(av) || 0;
          bv = Number(bv) || 0;
        } else {
          av = String(av || '').toLowerCase();
          bv = String(bv || '').toLowerCase();
        }
        if (av === bv) return 0;
        const cmp = av > bv ? 1 : -1;
        return sortDir === 'asc' ? cmp : -cmp;
      });
  }, [logs, search, levelFilter, sortCol, sortDir]);

  const handleFeedback = async (log, feedbackType) => {
    setSubmittingId(log.message_id);
    try {
      const res = await fetch(`/feedback/${log.message_id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          feedback: feedbackType,
          original_score: log.risk_score || 0,
          original_level: log.risk_level || 'Unknown',
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setFeedbackMap((prev) => ({ ...prev, [log.message_id]: feedbackType }));
      showToast(
        `Feedback submitted: Marked as ${feedbackType.charAt(0).toUpperCase() + feedbackType.slice(1)}`,
        'success'
      );
    } catch (err) {
      showToast(`Feedback failed: ${err.message}`, 'error');
    } finally {
      setSubmittingId(null);
    }
  };

  const handleClearHistory = async () => {
    setClearing(true);
    try {
      const res = await fetch('/history/clear', { method: 'POST' });
      const data = await res.json();
      if (!res.ok || !data.success) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setLogs([]);
      setConfirmClear(false);
      showToast('History cleared successfully', 'success');
      navigate('/history');
    } catch (err) {
      showToast(`Failed to clear history: ${err.message}`, 'error');
    } finally {
      setClearing(false);
    }
  };

  const SortHeader = ({ col, label, align = 'left' }) => (
    <th
      className={`px-4 py-3 text-[12px] font-medium text-[var(--text-secondary)] border-b border-[var(--border-hairline)] select-none ${
        align === 'center' ? 'text-center' : align === 'right' ? 'text-right' : 'text-left'
      }`}
    >
      <button
        type="button"
        onClick={() => toggleSort(col)}
        className={`inline-flex items-center gap-1 hover:text-[var(--text-primary)] cursor-pointer ${
          align === 'center' ? 'justify-center' : ''
        }`}
      >
        <span>{label}</span>
        {sortCol === col &&
          (sortDir === 'asc' ? (
            <Icon.ArrowUp size={12} strokeWidth={1.5} aria-hidden="true" />
          ) : (
            <Icon.ArrowDown size={12} strokeWidth={1.5} aria-hidden="true" />
          ))}
      </button>
    </th>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
            Analysis history
          </h1>
          <p className="text-[14px] text-[var(--text-secondary)] mt-1">
            Past email assessments and recorded feedback metadata
          </p>
        </div>

        {logs.length > 0 && (
          <button
            type="button"
            onClick={() => setConfirmClear(true)}
            className="h-9 px-3.5 rounded-lg border border-red-200 dark:border-red-500/30 bg-red-50 dark:bg-red-500/10 text-red-700 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-500/20 text-[13px] font-medium inline-flex items-center gap-1.5 transition-colors cursor-pointer self-start sm:self-auto"
          >
            <Icon.Trash2 size={14} strokeWidth={1.5} aria-hidden="true" />
            <span>Clear history</span>
          </button>
        )}
      </div>

      {logs.length > 0 ? (
        <>
          {/* Filter Controls */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="relative w-full sm:w-72">
              <Icon.Search
                size={15}
                strokeWidth={1.5}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-muted)]"
                aria-hidden="true"
              />
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search sender, subject, intent"
                aria-label="Search analysis history"
                className="w-full h-9 pl-9 pr-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] text-[13px] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
              />
            </div>

            <div className="flex items-center gap-1.5" role="group" aria-label="Filter by risk level">
              {['All', 'High', 'Medium', 'Low'].map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => setLevelFilter(lvl)}
                  aria-pressed={levelFilter === lvl}
                  className={`h-8 px-3 rounded-lg text-[12.5px] font-medium border transition-colors cursor-pointer ${
                    levelFilter === lvl
                      ? 'bg-[var(--bg-raised)] border-[var(--accent)] text-[var(--text-primary)]'
                      : 'bg-[var(--bg-card)] border-[var(--border-hairline)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>

          {/* Data Table */}
          <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-[var(--bg-raised)]">
                  <tr>
                    <SortHeader col="id" label="ID" />
                    <SortHeader col="timestamp" label="Timestamp" />
                    <SortHeader col="sender" label="Sender" />
                    <SortHeader col="subject" label="Subject" />
                    <SortHeader col="risk_score" label="Score" align="center" />
                    <SortHeader col="risk_level" label="Level" align="center" />
                    <SortHeader col="intent" label="Intent" />
                    <th className="px-4 py-3 text-[12px] font-medium text-[var(--text-secondary)] border-b border-[var(--border-hairline)] text-right">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-hairline)] text-[13px]">
                  {processedLogs.map((log) => {
                    const marked = feedbackMap[log.message_id];
                    const busy = submittingId === log.message_id;
                    return (
                      <tr
                        key={log.id}
                        className="hover:bg-[var(--bg-raised)]/50 transition-colors"
                      >
                        <td className="px-4 py-3 font-mono text-[12px] text-[var(--text-muted)] tabular-nums">
                          {log.id}
                        </td>
                        <td className="px-4 py-3 font-mono text-[12px] text-[var(--text-secondary)] whitespace-nowrap tabular-nums">
                          {(log.timestamp || '').slice(0, 19)}
                        </td>
                        <td
                          className="px-4 py-3 text-[var(--text-primary)] font-medium max-w-[200px] truncate"
                          title={log.sender}
                        >
                          {log.sender}
                        </td>
                        <td className="px-4 py-3 max-w-[280px] truncate" title={log.subject}>
                          <AppLink
                            href={`/analyze/${log.message_id}`}
                            className="text-[var(--text-secondary)] hover:text-[var(--accent)] hover:underline"
                          >
                            {log.subject}
                          </AppLink>
                        </td>
                        <td className="px-4 py-3 text-center">
                          <ScoreChip score={log.risk_score} level={log.risk_level} />
                        </td>
                        <td className="px-4 py-3 text-center">
                          <RiskBadge level={log.risk_level} />
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1.5 text-[12.5px] text-[var(--text-secondary)] whitespace-nowrap">
                            <IntentIcon intent={log.intent} size={14} className="text-[var(--text-muted)]" />
                            <span>{log.intent}</span>
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right whitespace-nowrap">
                          <div className="inline-flex items-center gap-1.5">
                            {marked ? (
                              <span
                                className={`text-[12px] font-medium px-2 py-0.5 rounded ${
                                  marked === 'phishing'
                                    ? 'text-red-600 dark:text-red-400'
                                    : 'text-emerald-600 dark:text-emerald-400'
                                }`}
                              >
                                Marked {marked}
                              </span>
                            ) : (
                              <>
                                <button
                                  type="button"
                                  disabled={busy}
                                  onClick={() => handleFeedback(log, 'phishing')}
                                  title="Mark as Phishing"
                                  aria-label={`Mark analysis ${log.id} as Phishing`}
                                  className="h-7 px-2 rounded border border-[var(--border-hairline)] hover:border-red-300 dark:hover:border-red-500/40 text-[11.5px] text-[var(--text-secondary)] hover:text-red-600 dark:hover:text-red-400 transition-colors cursor-pointer disabled:opacity-40"
                                >
                                  Phishing
                                </button>
                                <button
                                  type="button"
                                  disabled={busy}
                                  onClick={() => handleFeedback(log, 'safe')}
                                  title="Mark as Safe"
                                  aria-label={`Mark analysis ${log.id} as Safe`}
                                  className="h-7 px-2 rounded border border-[var(--border-hairline)] hover:border-emerald-300 dark:hover:border-emerald-500/40 text-[11.5px] text-[var(--text-secondary)] hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors cursor-pointer disabled:opacity-40"
                                >
                                  Safe
                                </button>
                              </>
                            )}
                            <a
                              href={`/export/${log.message_id}`}
                              download
                              title="Export forensic JSON"
                              aria-label={`Export forensic evidence for ${log.id}`}
                              className="h-7 w-7 inline-flex items-center justify-center rounded border border-[var(--border-hairline)] text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-raised)] transition-colors"
                            >
                              <Icon.Download size={13} strokeWidth={1.5} />
                            </a>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {processedLogs.length === 0 && (
                    <tr>
                      <td colSpan={8} className="px-4 py-10 text-center text-[13px] text-[var(--text-muted)]">
                        No records match the current filter.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <div className="py-16 px-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center">
          <Icon.History size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)] mb-3" aria-hidden="true" />
          <h2 className="text-[16px] font-medium text-[var(--text-primary)]">No analyses yet</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] max-w-sm mx-auto mt-1 mb-5">
            Analyze emails from your inbox to inspect findings and build historical telemetry.
          </p>
          <AppLink
            href="/inbox"
            className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center gap-1.5 transition-colors"
          >
            <span>Go to inbox</span>
          </AppLink>
        </div>
      )}

      {/* Confirmation Modal */}
      {confirmClear && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div className="fixed inset-0 bg-black/50" onClick={() => !clearing && setConfirmClear(false)} />
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="clear-history-title"
            className="relative z-10 w-full max-w-md rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] p-6 shadow-xl space-y-4 animate-surface-enter"
          >
            <div className="flex items-center gap-2.5 text-red-600 dark:text-red-400">
              <Icon.AlertTriangle size={18} strokeWidth={1.5} aria-hidden="true" />
              <h2 id="clear-history-title" className="text-[16px] font-medium text-[var(--text-primary)]">
                Clear all analysis history
              </h2>
            </div>
            <p className="text-[13.5px] text-[var(--text-secondary)] leading-relaxed">
              This removes all recorded email analysis logs and feedback entries from the local database. This action cannot be undone.
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                disabled={clearing}
                onClick={() => setConfirmClear(false)}
                className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] cursor-pointer"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={clearing}
                onClick={handleClearHistory}
                className="h-9 px-4 rounded-lg bg-red-600 hover:bg-red-700 text-white text-[13px] font-medium cursor-pointer disabled:opacity-50"
              >
                {clearing ? 'Clearing...' : 'Clear all logs'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

