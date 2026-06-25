import React from 'react';
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import Sidebar from './components/Sidebar';
import { Spinner } from './components/UI';

import LoginPage     from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import MatchesPage   from './pages/MatchesPage';
import StreamsPage   from './pages/StreamsPage';
import {
  HighlightsPage, NotificationsPage, TournamentsPage,
  AdminUsersPage, AuditLogsPage, SettingsPage,
} from './pages/OtherPages';

const AdminLayout: React.FC = () => (
  <div className="flex h-full overflow-hidden">
    <Sidebar />
    <main className="flex-1 flex flex-col overflow-hidden">
      <Routes>
        <Route path="/"              element={<DashboardPage />} />
        <Route path="/matches"       element={<MatchesPage />} />
        <Route path="/streams"       element={<StreamsPage />} />
        <Route path="/highlights"    element={<HighlightsPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/tournaments"   element={<TournamentsPage />} />
        <Route path="/admin-users"   element={<AdminUsersPage />} />
        <Route path="/audit-logs"    element={<AuditLogsPage />} />
        <Route path="/settings"      element={<SettingsPage />} />
        <Route path="*"              element={<Navigate to="/" replace />} />
      </Routes>
    </main>
  </div>
);

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { admin, loading } = useAuth();
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950">
      <Spinner size="lg" />
    </div>
  );
  return admin ? <>{children}</> : <Navigate to="/login" replace />;
};

const App: React.FC = () => (
  <AuthProvider>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/*" element={
          <ProtectedRoute>
            <AdminLayout />
          </ProtectedRoute>
        } />
      </Routes>
    </BrowserRouter>
  </AuthProvider>
);

export default App;
