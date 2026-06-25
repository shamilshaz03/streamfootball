// ── Enums ────────────────────────────────────────────────────────────────

export type MatchStatus = 'scheduled' | 'live' | 'halftime' | 'finished' | 'postponed' | 'cancelled';
export type StreamType  = 'hls' | 'mp4' | 'external' | 'webapp';
export type AdminRole   = 'super_admin' | 'manager' | 'moderator';

// ── Domain models ─────────────────────────────────────────────────────────

export interface Tournament {
  id: number;
  name: string;
  slug: string;
  season?: string;
  type: string;
  logo_url?: string;
  description?: string;
  start_date?: string;
  end_date?: string;
  is_active: boolean;
  created_at: string;
}

export interface Team {
  id: number;
  tournament_id: number;
  group_id?: number;
  name: string;
  short_name?: string;
  country_code?: string;
  logo_url?: string;
}

export interface Stream {
  id: number;
  match_id: number;
  language: string;
  quality: string;
  stream_type: StreamType;
  url: string;
  is_active: boolean;
  sort_order: number;
  label: string;
}

export interface Match {
  id: number;
  tournament_id: number;
  home_team_id: number;
  away_team_id: number;
  home_team: Team;
  away_team: Team;
  match_date: string;
  venue?: string;
  stage?: string;
  status: MatchStatus;
  home_score?: number;
  away_score?: number;
  thumbnail_url?: string;
  streams: Stream[];
  has_highlight: boolean;
  created_at: string;
  updated_at: string;
}

export interface Highlight {
  id: number;
  match_id: number;
  youtube_url: string;
  title?: string;
  thumbnail_url?: string;
  created_at: string;
}

export interface Notification {
  id: number;
  user_id: number;
  match_id: number;
  is_active: boolean;
  created_at: string;
}

export interface Standing {
  id: number;
  tournament_id: number;
  group_id?: number;
  team: Team;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  position?: number;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  role: AdminRole;
  is_active: boolean;
  created_at: string;
  last_login_at?: string;
}

export interface AuditLog {
  id: number;
  admin_id?: number;
  action: string;
  entity_type: string;
  entity_id?: string;
  details?: Record<string, unknown>;
  ip_address?: string;
  created_at: string;
}

export interface DashboardMetrics {
  total_users: number;
  live_matches: number;
  upcoming_matches_today: number;
  active_notifications: number;
  total_streams: number;
  total_tournaments: number;
}

export interface SystemSetting {
  key: string;
  value: string;
}
