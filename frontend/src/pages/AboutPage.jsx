import React from 'react';
import { AppLink } from '../components/AppLink';
import { Icon } from '../components/Icons';
import { useApp } from '../context/AppContext';

export function AboutPage() {
  const { state } = useApp();
  const authenticated = Boolean(state?.config?.authenticated);

  const analyzers = [
    { name: 'Keyword analyzer', max: '25 pts', desc: 'Detects known phishing phrases such as verify your account, account suspended, or immediate action demands.' },
    { name: 'URL analyzer', max: '25 pts', desc: 'Flags shortened links, raw IP destinations, excessive subdomains, and mismatched anchor text.' },
    { name: 'Sender analyzer', max: '20 pts', desc: 'Identifies brand impersonation and corporate claims sent from free webmail domains.' },
    { name: 'Urgency analyzer', max: '15 pts', desc: 'Detects artificial time pressure, excessive capitalization, and alarming punctuation patterns.' },
    { name: 'Structure analyzer', max: '15 pts', desc: 'Evaluates structural cues including generic greetings, credential requests, and minimal body copy.' },
  ];

  const extensions = [
    { icon: Icon.QrCode, title: 'QR code detection', desc: 'Decodes QR codes inside image attachments to uncover hidden redirect URLs.' },
    { icon: Icon.Eye, title: 'Image OCR analysis', desc: 'Extracts text embedded inside images to catch filter-evasion payloads.' },
    { icon: Icon.Network, title: 'Header forensics', desc: 'Evaluates SPF, DKIM, and DMARC status alongside mail routing hops.' },
    { icon: Icon.Languages, title: 'Multilingual AI', desc: 'Detects non-English text and translates messages prior to rule inspection.' },
    { icon: Icon.Globe, title: 'Threat intelligence', desc: 'Cross-references extracted URLs with external threat feeds and heuristic blacklists.' },
    { icon: Icon.Activity, title: 'User risk profiling', desc: 'Tracks personal exposure trends over time using metadata only.' },
    { icon: Icon.GitBranch, title: 'Campaign detection', desc: 'Clusters related phishing emails via SimHash fingerprinting and Jaccard similarity.' },
    { icon: Icon.MessageSquare, title: 'AI security assistant', desc: 'Answers questions in report context with automatic PII redaction.' },
    { icon: Icon.GraduationCap, title: 'Training simulator', desc: 'Interactive phishing scenarios for safe offline security awareness practice.' },
  ];

  const ascendModules = [
    { title: 'Counterfactual reasoning', desc: 'Demonstrates what changes in each analyzer category would alter the final risk score.' },
    { title: 'Threat ontology', desc: 'Maps detected evidence indicators to structured intent and impact attack chains.' },
    { title: 'Psychological profiling', desc: 'Measures social engineering triggers including fear, urgency, reward, and authority.' },
    { title: 'Incident reporter', desc: 'Compiles structured executive reports with forensic evidence for high-risk emails.' },
    { title: 'Adaptive rule feedback', desc: 'Aggregates user feedback to propose advisory analyzer weight adjustments.' },
    { title: 'What-if sandbox', desc: 'Simulates custom analyzer weights in memory without modifying engine defaults.' },
  ];

  const stack = ['Python', 'Flask', 'React.js', 'Tailwind CSS', 'Gmail API', 'SQLite', 'OpenCV', 'Tesseract OCR', 'Gemini AI', 'Ascend Framework'];

  return (
    <div className="max-w-5xl mx-auto space-y-10 py-2">
      {/* Header */}
      <section className="p-6 sm:p-8 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-6">
        <div className="space-y-2">
          <div className="text-[12px] font-mono text-[var(--accent)]">System documentation</div>
          <h1 className="text-3xl font-medium tracking-tight text-[var(--text-primary)]">
            About PhishGuard
          </h1>
          <p className="text-[15px] leading-relaxed text-[var(--text-secondary)] max-w-3xl">
            PhishGuard is a rule-based, explainable phishing detection workbench that integrates with Gmail via OAuth 2.0.
            Every risk score is broken down by analyzer contribution, extracted evidence, and threat intent.
          </p>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
          {[
            { value: '5', label: 'Core analyzers' },
            { value: '12+', label: 'Extension modules' },
            { value: '0', label: 'Email bodies stored' },
            { value: '100%', label: 'Rule transparency' },
          ].map((stat) => (
            <div key={stat.label} className="p-4 rounded-lg bg-[var(--bg-app)] border border-[var(--border-hairline)]">
              <div className="text-2xl font-medium font-mono tabular-nums text-[var(--text-primary)]">
                {stat.value}
              </div>
              <div className="text-[12.5px] text-[var(--text-muted)] mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* 5-Point Detection Engine */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-medium text-[var(--text-primary)]">5-point detection engine</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] mt-1">
            Five independent analyzers contribute to an additive risk score out of 100
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {analyzers.map((a) => (
            <div key={a.name} className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-2">
              <div className="flex items-center justify-between gap-2">
                <h3 className="text-[15px] font-medium text-[var(--text-primary)]">{a.name}</h3>
                <span className="font-mono text-[12px] px-2 py-0.5 rounded bg-[var(--bg-raised)] text-[var(--text-secondary)] border border-[var(--border-hairline)]">
                  Max {a.max}
                </span>
              </div>
              <p className="text-[13px] leading-relaxed text-[var(--text-secondary)]">{a.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* v2 Extensions */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-medium text-[var(--text-primary)]">Advanced capability modules</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] mt-1">
            Specialized forensic, visual, and behavioral extensions
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {extensions.map((ext) => {
            const ExtIcon = ext.icon;
            return (
              <div key={ext.title} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-2">
                <div className="flex items-center gap-2">
                  <ExtIcon size={16} strokeWidth={1.5} className="text-[var(--accent)] shrink-0" aria-hidden="true" />
                  <h3 className="text-[14px] font-medium text-[var(--text-primary)]">{ext.title}</h3>
                </div>
                <p className="text-[13px] text-[var(--text-secondary)] leading-relaxed">{ext.desc}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* Ascend Research Layer */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-medium text-[var(--text-primary)]">Ascend framework</h2>
          <p className="text-[13.5px] text-[var(--text-secondary)] mt-1">
            Read-only interpretability, psychological profiling, and weight simulation tools
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {ascendModules.map((mod) => (
            <div key={mod.title} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-1.5">
              <h3 className="text-[14px] font-medium text-[var(--text-primary)]">{mod.title}</h3>
              <p className="text-[13px] text-[var(--text-secondary)] leading-relaxed">{mod.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Scoring Scale & Architecture */}
      <section className="p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] space-y-6">
        <h2 className="text-xl font-medium text-[var(--text-primary)]">Scoring thresholds</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-lg bg-emerald-50/70 dark:bg-emerald-500/10 border border-emerald-200 dark:border-emerald-500/20">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[13px] font-medium text-emerald-800 dark:text-emerald-300">Low risk</span>
              <span className="font-mono text-[13px] font-medium text-emerald-700 dark:text-emerald-400">0 - 33</span>
            </div>
            <p className="text-[12.5px] text-[var(--text-secondary)]">
              Message shows few or no suspicious indicators.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-amber-50/70 dark:bg-amber-500/10 border border-amber-200 dark:border-amber-500/20">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[13px] font-medium text-amber-800 dark:text-amber-300">Medium risk</span>
              <span className="font-mono text-[13px] font-medium text-amber-700 dark:text-amber-400">34 - 66</span>
            </div>
            <p className="text-[12.5px] text-[var(--text-secondary)]">
              Some suspicious signals detected; inspect carefully before acting.
            </p>
          </div>
          <div className="p-4 rounded-lg bg-red-50/70 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[13px] font-medium text-red-800 dark:text-red-300">High risk</span>
              <span className="font-mono text-[13px] font-medium text-red-700 dark:text-red-400">67 - 100</span>
            </div>
            <p className="text-[12.5px] text-[var(--text-secondary)]">
              Strong phishing characteristics identified; verify through independent channels.
            </p>
          </div>
        </div>

        <div className="pt-4 border-t border-[var(--border-hairline)] flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap gap-2">
            {stack.map((tech) => (
              <span
                key={tech}
                className="px-2.5 py-1 rounded-md bg-[var(--bg-raised)] border border-[var(--border-hairline)] font-mono text-[12px] text-[var(--text-secondary)]"
              >
                {tech}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-3">
            <AppLink
              href="/"
              className="h-9 px-4 rounded-lg border border-[var(--border-hairline)] bg-[var(--bg-raised)] text-[13px] font-medium text-[var(--text-primary)] inline-flex items-center"
            >
              Overview
            </AppLink>
            <AppLink
              href={authenticated ? '/inbox' : '/training'}
              className="h-9 px-4 rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white text-[13px] font-medium inline-flex items-center"
            >
              {authenticated ? 'Open inbox' : 'Training lab'}
            </AppLink>
          </div>
        </div>
      </section>
    </div>
  );
}

