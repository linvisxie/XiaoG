"""Versioned, local-only backup and safe additive import for XiaoG-owned data."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.database.db import get_connection


class BackupFormatError(ValueError):
    """The supplied local backup does not match XiaoG's supported format."""


class BackupConflictError(BackupFormatError):
    """Import would overwrite existing local user data."""


class BackupService:
    FORMAT_VERSION = 1
    TABLES = ("conversations", "messages", "settings", "memories", "file_artifacts")

    def export_snapshot(self) -> dict[str, Any]:
        with get_connection() as conn:
            data = {table: [dict(row) for row in conn.execute(f"SELECT * FROM {table}").fetchall()] for table in self.TABLES}
        return {"format": "xiaog-local-backup", "version": self.FORMAT_VERSION, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "data": data}

    def import_snapshot(self, snapshot: dict[str, Any]) -> dict[str, int]:
        data = self._validated_data(snapshot)
        with get_connection() as conn:
            for table in self.TABLES:
                if table == "settings":
                    existing_settings = {row["key"]: row["value"] for row in conn.execute("SELECT key, value FROM settings")}
                    conflicts = [row["key"] for row in data[table] if row["key"] in existing_settings and row["value"] != existing_settings[row["key"]]]
                else:
                    existing = {row[0] for row in conn.execute(f"SELECT id FROM {table}").fetchall()}
                    conflicts = list(existing.intersection(row["id"] for row in data[table]))
                if conflicts:
                    raise BackupConflictError(f"导入会覆盖现有 {table} 数据，已安全取消。")
            for table in self.TABLES:
                for row in data[table]:
                    if table == "settings" and conn.execute("SELECT 1 FROM settings WHERE key = ?", (row["key"],)).fetchone():
                        continue
                    columns = list(row)
                    conn.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})", tuple(row[column] for column in columns))
        return {table: len(data[table]) for table in self.TABLES}

    def _validated_data(self, snapshot: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
        if not isinstance(snapshot, dict) or snapshot.get("format") != "xiaog-local-backup" or snapshot.get("version") != self.FORMAT_VERSION:
            raise BackupFormatError("不支持的 XiaoG 本地备份格式。")
        data = snapshot.get("data")
        if not isinstance(data, dict):
            raise BackupFormatError("备份缺少数据内容。")
        result = {}
        for table in self.TABLES:
            rows = data.get(table, [])
            if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
                raise BackupFormatError(f"备份中的 {table} 数据无效。")
            result[table] = rows
        return result


backup_service = BackupService()
