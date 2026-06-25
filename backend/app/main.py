"""
FastAPI application factory.

Run locally:
    uvicorn app.main:app --reload --port 8000

In Docker: see docker-compose.yml.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from starlette.responses import JSONResponse

from app.config import settings
from app.middleware.rate_limit import limiter
from app.routers import (
    admin_users,
    auth,
    dashboard,
    fifa,
    highlights,
    matches,
    notifications,
    standings,
    streams,
    tournaments,
    uploads,
    users,
    utilities,
)
from app.scheduler.jobs import shutdown_scheduler, start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: seed DB, start scheduler. Shutdown: stop scheduler."""
    _seed_super_admin()
    start_scheduler()
    yield
    shutdown_scheduler()


def _seed_super_admin() -> None:
    """Create the first super-admin account if no admins exist yet."""
    from app.database import SessionLocal
    from app.models.admin import AdminUser
    from app.models.enums import AdminRole
    from app.security import hash_password

    db = SessionLocal()
    try:
        if db.query(AdminUser).count() == 0:
            admin = AdminUser(
                username=settings.FIRST_SUPER_ADMIN_USERNAME,
                email=settings.FIRST_SUPER_ADMIN_EMAIL,
                hashed_password=hash_password(settings.FIRST_SUPER_ADMIN_PASSWORD),
                role=AdminRole.SUPER_ADMIN,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="1.0.0",
        description=(
            "Production-grade Football Streaming Platform API.\n\n"
            "All write endpoints require a Bearer JWT token obtained from **POST /api/v1/auth/login**."
        ),
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # ── Rate limiting ──────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    @app.exception_handler(RateLimitExceeded)
    async def _rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return JSONResponse({"detail": "Rate limit exceeded. Please slow down."}, status_code=429)

    # ── CORS ───────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Static files (uploaded thumbnails / logos) ─────────────────────────
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # ── Routers ────────────────────────────────────────────────────────────
    prefix = settings.API_PREFIX
    for r in [
        auth.router,
        dashboard.router,
        matches.router,
        streams.router,
        highlights.router,
        notifications.router,
        tournaments.router,
        standings.router,
        users.router,
        admin_users.router,
        uploads.router,
        utilities.router,
        fifa.router,
    ]:
        app.include_router(r, prefix=prefix)

    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()
