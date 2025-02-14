from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Consumer(BaseModel):
    id: str = Field(..., description="Unique identifier")
    full_name: str = Field(..., description="Full name")
    phone: str = Field(..., description="Phone number")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Hashed password")
    total_points: int = Field(..., description="Total number of points")
