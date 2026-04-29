import asyncio
import re
import pubchempy as pcp
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pubchem_cache import PubChemCache

import re
def parse_search_formula(raw_formula: str) -> str:
    # Убираем всё после первого '+', убираем пробелы, убираем ведущий коэффициент
    first = raw_formula.split('+')[0].strip()
    # Удаляем целочисленный коэффициент в начале (например '2H2O' -> 'H2O')
    return re.sub(r'^\d+', '', first)

async def get_compound_by_cid(cid: int, session: AsyncSession) -> dict:
    stmt = select(PubChemCache).where(PubChemCache.cid == cid)
    result = await session.execute(stmt)
    cache = result.scalar_one_or_none()
    if cache:
        return {"name": cache.name, "formula": cache.formula, "image_url": cache.image_url}

    def _fetch():
        compounds = pcp.get_compounds(cid, 'cid')
        if not compounds:
            return None
        comp = compounds[0]
        name = comp.iupac_name or comp.synonyms[0] if comp.synonyms else str(cid)
        formula = comp.molecular_formula
        image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG?image_size=300x300"
        return {"name": name, "formula": formula, "image_url": image_url}

    data = await asyncio.to_thread(_fetch)
    if not data:
        raise HTTPException(status_code=404, detail="Compound not found in PubChem")

    cache_entry = PubChemCache(cid=cid, name=data["name"], formula=data["formula"], image_url=data["image_url"])
    session.add(cache_entry)
    await session.commit()
    return data

async def get_compound_by_formula(formula: str, session: AsyncSession) -> dict:
    search_formula = parse_search_formula(formula)

    def _fetch():
        results = pcp.get_compounds(search_formula, 'formula', listkey_count=1)
        if not results:
            return None
        comp = results[0]
        cid = comp.cid
        name = comp.iupac_name or comp.synonyms[0] if comp.synonyms else str(cid)
        mol_formula = comp.molecular_formula
        image_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/PNG?image_size=300x300"
        return {"cid": cid, "name": name, "formula": mol_formula, "image_url": image_url}

    data = await asyncio.to_thread(_fetch)
    if not data:
        raise HTTPException(status_code=404, detail="No compound found for the given formula")

    stmt = select(PubChemCache).where(PubChemCache.cid == data["cid"])
    result = await session.execute(stmt)
    if not result.scalar_one_or_none():
        session.add(PubChemCache(cid=data["cid"], name=data["name"], formula=data["formula"], image_url=data["image_url"]))
        await session.commit()

    return data