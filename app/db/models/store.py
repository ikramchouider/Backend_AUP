from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class Store(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Task name")
    opening_time: datetime = Field(..., description="Start time")
    closing_time: datetime = Field(..., description="End time")
    location: str = Field(..., description="Task location")
    phone: str = Field(..., description="Phone number")
