from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class PredefinedReaction(Base):
    __tablename__ = "predefined_reactions"
    id = Column(Integer, primary_key=True, index=True)
    reaction_key = Column(String, unique=True, nullable=False)
    product_formula = Column(String, nullable=False)
    description = Column(String, nullable=True)

class UserReaction(Base):
    __tablename__ = "user_reactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    reactant1 = Column(String, nullable=False)
    reactant2 = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    product_formula = Column(String, nullable=False)
    product_image_url = Column(String, nullable=True)
    date_added = Column(DateTime, default=datetime.utcnow)
    mode = Column(String, nullable=False)  # 'independent' или 'aggregate'
