from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ReagentItem(BaseModel):
    id: int
    state: Optional[str] = None

class ReactionRequest(BaseModel):
    reagents: List[ReagentItem] = Field(..., min_items=2, max_items=3)
    mode: str = "aggregate"
    state: Optional[str] = None   # для обратной совместимости

class ReactionResponse(BaseModel):
    product_name: str = ""
    product_formula: str = ""
    product_image_url: Optional[str] = None
    cid: Optional[int] = None
    reaction_key: Optional[str] = None
    hint: Optional[str] = None
    suggestions: Optional[List[dict]] = None
    reaction_date: datetime = Field(default_factory=datetime.utcnow)

class CatalogItem(BaseModel):
    id: int
    reactant1: str
    reactant2: str
    product_name: str
    product_formula: str
    product_image_url: Optional[str]
    date_added: datetime
    mode: str

    class Config:
        from_attributes = True