import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Calendar, Tv2, Bell, Trophy, Play,
  Users, Settings, LogOut, Shield, ClipboardList,
} from 'lucide-react';
import { useAuth } from '../auth/AuthContext';

const NAV = [
  { to: '/',              icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/matches',       icon: Calendar,        label: 'Matches' },
  { to: '/streams',       icon: Tv2,             label: 'Streams' },
  { to: '/highlights',    icon: Play,            label: 'Highlights' },
  { to: '/notifications', icon: Bell,            label: 'Notifications' },
  { to: '/tournaments',   icon: Trophy,          label: 'Tournaments' },
  { to: '/admin-users',   icon: Users,           label: 'Admin Users' },
  { to: '/audit-logs',    icon: ClipboardList,   label: 'Audit Logs' },
  { to: '/settings',      icon: Settings,        label: 'Settings' },
];

const Sidebar: React.FC = () => {
  const { admin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <aside className="w-64 flex-shrink-0 bg-gray-900 border-r border-gray-800 flex flex-col h-full">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-600 flex items-center justify-center text-lg">⚽</div>
          <div>
            <p className="font-bold text-sm text-white leading-tight">Football Admin</p>
            <p className="text-xs text-gray-500">Streaming Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 overflow-y-auto space-y-1">
        {NAV.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-brand-600/20 text-brand-400 border border-brand-600/30'
                  : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full bg-gray-700 flex items-center justify-center">
            <Shield className="w-4 h-4 text-brand-400" />
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-white truncate">{admin?.username}</p>
            <p className="text-xs text-gray-500 capitalize">{admin?.role?.replace('_', ' ')}</p>
          </div>
        </div>
        <button onClick={handleLogout} className="btn-secondary w-full justify-center text-xs">
          <LogOut className="w-3.5 h-3.5" /> Sign out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
