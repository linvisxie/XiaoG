"""In-memory invite authentication and bounded abuse controls for ephemeral Preview."""
from __future__ import annotations
import secrets, time
from contextvars import ContextVar
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from backend.config import RuntimeConfig

@dataclass(frozen=True)
class PreviewSession:
    token: str; invite_id: str; database_path: Path; expires_at: float

class PreviewAccessControl:
    def __init__(self, runtime: RuntimeConfig):
        self.runtime=runtime; self.sessions={}; self.requests=defaultdict(deque); self.generations=defaultdict(deque); self.active=defaultdict(int); self.global_active=0; self.current_invite=ContextVar("preview_invite", default=None)
    def reset(self): self.sessions.clear(); self.requests.clear(); self.generations.clear(); self.active.clear(); self.global_active=0
    def exchange(self, credential: str, session_dir: Path) -> PreviewSession | None:
        for invite_id, expected in self.runtime.preview_invites.items():
            if secrets.compare_digest(credential, expected):
                token=secrets.token_urlsafe(32); session=PreviewSession(token, invite_id, session_dir / f"{secrets.token_hex(16)}.db", time.monotonic()+self.runtime.preview_session_ttl_seconds); self.sessions[token]=session; return session
        return None
    def session(self, token: str | None) -> PreviewSession | None:
        item=self.sessions.get(token or "")
        if not item or item.expires_at <= time.monotonic(): self.sessions.pop(token or "", None); return None
        return item
    def logout(self, token: str | None): self.sessions.pop(token or "", None)
    def _allow(self, bucket, key, limit):
        now=time.monotonic(); q=bucket[key]
        while q and q[0] <= now-self.runtime.preview_window_seconds: q.popleft()
        if len(q)>=limit: return False
        q.append(now); return True
    def allow_request(self, invite_id: str) -> bool: return self._allow(self.requests, invite_id, self.runtime.preview_request_limit) and self._allow(self.requests, "__global__", self.runtime.preview_request_limit*max(1,len(self.runtime.preview_invites)))
    def acquire_generation(self, invite_id: str) -> bool:
        if self.active[invite_id]>=self.runtime.preview_max_concurrent_per_invite or self.global_active>=self.runtime.preview_max_concurrent_global: return False
        if not self._allow(self.generations, invite_id, self.runtime.preview_generation_limit) or not self._allow(self.generations, "__global__", self.runtime.preview_generation_limit*max(1,len(self.runtime.preview_invites))): return False
        self.active[invite_id]+=1; self.global_active+=1; return True
    def release_generation(self, invite_id: str):
        if self.active[invite_id]: self.active[invite_id]-=1; self.global_active=max(0,self.global_active-1)
