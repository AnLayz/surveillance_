import asyncio
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse

from app.cv.frame_store import frame_store

router = APIRouter(prefix="/stream", tags=["stream"])


async def _mjpeg_generator() -> AsyncGenerator[bytes, None]:
    """Yield MJPEG multipart frames as they arrive from the pipeline."""
    while True:
        jpeg = await asyncio.wait_for(frame_store.get(), timeout=5.0)
        if jpeg is None:
            continue
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + jpeg +
            b"\r\n"
        )


@router.get("/video")
async def video_stream():
    """Live MJPEG stream with bounding boxes, track IDs and zones drawn."""
    return StreamingResponse(
        _mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )


@router.get("/", response_class=HTMLResponse)
async def stream_viewer():
    """Simple HTML viewer — open in browser to watch the live feed."""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html>
<head>
  <title>Survivalence — Live Feed</title>
  <style>
    body { background: #111; display: flex; flex-direction: column;
           align-items: center; justify-content: center; height: 100vh; margin: 0; }
    h2   { color: #eee; font-family: monospace; margin-bottom: 12px; }
    img  { border: 2px solid #444; max-width: 90vw; border-radius: 4px; }
  </style>
</head>
<body>
  <h2>Survivalence — Live Feed</h2>
  <img src="/api/v1/stream/video" alt="Live stream" />
</body>
</html>
""")
