from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Offer(BaseModel):
    id: str = Field(..., description="Unique identifier")
    description: str = Field(..., description="Description")
    points_required: int = Field(..., description="points required number ")
