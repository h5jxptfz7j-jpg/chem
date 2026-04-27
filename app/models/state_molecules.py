from sqlalchemy import Column, Integer, String
from app.database import Base

class LiquidMolecule(Base):
    __tablename__ = "liquid_molecules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    formula = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    cid = Column(Integer, nullable=True)

class GasMolecule(Base):
    __tablename__ = "gas_molecules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    formula = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    cid = Column(Integer, nullable=True)

class SolidMolecule(Base):
    __tablename__ = "solid_molecules"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    formula = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    cid = Column(Integer, nullable=True)
