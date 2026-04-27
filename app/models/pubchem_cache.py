from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class PubChemCache(Base):
    __tablename__ = "pubchem_cache"

    cid = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    formula = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    cached_at = Column(DateTime, default=datetime.utcnow)
