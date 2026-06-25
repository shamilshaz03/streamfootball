# Development Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16 running locally (or via Docker)
- Redis 7 running locally (or via Docker)

---

## Spin up just the infrastructure via Docker

```bash
# Start only DB and Redis (leaving app services for local dev)
docker compose up db redis -d
```

---

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Create a local .env (copy example and edit DATABASE_URL / REDIS_URL)
cp ../.env.example .env

# Apply migrations
alembic upgrade head

# Start with hot reload
uvicorn app.main:app --reload --port 8000
```

Swagger UI → http://localhost:8000/api/docs

### Creating a new migration

```bash
alembic revision --autogenerate -m "add some column"
alembic upgrade head
```

### Reverting the last migration

```bash
alembic downgrade -1
```

---

## Bot

```bash
cd bot
pip install -r requirements.txt

# .env must have TELEGRAM_BOT_TOKEN and API_BASE_URL=http://localhost:8000/api/v1
python -m bot.main
```

---

## Admin Panel

```bash
cd admin-panel
npm install
npm run dev     # http://localhost:5173
```

The Vite dev server proxies `/api/*` → `http://localhost:8000` so CORS is not an issue during development.

---

## Code Style

- **Python**: follow PEP 8; use type annotations throughout.
- **TypeScript**: strict mode enabled; avoid `any`.
- Keep business logic in `app/services/`; routers stay thin.

---

## Adding a new Bot feature

1. Add the backend endpoint in `backend/app/routers/`.
2. Add a wrapper in `bot/bot/api_client.py`.
3. Add a `cb_*` constant and keyboard builder in `bot/bot/keyboards.py`.
4. Handle the callback in `bot/bot/handlers/callbacks.py`.

## Adding a new Admin page

1. Add API wrappers in `admin-panel/src/api/index.ts`.
2. Create the page component in `admin-panel/src/pages/`.
3. Register the route and nav link in `App.tsx` and `Sidebar.tsx`.
