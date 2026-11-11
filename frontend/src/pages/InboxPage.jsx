import React, { useEffect, useMemo, useState } from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { useApp } from '../context/AppContext';

export function InboxPage() {
  const { state } = useApp();
  const emails = state?.props?.emails || [];

  const [search, setSearch] = useState('');
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState('');
  const [emailCache, setEmailCache] = useState({});

  const filteredEmails = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return emails;
    return emails.filter(
      (e) =>
        (e.sender || '').toLowerCase().includes(q) ||
        (e.subject || '').toLowerCase().includes(q) ||
        (e.snippet || '').toLowerCase().includes(q)
    );
  }, [emails, search]);

  const openPreview = async (email) => {
    setSelectedEmail(email);
    setPreviewError('');

    if (emailCache[email.id]) {
      setPreviewData(emailCache[email.id]);
      setPreviewLoading(false);
      return;
    }

    setPreviewData(null);
    setPreviewLoading(true);
    try {
      const res = await fetch(`/email/content/${email.id}`);
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setEmailCache((prev) => ({ ...prev, [email.id]: data }));
      setPreviewData(data);
    } catch (err) {
      setPreviewError(err.message);
    } finally {
      setPreviewLoading(false);
    }
  };

  const closePreview = () => {
    setSelectedEmail(null);
    setPreviewData(null);
    setPreviewError('');
  };

  useEffect(() => {
    const onKeyDown = (e) => {
      if (e.key === 'Escape' && selectedEmail) {
        closePreview();
      }
    };
    window.addEventListener('keydown', onKeyDown);
    return () => window.removeEventListener('keydown', onKeyDown);
  }, [selectedEmail]);

  const buildSandboxedHtml = (bodyHtml) => {
    const isDark = document.documentElement.classList.contains('dark');
    const bg = isDark ? '#0b0d14' : '#ffffff';
    const fg = isDark ? '#cbd5e1' : '#334155';
    return `<!DOCTYPE html><html><head><meta charset="utf-8"><style>
      body{margin:0;padding:12px;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;line-height:1.6;color:${fg};background:${bg};word-break:break-word;}
      img{max-width:100%;height:auto;}
      a{color:#3b82f6;}
      table{max-width:100%!important;width:auto!important;}
    </style></head><body>${bodyHtml}</body></html>`;
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-medium tracking-tight text-[var(--text-primary)]">
            Inbox
          </h1>
          <p className="text-[14px] text-[var(--text-secondary)] mt-1">
            Select a message to inspect headers and run phishing risk analysis
          </p>
        </div>

        {emails.length > 0 && (
          <div className="relative w-full sm:w-64">
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
              placeholder="Filter sender or subject"
              aria-label="Filter inbox messages"
              className="w-full h-9 pl-9 pr-3 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] text-[13px] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
            />
          </div>
        )}
      </div>

      {filteredEmails.length > 0 ? (
        <div className="rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] divide-y divide-[var(--border-hairline)] overflow-hidden">
          {filteredEmails.map((email) => {
            const initial = (email.sender || '?').trim().charAt(0).toUpperCase();
            return (
              <div
                key={email.id}
                className="p-4 sm:px-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 hover:bg-[var(--bg-raised)]/60 transition-colors"
              >
                <div className="flex items-start gap-3.5 min-w-0 flex-1">
                  <div
                    className="w-9 h-9 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[var(--text-secondary)] flex items-center justify-center font-mono text-[13px] font-medium shrink-0"
                    aria-hidden="true"
                  >
                    {initial}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mb-0.5">
                      <span className="text-[14px] font-medium text-[var(--text-primary)] truncate max-w-full">
                        {email.sender}
                      </span>
                      <span className="text-[11.5px] font-mono text-[var(--text-muted)] whitespace-nowrap">
                        {email.date}
                      </span>
                    </div>
                    <div className="text-[13.5px] text-[var(--text-primary)] truncate">{email.subject}</div>
                    {email.snippet && (
                      <div className="text-[12.5px] text-[var(--text-muted)] truncate mt-0.5">{email.snippet}</div>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 shrink-0 pl-12 sm:pl-0">
                  <button
                    type="button"
                    onClick={() => openPreview(email)}
                    className="h-8 px-3 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] hover:bg-black/5 dark:hover:bg-white/10 text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center gap-1.5 transition-colors cursor-pointer"
                  >
                    <Icon.Eye size={14} strokeWidth={1.5} aria-hidden="true" />
                    <span>Open</span>
                  </button>
                  <AppLink
                    href={`/analyze/${email.id}`}
                    className="h-8 px-3.5 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center gap-1.5 transition-colors"
                  >
                    <Icon.ScanSearch size={14} strokeWidth={1.5} aria-hidden="true" />
                    <span>Analyze</span>
                  </AppLink>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-16 px-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center">
          <Icon.Inbox size={32} strokeWidth={1.5} className="mx-auto text-[var(--text-muted)] mb-3" aria-hidden="true" />
          <h2 className="text-[16px] font-medium text-[var(--text-primary)]">
            {emails.length > 0 ? 'No matching emails' : 'No emails found'}
          </h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] max-w-sm mx-auto mt-1">
            {emails.length > 0
              ? 'Try clearing or adjusting your search query.'
              : 'Your inbox appears empty or messages could not be fetched from Gmail.'}
          </p>
        </div>
      )}

      {/* Slide-Over Email Preview Drawer */}
      {selectedEmail && (
        <div className="fixed inset-0 z-50 flex justify-end">
          <div
            className="fixed inset-0 bg-black/50"
            onClick={closePreview}
            aria-hidden="true"
          />
          <div
            role="dialog"
            aria-label="Email preview"
            className="relative z-10 w-full max-w-2xl bg-[var(--bg-card)] border-l border-[var(--border-hairline)] shadow-2xl flex flex-col h-full animate-surface-enter"
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-[var(--border-hairline)] flex items-start justify-between gap-4 shrink-0">
              <div className="min-w-0 space-y-1">
                <div className="text-[11.5px] font-mono text-[var(--text-muted)]">Email preview</div>
                <h2 className="text-[16px] font-medium text-[var(--text-primary)] leading-snug">
                  {selectedEmail.subject}
                </h2>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[12.5px] text-[var(--text-secondary)]">
                  <span>{selectedEmail.sender}</span>
                  <span className="font-mono text-[11.5px] text-[var(--text-muted)]">{selectedEmail.date}</span>
                </div>
              </div>
              <div className="flex items-center gap-2 shrink-0">
                <AppLink
                  href={`/analyze/${selectedEmail.id}`}
                  className="h-8 px-3 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[12.5px] font-medium inline-flex items-center gap-1.5 transition-colors"
                >
                  <Icon.ScanSearch size={14} strokeWidth={1.5} aria-hidden="true" />
                  <span>Analyze</span>
                </AppLink>
                <button
                  type="button"
                  onClick={closePreview}
                  aria-label="Close email preview"
                  className="h-8 w-8 inline-flex items-center justify-center rounded-lg border border-[var(--border-hairline)] text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-raised)] cursor-pointer"
                >
                  <Icon.X size={16} strokeWidth={1.5} />
                </button>
              </div>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-6 bg-[var(--bg-app)]">
              {previewLoading && (
                <div className="h-48 flex items-center justify-center text-[13px] font-mono text-[var(--text-muted)]">
                  Loading email content...
                </div>
              )}
              {previewError && (
                <div className="p-4 rounded-lg bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 text-[13px] text-red-700 dark:text-red-300">
                  Failed to load email: {previewError}
                </div>
              )}
              {previewData && !previewLoading && (
                <>
                  {previewData.body_html ? (
                    <iframe
                      title="Email content preview"
                      sandbox="allow-same-origin"
                      srcDoc={buildSandboxedHtml(previewData.body_html)}
                      className="w-full min-h-[480px] rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-card)]"
                    />
                  ) : previewData.body_text ? (
                    <pre className="whitespace-pre-wrap break-words text-[13.5px] leading-relaxed text-[var(--text-primary)] font-sans p-4 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)]">
                      {previewData.body_text}
                    </pre>
                  ) : (
                    <p className="text-center py-12 text-[13px] text-[var(--text-muted)]">
                      No email content available.
                    </p>
                  )}
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

