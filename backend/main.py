"""FastAPI application entry point for XiaoG."""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.db import initialize_database
from backend.database.models import ChatRequest, ConversationCreate, ConversationTitleUpdate, SettingsUpdate, ConversationModelSettingsUpdate
from backend.database.models import PersonalizationSettingsUpdate
from backend.pricing import estimate_deepseek_cost
from backend.providers.base import ProviderError, ReasoningEffortError
from backend.router.model_router import model_router
from backend.services.codex_app_server_manager import codex_app_server_manager
from backend.services.conversation_service import conversation_service
from backend.services.memory_service import memory_service
from backend.services.search_service import search_service
from backend.services.product_info_service import product_info_service


def configure_logging() -> None:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=getattr(logging, settings.log_level, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.FileHandler(settings.log_dir / "xiaog.log", encoding="utf-8"), logging.StreamHandler()],
    )


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    initialize_database()
    logging.getLogger(__name__).info("XiaoG database initialized")
    try:
        await codex_app_server_manager.start()
    except ProviderError as exc:
        # DeepSeek remains usable if Codex is unavailable at application boot.
        logging.getLogger(__name__).warning("Codex App Server was not ready at startup: %s", exc)
    try:
        yield
    finally:
        await codex_app_server_manager.close()


app = FastAPI(title="XiaoG", version=product_info_service.public_info().get("version", "unknown"), lifespan=lifespan)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def event_stream(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    info = product_info_service.public_info()
    return {"status": "ok", "app": "XiaoG", "version": info.get("version", "unknown"), "phase": info.get("phase", "unknown")}


@app.get("/api/about")
async def about() -> dict:
    info = product_info_service.public_info()
    if not info.get("version"):
        raise HTTPException(status_code=500, detail="无法读取 XiaoG 产品信息。")
    return info


@app.get("/api/provider-status")
async def provider_status() -> dict:
    return await model_router.status()


@app.get("/api/model-registry")
async def get_model_registry() -> dict:
    """Expose credential-free product model metadata for future XiaoG features."""
    return await model_router.registry.snapshot()


@app.get("/api/conversations")
async def list_conversations(archived: bool = False, deleted: bool = False) -> list[dict]:
    return conversation_service.list_conversations(archived=archived, deleted=deleted)


@app.get("/api/search")
async def search(query: str = Query(default="", max_length=120)) -> dict:
    """Search XiaoG-owned data through the shared Search Service."""
    result = search_service.search(query)
    return {"query": " ".join(query.split()), "results": result["conversations"]}


async def _resolve_manual_reasoning_effort(selection_key: str, preferences: dict[str, str]) -> tuple[str | None, dict]:
    """Resolve one Manual model through live Registry capability and System Defaults."""
    registry = (await model_router.status()).get("registry") or {}
    model = next(
        (item for item in registry.get("models") or [] if item.get("selection_key") == selection_key),
        None,
    )
    if not model:
        return None, {}
    options = [effort for effort in model.get("supported_reasoning_efforts") or [] if isinstance(effort, str)]
    if not options:
        return None, model
    system_preferences = conversation_service.get_manual_reasoning_preferences()
    requested = preferences.get(selection_key)
    system_default = system_preferences.get(selection_key) or system_preferences.get(model.get("model_id"))
    registry_default = model.get("default_reasoning_effort")
    effort = requested if requested in options else system_default if system_default in options else registry_default if registry_default in options else options[0]
    return effort, model


async def resolved_default_conversation_model_settings() -> dict:
    """Resolve persisted System Defaults through the live Registry capability snapshot."""
    defaults = conversation_service.default_model_settings()
    if defaults["model_mode"] == "auto":
        return defaults
    effort, _model = await _resolve_manual_reasoning_effort(defaults["manual_model"], {})
    preferences = {defaults["manual_model"]: effort} if effort else {}
    return {**defaults, "manual_reasoning_effort": effort, "manual_reasoning_preferences": preferences}


async def resolved_conversation_model_settings(conversation: dict, payload: ConversationModelSettingsUpdate) -> dict:
    """Merge explicit per-model choices; unseen models always begin at their System Default."""
    preferences = {
        **(conversation.get("manual_reasoning_preferences") or {}),
        **payload.manual_reasoning_preferences,
    }
    if payload.model_mode == "auto":
        return {
            "model_mode": "auto",
            "manual_model": payload.manual_model,
            "manual_reasoning_effort": None,
            "manual_reasoning_preferences": preferences,
        }
    effort, _model = await _resolve_manual_reasoning_effort(payload.manual_model, preferences)
    if effort:
        preferences[payload.manual_model] = effort
    else:
        preferences.pop(payload.manual_model, None)
    return {
        "model_mode": "manual",
        "manual_model": payload.manual_model,
        "manual_reasoning_effort": effort,
        "manual_reasoning_preferences": preferences,
    }

@app.get("/api/conversations/default-model-settings")
async def get_default_conversation_model_settings() -> dict:
    return await resolved_default_conversation_model_settings()


@app.post("/api/conversations", status_code=201)
async def create_conversation(payload: ConversationCreate) -> dict:
    return conversation_service.create_conversation(
        payload.title,
        await resolved_default_conversation_model_settings(),
    )

@app.patch("/api/conversations/{conversation_id}")
async def update_conversation_title(conversation_id: str, payload: ConversationTitleUpdate) -> dict:
    if not conversation_service.update_title(conversation_id, payload.title):
        raise HTTPException(status_code=404, detail="找不到该会话，或标题不能为空。")
    conversation = conversation_service.get_conversation(conversation_id)
    assert conversation is not None
    return conversation


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict:
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="找不到该会话。")
    return {**conversation, "messages": conversation_service.list_messages(conversation_id)}

