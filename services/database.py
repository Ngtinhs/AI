"""SQLite: một file data/app.db, mỗi bảng có vài cột tra cứu + một cột *_json chứa toàn bộ model."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar

from config.settings import DB_PATH, DB_TIMEOUT_SECONDS

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    username      TEXT PRIMARY KEY,
    password_hash TEXT NOT NULL,
    salt          TEXT NOT NULL,
    iterations    INTEGER NOT NULL,
    created_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles (
    user_id       TEXT PRIMARY KEY REFERENCES accounts(username),
    current_level TEXT,
    profile_json  TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assessments (
    assessment_id TEXT PRIMARY KEY,
    user_id       TEXT NOT NULL REFERENCES accounts(username),
    overall_level TEXT NOT NULL,
    completed_at  TEXT NOT NULL,
    result_json   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
    lesson_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        TEXT NOT NULL REFERENCES accounts(username),
    video_id       TEXT NOT NULL,
    video_url      TEXT NOT NULL,
    learner_level  TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    category       TEXT,
    analysis_json  TEXT NOT NULL,
    created_at     TEXT NOT NULL,
    UNIQUE (user_id, video_id, learner_level)
);

CREATE INDEX IF NOT EXISTS idx_assessments_user ON assessments(user_id, completed_at);
CREATE INDEX IF NOT EXISTS idx_lessons_user ON lessons(user_id, created_at);
"""

_initialized_paths: set[str] = set()
# Connection của transaction đang mở trong luồng/phiên hiện tại (None = chưa có).
_active_connection: ContextVar[sqlite3.Connection | None] = ContextVar("_active_connection", default=None)


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT_SECONDS)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    if str(DB_PATH) not in _initialized_paths:
        conn.executescript(SCHEMA)
        _initialized_paths.add(str(DB_PATH))
    return conn


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """
    Mở một transaction: commit khi thoát khối `with` bình thường, rollback khi có lỗi.

    Gọi lồng nhau sẽ dùng chung connection của khối ngoài cùng, nên nhiều thao tác
    (vd. lưu assessment + cập nhật profile) cùng thành công hoặc cùng bị hủy.
    """
    active = _active_connection.get()
    if active is not None:
        yield active
        return

    conn = _connect()
    token = _active_connection.set(conn)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _active_connection.reset(token)
        conn.close()


def fetch_one(sql: str, params: tuple = ()) -> sqlite3.Row | None:
    with get_connection() as conn:
        return conn.execute(sql, params).fetchone()


def fetch_all(sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(sql, params).fetchall()


def insert(table: str, row: dict, ignore: bool = False) -> int:
    """Trả về số dòng được thêm (0 khi `ignore=True` và bản ghi đã tồn tại)."""
    verb = "INSERT OR IGNORE" if ignore else "INSERT"
    columns = ", ".join(row)
    placeholders = ", ".join("?" * len(row))
    sql = f"{verb} INTO {table} ({columns}) VALUES ({placeholders})"
    with get_connection() as conn:
        return conn.execute(sql, tuple(row.values())).rowcount


def upsert(table: str, row: dict, keys: tuple[str, ...]) -> None:
    """Thêm mới, hoặc cập nhật mọi cột không thuộc `keys` nếu bản ghi đã tồn tại."""
    columns = ", ".join(row)
    placeholders = ", ".join("?" * len(row))
    updates = ", ".join(f"{col} = excluded.{col}" for col in row if col not in keys)
    sql = (
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
        f"ON CONFLICT({', '.join(keys)}) DO UPDATE SET {updates}"
    )
    with get_connection() as conn:
        conn.execute(sql, tuple(row.values()))
