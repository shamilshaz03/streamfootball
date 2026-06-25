import React from 'react';
import { X, AlertTriangle } from 'lucide-react';
import type { MatchStatus } from '../types';

// ── Modal ─────────────────────────────────────────────────────────────────

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

export const Modal: React.FC<ModalProps> = ({ open, onClose, title, children, size = 'md' }) => {
  if (!open) return null;
  const widths = { sm: 'max-w-md', md: 'max-w-2xl', lg: 'max-w-4xl' };
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />
      <div className={`relative bg-gray-900 border border-gray-700 rounded-2xl w-full ${widths[size]} shadow-2xl max-h-[90vh] flex flex-col`}>
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <h2 className="text-lg font-semibold text-white">{title}</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="p-6 overflow-y-auto flex-1">{children}</div>
      </div>
    </div>
  );
};

// ── Status Badge ──────────────────────────────────────────────────────────

const STATUS_MAP: Record<MatchStatus, { label: string; cls: string }> = {
  live:      { label: '🔴 LIVE',      cls: 'badge-live' },
  halftime:  { label: '⏸ HT',        cls: 'badge-halftime' },
  scheduled: { label: '📅 Scheduled', cls: 'badge-scheduled' },
  finished:  { label: '✅ Finished',  cls: 'badge-finished' },
  postponed: { label: '⏳ Postponed', cls: 'badge-scheduled' },
  cancelled: { label: '❌ Cancelled', cls: 'badge-finished' },
};

export const StatusBadge: React.FC<{ status: MatchStatus }> = ({ status }) => {
  const { label, cls } = STATUS_MAP[status] ?? { label: status, cls: 'badge-scheduled' };
  return <span className={cls}>{label}</span>;
};

// ── Spinner ───────────────────────────────────────────────────────────────

export const Spinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const s = { sm: 'w-4 h-4', md: 'w-8 h-8', lg: 'w-12 h-12' }[size];
  return (
    <div className={`${s} rounded-full border-2 border-gray-700 border-t-brand-500 animate-spin`} />
  );
};

// ── Confirm Dialog ────────────────────────────────────────────────────────

interface ConfirmProps {
  open: boolean;
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  danger?: boolean;
}

export const ConfirmDialog: React.FC<ConfirmProps> = ({ open, message, onConfirm, onCancel, danger = true }) => (
  <Modal open={open} onClose={onCancel} title="Confirm Action" size="sm">
    <div className="flex flex-col items-center gap-4 text-center py-4">
      <div className={`w-12 h-12 rounded-full flex items-center justify-center ${danger ? 'bg-red-500/20' : 'bg-brand-500/20'}`}>
        <AlertTriangle className={`w-6 h-6 ${danger ? 'text-red-400' : 'text-brand-400'}`} />
      </div>
      <p className="text-gray-300">{message}</p>
      <div className="flex gap-3">
        <button onClick={onCancel} className="btn-secondary">Cancel</button>
        <button onClick={onConfirm} className={danger ? 'btn-danger' : 'btn-primary'}>Confirm</button>
      </div>
    </div>
  </Modal>
);

// ── Empty State ───────────────────────────────────────────────────────────

export const EmptyState: React.FC<{ message: string; icon?: React.ReactNode }> = ({ message, icon }) => (
  <div className="flex flex-col items-center justify-center py-20 text-gray-500">
    <div className="text-5xl mb-4">{icon || '📭'}</div>
    <p className="text-lg">{message}</p>
  </div>
);

// ── Page Header ───────────────────────────────────────────────────────────

export const PageHeader: React.FC<{
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}> = ({ title, subtitle, actions }) => (
  <div className="flex items-start justify-between mb-8">
    <div>
      <h1 className="text-2xl font-bold text-white">{title}</h1>
      {subtitle && <p className="text-gray-400 text-sm mt-1">{subtitle}</p>}
    </div>
    {actions && <div className="flex items-center gap-3">{actions}</div>}
  </div>
);
