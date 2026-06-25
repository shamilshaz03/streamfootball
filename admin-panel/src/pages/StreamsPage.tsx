import React, { useCallback, useEffect, useState } from 'react';
import { Trash2, ToggleLeft, ToggleRight } from 'lucide-react';
import { streamsApi } from '../api';
import type { Stream } from '../types';
import { ConfirmDialog, EmptyState, PageHeader, Spinner } from '../components/UI';

const STREAM_TYPE_BADGE: Record<string, string> = {
  hls:      'bg-purple-500/20 text-purple-400',
  mp4:      'bg-blue-500/20   text-blue-400',
  external: 'bg-yellow-500/20 text-yellow-400',
  webapp:   'bg-green-500/20  text-green-400',
};

const StreamsPage: React.FC = () => {
  const [streams, setStreams] = useState<Stream[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);

  const load = useCallback(async () => {
    const r = await streamsApi.list();
    setStreams(r.data);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  const toggleActive = async (s: Stream) => {
    await streamsApi.update(s.id, { is_active: !s.is_active });
    load();
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await streamsApi.delete(deleteTarget);
    setDeleteTarget(null);
    load();
  };

  if (loading) return <div className="flex-1 flex items-center justify-center"><Spinner size="lg" /></div>;

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <PageHeader
        title="Streams"
        subtitle={`${streams.length} stream${streams.length !== 1 ? 's' : ''} across all matches`}
      />

      {streams.length === 0 ? (
        <EmptyState message="No streams yet. Add them from the Matches page." icon="📺" />
      ) : (
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left">
                {['Match ID', 'Label', 'Type', 'URL', 'Order', 'Active', ''].map(h => (
                  <th key={h} className="table-head pb-4 pr-4">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {streams.map(s => (
                <tr key={s.id} className="table-row">
                  <td className="py-3 pr-4 text-gray-400">#{s.match_id}</td>
                  <td className="py-3 pr-4 font-medium text-white">{s.label}</td>
                  <td className="py-3 pr-4">
                    <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${STREAM_TYPE_BADGE[s.stream_type] ?? ''}`}>
                      {s.stream_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-gray-400 max-w-xs truncate text-xs">{s.url}</td>
                  <td className="py-3 pr-4 text-gray-400">{s.sort_order}</td>
                  <td className="py-3 pr-4">
                    <button onClick={() => toggleActive(s)} className="text-gray-400 hover:text-white transition-colors">
                      {s.is_active
                        ? <ToggleRight className="w-5 h-5 text-green-400" />
                        : <ToggleLeft className="w-5 h-5" />}
                    </button>
                  </td>
                  <td className="py-3">
                    <button className="text-red-400 hover:text-red-300" onClick={() => setDeleteTarget(s.id)}>
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        message="Delete this stream? Users will no longer see this option in the bot."
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
};

export default StreamsPage;
