from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class PredefinedCompatibility(Base):
    __tablename__ = "predefined_compatibilities"
    id = Column(Integer, primary_key=True, index=True)
    element1_id = Column(Integer, ForeignKey("elements.id"), nullable=False)
    element2_id = Column(Integer, ForeignKey("elements.id"), nullable=False)
    suggested_product = Column(String, nullable=False)
    hint_text = Column(String, nullable=True)
