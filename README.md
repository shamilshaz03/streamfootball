# ⚽ Telegram Football Streaming Platform

A production-grade, fully dockerised football streaming platform with a Telegram bot, FastAPI backend, PostgreSQL + Redis, and a React admin dashboard.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Docker Network                     │
│                                                      │
│  ┌──────────┐   ┌──────────┐   ┌─────────────────┐ │
│  │ Telegram │   │  React   │   │   Telegram Bot  │ │
│  │  Users   │   │  Admin   │   │ (python-tg-bot) │ │
│  └────┬─────┘   └────┬─────┘   └────────┬────────┘ │
│       │              │                  │           │
│       └──────────────┼──────────────────┘           │
│                      │  HTTP / REST                 │
│              ┌───────▼────────┐                     │
│              │  FastAPI       │                     │
│              │  Backend :8000 │                     │
│              └───────┬────────┘                     │
│                      │                              │
│          ┌───────────┼───────────┐                  │
│          │           │           │                  │
│   ┌──────▼──┐ ┌──────▼──┐ ┌────▼──────┐           │
│   │PostgreSQL│ │  Redis  │ │ APScheduler│           │
│   │  :5432  │ │  :6379  │ │ (in-proc) │           │
│   └─────────┘ └─────────┘ └───────────┘           │
└─────────────────────────────────────────────────────┘
```

---

## Features

### Telegram Bot
| Menu Item | Description |
|---|---|
| 📅 Today's Matches | All matches scheduled for today |
| ⏭ Upcoming Matches | Future scheduled matches |
| 🔴 Live Now | Matches currently LIVE or at half time |
| ▶️ Watch Now | Auto-generated language × quality stream buttons |
| 🔔 Notify Me | Subscribe to pre-match and status reminders |
| 🎬 Highlights | YouTube highlight link for finished matches |
| 🏆 Points Table | Live standings per tournament and group |
| ℹ️ Tournaments | Browse active tournaments |

### Match Management (Admin)
- Full CRUD: create, edit, delete matches
- Set match time, venue, stage, thumbnail
- Add **unlimited** stream entries: any language × any quality
- Update match status (Scheduled → Live → Half Time → Finished)
- Scores update triggers subscriber notifications automatically

### Streaming
Stream buttons auto-generated from the database. Example keyboard:
```
📺 English 1080p
📺 English 720p
📺 Arabic 1080p
📺 Malayalam 720p
📺 Hindi 720p
```
Supported types: **HLS**, **MP4**, **External URL**, **Telegram Web App**

### Notifications (Scheduler-driven)
| Trigger | Type |
|---|---|
| 1 hour before kickoff | Time-based (APScheduler, polls every 30s) |
| 30 minutes before kickoff | Time-based |
| 15 minutes before kickoff | Time-based |
| Match started (LIVE) | Event-driven (admin status update) |
| Half time | Event-driven |
| Match finished | Event-driven |

Old broadcast channel messages are deleted before a new status update is posted, keeping the channel clean.

### FIFA Data Provider
Abstract `FifaDataProvider` base class with a `MockFifaProvider` for development. Swap in a real data vendor (e.g. football-data.org, Sportmonks) by implementing the abstract class and updating `get_provider()` in `mock_provider.py`.

### Admin Dashboard (React + Vite + TypeScript)
| Page | Features |
|---|---|
| Dashboard | Live metrics: users, live matches, today's matches, notifications, streams, tournaments |
| Matches | Full CRUD + inline stream manager + status controls |
| Streams | Global stream list; toggle active/inactive |
| Highlights | Add/remove YouTube highlight links per match |
| Notifications | View active subscriptions |
| Tournaments | Create, delete, trigger FIFA data sync |
| Admin Users | Manage staff accounts with role-based access |
| Audit Logs | Immutable log of every admin write action |
| Settings | Key/value system config |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Python 3.12, FastAPI 0.115, Uvicorn |
| Bot | python-telegram-bot v22 |
| Database | PostgreSQL 16 + SQLAlchemy 2.0 + Alembic |
| Cache | Redis 7 |
| Scheduler | APScheduler 3.10 |
| Rate limiting | slowapi (Redis-backed) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Admin panel | React 18, Vite 5, TypeScript, Tailwind CSS v3 |
| Container | Docker + Docker Compose |

---

## Quick Start

### Prerequisites
- Docker ≥ 24 and Docker Compose v2
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### 1 — Clone and configure

```bash
git clone <repo-url>
cd telegram-football-platform
cp .env.example .env
```

Edit `.env` and set at minimum:
```
TELEGRAM_BOT_TOKEN=your:token_here
JWT_SECRET_KEY=<64 random hex chars>
FIRST_SUPER_ADMIN_PASSWORD=<strong password>
```

Generate a secure JWT key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 2 — Start all services

```bash
docker compose up --build -d
```

This will:
1. Start PostgreSQL and Redis
2. Run Alembic migrations and seed the first super-admin
3. Start the FastAPI backend on **:8000**
4. Start the Telegram bot (long polling)
5. Build and serve the React admin panel on **:3000**

### 3 — Access the services

| Service | URL |
|---|---|
| Admin Panel | http://localhost:3000 |
| API Swagger | http://localhost:8000/api/docs |
| API ReDoc | http://localhost:8000/api/redoc |
| Health check | http://localhost:8000/health |

Login with the credentials from `FIRST_SUPER_ADMIN_USERNAME` / `FIRST_SUPER_ADMIN_PASSWORD`.

---

## Local Development (without Docker)

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for the full guide.

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # edit DATABASE_URL and REDIS_URL for local services
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Bot (separate terminal)
cd bot
pip install -r requirements.txt
python -m bot.main

# Admin panel (separate terminal)
cd admin-panel
npm install
npm run dev       # http://localhost:5173
```

