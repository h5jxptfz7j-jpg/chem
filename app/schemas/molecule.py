from typing import Optional
from pydantic import BaseModel

class MoleculeOut(BaseModel):
    id: int
    name: str
    formula: str
    image_url: Optional[str] = None
    class Config:
        orm_mode = True

class ElementOut(BaseModel):
    id: int
    symbol: str
    name_ru: str
    image_url: Optional[str] = None
    class Config:
        orm_mode = True
