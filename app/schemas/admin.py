from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class AdminBase(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    password: str 
    profile_image: Optional[str] 

class AdminCreate(AdminBase):
    pass

class AdminUpdate(AdminBase):
    full_name: Optional[str]  
    phone: Optional[str] 
    email: Optional[EmailStr ] 
    password: Optional[str] 
    profile_image: Optional[str] 

class AdminRead(BaseModel):
    full_name: str 
    phone: str 
    email: EmailStr 
    profile_image: Optional[str]    