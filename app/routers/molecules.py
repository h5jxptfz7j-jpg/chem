from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.molecule import Molecule
from app.schemas.molecule import MoleculeOut

router = APIRouter(prefix="/molecules", tags=["molecules"])

@router.get("", response_model=List[MoleculeOut])
async def get_molecules(
    state: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    if state not in ("gas", "liquid", "solid"):
        raise HTTPException(status_code=400, detail="Invalid state")
    
    result = await session.execute(
        select(Molecule)
        .where(Molecule.state == state)
        .offset(skip)
        .limit(limit)
    )
    molecules = result.scalars().all()
    return [MoleculeOut(id=m.id, name=m.name, formula=m.formula, image_url=m.pubchem_image_url) for m in molecules]