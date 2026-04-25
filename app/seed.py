import asyncio
import pubchempy as pcp
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.element import Element
from app.models.state_molecules import LiquidMolecule, GasMolecule, SolidMolecule
from app.models.reaction import PredefinedReaction
from app.models.compatibility import PredefinedCompatibility
 
async def seed_database(session: AsyncSession):
    # Проверка наличия данных
    if (await session.execute(select(Element.id))).scalars().first():
        return
 
    # ------------------- Элементы (50 шт.) -------------------
    elements_data = [
        ("H", "Водород"), ("He", "Гелий"), ("Li", "Литий"), ("Be", "Бериллий"), ("B", "Бор"),
        ("C", "Углерод"), ("N", "Азот"), ("O", "Кислород"), ("F", "Фтор"), ("Ne", "Неон"),
        ("Na", "Натрий"), ("Mg", "Магний"), ("Al", "Алюминий"), ("Si", "Кремний"), ("P", "Фосфор"),
        ("S", "Сера"), ("Cl", "Хлор"), ("Ar", "Аргон"), ("K", "Калий"), ("Ca", "Кальций"),
        ("Sc", "Скандий"), ("Ti", "Титан"), ("V", "Ванадий"), ("Cr", "Хром"), ("Mn", "Марганец"),
        ("Fe", "Железо"), ("Co", "Кобальт"), ("Ni", "Никель"), ("Cu", "Медь"), ("Zn", "Цинк"),
        ("Ga", "Галлий"), ("Ge", "Германий"), ("As", "Мышьяк"), ("Se", "Селен"), ("Br", "Бром"),
        ("Kr", "Криптон"), ("Rb", "Рубидий"), ("Sr", "Стронций"), ("Y", "Иттрий"), ("Zr", "Цирконий"),
        ("Nb", "Ниобий"), ("Mo", "Молибден"), ("Tc", "Технеций"), ("Ru", "Рутений"), ("Rh", "Родий"),
        ("Pd", "Палладий"), ("Ag", "Серебро"), ("Cd", "Кадмий"), ("In", "Индий"), ("Sn", "Олово")
    ]
    for sym, ru in elements_data:
        session.add(Element(symbol=sym, name_ru=ru))
 
    # ------------------- Молекулы (по 20 на состояние) -------------------
    liquids = [
        ("Вода", "H2O"), ("Этанол", "C2H5OH"), ("Ацетон", "C3H6O"), ("Серная кислота", "H2SO4"),
        ("Азотная кислота", "HNO3"), ("Соляная кислота", "HCl"), ("Бензол", "C6H6"), ("Метанол", "CH3OH"),
        ("Уксусная кислота", "CH3COOH"), ("Глицерин", "C3H8O3"), ("Этиленгликоль", "C2H6O2"),
        ("Тетрахлорметан", "CCl4"), ("Сероуглерод", "CS2"), ("Диэтиловый эфир", "C4H10O"),
        ("Ацетонитрил", "CH3CN"), ("ДМСО", "C2H6OS"), ("Формалин", "CH2O"), ("Пероксид водорода", "H2O2"),
        ("Ортофосфорная кислота", "H3PO4"), ("Пропионовая кислота", "C3H6O2")
    ]
    gases = [
        ("Водород", "H2"), ("Кислород", "O2"), ("Азот", "N2"), ("Хлор", "Cl2"),
        ("Углекислый газ", "CO2"), ("Аммиак", "NH3"), ("Метан", "CH4"), ("Сероводород", "H2S"),
        ("Оксид азота(II)", "NO"), ("Оксид азота(IV)", "NO2"), ("Озон", "O3"), ("Фтор", "F2"),
        ("Неон", "Ne"), ("Аргон", "Ar"), ("Криптон", "Kr"), ("Ксенон", "Xe"),
        ("Хлороводород", "HCl"), ("Монооксид углерода", "CO"), ("Диоксид серы", "SO2"), ("Ацетилен", "C2H2")
    ]
    solids = [
        ("Хлорид натрия", "NaCl"), ("Глюкоза", "C6H12O6"), ("Сахароза", "C12H22O11"),
        ("Карбонат кальция", "CaCO3"), ("Железо", "Fe"), ("Медь", "Cu"), ("Цинк", "Zn"),
        ("Алюминий", "Al"), ("Натрий", "Na"), ("Калий", "K"), ("Йод", "I2"), ("Сера", "S"),
        ("Белый фосфор", "P4"), ("Оксид алюминия", "Al2O3"), ("Диоксид кремния", "SiO2"),
        ("Гидроксид натрия", "NaOH"), ("Сульфат меди(II)", "CuSO4"), ("Перманганат калия", "KMnO4"),
        ("Нитрат серебра", "AgNO3"), ("Хлорид бария", "BaCl2")
    ]
    for name, formula in liquids:
        session.add(LiquidMolecule(name=name, formula=formula))
    for name, formula in gases:
        session.add(GasMolecule(name=name, formula=formula))
    for name, formula in solids:
        session.add(SolidMolecule(name=name, formula=formula))
 
    # ------------------- Предопределённые реакции -------------------
    reactions = [
        # Газы + газы
        ("Cl2+H2", "2HCl", "Хлороводород"),
        ("H2+O2", "2H2O", "Вода"),
        ("C+O2", "CO2", "Углекислый газ"),
        ("H2+N2", "2NH3", "Аммиак"),
        ("Na+Cl2", "2NaCl", "Хлорид натрия"),
        ("Cl2+O2", "2ClO", "Оксид хлора"),
        ("H2+F2", "2HF", "Фтороводород"),
        ("H2+Br2", "2HBr", "Бромоводород"),
        ("H2+I2", "2HI", "Йодоводород"),
        ("H2+S", "H2S", "Сероводород"),
        ("CO+O2", "2CO2", "Углекислый газ"),
        ("NO+O2", "2NO2", "Диоксид азота"),
        ("SO2+O2", "SO3", "Триоксид серы"),
        ("CH4+2O2", "CO2+2H2O", "Полное сгорание метана"),
        ("C2H2+2.5O2", "2CO2+H2O", "Сгорание ацетилена"),
        ("C2H4+3O2", "2CO2+2H2O", "Сгорание этилена"),
        ("C2H6+3.5O2", "2CO2+3H2O", "Сгорание этана"),
        # Газы + жидкости
        ("HCl+H2O", "H3O+Cl", "Раствор HCl"),
        ("NH3+H2O", "NH4OH", "Гидрат аммиака"),
        ("SO2+H2O", "H2SO3", "Сернистая кислота"),
        ("CO2+H2O", "H2CO3", "Угольная кислота"),
        ("NO2+H2O", "HNO3+HNO2", "Азотная и азотистая кислоты"),
        ("Cl2+H2O", "HClO+HCl", "Хлорная вода"),
        ("H2S+H2O", "H3O+HS", "Слабая сероводородная кислота"),
        # Жидкости + жидкости
        ("C2H5OH+CH3COOH", "CH3COOC2H5+H2O", "Этилацетат"),
        ("C2H5OH+H2SO4", "C2H5HSO4+H2O", "Этилсерная кислота"),
        ("HNO3+H2SO4", "NO2+HSO4+H2O", "Нитрующая смесь"),
        ("HCl+HNO3", "NOCl+Cl2+H2O", "Царская водка"),
        ("H2O+H2SO4", "H2SO4", "Разбавление серной кислоты"),
        ("H2O+HNO3", "HNO3", "Разбавление азотной кислоты"),
        ("CH3OH+H2O", "CH3OH", "Разбавление метанола"),
        ("C2H5OH+H2O", "C2H5OH", "Разбавление этанола"),
        ("C3H6O+H2O", "C3H6O", "Разбавление ацетона"),
        ("C6H6+H2O", "C6H6", "Бензол с водой"),
        ("CCl4+H2O", "CCl4", "Тетрахлорметан с водой"),
        ("CH3CN+H2O", "CH3CN", "Ацетонитрил с водой"),
        ("H2O+H2O2", "H2O", "Разложение пероксида"),
        ("H2O+H3PO4", "H3PO4", "Фосфорная кислота"),
        ("C3H6O2+H2O", "C3H6O2", "Пропионовая кислота"),
        # Жидкости + твёрдые
        ("Na+H2O", "NaOH+0.5H2", "Натрий + вода"),
        ("NaOH+HCl", "NaCl+H2O", "Нейтрализация"),
        ("H2SO4+NaCl", "NaHSO4+HCl", "Серная кислота + NaCl"),
        ("HNO3+NaOH", "NaNO3+H2O", "Нейтрализация NaOH"),
        ("CaCO3+2HCl", "CaCl2+H2O+CO2", "Известняк + HCl"),
        ("CuSO4+2NaOH", "Cu(OH)2+Na2SO4", "Осаждение Cu(OH)₂"),
        ("Fe+CuSO4", "FeSO4+Cu", "Замещение меди"),
        ("Zn+2HCl", "ZnCl2+H2", "Цинк + HCl"),
        ("Al+NaOH+H2O", "NaAlO2+1.5H2", "Алюминий + щёлочь"),
        ("Fe+S", "FeS", "Сульфид железа"),
        ("Zn+S", "ZnS", "Сульфид цинка"),
        ("2Al+Fe2O3", "Al2O3+2Fe", "Алюмотермия"),
        ("C+2H2", "CH4", "Метан"),
        # Твёрдые
        ("CaCO3", "CaO+CO2", "Разложение CaCO₃"),
        ("2NaHCO3", "Na2CO3+H2O+CO2", "Разложение NaHCO₃"),
    ]
 
    for key, prod, desc in reactions:
        existing = (await session.execute(
            select(PredefinedReaction).where(PredefinedReaction.reaction_key == key)
        )).scalar_one_or_none()
        if not existing:
            session.add(PredefinedReaction(reaction_key=key, product_formula=prod, description=desc))
 
    await session.flush()
 
    # ------------------- Совместимости элементов -------------------
    el = {}
    for sym in ["H", "O", "Cl", "Na", "C", "N"]:
        el[sym] = (await session.execute(select(Element).where(Element.symbol == sym))).scalar_one()
 
    compat = [
        (el["H"].id, el["O"].id, "H2O", "Вода"),
        (el["H"].id, el["Cl"].id, "HCl", "Хлороводород"),
        (el["Na"].id, el["Cl"].id, "NaCl", "Хлорид натрия"),
        (el["C"].id, el["O"].id, "CO2", "Углекислый газ"),
        (el["N"].id, el["H"].id, "NH3", "Аммиак"),
    ]
 
    for e1, e2, prod, hint in compat:
        existing = (await session.execute(
            select(PredefinedCompatibility).where(
                PredefinedCompatibility.element1_id == e1,
                PredefinedCompatibility.element2_id == e2
            )
        )).scalar_one_or_none()
        if not existing:
            session.add(PredefinedCompatibility(
                element1_id=e1, element2_id=e2,
                suggested_product=prod, hint_text=hint
            ))
 
    await session.commit()