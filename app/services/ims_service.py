import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)

_cached_token: str | None = None


async def _login() -> str | None:
    if not settings.ims_url or not settings.ims_username:
        return None
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{settings.ims_url}/api/v1/auth/login",
                data={"username": settings.ims_username, "password": settings.ims_password},
            )
            res.raise_for_status()
            token = res.json()["access_token"]
            logger.info("IMS login successful")
            return token
    except Exception as exc:
        logger.warning("IMS login failed: %s", exc)
        return None


async def create_incident(alert_id: int, camera_id: int, message: str) -> None:
    """
    Automatically create an IMS incident when a surveillance alert fires.
    Silently skipped if IMS_URL is not configured.
    """
    global _cached_token

    if not settings.ims_url:
        return

    if not _cached_token:
        _cached_token = await _login()
    if not _cached_token:
        return

    payload = {
        "title": f"Zone Intrusion - Camera #{camera_id}",
        "description": message,
        "severity": "high",
        "camera_id": camera_id,
        "alert_id": alert_id,
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.post(
                f"{settings.ims_url}/api/v1/incidents/",
                json=payload,
                headers={"Authorization": f"Bearer {_cached_token}"},
            )
            if res.status_code == 401:
                # Token expired — re-login once and retry
                _cached_token = await _login()
                if not _cached_token:
                    return
                res = await client.post(
                    f"{settings.ims_url}/api/v1/incidents/",
                    json=payload,
                    headers={"Authorization": f"Bearer {_cached_token}"},
                )
            res.raise_for_status()
            inc = res.json()
            logger.info("IMS incident created: id=%s for alert #%d", inc.get("id"), alert_id)
    except Exception as exc:
        logger.warning("IMS incident creation failed: %s", exc)
