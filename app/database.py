"""
Database engine and session management (synchronous SQLAlchemy 2.0 style).

Synchronous SQLAlchemy is used deliberately for simplicity and reliability;
FastAPI runs sync dependencies in a worker thread pool automatically, so this
does not block the event loop under normal load. See docs/DEVELOPMENT.md for
the rationale and notes on swapping to an async engine later if needed.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that yields a database session and guarantees closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
