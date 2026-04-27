from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.element import Element
from app.schemas.molecule import ElementOut

router = APIRouter(prefix="/elements", tags=["elements"])

@router.get("", response_model=List[ElementOut])
async def get_elements(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(Element).offset(skip).limit(limit)
    )
    return result.scalars().all()
