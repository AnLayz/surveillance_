import logging

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


async def send_alert(message: str) -> None:
    """
    Send a text alert to the configured Telegram chat.
    Silently skipped if TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID are not set.
    """
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return

    url = _TELEGRAM_API.format(token=settings.telegram_bot_token)
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": f"🚨 *SURVIVALENCE ALERT*\n\n{message}",
        "parse_mode": "Markdown",
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            logger.info("Telegram alert sent: %s", message)
    except httpx.HTTPError as exc:
        # Never crash the pipeline over a failed notification
        logger.warning("Telegram notification failed: %s", exc)
