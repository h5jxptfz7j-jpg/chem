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
    product_image_url: Optional[str]
    cid: Optional[int]
    reaction_key: Optional[str] = None
    suggestions: Optional[List[dict]] = None
    reaction_date: datetime
    state: Optional[str] = None

    class Config:
        from_attributes = True


class CatalogItem(BaseModel):
    id: int
    reaction_key: str
    product_formula: str
    description: Optional[str] = None

    class Config:
        from_attributes = True