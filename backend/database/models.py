"""Pydantic models used at XiaoG's HTTP boundary."""

import base64
import binascii

from pydantic import BaseModel, Field, field_validator


class ConversationCreate(BaseModel):
    title: str | None = Field(default=None, max_length=120)


class ConversationTitleUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=120)


class ChatRequest(BaseModel):
    content: str = Field(min_length=1, max_length=30000)
    model_preference: str = Field(default="auto", pattern="^(auto|deepseek|terra)$")
    reasoning_effort: str | None = Field(default=None, max_length=32)


class ConversationModelSettingsUpdate(BaseModel):
    model_mode: str = Field(pattern="^(auto|manual)$")
    manual_model: str = Field(pattern="^(deepseek|terra)$")
    manual_reasoning_effort: str | None = Field(default=None, max_length=32)
    manual_reasoning_preferences: dict[str, str] = Field(default_factory=dict)

    @field_validator("manual_reasoning_preferences")
    @classmethod
    def validate_conversation_manual_reasoning_preferences(cls, value: dict[str, str]) -> dict[str, str]:
        if len(value) > 20:
            raise ValueError("推理档位偏好数量过多。")
        normalized: dict[str, str] = {}
        for model_id, effort in value.items():
            if not isinstance(model_id, str) or not isinstance(effort, str):
                raise ValueError("推理档位偏好格式无效。")
            if not model_id or len(model_id) > 120 or not effort or len(effort) > 32:
                raise ValueError("推理档位偏好内容无效。")
            normalized[model_id] = effort
        return normalized


class SettingsUpdate(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=12000)
    user_profile: str = Field(default="", max_length=12000)


class PersonalizationSettingsUpdate(BaseModel):
    """Persisted presentation preferences, kept separate from model settings."""

    theme_mode: str = Field(pattern="^(light|dark)$")
    color_scheme: str = Field(pattern="^(green|blue|purple)$")
    assistant_avatar: str | None = Field(default=None, max_length=400000)
    user_avatar: str | None = Field(default=None, max_length=400000)
    font_scale: str | None = Field(default=None, pattern="^(small|standard|large|xlarge)$")
    default_model: str | None = Field(default=None, pattern="^(auto|deepseek|terra)$")
    reasoning_preference: str | None = Field(default=None, pattern="^(fast|balanced|deep)$")
    chat_density: str | None = Field(default=None, pattern="^(comfortable|compact)$")
    manual_reasoning_preferences: dict[str, str] | None = None
    show_message_time: bool | None = None
    enter_to_send: bool | None = None
    @field_validator("manual_reasoning_preferences")
    @classmethod
    def validate_manual_reasoning_preferences(cls, value: dict[str, str] | None) -> dict[str, str] | None:
        if value is None:
            return value
        if len(value) > 20:
            raise ValueError("推理档位偏好数量过多。")
        normalized: dict[str, str] = {}
        for model_id, effort in value.items():
            if not isinstance(model_id, str) or not isinstance(effort, str):
                raise ValueError("推理档位偏好格式无效。")
            if not model_id or len(model_id) > 120 or not effort or len(effort) > 32:
                raise ValueError("推理档位偏好内容无效。")
            normalized[model_id] = effort
        return normalized
    animations_enabled: bool | None = None
    ui_language: str | None = Field(default=None, pattern="^(zh-CN|en)$")

    @field_validator("assistant_avatar", "user_avatar")
    @classmethod
    def validate_avatar(cls, value: str | None) -> str | None:
        preset_avatars = {"default", "mario", "pikachu", "stitch", "compass", "cloud", "moon", "spark"}
        if value in (None, *preset_avatars):
            return value
        allowed_prefixes = ("data:image/png;base64,", "data:image/jpeg;base64,", "data:image/webp;base64,")
        prefix = next((item for item in allowed_prefixes if value.startswith(item)), None)
        if not prefix:
            raise ValueError("头像必须是 PNG、JPEG 或 WebP 图片。")
        try:
            image_bytes = base64.b64decode(value[len(prefix):], validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("头像图片数据无效。") from exc
        if len(image_bytes) > 300000:
            raise ValueError("头像图片过大。")
        return value