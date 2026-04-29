from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ReactionRequest(BaseModel):
    reagents: List[int] = Field(..., min_items=2, max_items=3)
    mode: str = "aggregate"
    state: Optional[str] = None


class ReactionResponse(BaseModel):
    product_name: str
    product_formula: str
    product_image_url: Optional[str] = None
    cid: Optional[int] = None
    reaction_key: Optional[str] = None
    suggestions: Optional[List[dict]] = None
    hint: Optional[str] = None          # ← поле было отсутствует — подсказки не приходили
    reaction_date: datetime
    state: Optional[str] = None

    class Config:
        from_attributes = True


class CatalogItem(BaseModel):
    id: int
    reactant1: str
    reactant2: str
    product_name: str
    product_formula: str
    product_image_url: Optional[str] = None
    date_added: datetime
    mode: str

    class Config:
        from_attributes = True