from sqlalchemy import Column, Integer, String
from app.database import Base

class Element(Base):
    __tablename__ = "elements"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, nullable=False)
    name_ru = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    cid = Column(Integer, nullable=True)
