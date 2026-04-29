from typing import List
from fastapi import APIRouter, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models.molecule import Molecule

router = APIRouter(prefix="/molecules", tags=["molecules"])

@router.get("", response_model=List[dict])
async def get_molecules(
    state: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session)
):
    if state not in ("gas", "liquid", "solid"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid state. Use gas, liquid or solid.")
    
    result = await session.execute(
        select(Molecule)
        .where(Molecule.state == state)
        .offset(skip)
        .limit(limit)
    )
    molecules = result.scalars().all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "formula": m.formula,
            "image_url": m.pubchem_image_url or ""
        } for m in molecules
    ]
