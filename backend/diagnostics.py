"""Safe, local diagnostics primitives shared by XiaoG runtime components."""

from __future__ import annotations

from collections import deque
from copy import copy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import logging
from pathlib import Path
import re
from threading import Lock
from typing import Any


_SECRET_PATTERNS = (
    re.compile(r"(?i)(authorization\s*[:=]\s*(?:bearer\s+)?)\S+"),
    re.compile(r"(?i)(\b(?:api[_-]?key|token|secret|password)\b\s*[:=]\s*[\"']?)([^\s,\"'}]+)"),
    re.compile(r"\b(?:sk|ds)-[A-Za-z0-9_\-]{8,}\b"),
)


def redact_text(value: object) -> str:
    """Return a log-safe representation without known credential values."""
    text = str(value)
    for pattern in _SECRET_PATTERNS:
        if pattern.groups >= 2:
            text = pattern.sub(r"\1[REDACTED]", text)
        else:
            text = pattern.sub("[REDACTED]", text)
    return text


class RedactingFormatter(logging.Formatter):
    """Format a copied record so logging cannot mutate application state."""

    def format(self, record: logging.LogRecord) -> str:
        safe = copy(record)
        safe.msg = redact_text(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                safe.args = {key: redact_text(value) for key, value in record.args.items()}
            else:
                safe.args = tuple(redact_text(value) for value in record.args)
        rendered = super().format(safe)
        return redact_text(rendered)


@dataclass(frozen=True)
class DiagnosticEvent:
    timestamp: str
    level: str
    logger: str
    message: str


class RecentDiagnosticsHandler(logging.Handler):
    """Bounded, credential-redacted events for future local diagnostics UI."""

    def __init__(self, limit: int = 200) -> None:
        super().__init__()
        self._events: deque[DiagnosticEvent] = deque(maxlen=limit)
        self._lock = Lock()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            event = DiagnosticEvent(
                timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
                level=record.levelname,
                logger=record.name,
                message=redact_text(record.getMessage()),
            )
            with self._lock:
                self._events.append(event)
        except Exception:
            self.handleError(record)

    def snapshot(self, limit: int = 100) -> list[dict[str, str]]:
        safe_limit = max(1, min(limit, 200))
        with self._lock:
            return [asdict(event) for event in list(self._events)[-safe_limit:]]


recent_diagnostics = RecentDiagnosticsHandler()


def configure_logging(log_dir: Path, level_name: str) -> None:
    """Configure idempotent, redacted local logging for the process."""
    log_dir.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(getattr(logging, level_name.upper(), logging.INFO))
    if getattr(root, "_xiaog_diagnostics_configured", False):
        return

    formatter = RedactingFormatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = logging.FileHandler(log_dir / "xiaog.log", encoding="utf-8")
    console_handler = logging.StreamHandler()
    for handler in (file_handler, console_handler, recent_diagnostics):
        handler.setFormatter(formatter)
        root.addHandler(handler)
    root._xiaog_diagnostics_configured = True  # type: ignore[attr-defined]


def diagnostic_logger(component: str) -> logging.Logger:
    return logging.getLogger(f"xiaog.{component}")


def log_event(logger: logging.Logger, level: int, event: str, **fields: Any) -> None:
    """Log low-cardinality component events without user content or secrets."""
    details = " ".join(f"{key}={redact_text(value)}" for key, value in sorted(fields.items()))
    logger.log(level, "event=%s%s", event, f" {details}" if details else "")