---

## Environment Variables Reference

| Variable | Description | Default |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | Bot token from @BotFather | **required** |
| `TELEGRAM_BROADCAST_CHAT_ID` | Optional channel for public status broadcasts | — |
| `DATABASE_URL` | PostgreSQL connection string | see .env.example |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `JWT_SECRET_KEY` | 64-char hex secret for signing tokens | **required** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT TTL in minutes | `720` (12 h) |
| `FIRST_SUPER_ADMIN_USERNAME` | Seeded on first boot | `admin` |
| `FIRST_SUPER_ADMIN_PASSWORD` | Seeded on first boot | **change this** |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `MAX_UPLOAD_SIZE_MB` | Max thumbnail upload size | `10` |

---

## Admin Roles

| Role | Capabilities |
|---|---|
| `super_admin` | Everything — including creating/deleting admin accounts |
| `manager` | Create/edit/delete matches, teams, tournaments, streams, standings |
| `moderator` | Add highlights, toggle stream active state, set match status |

---

## API Overview

Full interactive documentation at `/api/docs` (Swagger UI) or `/api/redoc`.

| Group | Base Path |
|---|---|
| Auth | `POST /api/v1/auth/login` |
| Matches | `/api/v1/matches` |
| Streams | `/api/v1/streams`, `/api/v1/matches/{id}/streams` |
| Highlights | `/api/v1/highlights` |
| Notifications | `/api/v1/notifications` |
| Tournaments | `/api/v1/tournaments` |
| Teams | `/api/v1/teams` |
| Standings | `/api/v1/standings` |
| FIFA Sync | `POST /api/v1/fifa/sync/{tournament_id}` |
| Dashboard | `/api/v1/dashboard/metrics` |
| Admin Users | `/api/v1/admin-users` |
| Audit Logs | `/api/v1/audit-logs` |
| Settings | `/api/v1/settings` |
| Uploads | `POST /api/v1/upload/image` |

---

## Database Schema

```
users              — Telegram end users
admins             — Admin panel staff
matches            — Football matches
teams              — Teams per tournament
tournaments        — Competition containers
groups             — Groups within a tournament
streams            — Language/quality stream URLs per match
standings          — Points table rows
notifications      — User match subscriptions + sent flags
highlights         — YouTube URLs per finished match
broadcast_messages — Tracks last Telegram broadcast per match for cleanup
audit_logs         — Immutable admin action log
system_settings    — Generic key/value config store
```

---

## Deploying to Production

1. Set strong passwords and a real `JWT_SECRET_KEY` in `.env`
2. Put an Nginx reverse proxy in front of the stack (handle TLS)
3. Point `CORS_ORIGINS` to your production admin panel domain
4. Consider replacing `uvicorn` with `gunicorn -k uvicorn.workers.UvicornWorker` for multi-worker stability
5. Mount `uploads` volume to persistent external storage (S3-compatible recommended for scale)

---

## Extending the FIFA Data Provider

Create `backend/app/services/fifa_provider/my_provider.py`:

```python
from app.services.fifa_provider.base import FifaDataProvider

class MyRealProvider(FifaDataProvider):
    def get_groups(self): ...
    def get_teams(self): ...
    def get_fixtures(self): ...
    def get_results(self): ...
    def get_standings(self): ...
```

Then in `mock_provider.py`, update `get_provider()`:

```python
def get_provider() -> FifaDataProvider:
    return MyRealProvider()
```

No other code needs to change.

---

## License

MIT
