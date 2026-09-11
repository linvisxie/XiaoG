"""Phase-1 memory interface. Retrieval is deliberately simple until Phase 6."""

from backend.database.db import get_connection


class MemoryService:
    def get_user_profile(self) -> str:
        with get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = 'user_profile'").fetchone()
        return row["value"] if row else ""

    def get_relevant_memories(self, _query: str) -> list[str]:
        # Later: embeddings + semantic search. Keep a stable service boundary now.
        return []


memory_service = MemoryService()
