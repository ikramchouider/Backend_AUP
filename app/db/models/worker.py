from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Worker(BaseModel):
    id: str = Field(..., description="Unique identifier")
    full_name: str = Field(..., description="Full name")
    phone: str = Field(..., description="Phone number")
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Hashed password")
    profile_image: Optional[str] = Field(None, description="URL of the profile picture")
