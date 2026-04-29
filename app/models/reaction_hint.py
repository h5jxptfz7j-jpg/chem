from sqlalchemy import Column, Integer, String
from app.database import Base

class ReactionHint(Base):
    __tablename__ = "reaction_hints"

    id = Column(Integer, primary_key=True, index=True)
    reaction_key = Column(String, unique=True, nullable=False)  # например "H2+N2"
    hint_text = Column(String, nullable=False)  # "Возможные реакции: H2+O2 (Вода)"
    suggested_products = Column(String, nullable=True)  # можно оставить пустым