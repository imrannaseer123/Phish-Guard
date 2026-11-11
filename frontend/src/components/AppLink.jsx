import React from 'react';
import { useApp } from '../context/AppContext';

export function AppLink({ href, className = '', children, onClick, external = false, ...rest }) {
  const { navigate } = useApp();

  const handleClick = (e) => {
    if (onClick) onClick(e);
    if (e.defaultPrevented) return;
    if (
      external ||
      !href ||
      href.startsWith('http') ||
      href.startsWith('mailto:') ||
      href.startsWith('/auth') ||
      href.startsWith('/logout') ||
      href.startsWith('/export/') ||
      href.includes('/export') ||
      e.metaKey ||
      e.ctrlKey ||
      e.shiftKey ||
      e.altKey ||
      e.button !== 0
    ) {
      return;
    }
    e.preventDefault();
    navigate(href);
  };

  return (
    <a href={href} onClick={handleClick} className={className} {...rest}>
      {children}
    </a>
  );
}

