"""XiaoG's conversation store. Providers never own the user's history."""

from datetime import datetime, timezone
from uuid import uuid4

from backend.database.db import get_connection, now_iso


class ConversationService:
    def create_conversation(self, title: str | None = None) -> dict:
        conversation_id = str(uuid4())
        timestamp = now_iso()
        record = {"id": conversation_id, "title": (title or "新对话").strip()[:120] or "新对话", "created_at": timestamp, "updated_at": timestamp, "archived_at": None}
        with get_connection() as conn:
            conn.execute("INSERT INTO conversations(id, title, created_at, updated_at, archived_at) VALUES (?, ?, ?, ?, ?)", tuple(record.values()))
        return record

    def list_conversations(self, archived: bool = False) -> list[dict]:
        archived_clause = "IS NOT NULL" if archived else "IS NULL"
        with get_connection() as conn:
            rows = conn.execute(
                f"SELECT id, title, created_at, updated_at, archived_at FROM conversations "
                f"WHERE archived_at {archived_clause} ORDER BY updated_at DESC"
            ).fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> dict | None:
        with get_connection() as conn:
            row = conn.execute("SELECT id, title, created_at, updated_at, archived_at FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        return dict(row) if row else None

    def archive_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET archived_at = ? WHERE id = ? AND archived_at IS NULL",
                (now_iso(), conversation_id),
            )
        return result.rowcount > 0

    def restore_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET archived_at = NULL WHERE id = ? AND archived_at IS NOT NULL",
                (conversation_id,),
            )
        return result.rowcount > 0

    def delete_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        return result.rowcount > 0

    def list_messages(self, conversation_id: str) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute("SELECT id, conversation_id, role, content, provider, model, created_at FROM messages WHERE conversation_id = ? ORDER BY created_at ASC, rowid ASC", (conversation_id,)).fetchall()
        return [dict(row) for row in rows]

    def add_message(self, conversation_id: str, role: str, content: str, provider: str | None = None, model: str | None = None) -> dict:
        message = {
            "id": str(uuid4()), "conversation_id": conversation_id, "role": role,
            "content": content, "provider": provider, "model": model, "created_at": now_iso(),
        }
        with get_connection() as conn:
            conn.execute("""INSERT INTO messages(id, conversation_id, role, content, provider, model, created_at)
                         VALUES (:id, :conversation_id, :role, :content, :provider, :model, :created_at)""", message)
            conn.execute("UPDATE conversations SET updated_at = ? WHERE id = ?", (message["created_at"], conversation_id))
        return message

    def set_title_from_first_message(self, conversation_id: str, content: str) -> None:
        conversation = self.get_conversation(conversation_id)
        if conversation and conversation["title"] == "新对话":
            title = " ".join(content.split())[:36] or "新对话"
            with get_connection() as conn:
                conn.execute("UPDATE conversations SET title = ?, updated_at = ? WHERE id = ?", (title, now_iso(), conversation_id))

    def build_model_messages(self, conversation_id: str, system_prompt: str, user_profile: str, memories: list[str]) -> list[dict[str, str]]:
        context = system_prompt
        if user_profile:
            context += f"\n\n用户资料（仅在相关时自然使用，不要机械复述）：\n{user_profile}"
        if memories:
            context += "\n\n相关长期记忆：\n" + "\n".join(f"- {item}" for item in memories)
        history = self.list_messages(conversation_id)[-30:]
        return [{"role": "system", "content": context}] + [{"role": item["role"], "content": item["content"]} for item in history if item["role"] in ("user", "assistant", "tool")]

    def record_usage(self, conversation_id: str, provider: str, model: str, usage: dict | None, estimated_cost: float | None, latency_ms: int, billing_type: str = "api") -> None:
        with get_connection() as conn:
            conn.execute("""INSERT INTO model_usage(id, conversation_id, provider, model, billing_type, input_tokens, output_tokens, estimated_cost, latency_ms, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                str(uuid4()), conversation_id, provider, model, billing_type,
                (usage or {}).get("prompt_tokens"), (usage or {}).get("completion_tokens"),
                estimated_cost, latency_ms, now_iso(),
            ))

    def get_setting(self, key: str) -> str:
        with get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else ""

    def update_settings(self, system_prompt: str, user_profile: str) -> None:
        with get_connection() as conn:
            timestamp = now_iso()
            conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'system_prompt'", (system_prompt, timestamp))
            conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'user_profile'", (user_profile, timestamp))


conversation_service = ConversationService()
