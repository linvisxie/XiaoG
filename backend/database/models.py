"""Pydantic models used at XiaoG's HTTP boundary."""

from pydantic import BaseModel, Field


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
