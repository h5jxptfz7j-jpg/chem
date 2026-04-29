from typing import Listобязателен!
from fastapi import APIRouter, Query, Depends 
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models.element import Element

router = APIRouter(prefix="/elements", tags=["elements"])

@router.get("", response_model=List[dict])
async def get_elements(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(select(Element).offset(skip).limit(limit))
    return [{"id": el.id, "symbol": el.symbol, "name_ru": el.name_ru} for el in result.scalars().all()]
