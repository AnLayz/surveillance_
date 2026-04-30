import asyncio
import threading

import numpy as np


class FrameStore:
    """
    Thread-safe single-slot buffer shared between the pipeline (writer)
    and the MJPEG stream endpoint (reader).
    Uses an asyncio.Event so the HTTP generator can await new frames
    without busy-polling.
    """

    def __init__(self) -> None:
        self._frame: bytes | None = None   # JPEG-encoded bytes
        self._lock = threading.Lock()
        self._event = asyncio.Event()

    def push(self, jpeg_bytes: bytes) -> None:
        """Called from the pipeline (sync context inside run_in_executor)."""
        with self._lock:
            self._frame = jpeg_bytes
        # Schedule the event set on the main event loop
        try:
            loop = asyncio.get_event_loop()
            loop.call_soon_threadsafe(self._event.set)
        except RuntimeError:
            pass

    async def get(self) -> bytes | None:
        """Wait for the next frame, then return it."""
        await self._event.wait()
        self._event.clear()
        with self._lock:
            return self._frame


# Single shared instance imported by pipeline and stream route
frame_store = FrameStore()
