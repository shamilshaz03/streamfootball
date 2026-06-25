// ── Highlights Page ───────────────────────────────────────────────────────
import React, { useCallback, useEffect, useState } from 'react';
import { Plus, Trash2, ExternalLink } from 'lucide-react';
import { format } from 'date-fns';
import { highlightsApi, matchesApi } from '../api';
import type { Highlight, Match } from '../types';
import { ConfirmDialog, EmptyState, Modal, PageHeader, Spinner } from '../components/UI';

export const HighlightsPage: React.FC = () => {
  const [highlights, setHighlights] = useState<Highlight[]>([]);
  const [matches, setMatches] = useState<Match[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [form, setForm] = useState({ match_id: 0, youtube_url: '', title: '' });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    const [h, m] = await Promise.all([highlightsApi.list(), matchesApi.list({ status_filter: 'finished' })]);
    setHighlights(h.data); setMatches(m.data); setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const matchName = (id: number) => {
    const m = matches.find(m => m.id === id);
    return m ? `${m.home_team?.name} vs ${m.away_team?.name}` : `Match #${id}`;
  };

  const handleSave = async () => {
    setSaving(true);
    try { await highlightsApi.create({ ...form, match_id: Number(form.match_id) }); setShowCreate(false); load(); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await highlightsApi.delete(deleteTarget); setDeleteTarget(null); load();
  };

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Highlights" subtitle="YouTube highlight links"
        actions={<button className="btn-primary" onClick={() => setShowCreate(true)}><Plus className="w-4 h-4" /> Add Highlight</button>} />
      {highlights.length === 0 ? <EmptyState message="No highlights yet." icon="🎬" /> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                {['Match', 'Title', 'URL', 'Added', ''].map(h => (
                  <th key={h} className="table-head pb-4 pr-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {highlights.map(h => (
                <tr key={h.id} className="table-row">
                  <td className="py-3 pr-4 text-white font-medium">{matchName(h.match_id)}</td>
                  <td className="py-3 pr-4 text-gray-300">{h.title || '—'}</td>
                  <td className="py-3 pr-4">
                    <a href={h.youtube_url} target="_blank" rel="noreferrer"
                      className="text-brand-400 hover:text-brand-300 flex items-center gap-1 text-xs">
                      <ExternalLink className="w-3 h-3" /> YouTube
                    </a>
                  </td>
                  <td className="py-3 pr-4 text-gray-500">{format(new Date(h.created_at), 'dd MMM yyyy')}</td>
                  <td className="py-3">
                    <button className="text-red-400 hover:text-red-300" onClick={() => setDeleteTarget(h.id)}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="Add Highlight" size="sm">
        <div className="space-y-4">
          <div>
            <label className="label">Match (finished matches)</label>
            <select className="select" value={form.match_id} onChange={e => setForm(f => ({ ...f, match_id: Number(e.target.value) }))}>
              <option value={0}>Select match…</option>
              {matches.map(m => <option key={m.id} value={m.id}>{matchName(m.id)}</option>)}
            </select>
          </div>
          <div>
            <label className="label">YouTube URL</label>
            <input className="input" value={form.youtube_url} onChange={e => setForm(f => ({ ...f, youtube_url: e.target.value }))} placeholder="https://youtube.com/watch?v=…" />
          </div>
          <div>
            <label className="label">Title (optional)</label>
            <input className="input" value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} placeholder="Match Highlights" />
          </div>
          <div className="flex justify-end gap-3">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleSave} disabled={saving || !form.youtube_url || !form.match_id}>
              {saving ? <Spinner size="sm" /> : 'Save'}
            </button>
          </div>
        </div>
      </Modal>
      <ConfirmDialog open={deleteTarget !== null} message="Remove this highlight?" onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
};

// ── Notifications Page ────────────────────────────────────────────────────

import { notificationsApi } from '../api';
import type { Notification } from '../types';

export const NotificationsPage: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { notificationsApi.list().then(r => { setNotifications(r.data); setLoading(false); }); }, []);

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Notifications" subtitle={`${notifications.length} active subscriptions`} />
      {notifications.length === 0 ? <EmptyState message="No active notification subscriptions." icon="🔔" /> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-left">
              {['ID', 'User ID', 'Match ID', 'Subscribed'].map(h => <th key={h} className="table-head pb-4 pr-4">{h}</th>)}
            </tr></thead>
            <tbody>
              {notifications.map(n => (
                <tr key={n.id} className="table-row">
                  <td className="py-3 pr-4 text-gray-400">{n.id}</td>
                  <td className="py-3 pr-4 text-white">{n.user_id}</td>
                  <td className="py-3 pr-4 text-gray-300">{n.match_id}</td>
                  <td className="py-3 pr-4 text-gray-500">{format(new Date(n.created_at), 'dd MMM yyyy HH:mm')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

// ── Tournaments Page ──────────────────────────────────────────────────────

import { tournamentsApi } from '../api';
import type { Tournament } from '../types';

export const TournamentsPage: React.FC = () => {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [syncing, setSyncing] = useState<number | null>(null);
  const [form, setForm] = useState({ name: '', slug: '', season: '', type: 'group_knockout', is_active: true });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    const r = await tournamentsApi.list(); setTournaments(r.data); setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSave = async () => {
    setSaving(true);
    try { await tournamentsApi.create(form); setShowCreate(false); load(); }
    finally { setSaving(false); }
  };

  const handleSync = async (id: number) => {
    setSyncing(id);
    try { await tournamentsApi.sync(id); alert('FIFA data synced!'); }
    catch { alert('Sync failed — check API logs.'); }
    finally { setSyncing(null); }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await tournamentsApi.delete(deleteTarget); setDeleteTarget(null); load();
  };

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Tournaments" subtitle={`${tournaments.length} tournaments`}
        actions={<button className="btn-primary" onClick={() => setShowCreate(true)}><Plus className="w-4 h-4" /> New Tournament</button>} />
      {tournaments.length === 0 ? <EmptyState message="No tournaments yet." icon="🏆" /> : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="text-left">
              {['Name', 'Season', 'Type', 'Status', ''].map(h => <th key={h} className="table-head pb-4 pr-4">{h}</th>)}
            </tr></thead>
            <tbody>
              {tournaments.map(t => (
                <tr key={t.id} className="table-row">
                  <td className="py-3 pr-4 font-medium text-white">{t.name}</td>
                  <td className="py-3 pr-4 text-gray-400">{t.season || '—'}</td>
                  <td className="py-3 pr-4 text-gray-400 capitalize">{t.type.replace('_', ' ')}</td>
                  <td className="py-3 pr-4">
                    <span className={t.is_active ? 'text-green-400 text-xs' : 'text-gray-500 text-xs'}>
                      {t.is_active ? '● Active' : '○ Inactive'}
                    </span>
                  </td>
                  <td className="py-3">
                    <div className="flex items-center gap-2">
                      <button className="btn-secondary text-xs py-1 px-2" onClick={() => handleSync(t.id)} disabled={syncing === t.id}>
                        {syncing === t.id ? <Spinner size="sm" /> : 'Sync FIFA'}
                      </button>
                      <button className="text-red-400 hover:text-red-300" onClick={() => setDeleteTarget(t.id)}>
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
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="New Tournament" size="sm">
        <div className="space-y-4">
          {[['name', 'Name', 'FIFA World Cup 2026'], ['slug', 'Slug (unique)', 'fifa-wc-2026'], ['season', 'Season', '2026']].map(([k, l, p]) => (
            <div key={k}>
              <label className="label">{l}</label>
              <input className="input" value={(form as Record<string, unknown>)[k] as string}
                onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))} placeholder={p} />
            </div>
          ))}
          <div>
            <label className="label">Type</label>
            <select className="select" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))}>
              {['group_knockout', 'league', 'knockout'].map(t => <option key={t} value={t}>{t.replace('_', ' ')}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleSave} disabled={saving || !form.name || !form.slug}>
              {saving ? <Spinner size="sm" /> : 'Create'}
            </button>
          </div>
        </div>
      </Modal>
      <ConfirmDialog open={deleteTarget !== null} message="Delete this tournament and ALL its matches, teams and standings?" onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
};

// ── Admin Users Page ──────────────────────────────────────────────────────

import { adminUsersApi } from '../api';
import type { AdminUser } from '../types';

export const AdminUsersPage: React.FC = () => {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [form, setForm] = useState({ username: '', email: '', password: '', role: 'moderator' });
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    const r = await adminUsersApi.list(); setUsers(r.data); setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const handleSave = async () => {
    setSaving(true);
    try { await adminUsersApi.create(form); setShowCreate(false); load(); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await adminUsersApi.delete(deleteTarget); setDeleteTarget(null); load();
  };

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  const ROLES: Array<[string, string]> = [['super_admin', '🔑 Super Admin'], ['manager', '🛠 Manager'], ['moderator', '👁 Moderator']];

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Admin Users" subtitle={`${users.length} staff accounts`}
        actions={<button className="btn-primary" onClick={() => setShowCreate(true)}><Plus className="w-4 h-4" /> New Admin</button>} />
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-left">
            {['Username', 'Email', 'Role', 'Status', 'Last Login', ''].map(h => <th key={h} className="table-head pb-4 pr-4">{h}</th>)}
          </tr></thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} className="table-row">
                <td className="py-3 pr-4 font-medium text-white">{u.username}</td>
                <td className="py-3 pr-4 text-gray-400">{u.email}</td>
                <td className="py-3 pr-4 text-gray-300 capitalize">{u.role.replace('_', ' ')}</td>
                <td className="py-3 pr-4"><span className={u.is_active ? 'text-green-400 text-xs' : 'text-red-400 text-xs'}>{u.is_active ? '● Active' : '○ Disabled'}</span></td>
                <td className="py-3 pr-4 text-gray-500 text-xs">{u.last_login_at ? format(new Date(u.last_login_at), 'dd MMM HH:mm') : 'Never'}</td>
                <td className="py-3">
                  <button className="text-red-400 hover:text-red-300" onClick={() => setDeleteTarget(u.id)}><Trash2 className="w-4 h-4" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Modal open={showCreate} onClose={() => setShowCreate(false)} title="New Admin User" size="sm">
        <div className="space-y-4">
          {[['username', 'Username', 'janesmith'], ['email', 'Email', 'jane@example.com'], ['password', 'Password', '']].map(([k, l, p]) => (
            <div key={k}>
              <label className="label">{l}</label>
              <input className="input" type={k === 'password' ? 'password' : 'text'}
                value={(form as Record<string, string>)[k]}
                onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))} placeholder={p} />
            </div>
          ))}
          <div>
            <label className="label">Role</label>
            <select className="select" value={form.role} onChange={e => setForm(f => ({ ...f, role: e.target.value }))}>
              {ROLES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </div>
          <div className="flex justify-end gap-3">
            <button className="btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
            <button className="btn-primary" onClick={handleSave} disabled={saving || !form.username || !form.email || !form.password}>
              {saving ? <Spinner size="sm" /> : 'Create Admin'}
            </button>
          </div>
        </div>
      </Modal>
      <ConfirmDialog open={deleteTarget !== null} message="Remove this admin account?" onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
    </div>
  );
};

// ── Audit Logs Page ───────────────────────────────────────────────────────

import { auditApi } from '../api';
import type { AuditLog } from '../types';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  const load = useCallback(async () => {
    const r = await auditApi.list(filter || undefined); setLogs(r.data); setLoading(false);
  }, [filter]);

  useEffect(() => { load(); }, [load]);

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  const ENTITIES = ['match', 'stream', 'tournament', 'team', 'highlight', 'admin_user'];

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Audit Logs" subtitle="All admin write actions"
        actions={
          <select className="select w-44" value={filter} onChange={e => setFilter(e.target.value)}>
            <option value="">All entities</option>
            {ENTITIES.map(e => <option key={e} value={e}>{e}</option>)}
          </select>
        }
      />
      <div className="card overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="text-left">
            {['Time', 'Admin', 'Action', 'Entity', 'ID', 'IP'].map(h => <th key={h} className="table-head pb-4 pr-4">{h}</th>)}
          </tr></thead>
          <tbody>
            {logs.map(l => (
              <tr key={l.id} className="table-row">
                <td className="py-3 pr-4 text-gray-500 text-xs whitespace-nowrap">{format(new Date(l.created_at), 'dd MMM HH:mm:ss')}</td>
                <td className="py-3 pr-4 text-gray-300">{l.admin_id || '—'}</td>
                <td className="py-3 pr-4">
                  <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                    l.action === 'delete' ? 'bg-red-500/20 text-red-400' :
                    l.action === 'create' ? 'bg-green-500/20 text-green-400' :
                    'bg-blue-500/20 text-blue-400'}`}>{l.action}</span>
                </td>
                <td className="py-3 pr-4 text-gray-300">{l.entity_type}</td>
                <td className="py-3 pr-4 text-gray-500">{l.entity_id || '—'}</td>
                <td className="py-3 text-gray-500 text-xs">{l.ip_address || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ── Settings Page ─────────────────────────────────────────────────────────

import { settingsApi } from '../api';
import type { SystemSetting } from '../types';

export const SettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<SystemSetting[]>([]);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<Record<string, string>>({});
  const [saving, setSaving] = useState<string | null>(null);

  useEffect(() => {
    settingsApi.list().then(r => {
      setSettings(r.data);
      const edits: Record<string, string> = {};
      r.data.forEach((s: SystemSetting) => { edits[s.key] = s.value; });
      setEditing(edits);
      setLoading(false);
    });
  }, []);

  const handleSave = async (key: string) => {
    setSaving(key);
    try { await settingsApi.update(key, editing[key]); }
    finally { setSaving(null); }
  };

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader title="Settings" subtitle="System-wide configuration" />
      {settings.length === 0 ? (
        <div className="card text-gray-500 text-sm">No settings configured. Settings are created via the API or .env.</div>
      ) : (
        <div className="space-y-4">
          {settings.map(s => (
            <div key={s.key} className="card flex items-center gap-4">
              <div className="w-48 flex-shrink-0">
                <p className="text-sm font-medium text-white">{s.key}</p>
              </div>
              <input className="input flex-1" value={editing[s.key] ?? ''} onChange={e => setEditing(ed => ({ ...ed, [s.key]: e.target.value }))} />
              <button className="btn-primary flex-shrink-0" onClick={() => handleSave(s.key)} disabled={saving === s.key}>
                {saving === s.key ? <Spinner size="sm" /> : 'Save'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
