from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.config import get_settings
from app.schemas import TelegramUpdate
from app.services.gemini import GeminiService
from app.services.telegram import TelegramService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()
gemini_service = GeminiService(
    api_key=settings.openrouter_api_key,
    model=settings.openrouter_model,
)
telegram_service = TelegramService(bot_token=settings.telegram_token)

app = FastAPI(title="Telegram Gemini Bot", version="1.0.0")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/webhook/{token}")
async def verify_webhook(token: str) -> dict:
    if token != settings.telegram_token:
        raise HTTPException(status_code=403, detail="Invalid webhook token")
    webhook_info = await telegram_service.get_webhook_info()
    return {"verified": True, "webhook_info": webhook_info.get("result")}


@app.post("/webhook/{token}")
async def telegram_webhook(token: str, update: TelegramUpdate) -> JSONResponse:
    if token != settings.telegram_token:
        raise HTTPException(status_code=403, detail="Invalid webhook token")

    message = update.message
    if message is None or not message.text:
        return JSONResponse({"ok": True, "ignored": "no text message"})

    try:
        parsed = await gemini_service.parse_message(message.text)
    except (ValueError, ValidationError) as exc:
        logger.exception("Failed to parse Gemini output")
        await telegram_service.send_message(
            chat_id=message.chat.id,
            text="I couldn't understand that. Please try again with a clearer message.",
        )
        return JSONResponse({"ok": True, "error": str(exc)})
    except Exception:
        logger.exception("Gemini request failed")
        await telegram_service.send_message(
            chat_id=message.chat.id,
            text="AI processing failed. Please try again shortly.",
        )
        return JSONResponse({"ok": True, "error": "gemini request failed"})

    if parsed.type == "task":
        confirmation = (
            f"Task added: {parsed.title}"
            f"{' on ' + parsed.date if parsed.date else ''}"
            f"{' at ' + parsed.time if parsed.time else ''}"
        )
    else:
        confirmation = (
            f"Event scheduled: {parsed.title}"
            f"{' on ' + parsed.date if parsed.date else ''}"
            f"{' at ' + parsed.time if parsed.time else ''}"
        )

    await telegram_service.send_message(chat_id=message.chat.id, text=confirmation)
    return JSONResponse({"ok": True, "parsed": parsed.model_dump()})

