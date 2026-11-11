import React from 'react';
import { AppShell } from './components/AppShell';
import { ErrorBoundary } from './components/ErrorBoundary';
import { AppProvider, useApp } from './context/AppContext';
import { AboutPage } from './pages/AboutPage';
import { AdminWeightsPage } from './pages/AdminWeightsPage';
import { AscendDashboardPage } from './pages/AscendDashboardPage';
import { CampaignsPage } from './pages/CampaignsPage';
import { DashboardPage } from './pages/DashboardPage';
import { HistoryPage } from './pages/HistoryPage';
import { HomePage } from './pages/HomePage';
import { InboxPage } from './pages/InboxPage';
import { IncidentReportPage } from './pages/IncidentReportPage';
import { ReportPage } from './pages/ReportPage';
import { RiskProfilePage } from './pages/RiskProfilePage';
import { TrainingPage } from './pages/TrainingPage';
import { WhatIfPage } from './pages/WhatIfPage';

function PageRouter() {
  const { state } = useApp();
  const page = state?.page || 'home';

  switch (page) {
    case 'home':
      return <HomePage />;
    case 'about':
      return <AboutPage />;
    case 'inbox':
      return <InboxPage />;
    case 'report':
      return <ReportPage />;
    case 'history':
      return <HistoryPage />;
    case 'admin':
      return <AdminWeightsPage />;
    case 'dashboard':
      return <DashboardPage />;
    case 'campaigns':
      return <CampaignsPage />;
    case 'risk_profile':
      return <RiskProfilePage />;
    case 'training':
      return <TrainingPage />;
    case 'ascend_dashboard':
      return <AscendDashboardPage />;
    case 'whatif':
      return <WhatIfPage />;
    case 'incident_report':
      return <IncidentReportPage />;
    default:
      return <HomePage />;
  }
}

export default function App() {
  return (
    <AppProvider>
      <AppShell>
        <ErrorBoundary>
          <PageRouter />
        </ErrorBoundary>
      </AppShell>
    </AppProvider>
  );
}

