
from pydantic import BaseModel, Field, EmailStr
from typing import Optional,Dict
from datetime import datetime

class VisitBase(BaseModel):
    name: str 
    time: datetime 
    day: datetime
    total_pics: int 
    worker: str 
    store: str   
    brand_detected: Dict[str,int] 

class VisitCreate(VisitBase):
    pass

class VisitRead(VisitBase):
    pass

class VisitUpdate(BaseModel):
    name: Optional[str] 
    total_pics: Optional[int] 
    consumer: Optional[str]  
    store: Optional[str]    
    is_complete: Optional[bool] 
