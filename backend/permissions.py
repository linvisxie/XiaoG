"""Local-first capability boundary for future XiaoG actions.

This module deliberately has no users, accounts, roles, grants, network calls,
or persistence. It classifies an action before a future tool executes it so
that every new integration has one conservative, testable decision point.
Existing Phase 5 routes do not opt into this contract yet and therefore retain
their established behaviour.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class PermissionAction(StrEnum):
    """The small action vocabulary required by XiaoG's local roadmap."""

    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXTERNAL_ACTION = "external_action"
    SENSITIVE_ACTION = "sensitive_action"


class PermissionScope(StrEnum):
    """Execution locality; only local scope is supported at this stage."""

    LOCAL = "local"
    REMOTE = "remote"


class PermissionDecision(StrEnum):
    ALLOW = "allow"
    REQUIRE_CONFIRMATION = "require_confirmation"
    DENY = "deny"


@dataclass(frozen=True)
class PermissionRequest:
    action: PermissionAction
    resource: str
    scope: PermissionScope = PermissionScope.LOCAL
    reason: str | None = None


@dataclass(frozen=True)
class PermissionResult:
    decision: PermissionDecision
    reason: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


class LocalPermissionPolicy:
    """A deterministic policy for local XiaoG capabilities.

    Irreversible, external, and sensitive actions must be designed with an
    explicit user-facing confirmation or a dedicated secure flow later. They
    are intentionally not granted implicitly by a model or a tool registry.
    """

    def evaluate(self, request: PermissionRequest) -> PermissionResult:
        if request.scope is not PermissionScope.LOCAL:
            return PermissionResult(PermissionDecision.DENY, "仅支持本地执行范围。")
        if not request.resource.strip():
            return PermissionResult(PermissionDecision.DENY, "必须声明受影响的本地资源。")
        if request.action in (PermissionAction.READ, PermissionAction.WRITE):
            return PermissionResult(PermissionDecision.ALLOW, "允许本地读写操作。")
        if request.action in (PermissionAction.DELETE, PermissionAction.EXTERNAL_ACTION):
            return PermissionResult(PermissionDecision.REQUIRE_CONFIRMATION, "该操作需要明确用户确认。")
        if request.action is PermissionAction.SENSITIVE_ACTION:
            return PermissionResult(PermissionDecision.DENY, "敏感操作需要专用安全流程。")
        return PermissionResult(PermissionDecision.DENY, "不支持的权限操作。")


local_permission_policy = LocalPermissionPolicy()