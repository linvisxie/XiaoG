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
    terra_reasoning_effort: str | None = Field(default=None, pattern="^(low|medium|high)$")


class SettingsUpdate(BaseModel):
    system_prompt: str = Field(min_length=1, max_length=12000)
    user_profile: str = Field(default="", max_length=12000)


class PersonalizationSettingsUpdate(BaseModel):
    """Persisted presentation preferences, kept separate from model settings."""

    theme_mode: str = Field(pattern="^(light|dark)$")
    color_scheme: str = Field(pattern="^(green|blue|purple)$")
    assistant_avatar: str | None = Field(default=None, pattern="^(default|mario|pikachu|stitch|compass|cloud|moon|spark)$")
    user_avatar: str | None = Field(default=None, max_length=400000)
    font_scale: str | None = Field(default=None, pattern="^(small|standard|large|xlarge)$")
    default_model: str | None = Field(default=None, pattern="^(deepseek|terra)$")
    reasoning_preference: str | None = Field(default=None, pattern="^(fast|balanced|deep)$")
    chat_density: str | None = Field(default=None, pattern="^(comfortable|compact)$")
    show_message_time: bool | None = None
    enter_to_send: bool | None = None
    animations_enabled: bool | None = None
    ui_language: str | None = Field(default=None, pattern="^(zh-CN|en)$")

    @field_validator("user_avatar")
    @classmethod
    def validate_user_avatar(cls, value: str | None) -> str | None:
        if value in (None, "default"):
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