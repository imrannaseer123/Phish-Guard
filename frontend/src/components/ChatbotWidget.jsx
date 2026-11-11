import React, { useEffect, useRef, useState } from 'react';
import { Icon } from './Icons';
import { useApp } from '../context/AppContext';

function renderSafeMarkdown(text) {
  if (!text) return null;
  const lines = String(text).split('\n');
  return lines.map((line, lineIdx) => {
    const isBullet = /^\s*[-*]\s+/.test(line);
    const cleanLine = isBullet ? line.replace(/^\s*[-*]\s+/, '') : line;
    const segments = cleanLine.split(/(\*\*.*?\*\*|`.*?`)/g);
    const rendered = segments.map((seg, i) => {
      if (seg.startsWith('**') && seg.endsWith('**')) {
        return <strong key={i} className="font-semibold">{seg.slice(2, -2)}</strong>;
      }
      if (seg.startsWith('`') && seg.endsWith('`')) {
        return (
          <code
            key={i}
            className="font-mono text-[11px] px-1 py-0.5 rounded bg-black/10 dark:bg-white/10"
          >
            {seg.slice(1, -1)}
          </code>
        );
      }
      return <React.Fragment key={i}>{seg}</React.Fragment>;
    });

    if (isBullet) {
      return (
        <div key={lineIdx} className="flex items-start gap-1.5 pl-1 mt-0.5">
          <span className="text-[var(--text-muted)] select-none">-</span>
          <span>{rendered}</span>
        </div>
      );
    }
    return (
      <div key={lineIdx} className={lineIdx > 0 && cleanLine ? 'mt-1' : ''}>
        {cleanLine ? rendered : <span className="block h-1.5" />}
      </div>
    );
  });
}

export function ChatbotWidget() {
  const { state } = useApp();
  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState('');
  const [sending, setSending] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      isUser: false,
      source: 'OpenClaw AI',
      text: 'I can explain risk scores, analyzer breakdown, or security concepts for the current view.',
    },
  ]);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      setTimeout(() => inputRef.current?.focus(), 60);
    }
  }, [isOpen, messages.length]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || sending) return;

    const userMsg = {
      id: `u-${Date.now()}`,
      isUser: true,
      source: 'You',
      text: trimmed,
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setSending(true);

    // Gather live page context (exact match with legacy .risk-score-value behavior + rich report props)
    const context = {};
    if (state?.page === 'report' && state?.props?.report) {
      context.risk_score = Math.round(state.props.report.risk_score || 0);
      context.risk_level = state.props.report.risk_level;
      context.intent = state.props.report.intent;
      if (state.props.findings_serialized) {
        context.findings = state.props.findings_serialized.slice(0, 8);
      }
    }

    try {
      const res = await fetch('/chatbot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: trimmed, context }),
      });
      const data = await res.json();
      if (!res.ok || data.error) {
        throw new Error(data.error || `Server error ${res.status}`);
      }
      setMessages((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          isUser: false,
          source: data.source || 'Assistant',
          text: data.response,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: `e-${Date.now()}`,
          isUser: false,
          source: 'System',
          text: 'Could not reach the security assistant endpoint. Check server logs or API key configuration.',
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col items-end gap-3">
      {isOpen && (
        <div
          role="dialog"
          aria-label="Security Assistant"
          className="w-[360px] max-w-[calc(100vw-2.5rem)] h-[440px] max-h-[calc(100vh-6rem)] flex flex-col rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] shadow-xl overflow-hidden animate-surface-enter"
        >
          {/* Header */}
          <div className="px-4 py-3 border-b border-[var(--border-hairline)] flex items-center justify-between bg-[var(--bg-raised)]">
            <div className="flex items-center gap-2.5">
              <Icon.Shield size={16} strokeWidth={1.5} className="text-[var(--accent)]" aria-hidden="true" />
              <div>
                <h3 className="text-[13px] font-medium text-[var(--text-primary)] leading-tight">
                  Security assistant
                </h3>
                <p className="text-[11px] font-mono text-[var(--text-muted)]">OpenClaw AI · PII redacted</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              aria-label="Close security assistant"
              className="p-1.5 rounded-lg text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
            >
              <Icon.X size={16} strokeWidth={1.5} />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-[var(--bg-app)]">
            {messages.map((m) => (
              <div
                key={m.id}
                className={`flex flex-col gap-1 max-w-[88%] ${m.isUser ? 'ml-auto items-end' : 'mr-auto items-start'}`}
              >
                <div
                  className={`px-3 py-2 rounded-lg text-[13px] leading-relaxed break-words ${
                    m.isUser
                      ? 'bg-[var(--accent)] text-white'
                      : 'bg-[var(--bg-card)] border border-[var(--border-hairline)] text-[var(--text-primary)]'
                  }`}
                >
                  {m.isUser ? m.text : renderSafeMarkdown(m.text)}
                </div>
                <span className="text-[11px] font-mono text-[var(--text-muted)] px-0.5">{m.source}</span>
              </div>
            ))}
            {sending && (
              <div className="flex flex-col gap-1 items-start max-w-[80%]">
                <div className="px-3 py-2 rounded-lg bg-[var(--bg-card)] border border-[var(--border-hairline)] text-[12px] text-[var(--text-muted)] font-mono">
                  Evaluating context...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form
            onSubmit={handleSubmit}
            className="p-3 bg-[var(--bg-card)] border-t border-[var(--border-hairline)] flex items-center gap-2"
          >
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about findings or risk score"
              disabled={sending}
              className="flex-1 h-9 px-3 rounded-lg bg-[var(--bg-raised)] border border-[var(--border-hairline)] text-[13px] text-[var(--text-primary)] placeholder-[var(--text-muted)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)]"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              aria-label="Send message"
              className="h-9 w-9 inline-flex items-center justify-center rounded-lg bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white disabled:opacity-40 transition-colors cursor-pointer"
            >
              <Icon.Send size={15} strokeWidth={1.5} />
            </button>
          </form>
        </div>
      )}

      <button
        type="button"
        onClick={() => setIsOpen((v) => !v)}
        aria-label={isOpen ? 'Close assistant' : 'Open security assistant'}
        className="h-11 px-3.5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-[var(--text-primary)] hover:bg-[var(--bg-raised)] shadow-md flex items-center gap-2 text-[13px] font-medium transition-colors cursor-pointer"
      >
        <Icon.MessageSquare size={16} strokeWidth={1.5} className="text-[var(--accent)]" aria-hidden="true" />
        <span>Assistant</span>
      </button>
    </div>
  );
}

