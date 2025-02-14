from pydantic import BaseModel, Field, EmailStr
from typing import Optional,Dict
from datetime import datetime

class ActivityBase(BaseModel):
    name: str 
    time: datetime 
    day: datetime
    total_pics: int 
    consumer: str 
    store: str   

class ActivityCreate(ActivityBase):
    pass

class ActivityRead(ActivityBase):
    pass

class ActivityUpdate(BaseModel):
    name: Optional[str] 
    total_pics: Optional[int] 
    consumer: Optional[str]  
    store: Optional[str]    
    gained_points: Optional[int] 
    brand_detected: Optional[Dict[str,int]]
    is_complete: Optional[bool]
