"""FastAPI application entry point for XiaoG."""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings, validate_preview_startup
from backend.diagnostics import configure_logging, diagnostic_logger, log_event
from backend.errors import error_detail, normalize_http_detail
from backend.database.db import active_database_path, initialize_database, use_database_path
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
from backend.preview import PreviewSessionRegistry, preview_surface_options
from backend.preview_access import PreviewAccessControl


logger = diagnostic_logger('api')


@asynccontextmanager
async def lifespan(_app: FastAPI):
    validate_preview_startup()
    configure_logging(settings.log_dir, settings.log_level)
    if settings.runtime.preview_enabled:
        preview_sessions.reset_for_startup()
        preview_access.reset()
    else:
        initialize_database()
    log_event(logger, 20, "database_initialized")
    if not settings.runtime.preview_enabled or "terra" in settings.runtime.preview_provider_allowlist:
        try:
            await codex_app_server_manager.start()
        except ProviderError as exc:
            # DeepSeek remains usable if Codex is unavailable at application boot.
            logger.warning("Codex App Server was not ready at startup: %s", exc)
    try:
        yield
    finally:
        await codex_app_server_manager.close()


app = FastAPI(
    title="XiaoG",
    version=product_info_service.public_info().get("version", "unknown"),
    lifespan=lifespan,
    **preview_surface_options(settings.runtime),
)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
preview_sessions = PreviewSessionRegistry(settings.runtime.data_dir)
preview_access = PreviewAccessControl(settings.runtime)
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.middleware("http")
async def preview_session_boundary(request: Request, call_next):
    """Give every Preview browser an opaque, server-issued, isolated SQLite scope."""
    if not settings.runtime.preview_enabled or not request.url.path.startswith("/api/"):
        return await call_next(request)
    if request.url.path == "/api/preview/access": return await call_next(request)
    token=request.cookies.get("xiaog_preview_session"); session=preview_access.session(token)
    if not session: return JSONResponse(status_code=401, content={"detail": error_detail("preview_auth_required", "需要有效的邀请码访问 Preview。")})
    if not preview_access.allow_request(session.invite_id): return JSONResponse(status_code=429, content={"detail": error_detail("preview_rate_limited", "请求过于频繁，请稍后重试。", retryable=True)})
    request.state.preview_session=session; invite_token=preview_access.current_invite.set(session.invite_id)
    try:
        with use_database_path(session.database_path):
            initialize_database(); response = await call_next(request)
    finally: preview_access.current_invite.reset(invite_token)
    return response
@app.exception_handler(HTTPException)
async def http_error_boundary(_request: Request, error: HTTPException) -> JSONResponse:
    return JSONResponse(status_code=error.status_code, content={"detail": normalize_http_detail(error)})


@app.exception_handler(RequestValidationError)
async def validation_error_boundary(_request: Request, _error: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": error_detail("validation_error", "请求参数无效，请检查后重试。")},
    )


@app.exception_handler(Exception)
async def unexpected_error_boundary(_request: Request, error: Exception) -> JSONResponse:
    logger.exception("Unhandled API error: %s", error)
    return JSONResponse(
        status_code=500,
        content={"detail": error_detail("internal_error", "小G遇到了意外问题，请稍后重试。", retryable=True)},
    )


def event_stream(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    info = product_info_service.public_info()
    return {
        "status": "ok", "app": "XiaoG", "version": info.get("version", "unknown"),
        "phase": info.get("phase", "unknown"), "commit": info.get("commit", "unavailable"),
        "runtime_mode": settings.runtime.runtime_mode, "release_id": settings.runtime.release_id,
    }

@app.post("/api/preview/access")
async def preview_access_exchange(payload: dict, request: Request) -> JSONResponse:
    if not settings.runtime.preview_enabled:
        raise HTTPException(status_code=404, detail="Preview access is unavailable in local mode.")
    credential = payload.get("credential") if isinstance(payload, dict) else None
    if not isinstance(credential, str) or len(credential) > 512:
        raise HTTPException(status_code=401, detail="邀请码无效或已过期。")
    session = preview_access.exchange(credential, preview_sessions.session_dir)
    if not session:
        raise HTTPException(status_code=401, detail="邀请码无效或已过期。")
    response = JSONResponse({"authenticated": True, "invite_id": session.invite_id})
    response.set_cookie("xiaog_preview_session", session.token, max_age=settings.runtime.preview_session_ttl_seconds, httponly=True, samesite="lax", secure=True, path="/")
    return response

@app.post("/api/preview/logout")
async def preview_logout(request: Request) -> JSONResponse:
    preview_access.logout(request.cookies.get("xiaog_preview_session"))
    response = JSONResponse({"authenticated": False}); response.delete_cookie("xiaog_preview_session", path="/"); return response


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


@app.get("/api/providers")
async def get_providers() -> dict:
    """Provider Management reads the same live, credential-free Registry snapshot."""
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
    preview_invite_id = None
    if settings.runtime.preview_enabled:
        preview_invite_id = preview_access.current_invite.get()
        if not preview_invite_id: raise HTTPException(status_code=401, detail="Preview authentication required.")
        if len(content) > settings.runtime.preview_max_input_chars:
            raise HTTPException(status_code=413, detail="Preview 输入长度超过限制。")
        if not preview_access.acquire_generation(preview_invite_id):
            raise HTTPException(status_code=429, detail="Preview 生成额度或并发已达上限，请稍后重试。")

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
    request_database_path = active_database_path()

    async def generate():
        # Streaming may outlive middleware dispatch; retain the caller's isolated scope.
        with use_database_path(request_database_path):
            try:
                async for event in _generate_chat_events(conversation_id, content, conversation, provider, display_name, selected_effort, model_metadata, routing, user_message): yield event
            finally:
                if preview_invite_id: preview_access.release_generation(preview_invite_id)

    return StreamingResponse(generate(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


async def _generate_chat_events(
    conversation_id: str, content: str, conversation: dict, provider, display_name: str,
    selected_effort: str | None, model_metadata: dict, routing: dict | None, user_message: dict,
):
    """The existing SSE contract, factored to preserve a Preview request database scope."""
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
        if answer:
            conversation_service.add_message(conversation_id, "assistant", answer + "\n\n[已停止生成]", provider_name, actual_model)
        raise
    except ProviderError as exc:
        logger.warning("Provider request failed: %s", exc)
        yield event_stream("error", error_detail("provider_request_failed", str(exc), retryable=True))
    except Exception:
        logger.exception("Unexpected chat failure")
        yield event_stream("error", error_detail("internal_error", "小G遇到了意外问题，请稍后重试。", retryable=True))
