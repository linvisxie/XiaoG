"""Local metadata lifecycle for future XiaoG files and artifacts.

No file content, upload endpoint, project system, or cloud storage is enabled
here. This service establishes one persistent lifecycle vocabulary first.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from uuid import uuid4
from backend.database.db import get_connection, now_iso

class ArtifactKind(StrEnum):
    TEMPORARY_CHAT_ATTACHMENT = "temporary_chat_attachment"
    ARTIFACT = "artifact"
    KNOWLEDGE_FILE = "knowledge_file"
    PROJECT_ASSET = "project_asset"
class ArtifactScope(StrEnum):
    CONVERSATION = "conversation"
    PROJECT = "project"
    GLOBAL = "global"
class ArtifactPersistence(StrEnum):
    TEMPORARY = "temporary"
    DURABLE = "durable"
@dataclass(frozen=True)
class ArtifactLifecycle:
    scope: ArtifactScope
    persistence: ArtifactPersistence
    requires_conversation_owner: bool = False
    requires_project_owner: bool = False
LIFECYCLE_BY_KIND = {
    ArtifactKind.TEMPORARY_CHAT_ATTACHMENT: ArtifactLifecycle(ArtifactScope.CONVERSATION, ArtifactPersistence.TEMPORARY, True),
    ArtifactKind.ARTIFACT: ArtifactLifecycle(ArtifactScope.CONVERSATION, ArtifactPersistence.DURABLE, True),
    ArtifactKind.KNOWLEDGE_FILE: ArtifactLifecycle(ArtifactScope.GLOBAL, ArtifactPersistence.DURABLE),
    ArtifactKind.PROJECT_ASSET: ArtifactLifecycle(ArtifactScope.PROJECT, ArtifactPersistence.DURABLE, False, True),
}
class ArtifactService:
    def lifecycle_for(self, kind: ArtifactKind) -> ArtifactLifecycle:
        return LIFECYCLE_BY_KIND[kind]
    def create_metadata(self, kind: ArtifactKind, display_name: str, *, conversation_id: str | None = None, project_id: str | None = None, storage_reference: str | None = None) -> dict:
        lifecycle=self.lifecycle_for(kind); name=" ".join(display_name.split())[:240]
        if not name: raise ValueError("文件或 Artifact 必须具有名称。")
        if lifecycle.requires_conversation_owner != bool(conversation_id): raise ValueError("该类型必须且只能归属于一个 Conversation。")
        if lifecycle.requires_project_owner != bool(project_id): raise ValueError("该类型必须且只能归属于一个 Project。")
        if conversation_id and project_id: raise ValueError("一个对象不能同时属于 Conversation 和 Project。")
        timestamp=now_iso(); record={"id":str(uuid4()),"kind":kind,"scope":lifecycle.scope,"persistence":lifecycle.persistence,"display_name":name,"owner_conversation_id":conversation_id,"owner_project_id":project_id,"storage_reference":storage_reference,"deleted_at":None,"created_at":timestamp,"updated_at":timestamp}
        with get_connection() as conn:
            conn.execute("""INSERT INTO file_artifacts(id,kind,scope,persistence,display_name,owner_conversation_id,owner_project_id,storage_reference,deleted_at,created_at,updated_at) VALUES (:id,:kind,:scope,:persistence,:display_name,:owner_conversation_id,:owner_project_id,:storage_reference,:deleted_at,:created_at,:updated_at)""",record)
        return self.get_metadata(record["id"])
    def get_metadata(self, artifact_id: str) -> dict | None:
        with get_connection() as conn: row=conn.execute("SELECT * FROM file_artifacts WHERE id = ?",(artifact_id,)).fetchone()
        return dict(row) if row else None
    def move_to_trash(self, artifact_id: str) -> bool:
        timestamp=now_iso()
        with get_connection() as conn: result=conn.execute("UPDATE file_artifacts SET deleted_at=?,updated_at=? WHERE id=? AND deleted_at IS NULL",(timestamp,timestamp,artifact_id))
        return result.rowcount>0
    def restore_from_trash(self, artifact_id: str) -> bool:
        with get_connection() as conn: result=conn.execute("UPDATE file_artifacts SET deleted_at=NULL,updated_at=? WHERE id=? AND deleted_at IS NOT NULL",(now_iso(),artifact_id))
        return result.rowcount>0
artifact_service=ArtifactService()