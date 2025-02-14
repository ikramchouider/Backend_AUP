from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class WorkerBase(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    password: str 
    profile_image: Optional[str] 

class WorkerCreate(WorkerBase):
    pass

class WorkerUpdate(WorkerBase):
    full_name: Optional[str]  
    phone: Optional[str] 
    email: Optional[EmailStr ] 
    password: Optional[str] 
    profile_image: Optional[str] 

class WorkerRead(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    profile_image: Optional[str]    