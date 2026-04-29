from sqlalchemy import Column, Integer, String
from app.database import Base


class ReactionHint(Base):
    """Подсказки для пар веществ, которые не реагируют между собой."""
    __tablename__ = "reaction_hints"

    id = Column(Integer, primary_key=True, index=True)
    reaction_key = Column(String, unique=True, nullable=False)  # sorted: "A+B"
    hint_text = Column(String, nullable=False)