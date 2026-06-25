FROM python:3.12-slim

# System deps for psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create upload directory
RUN mkdir -p app/static/uploads

# Run migrations then start uvicorn
CMD alembic upgrade head && \
    uvicorn app.main:app \
      --host 0.0.0.0 \
      --port 8000 \
      --workers 2 \
      --log-level info
