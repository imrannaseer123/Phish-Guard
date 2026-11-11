import React, { useState } from 'react';
import { AppLink } from './AppLink';
import { Icon } from './Icons';
import { ChatbotWidget } from './ChatbotWidget';
import { useApp } from '../context/AppContext';

export function AppShell({ children }) {
  const { state, loading, theme, toggleTheme, toasts, flashes, dismissFlash } = useApp();
  const [mobileOpen, setMobileOpen] = useState(false);

  const currentPage = state?.page || 'home';
  const currentPath = state?.path || '/';
  const config = state?.config || {};
  const authenticated = Boolean(config.authenticated);
  const ascendEnabled = Boolean(config.ASCEND_ENABLED);
  const chatbotEnabled = Boolean(config.ENABLE_CHATBOT);

  const navSections = [
    {
      label: 'Workspace',
      items: [
        { label: 'Overview', href: '/', match: (p) => p === 'home', icon: Icon.Home },
        { label: 'Inbox', href: '/inbox', match: (p) => p === 'inbox', icon: Icon.Inbox },
        { label: 'History', href: '/history', match: (p) => p === 'history', icon: Icon.History },
        { label: 'Security dashboard', href: '/dashboard', match: (p) => p === 'dashboard', icon: Icon.BarChart3 },
      ],
    },
    {
      label: 'Threat intelligence',
      items: [
        { label: 'Campaigns', href: '/campaigns', match: (p) => p === 'campaigns', icon: Icon.Network },
        { label: 'Risk profile', href: '/risk-profile', match: (p) => p === 'risk_profile', icon: Icon.UserCheck },
        { label: 'Training lab', href: '/training', match: (p) => p === 'training', icon: Icon.GraduationCap },
      ],
    },
    {
      label: 'Governance',
      items: [
        { label: 'Weight advisor', href: '/admin/weights', match: (p) => p === 'admin', icon: Icon.Scale },
        ...(ascendEnabled
          ? [
              { label: 'Ascend console', href: '/ascend/dashboard', match: (p) => p === 'ascend_dashboard', icon: Icon.FlaskConical },
              { label: 'What-if sandbox', href: '/ascend/whatif', match: (p) => p === 'whatif', icon: Icon.SlidersHorizontal },
            ]
          : []),
        { label: 'Documentation', href: '/about', match: (p) => p === 'about', icon: Icon.BookOpen },
      ],
    },
  ];

  const pageLabelMap = {
    home: 'Overview',
    inbox: 'Inbox inspection',
    report: 'Forensic report',
    history: 'Analysis history',
    dashboard: 'Security dashboard',
    campaigns: 'Campaign clusters',
    risk_profile: 'User risk profile',
    training: 'Training simulation',
    admin: 'Weight advisor',
    ascend_dashboard: 'Ascend framework',
    whatif: 'What-if sandbox',
    incident_report: 'Incident report',
    about: 'System architecture',
  };

  const renderSidebarBody = (onNavigateClose) => (
    <div className="flex flex-col h-full">
      {/* Brand header */}
      <div className="h-14 px-4 flex items-center justify-between border-b border-[var(--border-hairline)] shrink-0">
        <AppLink
          href="/"
          onClick={onNavigateClose}
          className="flex items-center gap-2.5 text-[15px] font-medium tracking-tight text-[var(--text-primary)]"
        >
          <span className="w-7 h-7 rounded-lg bg-[var(--accent)] text-white flex items-center justify-center shrink-0">
            <Icon.Shield size={15} strokeWidth={1.75} aria-hidden="true" />
          </span>
          <span>PhishGuard</span>
        </AppLink>
        {onNavigateClose && (
          <button
            type="button"
            onClick={onNavigateClose}
            aria-label="Close navigation"
            className="lg:hidden p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] cursor-pointer"
          >
            <Icon.X size={16} strokeWidth={1.5} />
          </button>
        )}
      </div>

      {/* Navigation groups */}
      <nav aria-label="Primary navigation" className="flex-1 overflow-y-auto px-3 py-4">
        {navSections.map((section, sIdx) => (
          <div key={section.label} className={sIdx === 0 ? '' : 'mt-6'}>
            <div className="px-2.5 mb-2 text-[12px] font-medium text-[var(--text-muted)]">
              {section.label}
            </div>
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const ItemIcon = item.icon;
                const active = item.match(currentPage, currentPath);
                return (
                  <AppLink
                    key={item.href}
                    href={item.href}
                    onClick={onNavigateClose}
                    aria-current={active ? 'page' : undefined}
                    className={`h-9 px-2.5 rounded-lg flex items-center gap-2.5 text-[13.5px] transition-colors ${
                      active
                        ? 'bg-[var(--bg-raised)] text-[var(--text-primary)] font-medium border border-[var(--border-hairline)]'
                        : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-black/[0.03] dark:hover:bg-white/[0.03] border border-transparent'
                    }`}
                  >
                    <ItemIcon
                      size={16}
                      strokeWidth={1.5}
                      className={`shrink-0 ${active ? 'text-[var(--accent)]' : 'text-[var(--text-muted)]'}`}
                      aria-hidden="true"
                    />
                    <span className="truncate">{item.label}</span>
                  </AppLink>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* Account / OAuth Connection Footer */}
      <div className="p-3 border-t border-[var(--border-hairline)] shrink-0">
        <div className="p-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)]">
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-2 min-w-0">
              <span
                className={`w-2 h-2 rounded-full shrink-0 ${
                  authenticated ? 'bg-emerald-500' : 'bg-slate-400 dark:bg-slate-600'
                }`}
                aria-hidden="true"
              />
              <span className="text-[12.5px] font-medium text-[var(--text-primary)] truncate">
                {authenticated ? 'Gmail connected' : 'Gmail offline'}
              </span>
            </div>
            {authenticated ? (
              <a
                href="/logout"
                title="Disconnect Gmail session"
                className="inline-flex items-center gap-1 text-[12px] text-red-600 dark:text-red-400 hover:underline shrink-0"
              >
                <Icon.LogOut size={13} strokeWidth={1.5} aria-hidden="true" />
                <span>Logout</span>
              </a>
            ) : (
              <a
                href="/auth"
                className="text-[12px] font-medium text-[var(--accent)] hover:underline shrink-0"
              >
                Connect
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex bg-[var(--bg-app)] text-[var(--text-primary)]">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:block w-[248px] shrink-0 bg-[var(--bg-sidebar)] border-r border-[var(--border-hairline)] sticky top-0 h-screen">
        {renderSidebarBody(null)}
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div
            className="fixed inset-0 bg-black/50"
            onClick={() => setMobileOpen(false)}
            aria-hidden="true"
          />
          <aside className="relative z-10 w-[264px] max-w-[85vw] bg-[var(--bg-sidebar)] border-r border-[var(--border-hairline)] h-full">
            {renderSidebarBody(() => setMobileOpen(false))}
          </aside>
        </div>
      )}

      {/* Main Column */}
      <div className="flex-1 min-w-0 flex flex-col">
        {/* Quiet Top Bar */}
        <header className="h-14 px-4 sm:px-6 border-b border-[var(--border-hairline)] bg-[var(--bg-card)]/90 backdrop-blur-sm sticky top-0 z-30 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <button
              type="button"
              onClick={() => setMobileOpen(true)}
              aria-label="Open navigation menu"
              className="lg:hidden p-2 -ml-2 rounded-lg text-[var(--text-secondary)] hover:bg-[var(--bg-raised)] cursor-pointer"
            >
              <Icon.Menu size={18} strokeWidth={1.5} />
            </button>
            <div className="flex items-center gap-2 text-[13.5px] min-w-0">
              <span className="text-[var(--text-muted)] hidden sm:inline">PhishGuard</span>
              <span className="text-[var(--text-muted)] hidden sm:inline">/</span>
              <span className="font-medium text-[var(--text-primary)] truncate">
                {pageLabelMap[currentPage] || 'Console'}
              </span>
            </div>
            {loading && (
              <span className="text-[12px] font-mono text-[var(--text-muted)] ml-2">Loading...</span>
            )}
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {authenticated ? (
              <AppLink
                href="/inbox"
                className="hidden sm:inline-flex items-center gap-1.5 h-8 px-3 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium transition-colors"
              >
                <Icon.Mail size={14} strokeWidth={1.5} aria-hidden="true" />
                <span>Open inbox</span>
              </AppLink>
            ) : (
              <a
                href="/auth"
                className="hidden sm:inline-flex items-center gap-1.5 h-8 px-3 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium transition-colors"
              >
                <Icon.Link2 size={14} strokeWidth={1.5} aria-hidden="true" />
                <span>Connect Gmail</span>
              </a>
            )}
            <button
              type="button"
              onClick={toggleTheme}
              aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
              className="h-8 w-8 inline-flex items-center justify-center rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors cursor-pointer"
            >
              {theme === 'dark' ? (
                <Icon.Sun size={15} strokeWidth={1.5} />
              ) : (
                <Icon.Moon size={15} strokeWidth={1.5} />
              )}
            </button>
          </div>
        </header>

        {/* Flash Messages */}
        {flashes.length > 0 && (
          <div className="max-w-[1440px] w-full mx-auto px-4 sm:px-6 lg:px-8 pt-4 space-y-2">
            {flashes.map((f) => {
              const isSuccess = f.category === 'success';
              const isWarning = f.category === 'warning';
              return (
                <div
                  key={f.id}
                  role="alert"
                  className={`px-4 py-3 rounded-lg border flex items-center justify-between gap-3 text-[13px] ${
                    isSuccess
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-800 dark:bg-emerald-500/10 dark:border-emerald-500/20 dark:text-emerald-300'
                      : isWarning
                      ? 'bg-amber-50 border-amber-200 text-amber-800 dark:bg-amber-500/10 dark:border-amber-500/20 dark:text-amber-300'
                      : 'bg-red-50 border-red-200 text-red-800 dark:bg-red-500/10 dark:border-red-500/20 dark:text-red-300'
                  }`}
                >
                  <div className="flex items-center gap-2.5">
                    {isSuccess ? (
                      <Icon.CheckCircle2 size={16} strokeWidth={1.5} className="shrink-0" aria-hidden="true" />
                    ) : (
                      <Icon.AlertTriangle size={16} strokeWidth={1.5} className="shrink-0" aria-hidden="true" />
                    )}
                    <span>{f.message}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => dismissFlash(f.id)}
                    aria-label="Dismiss alert"
                    className="p-1 opacity-70 hover:opacity-100 cursor-pointer"
                  >
                    <Icon.X size={15} strokeWidth={1.5} />
                  </button>
                </div>
              );
            })}
          </div>
        )}

        {/* Main Content Area */}
        <main className="flex-1 w-full max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div key={currentPage + currentPath} className="animate-surface-enter">
            {children}
          </div>
        </main>

        {/* Quiet Footer */}
        <footer className="border-t border-[var(--border-hairline)] px-4 sm:px-6 lg:px-8 py-4 text-[12px] text-[var(--text-muted)] flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>PhishGuard — Explainable phishing email risk analyzer</span>
          <span className="font-mono">Read-only Gmail OAuth · Local SQLite telemetry</span>
        </footer>
      </div>

      {/* Toast Stack */}
      {toasts.length > 0 && (
        <div
          aria-live="polite"
          className="fixed bottom-5 left-5 z-50 flex flex-col gap-2 pointer-events-none"
        >
          {toasts.map((t) => (
            <div
              key={t.id}
              className={`pointer-events-auto flex items-center gap-2.5 px-4 py-2.5 rounded-lg border shadow-lg text-[13px] font-medium bg-[var(--bg-card)] ${
                t.type === 'success'
                  ? 'border-emerald-300 dark:border-emerald-500/30 text-emerald-700 dark:text-emerald-300'
                  : t.type === 'error'
                  ? 'border-red-300 dark:border-red-500/30 text-red-700 dark:text-red-300'
                  : 'border-[var(--border-hairline)] text-[var(--text-primary)]'
              }`}
            >
              {t.type === 'success' ? (
                <Icon.CheckCircle2 size={15} strokeWidth={1.5} aria-hidden="true" />
              ) : t.type === 'error' ? (
                <Icon.XCircle size={15} strokeWidth={1.5} aria-hidden="true" />
              ) : (
                <Icon.Info size={15} strokeWidth={1.5} aria-hidden="true" />
              )}
              <span>{t.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Floating Chatbot */}
      {chatbotEnabled && <ChatbotWidget />}
    </div>
  );
}