@app.put("/api/conversations/{conversation_id}/model-settings")
async def update_conversation_model_settings(conversation_id: str, payload: ConversationModelSettingsUpdate) -> dict:
    existing = conversation_service.get_conversation(conversation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="找不到可更新的会话。")
    resolved = await resolved_conversation_model_settings(existing, payload)
    conversation = conversation_service.update_model_settings(conversation_id, **resolved)
    assert conversation is not None
    return conversation

@app.delete("/api/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str) -> None:
    if not conversation_service.move_to_trash(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可移入回收站的会话。")


@app.post("/api/conversations/{conversation_id}/pin")
async def pin_conversation(conversation_id: str) -> dict:
    if not conversation_service.pin_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可置顶的会话。")
    return {"message": "会话已置顶。"}


@app.post("/api/conversations/{conversation_id}/unpin")
async def unpin_conversation(conversation_id: str) -> dict:
    if not conversation_service.unpin_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可取消置顶的会话。")
    return {"message": "已取消置顶。"}


@app.post("/api/conversations/{conversation_id}/restore-deleted")
async def restore_deleted_conversation(conversation_id: str) -> dict:
    if not conversation_service.restore_from_trash(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可恢复的会话。")
    return {"message": "会话已恢复。"}


@app.delete("/api/conversations/{conversation_id}/permanent", status_code=204)
async def permanently_delete_conversation(conversation_id: str) -> None:
    if not conversation_service.permanently_delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可永久删除的会话。")


@app.delete("/api/trash")
async def empty_trash() -> dict:
    return {"deleted": conversation_service.empty_trash()}


@app.post("/api/conversations/{conversation_id}/archive")
async def archive_conversation(conversation_id: str) -> dict:
    if not conversation_service.archive_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可归档的会话。")
    return {"message": "会话已归档。"}


@app.post("/api/conversations/{conversation_id}/restore")
async def restore_conversation(conversation_id: str) -> dict:
    if not conversation_service.restore_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="找不到可恢复的会话。")
    return {"message": "会话已恢复。"}
@app.get("/api/settings")
async def get_settings() -> dict:
    return {"system_prompt": conversation_service.get_setting("system_prompt"), "user_profile": conversation_service.get_setting("user_profile")}


@app.put("/api/settings")
async def update_settings(payload: SettingsUpdate) -> dict:
    conversation_service.update_settings(payload.system_prompt.strip(), payload.user_profile.strip())
    return {"message": "设置已保存。"}


@app.get("/api/settings/personalization")
async def get_personalization_settings() -> dict:
    return conversation_service.get_personalization_settings()


@app.put("/api/settings/personalization")
async def update_personalization_settings(payload: PersonalizationSettingsUpdate) -> dict:
    conversation_service.update_personalization_settings(payload.model_dump())
    return conversation_service.get_personalization_settings()


@app.post("/api/conversations/{conversation_id}/chat")
async def chat(conversation_id: str, payload: ChatRequest) -> StreamingResponse:
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="找不到该会话。")
    if conversation.get("deleted_at"):
        raise HTTPException(status_code=409, detail="请先从回收站恢复该会话后再继续聊天。")
    if conversation.get("archived_at"):
        raise HTTPException(status_code=409, detail="请先恢复已归档会话后再继续聊天。")
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="消息不能为空。")

    try:
        context_characters = sum(len(str(message.get("content") or "")) for message in conversation_service.list_messages(conversation_id))
        if conversation.get("model_mode") == "auto":
            provider, display_name, selected_effort, model_metadata, routing = await model_router.select_auto(content, context_characters)
        else:
            provider, display_name, selected_effort, model_metadata = await model_router.select_manual(
                conversation.get("manual_model") or "deepseek", conversation.get("manual_reasoning_effort")
            )
            routing = None
    except ReasoningEffortError as exc:
        raise HTTPException(status_code=422, detail={"code": "unsupported_reasoning_effort", "message": str(exc)}) from exc
    except ProviderError as exc:
        raise HTTPException(status_code=503, detail={"code": "provider_unavailable", "message": str(exc)}) from exc

    user_message = conversation_service.add_message(conversation_id, "user", content)
    conversation_service.set_title_from_first_message(conversation_id, content)
    async def generate():
        answer = ""
        usage = None
        actual_model = model_metadata["model_id"]
        provider_name = provider.name
        billing_type = getattr(provider, "billing_type", "api")
        started = time.perf_counter()
        try:
            system_prompt = conversation_service.get_setting("system_prompt")
            profile = memory_service.get_user_profile()
            memories = memory_service.get_relevant_memories(content)
            model_messages = conversation_service.build_model_messages(conversation_id, system_prompt, profile, memories)
            yield event_stream("meta", {"provider": provider.name, "provider_id": model_metadata["provider_id"], "model": actual_model, "model_id": actual_model, "display_name": display_name, "reasoning_effort": selected_effort, "routing": routing})
            stream = (
                provider.stream_chat(
                    model_messages,
                    selected_effort,
                    conversation_id=conversation_id,
                    user_message_id=user_message["id"],
                )
                if provider.name == "openai_codex"
                else provider.stream_chat(model_messages, selected_effort)
            )
            async for item in stream:
                if item["type"] == "delta":
                    answer += item["content"]
                    yield event_stream("delta", {"content": item["content"]})
                elif item["type"] == "usage":
                    usage = item["usage"]
                    actual_model = item.get("model") or actual_model
            if not answer:
                raise ProviderError("模型没有返回可显示的内容，请稍后重试。")
            latency_ms = round((time.perf_counter() - started) * 1000)
            conversation_service.add_message(conversation_id, "assistant", answer, provider_name, actual_model)
            cost = estimate_deepseek_cost(actual_model, usage) if provider.name == "deepseek" else None
            conversation_service.record_usage(conversation_id, provider_name, actual_model, usage, cost, latency_ms, billing_type)
            yield event_stream("done", {"provider": provider.name, "provider_id": model_metadata["provider_id"], "model": actual_model, "model_id": actual_model, "display_name": display_name, "reasoning_effort": selected_effort, "usage": usage, "latency_ms": latency_ms})
        except asyncio.CancelledError:
            # A browser-side Stop cancels the request. Save any content already received.
            if answer:
                conversation_service.add_message(conversation_id, "assistant", answer + "\n\n[已停止生成]", provider_name, actual_model)
            raise
        except ProviderError as exc:
            logging.getLogger(__name__).warning("Provider request failed: %s", exc)
            yield event_stream("error", {"message": str(exc)})
        except Exception:
            logging.getLogger(__name__).exception("Unexpected chat failure")
            yield event_stream("error", {"message": "小G遇到了意外问题，请稍后重试。"})

    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
