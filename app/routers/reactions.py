from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.reaction import PredefinedReaction, UserReaction
from app.models.element import Element
from app.models.state_molecules import LiquidMolecule, GasMolecule, SolidMolecule
from app.models.compatibility import PredefinedCompatibility
from app.schemas.reaction import ReactionRequest, ReactionResponse
from app.services.pubchem import get_compound_by_formula

router = APIRouter(prefix="/reactions", tags=["reactions"])

@router.post("/execute", response_model=ReactionResponse)
async def execute_reaction(
    payload: ReactionRequest,
    user_id: int = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    reagent_ids = payload.reagents
    mode = payload.mode

    if mode == "aggregate":
        state_table_map = {
            "liquid": LiquidMolecule,
            "gas": GasMolecule,
            "solid": SolidMolecule,
        }
        model = state_table_map.get(payload.state)
        if not model:
            reagents = []
            for rid in reagent_ids:
                for m in [LiquidMolecule, GasMolecule, SolidMolecule]:
                    stmt = select(m).where(m.id == rid)
                    res = await session.execute(stmt)
                    mol = res.scalar_one_or_none()
                    if mol:
                        reagents.append(mol)
                        break
        else:
            reagents = (await session.execute(
                select(model).where(model.id.in_(reagent_ids))
            )).scalars().all()

        if len(reagents) != len(reagent_ids):
            raise HTTPException(status_code=400, detail="Some reagents not found")

        formulas = sorted([r.formula for r in reagents])
        reaction_key = "+".join(formulas)
        print(f"DEBUG formulas: {formulas}")
        print(f"DEBUG reaction_key: '{reaction_key}'")

        # Проверим что есть в таблице
        all_reactions = (await session.execute(select(PredefinedReaction))).scalars().all()
        print(f"DEBUG all reaction_keys: {[r.reaction_key for r in all_reactions]}")

        # Диагностика – будет видна в ответе при ошибке
        reaction = (await session.execute(
            select(PredefinedReaction).where(PredefinedReaction.reaction_key == reaction_key)
        )).scalar_one_or_none()

        if not reaction:
            return ReactionResponse(
        product_name="",
        product_formula="",
        product_image_url=None,
        cid=None,
        reaction_key=None,
        suggestions=None,
        hint=f"Реакция между {reagents[0].name} ({reagents[0].formula}) и {reagents[1].name} ({reagents[1].formula}) не найдена в базе данных.",
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
            suggestions=None,
            reaction_date=user_reaction.date_added
        )

    elif mode == "independent":
        elements = (await session.execute(
            select(Element).where(Element.id.in_(reagent_ids))
        )).scalars().all()

        if len(elements) != len(reagent_ids) or len(elements) != 2:
            raise HTTPException(status_code=400, detail="Elements not found or wrong count")

        e1, e2 = elements[0], elements[1]

        compat = (await session.execute(
            select(PredefinedCompatibility).where(
                ((PredefinedCompatibility.element1_id == e1.id) & (PredefinedCompatibility.element2_id == e2.id)) |
                ((PredefinedCompatibility.element1_id == e2.id) & (PredefinedCompatibility.element2_id == e1.id))
            )
        )).scalar_one_or_none()

        if not compat:
            hints = (await session.execute(
                select(PredefinedCompatibility).where(
                    or_(PredefinedCompatibility.element1_id == e1.id,
                        PredefinedCompatibility.element2_id == e1.id)
                )
            )).scalars().all()

            suggested_elements = []
            seen_ids = set()
            for h in hints:
                other_id = h.element2_id if h.element1_id == e1.id else h.element1_id
                if other_id not in seen_ids:
                    other = (await session.execute(
                        select(Element).where(Element.id == other_id)
                    )).scalar_one_or_none()
                    if other:
                        suggested_elements.append({
                            "symbol": other.symbol,
                            "name_ru": other.name_ru,
                        })
                        seen_ids.add(other_id)
            return ReactionResponse(
                product_name="",
                product_formula="",
                product_image_url=None,
                cid=None,
                reaction_key=None,
                suggestions=suggested_elements,
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
            reaction_key=None,
            suggestions=None,
            reaction_date=user_reaction.date_added
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid mode")