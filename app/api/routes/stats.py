from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.services import alert_service

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/")
async def get_stats(db: AsyncSession = Depends(get_db)):
    return await alert_service.get_stats(db)
