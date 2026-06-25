import React, { useCallback, useEffect, useState } from 'react';
import { Plus, Edit2, Trash2, Radio, PlusCircle, X } from 'lucide-react';
import { format } from 'date-fns';
import { matchesApi, streamsApi, teamsApi, tournamentsApi } from '../api';
import type { Match, Stream, Team, Tournament } from '../types';
import { ConfirmDialog, EmptyState, Modal, PageHeader, Spinner, StatusBadge } from '../components/UI';

const STATUSES = ['scheduled', 'live', 'halftime', 'finished', 'postponed', 'cancelled'] as const;
const STREAM_TYPES = ['hls', 'mp4', 'external', 'webapp'] as const;

const MatchesPage: React.FC = () => {
  const [matches, setMatches] = useState<Match[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  const [editMatch, setEditMatch] = useState<Match | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [streamsMatch, setStreamsMatch] = useState<Match | null>(null);
  const [filterStatus, setFilterStatus] = useState('');

  const load = useCallback(async () => {
    const params = filterStatus ? { status_filter: filterStatus } : {};
    const [m, t, tm] = await Promise.all([
      matchesApi.list(params), tournamentsApi.list(), teamsApi.list(),
    ]);
    setMatches(m.data); setTournaments(t.data); setTeams(tm.data);
    setLoading(false);
  }, [filterStatus]);

  useEffect(() => { load(); }, [load]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await matchesApi.delete(deleteTarget);
    setDeleteTarget(null);
    load();
  };

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader
        title="Matches"
        subtitle={`${matches.length} match${matches.length !== 1 ? 'es' : ''}`}
        actions={
          <>
            <select className="select w-44" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="">All statuses</option>
              {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
            <button className="btn-primary" onClick={() => setShowCreate(true)}>
              <Plus className="w-4 h-4" /> New Match
            </button>
          </>
        }
      />

      {matches.length === 0 ? (
        <EmptyState message="No matches yet. Create one to get started." icon="📅" />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                {['Match', 'Date', 'Tournament', 'Status', 'Score', 'Streams', ''].map(h => (
                  <th key={h} className="table-head pb-4 pr-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {matches.map(m => (
                <tr key={m.id} className="table-row">
                  <td className="py-3 pr-4">
                    <p className="font-medium text-white">{m.home_team?.name} vs {m.away_team?.name}</p>
                    <p className="text-xs text-gray-500">{m.venue || '—'} · {m.stage || '—'}</p>
                  </td>
                  <td className="py-3 pr-4 text-gray-300 whitespace-nowrap">
                    {format(new Date(m.match_date), 'dd MMM HH:mm')}
                  </td>
                  <td className="py-3 pr-4 text-gray-400">
                    {tournaments.find(t => t.id === m.tournament_id)?.name || '—'}
                  </td>
                  <td className="py-3 pr-4"><StatusBadge status={m.status} /></td>
                  <td className="py-3 pr-4 font-mono text-gray-300">
                    {m.home_score ?? '—'} – {m.away_score ?? '—'}
                  </td>
                  <td className="py-3 pr-4">
                    <button
                      className="text-brand-400 hover:text-brand-300 text-xs flex items-center gap-1"
                      onClick={() => setStreamsMatch(m)}
                    >
                      <Radio className="w-3 h-3" /> {m.streams?.length ?? 0}
                    </button>
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <button className="text-gray-400 hover:text-white" onClick={() => setEditMatch(m)}>
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button className="text-red-400 hover:text-red-300" onClick={() => setDeleteTarget(m.id)}>
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Create / Edit modal */}
      {(showCreate || editMatch) && (
        <MatchFormModal
          match={editMatch}
          tournaments={tournaments}
          teams={teams}
          onClose={() => { setShowCreate(false); setEditMatch(null); }}
          onSaved={() => { setShowCreate(false); setEditMatch(null); load(); }}
        />
      )}

      {/* Streams modal */}
      {streamsMatch && (
        <StreamsModal
          match={streamsMatch}
          onClose={() => setStreamsMatch(null)}
          onSaved={load}
        />
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        message="Delete this match? All streams and notifications will also be removed."
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
};

// ── Match Form ────────────────────────────────────────────────────────────

const MatchFormModal: React.FC<{
  match: Match | null;
  tournaments: Tournament[];
  teams: Team[];
  onClose: () => void;
  onSaved: () => void;
}> = ({ match, tournaments, teams, onClose, onSaved }) => {
  const [form, setForm] = useState({
    tournament_id: match?.tournament_id ?? (tournaments[0]?.id ?? 0),
    home_team_id:  match?.home_team_id  ?? (teams[0]?.id ?? 0),
    away_team_id:  match?.away_team_id  ?? (teams[1]?.id ?? 0),
    match_date:    match ? match.match_date.slice(0, 16) : '',
    venue:         match?.venue  ?? '',
    stage:         match?.stage  ?? '',
    thumbnail_url: match?.thumbnail_url ?? '',
    status:        match?.status ?? 'scheduled',
    home_score:    match?.home_score ?? '',
    away_score:    match?.away_score ?? '',
  });
  const [saving, setSaving] = useState(false);

  const set = (k: string, v: unknown) => setForm(f => ({ ...f, [k]: v }));

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = {
        ...form,
        tournament_id: Number(form.tournament_id),
        home_team_id:  Number(form.home_team_id),
        away_team_id:  Number(form.away_team_id),
        home_score:    form.home_score === '' ? null : Number(form.home_score),
        away_score:    form.away_score === '' ? null : Number(form.away_score),
      };
      if (match) await matchesApi.update(match.id, payload);
      else await matchesApi.create(payload);
      onSaved();
    } finally {
      setSaving(false);
    }
  };

  return (
    <Modal open title={match ? 'Edit Match' : 'New Match'} onClose={onClose} size="lg">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="label">Tournament</label>
          <select className="select" value={form.tournament_id} onChange={e => set('tournament_id', e.target.value)}>
            {tournaments.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Match Date (UTC)</label>
          <input className="input" type="datetime-local" value={form.match_date} onChange={e => set('match_date', e.target.value)} />
        </div>
        <div>
          <label className="label">Home Team</label>
          <select className="select" value={form.home_team_id} onChange={e => set('home_team_id', e.target.value)}>
            {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Away Team</label>
          <select className="select" value={form.away_team_id} onChange={e => set('away_team_id', e.target.value)}>
            {teams.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Venue</label>
          <input className="input" value={form.venue} onChange={e => set('venue', e.target.value)} placeholder="Stadium name" />
        </div>
        <div>
          <label className="label">Stage</label>
          <input className="input" value={form.stage} onChange={e => set('stage', e.target.value)} placeholder="Group A / Quarter Final …" />
        </div>
        <div>
          <label className="label">Status</label>
          <select className="select" value={form.status} onChange={e => set('status', e.target.value)}>
            {STATUSES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div>
          <label className="label">Thumbnail URL</label>
          <input className="input" value={form.thumbnail_url} onChange={e => set('thumbnail_url', e.target.value)} placeholder="https://…" />
        </div>
        <div>
          <label className="label">Home Score</label>
          <input className="input" type="number" min={0} value={form.home_score} onChange={e => set('home_score', e.target.value)} placeholder="—" />
        </div>
        <div>
          <label className="label">Away Score</label>
          <input className="input" type="number" min={0} value={form.away_score} onChange={e => set('away_score', e.target.value)} placeholder="—" />
        </div>
      </div>
      <div className="flex justify-end gap-3 mt-6">
        <button className="btn-secondary" onClick={onClose}>Cancel</button>
        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? <Spinner size="sm" /> : 'Save Match'}
        </button>
      </div>
    </Modal>
  );
};

// ── Streams Modal ─────────────────────────────────────────────────────────

const StreamsModal: React.FC<{
  match: Match;
  onClose: () => void;
  onSaved: () => void;
}> = ({ match, onClose, onSaved }) => {
  const [streams, setStreams] = useState<Stream[]>(match.streams ?? []);
  const [newStream, setNewStream] = useState({ language: '', quality: '1080p', stream_type: 'hls', url: '', sort_order: 0, is_active: true });
  const [adding, setAdding] = useState(false);

  const reloadStreams = async () => {
    const r = await matchesApi.getStreams(match.id);
    setStreams(r.data);
  };

  const handleAdd = async () => {
    setAdding(true);
    try { await matchesApi.addStream(match.id, newStream); await reloadStreams(); onSaved(); }
    finally { setAdding(false); }
  };

  const handleDelete = async (id: number) => {
    await streamsApi.delete(id); await reloadStreams(); onSaved();
  };

  const toggleActive = async (s: Stream) => {
    await streamsApi.update(s.id, { is_active: !s.is_active }); await reloadStreams();
  };

  return (
    <Modal open title={`Streams — ${match.home_team?.name} vs ${match.away_team?.name}`} onClose={onClose} size="lg">
      {/* Existing streams */}
      <div className="space-y-2 mb-6">
        {streams.length === 0 && <p className="text-gray-500 text-sm">No streams yet.</p>}
        {streams.map(s => (
          <div key={s.id} className="flex items-center justify-between bg-gray-800 rounded-lg px-4 py-3">
            <div className="flex items-center gap-3 min-w-0">
              <span className={`w-2 h-2 rounded-full flex-shrink-0 ${s.is_active ? 'bg-green-400' : 'bg-gray-500'}`} />
              <span className="font-medium text-white">{s.label}</span>
              <span className="text-xs text-gray-500 bg-gray-700 rounded px-2 py-0.5">{s.stream_type}</span>
              <span className="text-xs text-gray-400 truncate">{s.url}</span>
            </div>
            <div className="flex items-center gap-2 flex-shrink-0 ml-3">
              <button onClick={() => toggleActive(s)} className="text-xs text-gray-400 hover:text-white">
                {s.is_active ? 'Disable' : 'Enable'}
              </button>
              <button onClick={() => handleDelete(s.id)} className="text-red-400 hover:text-red-300">
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add new stream */}
      <div className="border-t border-gray-800 pt-5">
        <p className="text-sm font-semibold text-gray-300 mb-3 flex items-center gap-2">
          <PlusCircle className="w-4 h-4 text-brand-400" /> Add Stream
        </p>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">Language</label>
            <input className="input" placeholder="English / Arabic / Hindi …" value={newStream.language}
              onChange={e => setNewStream(s => ({ ...s, language: e.target.value }))} />
          </div>
          <div>
            <label className="label">Quality</label>
            <input className="input" placeholder="1080p / 720p / 480p" value={newStream.quality}
              onChange={e => setNewStream(s => ({ ...s, quality: e.target.value }))} />
          </div>
          <div>
            <label className="label">Type</label>
            <select className="select" value={newStream.stream_type}
              onChange={e => setNewStream(s => ({ ...s, stream_type: e.target.value }))}>
              {STREAM_TYPES.map(t => <option key={t} value={t}>{t.toUpperCase()}</option>)}
            </select>
          </div>
          <div>
            <label className="label">Sort Order</label>
            <input className="input" type="number" value={newStream.sort_order}
              onChange={e => setNewStream(s => ({ ...s, sort_order: Number(e.target.value) }))} />
          </div>
          <div className="col-span-2">
            <label className="label">Stream URL</label>
            <input className="input" placeholder="https://…" value={newStream.url}
              onChange={e => setNewStream(s => ({ ...s, url: e.target.value }))} />
          </div>
        </div>
        <div className="flex justify-end mt-4">
          <button className="btn-primary" onClick={handleAdd} disabled={adding || !newStream.language || !newStream.url}>
            {adding ? <Spinner size="sm" /> : <><PlusCircle className="w-4 h-4" /> Add Stream</>}
          </button>
        </div>
      </div>
    </Modal>
  );
};

export default MatchesPage;
