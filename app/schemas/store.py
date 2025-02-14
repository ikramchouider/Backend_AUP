from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class StoreBase(BaseModel):
    name: str 
    opening_time: datetime 
    closing_time: datetime
    location: str 
    phone: str

class StoreCreate(StoreBase):
    pass

class StoreRead(StoreBase):
    pass

class StoreUpdate(BaseModel):
    name: Optional[str]
    opening_time: Optional[datetime] 
    closing_time: Optional[datetime] 
    location: Optional[str]
    phone: Optional[str]
