from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ParsedIntent(BaseModel):
    type: Literal["task", "event"]
    title: str = Field(min_length=1)
    date: str | None = None
    time: str | None = None

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("title cannot be empty")
        return cleaned


class TelegramChat(BaseModel):
    id: int


class TelegramMessage(BaseModel):
    message_id: int
    chat: TelegramChat
    text: str | None = None


class TelegramUpdate(BaseModel):
    update_id: int
    message: TelegramMessage | None = None

