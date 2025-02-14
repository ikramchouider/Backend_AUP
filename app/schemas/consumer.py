from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ConsumerBase(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    password: str 
    profile_image: Optional[str] 

class ConsumerCreate(ConsumerBase):
    pass

class ConsumerUpdate(ConsumerBase):
    full_name: Optional[str]  
    phone: Optional[str] 
    email: Optional[EmailStr ] 
    password: Optional[str] 
    profile_image: Optional[str] 
    total_points: Optional[int] 


class ConsumerRead(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    profile_image: Optional[str]  
    total_points: int 