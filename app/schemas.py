from pydantic import BaseModel
from datetime import datetime
from typing import List

class DocumentBase(BaseModel):
    rubrics: List[str]
    text: str
    created_date: datetime

class DocumentResponse(DocumentBase):
    id: int

    class Config:
        from_attributes = True