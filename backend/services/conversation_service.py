"""XiaoG's conversation store. Providers never own the user's history."""
import json

from uuid import uuid4

from backend.database.db import get_connection, now_iso
from backend.services.product_info_service import product_info_service


CONVERSATION_COLUMNS = (
    "id, title, created_at, updated_at, archived_at, codex_thread_id, "
    "codex_last_synced_message_id, is_pinned, pinned_at, deleted_at, deleted_from, "
    "model_mode, manual_model, manual_reasoning_effort"
)


class ConversationService:
    def default_model_settings(self) -> dict:
        default_model = self.get_setting("default_model") or "deepseek"
        manual_model = default_model if default_model in {"deepseek", "terra"} else "deepseek"
        return {
            "model_mode": "auto" if default_model == "auto" else "manual",
            "manual_model": manual_model,
            "manual_reasoning_effort": self.get_manual_reasoning_preferences().get(manual_model),
        }

    def create_conversation(self, title: str | None = None) -> dict:
        conversation_id = str(uuid4())
        timestamp = now_iso()
        model_settings = self.default_model_settings()
        record = {
            "id": conversation_id, "title": (title or "新对话").strip()[:120] or "新对话",
            "created_at": timestamp, "updated_at": timestamp, "archived_at": None,
            "codex_thread_id": None, "codex_last_synced_message_id": None,
            "is_pinned": 0, "pinned_at": None, "deleted_at": None, "deleted_from": None,
            **model_settings,
        }
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO conversations(id, title, created_at, updated_at, archived_at, codex_thread_id, "
                "codex_last_synced_message_id, is_pinned, pinned_at, deleted_at, deleted_from, model_mode, manual_model, manual_reasoning_effort) "
                "VALUES (:id, :title, :created_at, :updated_at, :archived_at, :codex_thread_id, "
                ":codex_last_synced_message_id, :is_pinned, :pinned_at, :deleted_at, :deleted_from, :model_mode, :manual_model, :manual_reasoning_effort)", record)
        return record

    def update_model_settings(self, conversation_id: str, model_mode: str, manual_model: str, manual_reasoning_effort: str | None) -> dict | None:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET model_mode = ?, manual_model = ?, manual_reasoning_effort = ?, updated_at = ? WHERE id = ? AND deleted_at IS NULL",
                (model_mode, manual_model, manual_reasoning_effort, now_iso(), conversation_id),
            )
        return self.get_conversation(conversation_id) if result.rowcount else None
    def list_conversations(self, archived: bool = False, deleted: bool = False) -> list[dict]:
        if deleted:
            where = "deleted_at IS NOT NULL"
            order = "deleted_at DESC"
        elif archived:
            where = "deleted_at IS NULL AND archived_at IS NOT NULL"
            order = "updated_at DESC"
        else:
            where = "deleted_at IS NULL AND archived_at IS NULL"
            order = "is_pinned DESC, CASE WHEN is_pinned = 1 THEN pinned_at END DESC, updated_at DESC"
        with get_connection() as conn:
            rows = conn.execute(f"SELECT {CONVERSATION_COLUMNS} FROM conversations WHERE {where} ORDER BY {order}").fetchall()
        return [dict(row) for row in rows]

    def get_conversation(self, conversation_id: str) -> dict | None:
        with get_connection() as conn:
            row = conn.execute(f"SELECT {CONVERSATION_COLUMNS} FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        return dict(row) if row else None

    def archive_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET archived_at = ?, is_pinned = 0, pinned_at = NULL "
                "WHERE id = ? AND archived_at IS NULL AND deleted_at IS NULL",
                (now_iso(), conversation_id),
            )
        return result.rowcount > 0

    def restore_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET archived_at = NULL WHERE id = ? AND archived_at IS NOT NULL AND deleted_at IS NULL",
                (conversation_id,),
            )
        return result.rowcount > 0

    def move_to_trash(self, conversation_id: str) -> bool:
        conversation = self.get_conversation(conversation_id)
        if not conversation or conversation.get("deleted_at"):
            return False
        source = "archived" if conversation.get("archived_at") else "active"
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET deleted_at = ?, deleted_from = ? WHERE id = ? AND deleted_at IS NULL",
                (now_iso(), source, conversation_id),
            )
        return result.rowcount > 0

    def restore_from_trash(self, conversation_id: str) -> bool:
        conversation = self.get_conversation(conversation_id)
        if not conversation or not conversation.get("deleted_at"):
            return False
        with get_connection() as conn:
            if conversation.get("deleted_from") == "archived":
                result = conn.execute(
                    "UPDATE conversations SET deleted_at = NULL, deleted_from = NULL, archived_at = COALESCE(archived_at, ?) WHERE id = ?",
                    (now_iso(), conversation_id),
                )
            else:
                result = conn.execute(
                    "UPDATE conversations SET deleted_at = NULL, deleted_from = NULL, archived_at = NULL WHERE id = ?",
                    (conversation_id,),
                )
        return result.rowcount > 0

    def permanently_delete_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "DELETE FROM conversations WHERE id = ? AND (deleted_at IS NOT NULL OR archived_at IS NOT NULL)",
                (conversation_id,),
            )
        return result.rowcount > 0

    def empty_trash(self) -> int:
        with get_connection() as conn:
            result = conn.execute("DELETE FROM conversations WHERE deleted_at IS NOT NULL")
        return result.rowcount

    def delete_conversation(self, conversation_id: str) -> bool:
        """Backward-compatible name: ordinary deletion is now recoverable."""
        return self.move_to_trash(conversation_id)

    def pin_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET is_pinned = 1, pinned_at = ? "
                "WHERE id = ? AND archived_at IS NULL AND deleted_at IS NULL",
                (now_iso(), conversation_id),
            )
        return result.rowcount > 0

    def unpin_conversation(self, conversation_id: str) -> bool:
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET is_pinned = 0, pinned_at = NULL WHERE id = ? AND deleted_at IS NULL",
                (conversation_id,),
            )
        return result.rowcount > 0

    def update_title(self, conversation_id: str, title: str) -> bool:
        clean_title = " ".join(title.split())[:120]
        if not clean_title:
            return False
        with get_connection() as conn:
            result = conn.execute(
                "UPDATE conversations SET title = ?, updated_at = ? WHERE id = ? AND deleted_at IS NULL",
                (clean_title, now_iso(), conversation_id),
            )
        return result.rowcount > 0

    def set_codex_thread(self, conversation_id: str, thread_id: str) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE conversations SET codex_thread_id = ? WHERE id = ?", (thread_id, conversation_id))

    def clear_codex_thread(self, conversation_id: str) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE conversations SET codex_thread_id = NULL, codex_last_synced_message_id = NULL WHERE id = ?", (conversation_id,))

    def set_codex_last_synced_message(self, conversation_id: str, message_id: str) -> None:
        with get_connection() as conn:
            conn.execute("UPDATE conversations SET codex_last_synced_message_id = ? WHERE id = ?", (message_id, conversation_id))

    def messages_after(self, conversation_id: str, message_id: str | None) -> list[dict]:
        messages = self.list_messages(conversation_id)
        if not message_id:
            return messages
        for index, message in enumerate(messages):
            if message["id"] == message_id:
                return messages[index + 1:]
        return messages

    def list_messages(self, conversation_id: str) -> list[dict]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, conversation_id, role, content, provider, model, created_at FROM messages "
                "WHERE conversation_id = ? ORDER BY created_at ASC, rowid ASC",
                (conversation_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def add_message(self, conversation_id: str, role: str, content: str, provider: str | None = None, model: str | None = None) -> dict:
        message = {
            "id": str(uuid4()), "conversation_id": conversation_id, "role": role,
            "content": content, "provider": provider, "model": model, "created_at": now_iso(),
        }
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO messages(id, conversation_id, role, content, provider, model, created_at)
                   VALUES (:id, :conversation_id, :role, :content, :provider, :model, :created_at)""",
                message,
            )
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
        latest_user_message = next((item["content"] for item in reversed(history) if item["role"] == "user"), "")
        context += product_info_service.context_for(latest_user_message)
        return [{"role": "system", "content": context}] + [
            {"role": item["role"], "content": item["content"]}
            for item in history if item["role"] in ("user", "assistant", "tool")
        ]

    def record_usage(self, conversation_id: str, provider: str, model: str, usage: dict | None, estimated_cost: float | None, latency_ms: int, billing_type: str = "api") -> None:
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO model_usage(id, conversation_id, provider, model, billing_type, input_tokens, output_tokens, estimated_cost, latency_ms, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    str(uuid4()), conversation_id, provider, model, billing_type,
                    (usage or {}).get("prompt_tokens"), (usage or {}).get("completion_tokens"),
                    estimated_cost, latency_ms, now_iso(),
                ),
            )

    def get_setting(self, key: str) -> str:
        with get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else ""

    def update_settings(self, system_prompt: str, user_profile: str) -> None:
        with get_connection() as conn:
            timestamp = now_iso()
            conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'system_prompt'", (system_prompt, timestamp))
            conn.execute("UPDATE settings SET value = ?, updated_at = ? WHERE key = 'user_profile'", (user_profile, timestamp))

    def get_manual_reasoning_preferences(self) -> dict[str, str]:
        try:
            raw = json.loads(self.get_setting("manual_reasoning_preferences") or "{}")
        except json.JSONDecodeError:
            return {}
        if not isinstance(raw, dict):
            return {}
        return {
            model_id: effort
            for model_id, effort in raw.items()
            if isinstance(model_id, str) and isinstance(effort, str) and model_id and effort
        }

    def get_personalization_settings(self) -> dict[str, str | bool | dict[str, str]]:
        def setting_bool(key: str, default: bool) -> bool:
            value = self.get_setting(key).strip().lower()
            return default if value not in {"true", "false"} else value == "true"

        return {
            "theme_mode": self.get_setting("theme_mode") or "light",
            "color_scheme": self.get_setting("color_scheme") or "green",
            "assistant_avatar": self.get_setting("assistant_avatar") or "default",
            "user_avatar": self.get_setting("user_avatar") or "default",
            "font_scale": self.get_setting("font_scale") or "standard",
            "default_model": self.get_setting("default_model") or "deepseek",
            "reasoning_preference": self.get_setting("reasoning_preference") or "balanced",
            "chat_density": self.get_setting("chat_density") or "comfortable",
            "manual_reasoning_preferences": self.get_manual_reasoning_preferences(),
            "show_message_time": setting_bool("show_message_time", True),
            "enter_to_send": setting_bool("enter_to_send", True),
            "animations_enabled": setting_bool("animations_enabled", True),
            "ui_language": self.get_setting("ui_language") or "zh-CN",
        }

    def update_personalization_settings(self, values: dict[str, str | bool | dict[str, str] | None]) -> None:
        allowed = {
            "theme_mode", "color_scheme", "assistant_avatar", "user_avatar", "font_scale",
            "default_model", "reasoning_preference", "manual_reasoning_preferences", "chat_density",
            "show_message_time", "enter_to_send", "animations_enabled", "ui_language",
        }
        with get_connection() as conn:
            timestamp = now_iso()
            for key, value in values.items():
                if key not in allowed or value is None:
                    continue
                conn.execute(
                    "INSERT INTO settings(key, value, updated_at) VALUES (?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
                    (key, json.dumps(value, ensure_ascii=False, separators=(",", ":")) if key == "manual_reasoning_preferences" else str(value).lower() if isinstance(value, bool) else value, timestamp),
                )


conversation_service = ConversationService()