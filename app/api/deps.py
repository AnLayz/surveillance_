from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db

# Re-export so routes only need to import from api.deps
__all__ = ["get_db"]
