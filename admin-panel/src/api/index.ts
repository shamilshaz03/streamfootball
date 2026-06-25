import axios from 'axios';

export const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

// ── Request interceptor: attach JWT ──────────────────────────────────────
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ── Response interceptor: redirect to login on 401 ───────────────────────
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

// ── Auth ─────────────────────────────────────────────────────────────────
export const authApi = {
  login:  (u: string, p: string) => api.post('/auth/login', { username: u, password: p }),
  me:     ()                     => api.get('/auth/me'),
};

// ── Dashboard ─────────────────────────────────────────────────────────────
export const dashboardApi = {
  metrics: () => api.get('/dashboard/metrics'),
};

// ── Matches ───────────────────────────────────────────────────────────────
export const matchesApi = {
  list:         (params?: object)   => api.get('/matches', { params }),
  get:          (id: number)        => api.get(`/matches/${id}`),
  create:       (data: object)      => api.post('/matches', data),
  update:       (id: number, d: object) => api.put(`/matches/${id}`, d),
  setStatus:    (id: number, d: object) => api.patch(`/matches/${id}/status`, d),
  delete:       (id: number)        => api.delete(`/matches/${id}`),
  getStreams:   (id: number)        => api.get(`/matches/${id}/streams`),
  addStream:    (id: number, d: object) => api.post(`/matches/${id}/streams`, d),
  getHighlight: (id: number)        => api.get(`/matches/${id}/highlight`),
};

// ── Streams ───────────────────────────────────────────────────────────────
export const streamsApi = {
  list:   ()                      => api.get('/streams'),
  update: (id: number, d: object) => api.put(`/streams/${id}`, d),
  delete: (id: number)            => api.delete(`/streams/${id}`),
};

// ── Highlights ────────────────────────────────────────────────────────────
export const highlightsApi = {
  list:   ()                      => api.get('/highlights'),
  create: (data: object)          => api.post('/highlights', data),
  update: (id: number, d: object) => api.put(`/highlights/${id}`, d),
  delete: (id: number)            => api.delete(`/highlights/${id}`),
};

// ── Tournaments & Teams ───────────────────────────────────────────────────
export const tournamentsApi = {
  list:   ()                      => api.get('/tournaments'),
  create: (data: object)          => api.post('/tournaments', data),
  update: (id: number, d: object) => api.put(`/tournaments/${id}`, d),
  delete: (id: number)            => api.delete(`/tournaments/${id}`),
  sync:   (id: number)            => api.post(`/fifa/sync/${id}`),
};

export const teamsApi = {
  list:   (tournament_id?: number) => api.get('/teams', { params: { tournament_id } }),
  create: (data: object)           => api.post('/teams', data),
  update: (id: number, d: object)  => api.put(`/teams/${id}`, d),
  delete: (id: number)             => api.delete(`/teams/${id}`),
};

// ── Notifications ─────────────────────────────────────────────────────────
export const notificationsApi = {
  list: () => api.get('/notifications'),
};

// ── Admin Users ───────────────────────────────────────────────────────────
export const adminUsersApi = {
  list:   ()                      => api.get('/admin-users'),
  create: (data: object)          => api.post('/admin-users', data),
  update: (id: number, d: object) => api.put(`/admin-users/${id}`, d),
  delete: (id: number)            => api.delete(`/admin-users/${id}`),
};

// ── Audit Logs ────────────────────────────────────────────────────────────
export const auditApi = {
  list: (entity_type?: string) => api.get('/audit-logs', { params: { entity_type } }),
};

// ── Settings ──────────────────────────────────────────────────────────────
export const settingsApi = {
  list:   ()                      => api.get('/settings'),
  update: (key: string, value: string) => api.put(`/settings/${key}`, { value }),
};

// ── Uploads ───────────────────────────────────────────────────────────────
export const uploadsApi = {
  image: (file: File) => {
    const fd = new FormData();
    fd.append('file', file);
    return api.post('/upload/image', fd, { headers: { 'Content-Type': 'multipart/form-data' } });
  },
};
