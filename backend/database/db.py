"""SQLite connection and schema initialization for XiaoG-owned data."""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from backend.config import settings


DEFAULT_SYSTEM_PROMPT = """你叫“小G”。

交流原则：自然、诚实、直接、简洁；不刻意讨好用户；能够理解用户，但保持独立判断；发现用户逻辑有问题时可以指出；不知道的事情明确说不知道；不要为了显得聪明而编造事实；不要机械重复用户长期资料。"""


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


def initialize_database() -> None:
    with get_connection() as conn:
        conn.executescript("""
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
        """)
        # Additive migration: never recreate or clear the user's SQLite database.
        conversation_columns = {row["name"] for row in conn.execute("PRAGMA table_info(conversations)").fetchall()}
        if "archived_at" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN archived_at TEXT")
        if "codex_thread_id" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN codex_thread_id TEXT")
        if "codex_last_synced_message_id" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN codex_last_synced_message_id TEXT")
        if "is_pinned" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER NOT NULL DEFAULT 0")
        if "pinned_at" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN pinned_at TEXT")
        if "deleted_at" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN deleted_at TEXT")
        if "deleted_from" not in conversation_columns:
            conn.execute("ALTER TABLE conversations ADD COLUMN deleted_from TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_archived_updated ON conversations(archived_at, updated_at DESC)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_state ON conversations(deleted_at, archived_at, is_pinned DESC, pinned_at DESC, updated_at DESC)")
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
            ("system_prompt", DEFAULT_SYSTEM_PROMPT, now_iso()),
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
            ("user_profile", "", now_iso()),
        )
        # Additive defaults for the extensible, local user-preferences store.
        # Existing databases keep all settings and conversation data intact.
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
            ("theme_mode", "light", now_iso()),
        )
        conn.execute(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
            ("color_scheme", "green", now_iso()),
        )
        for key, value in (
            ("assistant_avatar", "default"),
            ("user_avatar", "default"),
            ("font_scale", "standard"),
            ("default_model", "deepseek"),
            ("reasoning_preference", "balanced"),
            ("chat_density", "comfortable"),
            ("show_message_time", "true"),
            ("enter_to_send", "true"),
            ("animations_enabled", "true"),
            ("ui_language", "zh-CN"),
        ):
            conn.execute(
                "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
                (key, value, now_iso()),
            )
