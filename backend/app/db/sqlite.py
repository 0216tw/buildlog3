from collections.abc import Generator
from pathlib import Path
import sqlite3

from app.core.config import get_settings


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    nickname TEXT NOT NULL UNIQUE,
    is_operator INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def database_path() -> Path:
    configured_value = get_settings().database_path
    if configured_value == ":memory:":
        return Path(configured_value)
    configured_path = Path(configured_value)
    if configured_path.is_absolute():
        return configured_path
    project_root = Path(__file__).resolve().parents[3]
    return project_root / configured_path


def get_connection() -> sqlite3.Connection:
    path = database_path()
    if str(path) != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    return connection


def get_db() -> Generator[sqlite3.Connection, None, None]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()
