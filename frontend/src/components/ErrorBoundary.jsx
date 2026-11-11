import React from 'react';
import { Icon } from './Icons';

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-lg mx-auto my-12 p-6 rounded-xl bg-[var(--bg-card)] border border-[var(--border-hairline)] text-center space-y-3">
          <Icon.AlertTriangle size={28} strokeWidth={1.5} className="mx-auto text-red-500" aria-hidden="true" />
          <h2 className="text-[16px] font-medium text-[var(--text-primary)]">View rendering error</h2>
          <p className="text-[13px] text-[var(--text-secondary)]">
            {this.state.error?.message || 'An unexpected interface error occurred.'}
          </p>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="h-9 px-4 rounded-lg bg-[var(--accent)] text-white text-[13px] font-medium cursor-pointer"
          >
            Reload page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

