import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './hooks/useAuth';
import { LoadingSpinner } from './components/ui/LoadingSpinner';

// Layout & Shared
import { AppLayout } from './components/layout/AppLayout';

// Public Pages
import { SplashScreen } from './pages/Splash/SplashScreen';
import { OverviewPage } from './pages/Overview/OverviewPage';
import { LoginPage } from './pages/Auth/LoginPage';
import { RegisterPage } from './pages/Auth/RegisterPage';

// Protected App Pages
import { DashboardPage } from './pages/Dashboard/DashboardPage';
import { TelemetryPage } from './pages/Telemetry/TelemetryPage';
import { GISPage } from './pages/GIS/GISPage';
import { NodesPage } from './pages/Nodes/NodesPage';
import { NodeDetailPage } from './pages/Nodes/NodeDetailPage';
import { AlertsPage } from './pages/Alerts/AlertsPage';
import { AlertDetailPage } from './pages/Alerts/AlertDetailPage';
import { AIAnalyticsPage } from './pages/AIAnalytics/AIAnalyticsPage';
import { NetworkPage } from './pages/Network/NetworkPage';
import { GatewayPage } from './pages/Gateway/GatewayPage';
import { ReportsPage } from './pages/Reports/ReportsPage';
import { SystemHealthPage } from './pages/Health/SystemHealthPage';
import { NotificationsPage } from './pages/Notifications/NotificationsPage';
import { SettingsPage } from './pages/Settings/SettingsPage';

interface RouteProps {
  children: React.ReactElement;
}

const ProtectedRoute: React.FC = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <LoadingSpinner size="lg" label="Authenticating session..." />
      </div>
    );
  }

  // Dev bypass / production fallback
  if (!user && !localStorage.getItem('auth_token') && process.env.NODE_ENV === 'production') {
    return <Navigate to="/login" replace />;
  }

  return <AppLayout />;
};

const PublicOnlyRoute: React.FC<RouteProps> = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <LoadingSpinner size="lg" label="Loading..." />
      </div>
    );
  }

  if (user) {
    return <Navigate to="/app/dashboard" replace />;
  }

  return children;
};

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* Entry / Splash */}
        <Route path="/" element={<SplashScreen />} />

        {/* Public Marketing & Information */}
        <Route path="/overview" element={<OverviewPage />} />

        {/* Public Auth */}
        <Route
          path="/login"
          element={
            <PublicOnlyRoute>
              <LoginPage />
            </PublicOnlyRoute>
          }
        />
        <Route
          path="/register"
          element={
            <PublicOnlyRoute>
              <RegisterPage />
            </PublicOnlyRoute>
          }
        />

        {/* Protected App Routes */}
        <Route path="/app" element={<ProtectedRoute />}>
          <Route index element={<Navigate to="/app/dashboard" replace />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="telemetry" element={<TelemetryPage />} />
          <Route path="gis" element={<GISPage />} />
          <Route path="nodes" element={<NodesPage />} />
          <Route path="nodes/:nodeId" element={<NodeDetailPage />} />
          <Route path="alerts" element={<AlertsPage />} />
          <Route path="alerts/:alertId" element={<AlertDetailPage />} />
          <Route path="ai" element={<AIAnalyticsPage />} />
          <Route path="network" element={<NetworkPage />} />
          <Route path="gateway" element={<GatewayPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="health" element={<SystemHealthPage />} />
          <Route path="notifications" element={<NotificationsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/overview" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
