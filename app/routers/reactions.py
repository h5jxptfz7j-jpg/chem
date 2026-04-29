from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.reaction import PredefinedReaction, UserReaction
from app.models.reaction_hint import ReactionHint
from app.models.element import Element
from app.models.molecule import Molecule
from app.models.compatibility import PredefinedCompatibility
from app.schemas.reaction import ReactionRequest, ReactionResponse
from app.services.pubchem import get_compound_by_formula

router = APIRouter(prefix="/reactions", tags=["reactions"])


def make_key(*formulas: str) -> str:
    return "+".join(sorted(formulas))


async def get_hint_for_key(reaction_key: str, formula: str, session: AsyncSession) -> str:
    # 1. Готовая подсказка из таблицы reaction_hints
    hint_row = (await session.execute(
        select(ReactionHint).where(ReactionHint.reaction_key == reaction_key)
    )).scalar_one_or_none()
    if hint_row:
        return hint_row.hint_text

    # 2. Генерируем из predefined_reactions
    possible = (await session.execute(
        select(PredefinedReaction)
        .where(PredefinedReaction.reaction_key.contains(formula))
        .where(PredefinedReaction.product_formula != "")
    )).scalars().all()

    hints = []
    for r in possible[:5]:
        parts = r.reaction_key.split("+")
        other = next((p for p in parts if p != formula), parts[0])
        desc = f" ({r.description})" if r.description else ""
        hints.append(f"{other}{desc}")

    if hints:
        return "Попробуй вступить в реакцию с: " + ", ".join(hints)
    return f"Нет известных реакций для {formula}"


@router.post("/execute", response_model=ReactionResponse)
async def execute_reaction(
    payload: ReactionRequest,
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    reagent_ids = payload.reagents
    mode = payload.mode

    # ─────────────────────── AGGREGATE MODE ───────────────────────
    if mode == "aggregate":
        # Ищем молекулы в единой таблице molecules
        result = await session.execute(
            select(Molecule).where(Molecule.id.in_(reagent_ids))
        )
        reagents = result.scalars().all()
        
        # Сортируем в порядке исходных ID
        reagents = sorted(reagents, key=lambda r: reagent_ids.index(r.id))

        if len(reagents) != len(reagent_ids):
            raise HTTPException(status_code=400, detail="Some reagents not found")

        formulas = [r.formula for r in reagents]
        reaction_key = make_key(*formulas)

        reaction = (await session.execute(
            select(PredefinedReaction).where(PredefinedReaction.reaction_key == reaction_key)
        )).scalar_one_or_none()

        if not reaction:
            hint_text = await get_hint_for_key(reaction_key, formulas[0], session)
            return ReactionResponse(
                product_name="", product_formula="",
                product_image_url=None, cid=None,
                reaction_key=None, suggestions=None,
                hint=hint_text,
                reaction_date=datetime.utcnow()
            )

        try:
            product_data = await get_compound_by_formula(reaction.product_formula, session)
        except HTTPException as e:
            raise HTTPException(status_code=404, detail=f"Product not found: {e.detail}")

        user_reaction = UserReaction(
            user_id=user_id,
            reactant1=reagents[0].formula,
            reactant2=reagents[1].formula,
            product_name=product_data["name"],
            product_formula=product_data["formula"],
            product_image_url=product_data["image_url"],
            mode=mode
        )
        session.add(user_reaction)
        await session.commit()

        return ReactionResponse(
            product_name=product_data["name"],
            product_formula=product_data["formula"],
            product_image_url=product_data["image_url"],
            cid=product_data["cid"],
            reaction_key=reaction_key,
            suggestions=None, hint=None,
            reaction_date=user_reaction.date_added
        )

    # ─────────────────────── INDEPENDENT MODE ───────────────────────
    elif mode == "independent":
        elements = (await session.execute(
            select(Element).where(Element.id.in_(reagent_ids))
        )).scalars().all()

        if len(elements) != len(reagent_ids) or len(elements) != 2:
            raise HTTPException(status_code=400, detail="Elements not found or wrong count")

        elements = sorted(elements, key=lambda e: reagent_ids.index(e.id))
        e1, e2 = elements[0], elements[1]

        compat = (await session.execute(
            select(PredefinedCompatibility).where(
                or_(
                    (PredefinedCompatibility.element1_id == e1.id) & (PredefinedCompatibility.element2_id == e2.id),
                    (PredefinedCompatibility.element1_id == e2.id) & (PredefinedCompatibility.element2_id == e1.id)
                )
            )
        )).scalar_one_or_none()

        if not compat:
            hints_rows = (await session.execute(
                select(PredefinedCompatibility).where(
                    or_(
                        PredefinedCompatibility.element1_id == e1.id,
                        PredefinedCompatibility.element2_id == e1.id
                    )
                )
            )).scalars().all()

            suggested_elements = []
            seen_ids = set()
            for h in hints_rows:
                other_id = h.element2_id if h.element1_id == e1.id else h.element1_id
                if other_id not in seen_ids:
                    other = (await session.execute(
                        select(Element).where(Element.id == other_id)
                    )).scalar_one_or_none()
                    if other:
                        suggested_elements.append({"symbol": other.symbol, "name_ru": other.name_ru})
                        seen_ids.add(other_id)

            return ReactionResponse(
                product_name="", product_formula="",
                product_image_url=None, cid=None,
                reaction_key=None,
                suggestions=suggested_elements or None,
                hint=None if suggested_elements else f"Нет известных реакций для {e1.symbol}",
                reaction_date=datetime.utcnow()
            )

        try:
            product_data = await get_compound_by_formula(compat.suggested_product, session)
        except HTTPException as e:
            raise HTTPException(status_code=404, detail=f"Product not found: {e.detail}")

        user_reaction = UserReaction(
            user_id=user_id,
            reactant1=e1.symbol,
            reactant2=e2.symbol,
            product_name=product_data["name"],
            product_formula=product_data["formula"],
            product_image_url=product_data["image_url"],
            mode=mode
        )
        session.add(user_reaction)
        await session.commit()

        return ReactionResponse(
            product_name=product_data["name"],
            product_formula=product_data["formula"],
            product_image_url=product_data["image_url"],
            cid=product_data["cid"],
            reaction_key=None, suggestions=None, hint=None,
            reaction_date=user_reaction.date_added
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid mode")