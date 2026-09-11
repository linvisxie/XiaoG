"""Unified local search entry point for XiaoG-owned data."""

from __future__ import annotations

from backend.database.db import get_connection


class SearchService:
    """Search boundary shared by current and future XiaoG data domains.

    Conversation Search is the only enabled domain in v1. File, memory,
    knowledge, and project search can join this service without adding
    separate, competing search paths.
    """

    def search(self, query: str, *, limit: int = 50) -> dict[str, list[dict]]:
        return {"conversations": self.search_conversations(query, limit=limit)}

    def search_conversations(self, query: str, *, limit: int = 50) -> list[dict]:
        clean_query = " ".join(query.split())
        if not clean_query:
            return []

        safe_limit = max(1, min(limit, 100))
        pattern = f"%{self._escape_like(clean_query)}%"
        with get_connection() as conn:
            rows = conn.execute(
                """
                WITH matches AS (
                    SELECT
                        c.id AS conversation_id,
                        c.title AS conversation_title,
                        'title' AS match_type,
                        NULL AS message_id,
                        c.title AS matched_content,
                        c.updated_at AS matched_at,
                        c.archived_at IS NOT NULL AS is_archived
                    FROM conversations AS c
                    WHERE c.deleted_at IS NULL
                      AND c.title LIKE ? ESCAPE '!'

                    UNION ALL

                    SELECT
                        c.id AS conversation_id,
                        c.title AS conversation_title,
                        CASE m.role
                            WHEN 'user' THEN 'user_message'
                            ELSE 'assistant_message'
                        END AS match_type,
                        m.id AS message_id,
                        m.content AS matched_content,
                        m.created_at AS matched_at,
                        c.archived_at IS NOT NULL AS is_archived
                    FROM messages AS m
                    INNER JOIN conversations AS c ON c.id = m.conversation_id
                    WHERE c.deleted_at IS NULL
                      AND m.role IN ('user', 'assistant')
                      AND m.content LIKE ? ESCAPE '!'
                )
                SELECT conversation_id, conversation_title, match_type, message_id,
                       matched_content, matched_at, is_archived
                FROM matches
                ORDER BY
                    CASE match_type
                        WHEN 'title' THEN 0
                        WHEN 'user_message' THEN 1
                        ELSE 2
                    END,
                    matched_at DESC
                LIMIT ?
                """,
                (pattern, pattern, safe_limit),
            ).fetchall()

        results = []
        for row in rows:
            record = dict(row)
            record["is_archived"] = bool(record["is_archived"])
            record["snippet"] = "" if record["match_type"] == "title" else self._snippet(record["matched_content"], clean_query)
            record.pop("matched_content", None)
            results.append(record)
        return results

    @staticmethod
    def _escape_like(value: str) -> str:
        return value.replace("!", "!!").replace("%", "!%").replace("_", "!_")

    @staticmethod
    def _snippet(content: str, query: str, *, radius: int = 54) -> str:
        compact = " ".join(content.split())
        if len(compact) <= radius * 2 + len(query):
            return compact
        position = compact.casefold().find(query.casefold())
        if position < 0:
            return compact[: radius * 2].rstrip() + "…"
        start = max(0, position - radius)
        end = min(len(compact), position + len(query) + radius)
        prefix = "…" if start else ""
        suffix = "…" if end < len(compact) else ""
        return prefix + compact[start:end].strip() + suffix


search_service = SearchService()