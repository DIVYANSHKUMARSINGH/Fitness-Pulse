"""
Database engine and session configuration.

Creates the SQLAlchemy engine (database connection), the SessionLocal factory
(for creating per-request database sessions), and the Base class (parent for
all ORM models). The connect_args conditional ensures SQLite-specific threading
workarounds are only applied when using SQLite.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Create the SQLAlchemy engine
# connect_args is needed only for SQLite to allow multi-threaded access
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models to inherit from
Base = declarative_base()