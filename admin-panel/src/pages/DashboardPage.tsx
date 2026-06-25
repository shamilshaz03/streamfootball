import React, { useEffect, useState } from 'react';
import { Users, Tv2, Bell, Trophy, Radio, Calendar } from 'lucide-react';
import { dashboardApi, matchesApi } from '../api';
import type { DashboardMetrics, Match } from '../types';
import { Spinner, StatusBadge, PageHeader } from '../components/UI';

const MetricCard: React.FC<{
  label: string; value: number; icon: React.ReactNode; accent: string;
}> = ({ label, value, icon, accent }) => (
  <div className="card flex items-center gap-5">
    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${accent}`}>
      {icon}
    </div>
    <div>
      <p className="text-3xl font-bold text-white">{value.toLocaleString()}</p>
      <p className="text-sm text-gray-400">{label}</p>
    </div>
  </div>
);

const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [liveMatches, setLiveMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([dashboardApi.metrics(), matchesApi.list({ status_filter: 'live' })])
      .then(([m, l]) => { setMetrics(m.data); setLiveMatches(l.data); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex-1 flex items-center justify-center">
      <Spinner size="lg" />
    </div>
  );

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Dashboard" subtitle="Platform overview at a glance" />

      {metrics && (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-5 mb-10">
          <MetricCard label="Total Users"         value={metrics.total_users}            icon={<Users className="w-6 h-6 text-blue-400" />}   accent="bg-blue-500/20" />
          <MetricCard label="Live Matches"         value={metrics.live_matches}           icon={<Radio className="w-6 h-6 text-red-400" />}    accent="bg-red-500/20" />
          <MetricCard label="Today's Matches"      value={metrics.upcoming_matches_today} icon={<Calendar className="w-6 h-6 text-green-400" />} accent="bg-green-500/20" />
          <MetricCard label="Active Notifications" value={metrics.active_notifications}   icon={<Bell className="w-6 h-6 text-yellow-400" />}  accent="bg-yellow-500/20" />
          <MetricCard label="Total Streams"        value={metrics.total_streams}          icon={<Tv2 className="w-6 h-6 text-purple-400" />}   accent="bg-purple-500/20" />
          <MetricCard label="Active Tournaments"   value={metrics.total_tournaments}      icon={<Trophy className="w-6 h-6 text-brand-400" />} accent="bg-brand-500/20" />
        </div>
      )}

      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
          <Radio className="w-5 h-5 text-red-400" />
          Currently Live
        </h2>
        {liveMatches.length === 0 ? (
          <p className="text-gray-500 text-sm py-6 text-center">No live matches right now.</p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                <th className="table-head pb-3">Match</th>
                <th className="table-head pb-3">Score</th>
                <th className="table-head pb-3">Status</th>
                <th className="table-head pb-3">Streams</th>
              </tr>
            </thead>
            <tbody>
              {liveMatches.map((m) => (
                <tr key={m.id} className="table-row">
                  <td className="py-3 pr-4 font-medium text-white">
                    {m.home_team?.name} vs {m.away_team?.name}
                  </td>
                  <td className="py-3 pr-4 text-gray-300 font-mono">
                    {m.home_score ?? '—'} – {m.away_score ?? '—'}
                  </td>
                  <td className="py-3 pr-4"><StatusBadge status={m.status} /></td>
                  <td className="py-3 text-gray-400">{m.streams?.length ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
