"""Database configuration utilities for the dental CRM application."""
from collections.abc import Iterator

from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "sqlite:///./crm.db"

# sqlite needs check_same_thread set to False when used with FastAPI dependency injection
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)


def init_db() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    """Yield a database session for use as a FastAPI dependency."""
    with Session(engine) as session:
        yield session
