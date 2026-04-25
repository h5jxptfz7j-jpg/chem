from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.reaction import UserReaction
from app.schemas.reaction import CatalogItem

router = APIRouter(prefix="/catalog", tags=["catalog"])

@router.get("", response_model=List[CatalogItem])
async def get_catalog(
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(UserReaction).where(UserReaction.user_id == user_id)
               .order_by(UserReaction.date_added.desc())
    )
    return result.scalars().all()

@router.delete("/{reaction_id}")
async def delete_reaction(
    reaction_id: int,
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    stmt = delete(UserReaction).where(UserReaction.id == reaction_id, UserReaction.user_id == user_id)
    await session.execute(stmt)
    await session.commit()
    return {"detail": "Deleted"}
