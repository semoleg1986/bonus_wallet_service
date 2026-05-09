"""SQLAlchemy engine and session factory helpers."""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


def build_engine(url: str) -> Engine:
    """Create SQLAlchemy engine for configured database URL."""

    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(
        url,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def build_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create session factory bound to an engine."""

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
