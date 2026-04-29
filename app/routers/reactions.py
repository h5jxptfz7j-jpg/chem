from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_session
from app.dependencies.auth import get_telegram_user
from app.models.reaction import PredefinedReaction, UserReaction
from app.models.reaction_hint import ReactionHint  
from app.models.element import Element
from app.models.state_molecules import LiquidMolecule, GasMolecule, SolidMolecule
from app.models.compatibility import PredefinedCompatibility
from app.schemas.reaction import ReactionRequest, ReactionResponse
from app.services.pubchem import get_compound_by_formula

router = APIRouter(prefix="/reactions", tags=["reactions"])

ALL_STATE_MODELS = [GasMolecule, LiquidMolecule, SolidMolecule]


async def find_molecule_in_all_tables(mol_id: int, session: AsyncSession):
    """Ищет молекулу по id во всех таблицах агрегатных состояний."""
    for model in ALL_STATE_MODELS:
        result = await session.execute(select(model).where(model.id == mol_id))
        mol = result.scalar_one_or_none()
        if mol:
            return mol
    return None


async def build_reaction_key(formulas: list[str]) -> str:
    """Строит ключ реакции: сортирует формулы и соединяет через '+'."""
    return "+".join(sorted(formulas))


async def get_hint_for_formula(formula: str, session: AsyncSession) -> str:
    """Генерирует подсказку: с чем реагирует данное вещество."""
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
    reagent_ids = [item.id for item in payload.reagents]
    mode = payload.mode

    # ─────────────────────────── AGGREGATE MODE ───────────────────────────
    if mode == "aggregate":
        state_table_map = {
            "liquid": LiquidMolecule,
            "gas": GasMolecule,
            "solid": SolidMolecule,
        }

        reagents = []
        for item in payload.reagents:
            mol = None
            # Если передан state, ищем только в указанной таблице
            if item.state and item.state in state_table_map:
                model = state_table_map[item.state]
                result = await session.execute(select(model).where(model.id == item.id))
                mol = result.scalar_one_or_none()
            else:
                # Старый режим: ищем во всех таблицах
                mol = await find_molecule_in_all_tables(item.id, session)
            if not mol:
                raise HTTPException(status_code=400, detail=f"Reagent id={item.id} not found")
            reagents.append(mol)

        if len(reagents) != len(reagent_ids):
            raise HTTPException(status_code=400, detail="Some reagents not found")

        # Строим ключ: сортируем формулы
        formulas = [r.formula for r in reagents]
        reaction_key = await build_reaction_key(formulas)

        # Ищем реакцию в БД
        reaction = (await session.execute(
            select(PredefinedReaction).where(PredefinedReaction.reaction_key == reaction_key)
        )).scalar_one_or_none()

        if not reaction:
            # Сначала пробуем найти точную подсказку в ReactionHint
            hint_obj = (await session.execute(
                select(ReactionHint).where(ReactionHint.reaction_key == reaction_key)
            )).scalar_one_or_none()
            if hint_obj:
                hint_text = hint_obj.hint_text
            else:
                # Fallback: генерируем умную подсказку на основе реальных реакций
                formula = reagents[0].formula
                hint_text = await get_hint_for_formula(formula, session)
            return ReactionResponse(
                product_name="",
                product_formula="",
                product_image_url=None,
                cid=None,
                reaction_key=None,
                hint=hint_text,
                suggestions=None,
                reaction_date=datetime.utcnow()
            )

        # Реакция найдена — получаем продукт из PubChem
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
            hint=None,
            reaction_date=user_reaction.date_added
        )

    # ─────────────────────────── INDEPENDENT MODE ───────────────────────────
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
                        suggested_elements.append({
                            "symbol": other.symbol,
                            "name_ru": other.name_ru,
                        })
                        seen_ids.add(other_id)

            hint_msg = None
            if not suggested_elements:
                hint_msg = f"Нет известных реакций для элемента {e1.symbol}"

            return ReactionResponse(
                product_name="",
                product_formula="",
                product_image_url=None,
                cid=None,
                reaction_key=None,
                suggestions=suggested_elements if suggested_elements else None,
                hint=hint_msg,
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
            hint=None,
            reaction_date=user_reaction.date_added
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid mode")