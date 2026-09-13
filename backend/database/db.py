"""SQLite connection and safe, additive schema migrations for XiaoG-owned data."""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

from backend.config import settings


DEFAULT_SYSTEM_PROMPT = """你叫“小G”。

交流原则：自然、诚实、直接、简洁；不刻意讨好用户；能够理解用户，但保持独立判断；发现用户逻辑有问题时可以指出；不知道的事情明确说不知道；不要为了显得聪明而编造事实；不要机械重复用户长期资料。"""

Migration = tuple[str, Callable[[sqlite3.Connection], None]]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(settings.database_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def _migrate_core_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('system', 'user', 'assistant', 'tool')),
            content TEXT NOT NULL,
            provider TEXT,
            model TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'general',
            importance INTEGER NOT NULL DEFAULT 1 CHECK(importance BETWEEN 1 AND 5),
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS model_usage (
            id TEXT PRIMARY KEY,
            conversation_id TEXT NOT NULL,
            provider TEXT NOT NULL,
            model TEXT NOT NULL,
            billing_type TEXT NOT NULL DEFAULT 'api',
            input_tokens INTEGER,
            output_tokens INTEGER,
            estimated_cost REAL,
            latency_ms INTEGER,
            created_at TEXT NOT NULL,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_messages_conversation_created ON messages(conversation_id, created_at);
        CREATE INDEX IF NOT EXISTS idx_usage_conversation_created ON model_usage(conversation_id, created_at);
        """
    )


def _ensure_conversation_column(conn: sqlite3.Connection, name: str, definition: str) -> None:
    columns = {row["name"] for row in conn.execute("PRAGMA table_info(conversations)").fetchall()}
    if name not in columns:
        conn.execute(f"ALTER TABLE conversations ADD COLUMN {definition}")


def _migrate_conversation_lifecycle(conn: sqlite3.Connection) -> None:
    # Every change is additive: existing rows and SQLite files are retained.
    for name, definition in (
        ("archived_at", "archived_at TEXT"),
        ("codex_thread_id", "codex_thread_id TEXT"),
        ("codex_last_synced_message_id", "codex_last_synced_message_id TEXT"),
        ("is_pinned", "is_pinned INTEGER NOT NULL DEFAULT 0"),
        ("pinned_at", "pinned_at TEXT"),
        ("deleted_at", "deleted_at TEXT"),
        ("deleted_from", "deleted_from TEXT"),
        ("model_mode", "model_mode TEXT NOT NULL DEFAULT 'auto'"),
        ("manual_model", "manual_model TEXT NOT NULL DEFAULT 'deepseek'"),
        ("manual_reasoning_effort", "manual_reasoning_effort TEXT"),
        # Do not populate this JSON map from a legacy scalar. Hydration assigns
        # the scalar only to its recorded Manual model at read time.
        ("manual_reasoning_preferences", "manual_reasoning_preferences TEXT"),
    ):
        _ensure_conversation_column(conn, name, definition)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_archived_updated ON conversations(archived_at, updated_at DESC)")
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversations_state "
        "ON conversations(deleted_at, archived_at, is_pinned DESC, pinned_at DESC, updated_at DESC)"
    )


def _migrate_settings_defaults(conn: sqlite3.Connection) -> None:
    defaults = (
        ("system_prompt", DEFAULT_SYSTEM_PROMPT),
        ("user_profile", ""),
        ("theme_mode", "light"),
        ("color_scheme", "green"),
        ("assistant_avatar", "default"),
        ("user_avatar", "default"),
        ("font_scale", "standard"),
        ("default_model", "deepseek"),
        ("reasoning_preference", "balanced"),
        ("manual_reasoning_preferences", "{}"),
        ("chat_density", "comfortable"),
        ("show_message_time", "true"),
        ("enter_to_send", "true"),
        ("animations_enabled", "true"),
        ("ui_language", "zh-CN"),
    )
    for key, value in defaults:
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
            (key, value, now_iso()),
        )



def _migrate_file_artifact_lifecycle(conn: sqlite3.Connection) -> None:
    """Add metadata only; XiaoG does not accept or store file bytes yet."""
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS file_artifacts (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL CHECK(kind IN ('temporary_chat_attachment', 'artifact', 'knowledge_file', 'project_asset')),
            scope TEXT NOT NULL CHECK(scope IN ('conversation', 'project', 'global')),
            persistence TEXT NOT NULL CHECK(persistence IN ('temporary', 'durable')),
            display_name TEXT NOT NULL,
            owner_conversation_id TEXT,
            owner_project_id TEXT,
            storage_reference TEXT,
            deleted_at TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_file_artifacts_lifecycle
            ON file_artifacts(deleted_at, kind, scope, updated_at DESC);
        """
    )

MIGRATIONS: tuple[Migration, ...] = (
    ("001_core_schema", _migrate_core_schema),
    ("002_conversation_lifecycle", _migrate_conversation_lifecycle),
    ("003_personalization_defaults", _migrate_settings_defaults),
    ("004_file_artifact_lifecycle", _migrate_file_artifact_lifecycle),
)


def _apply_migration(conn: sqlite3.Connection, version: str, operation: Callable[[sqlite3.Connection], None]) -> None:
    applied = conn.execute("SELECT 1 FROM schema_migrations WHERE version = ?", (version,)).fetchone()
    if applied:
        return
    operation(conn)
    conn.execute(
        "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
        (version, now_iso()),
    )


def initialize_database() -> None:
    """Apply all ordered, additive migrations in one SQLite transaction."""
    with get_connection() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
        )
        for version, operation in MIGRATIONS:
            _apply_migration(conn, version, operation)


def schema_version() -> str | None:
    """Return the latest applied additive migration, if the database is initialized."""
    history = migration_history()
    return history[-1]["version"] if history else None

def migration_history() -> list[dict[str, str]]:
    """Expose applied migration metadata without exposing application data."""
    with get_connection() as conn:
        rows = conn.execute("SELECT version, applied_at FROM schema_migrations ORDER BY version").fetchall()
    return [dict(row) for row in rows]