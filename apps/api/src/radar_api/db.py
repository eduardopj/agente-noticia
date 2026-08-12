from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from radar_api.config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    from radar_api import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _add_missing_episode_columns()
    _add_missing_source_columns()


def _add_missing_episode_columns() -> None:
    columns = {
        column["name"]
        for column in inspect(engine).get_columns("episodes")
    }
    expected = {
        "summary_input_tokens": "INTEGER DEFAULT 0",
        "summary_output_tokens": "INTEGER DEFAULT 0",
        "script_input_tokens": "INTEGER DEFAULT 0",
        "script_output_tokens": "INTEGER DEFAULT 0",
        "tts_input_chars": "INTEGER DEFAULT 0",
        "estimated_audio_minutes": "FLOAT DEFAULT 0",
        "estimated_cost_usd": "FLOAT DEFAULT 0",
        "cost_breakdown_json": "TEXT",
    }
    with engine.begin() as connection:
        for name, definition in expected.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE episodes ADD COLUMN {name} {definition}"))


def _add_missing_source_columns() -> None:
    columns = {
        column["name"]
        for column in inspect(engine).get_columns("source_items")
    }
    expected = {
        "updated_at": "DATETIME",
    }
    with engine.begin() as connection:
        for name, definition in expected.items():
            if name not in columns:
                connection.execute(text(f"ALTER TABLE source_items ADD COLUMN {name} {definition}"))


def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
