# ── Stage 1: Build Admin Panel ─────────────────────────────────────────────
FROM node:20-alpine AS admin-builder
WORKDIR /admin
COPY admin-panel/package.json .
RUN npm install
COPY admin-panel/ .
RUN npm run build

# ── Stage 2: Backend + Bot ─────────────────────────────────────────────────
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Copy built admin panel into FastAPI static folder
COPY --from=admin-builder /admin/dist /app/app/static/admin

RUN mkdir -p app/static/uploads

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && supervisord -c /etc/supervisor/conf.d/supervisord.conf"]
