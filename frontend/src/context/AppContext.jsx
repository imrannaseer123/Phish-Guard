import React, { createContext, useCallback, useContext, useEffect, useState } from 'react';

const AppContext = createContext(null);

function readInitialData() {
  const el = document.getElementById('__PHISHGUARD_DATA__');
  if (!el) {
    return {
      page: 'home',
      path: window.location.pathname,
      title: 'PhishGuard',
      props: {},
      flash: [],
      config: { authenticated: false, ENABLE_CHATBOT: true, ASCEND_ENABLED: true },
    };
  }
  try {
    return JSON.parse(el.textContent || '{}');
  } catch {
    return {
      page: 'home',
      path: '/',
      title: 'PhishGuard',
      props: {},
      flash: [],
      config: { authenticated: false, ENABLE_CHATBOT: true, ASCEND_ENABLED: true },
    };
  }
}

function stripLeadingEmojis(str) {
  if (typeof str !== 'string') return str;
  return str.replace(/^[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{2705}\u{26A0}\u{FE0F}\s]+/u, '').trim();
}

export function AppProvider({ children }) {
  const [state, setState] = useState(() => readInitialData());
  const [loading, setLoading] = useState(false);
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem('phishguard-theme') || 'dark';
    } catch {
      return 'dark';
    }
  });
  const [toasts, setToasts] = useState([]);
  const [flashes, setFlashes] = useState(() =>
    (readInitialData().flash || []).map((f, idx) => ({
      id: `init-${idx}`,
      category: f.category,
      message: stripLeadingEmojis(f.message),
    }))
  );

  // Sync theme on html element
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'light') {
      root.classList.remove('dark');
      root.setAttribute('data-theme', 'light');
    } else {
      root.classList.add('dark');
      root.setAttribute('data-theme', 'dark');
    }
    try {
      localStorage.setItem('phishguard-theme', theme);
    } catch {}
  }, [theme]);

  // Update document title on state changes
  useEffect(() => {
    if (state?.title) {
      document.title = state.title;
    }
  }, [state?.title]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const showToast = useCallback((message, type = 'info') => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    const cleanMessage = stripLeadingEmojis(message);
    setToasts((prev) => [...prev, { id, message: cleanMessage, type }]);
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3600);
  }, []);

  const dismissFlash = useCallback((id) => {
    setFlashes((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const applyResponsePayload = useCallback((data, pushHistory = true) => {
    if (!data || !data.page) return;
    setState(data);
    if (Array.isArray(data.flash) && data.flash.length > 0) {
      setFlashes(
        data.flash.map((f, idx) => ({
          id: `${Date.now()}-${idx}`,
          category: f.category,
          message: stripLeadingEmojis(f.message),
        }))
      );
    } else {
      setFlashes([]);
    }

    if (pushHistory && data.path && window.location.pathname !== data.path) {
      window.history.pushState({ path: data.path }, '', data.path);
    }
    window.scrollTo({ top: 0, behavior: 'instant' });
  }, []);

  const navigate = useCallback(
    async (targetUrl, { push = true } = {}) => {
      if (!targetUrl) return;
      // Full browser navigation for OAuth and file exports
      if (
        targetUrl.startsWith('/auth') ||
        targetUrl.startsWith('/logout') ||
        targetUrl.startsWith('/export/') ||
        targetUrl.includes('/export')
      ) {
        window.location.href = targetUrl;
        return;
      }

      setLoading(true);
      try {
        const res = await fetch(targetUrl, {
          headers: {
            'X-PhishGuard-SPA': '1',
            Accept: 'application/json',
          },
        });
        const contentType = res.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
          window.location.href = targetUrl;
          return;
        }
        const data = await res.json();
        if (push && data.path) {
          const dest = data.path;
          if (window.location.pathname !== dest) {
            window.history.pushState({ path: dest }, '', dest);
          }
        }
        applyResponsePayload(data, false);
      } catch (err) {
        showToast(`Navigation error: ${err.message}`, 'error');
      } finally {
        setLoading(false);
      }
    },
    [applyResponsePayload, showToast]
  );

  const submitForm = useCallback(
    async (actionUrl, formData) => {
      setLoading(true);
      try {
        const res = await fetch(actionUrl, {
          method: 'POST',
          headers: {
            'X-PhishGuard-SPA': '1',
            Accept: 'application/json',
          },
          body: formData,
        });
        const contentType = res.headers.get('content-type') || '';
        if (!contentType.includes('application/json')) {
          window.location.href = actionUrl;
          return null;
        }
        const data = await res.json();
        if (data.path && window.location.pathname !== data.path) {
          window.history.pushState({ path: data.path }, '', data.path);
        }
        applyResponsePayload(data, false);
        return data;
      } catch (err) {
        showToast(`Request failed: ${err.message}`, 'error');
        return null;
      } finally {
        setLoading(false);
      }
    },
    [applyResponsePayload, showToast]
  );

  // Handle browser back / forward buttons
  useEffect(() => {
    const onPopState = () => {
      navigate(window.location.pathname + window.location.search, { push: false });
    };
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, [navigate]);

  return (
    <AppContext.Provider
      value={{
        state,
        loading,
        theme,
        toggleTheme,
        navigate,
        submitForm,
        toasts,
        showToast,
        flashes,
        dismissFlash,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used inside AppProvider');
  return ctx;
}

