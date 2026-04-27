from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class Molecule(Base):
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    formula = Column(String, nullable=False)
    state = Column(String, nullable=False)
    cid = Column(Integer, nullable=True)
    pubchem_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
