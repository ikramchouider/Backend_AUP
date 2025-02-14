from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class ConsumerBase(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    password: str 


class ConsumerCreate(ConsumerBase):
     pass

class ConsumerUpdate(ConsumerBase):
    full_name: Optional[str]  
    phone: Optional[str] 
    email: Optional[EmailStr ] 
    password: Optional[str] 
    total_points: Optional[int] 


class ConsumerRead(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    total_points: int 