"""FastAPI application entry point for XiaoG v0.1."""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database.db import initialize_database
from backend.database.models import ChatRequest, ConversationCreate, SettingsUpdate
from backend.pricing import estimate_deepseek_cost
from backend.providers.base import ProviderError
from backend.router.model_router import model_router
from backend.services.conversation_service import conversation_service
from backend.services.memory_service import memory_service


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
    yield


app = FastAPI(title="XiaoG", version="0.1.0", lifespan=lifespan)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


def event_stream(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "app": "XiaoG", "version": "0.1.0"}


@app.get("/api/provider-status")
async def provider_status() -> dict:
    return await model_router.status()


@app.get("/api/conversations")
async def list_conversations(archived: bool = False) -> list[dict]:
    return conversation_service.list_conversations(archived=archived)


@app.post("/api/conversations", status_code=201)
async def create_conversation(payload: ConversationCreate) -> dict:
    return conversation_service.create_conversation(payload.title)


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str) -> dict:
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="找不到该会话。")
    return {**conversation, "messages": conversation_service.list_messages(conversation_id)}


@app.delete("/api/conversations/{conversation_id}", status_code=204)
async def delete_conversation(conversation_id: str) -> None:
    if not conversation_service.delete_conversation(conversation_id):
        raise HTTPException(status_code=404, detail="找不到该会话。")


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


@app.post("/api/conversations/{conversation_id}/chat")
async def chat(conversation_id: str, payload: ChatRequest) -> StreamingResponse:
    conversation = conversation_service.get_conversation(conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="找不到该会话。")
    if conversation.get("archived_at"):
        raise HTTPException(status_code=409, detail="请先恢复已归档会话后再继续聊天。")
    content = payload.content.strip()
    if not content:
        raise HTTPException(status_code=422, detail="消息不能为空。")
    conversation_service.add_message(conversation_id, "user", content)
    conversation_service.set_title_from_first_message(conversation_id, content)

    async def generate():
        answer = ""
        usage = None
        actual_model = settings.deepseek_model_id
        provider_name = "deepseek"
        billing_type = "api"
        started = time.perf_counter()
        try:
            provider, display_name = await model_router.select(payload.model_preference)
            provider_name = provider.name
            actual_model = getattr(provider, "model_id", actual_model)
            billing_type = getattr(provider, "billing_type", "api")
            system_prompt = conversation_service.get_setting("system_prompt")
            profile = memory_service.get_user_profile()
            memories = memory_service.get_relevant_memories(content)
            model_messages = conversation_service.build_model_messages(conversation_id, system_prompt, profile, memories)
            yield event_stream("meta", {"provider": provider.name, "model": actual_model, "display_name": display_name, "reasoning_effort": payload.terra_reasoning_effort if payload.model_preference == "terra" else None})
            async for item in provider.stream_chat(model_messages, payload.terra_reasoning_effort):
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
            yield event_stream("done", {"provider": provider.name, "model": actual_model, "display_name": display_name, "usage": usage, "latency_ms": latency_ms})
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
