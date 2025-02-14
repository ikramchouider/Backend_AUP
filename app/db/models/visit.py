from pydantic import BaseModel, Field, EmailStr
from typing import Optional,Dict
from datetime import datetime

class Visit(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Task name")
    time: datetime = Field(..., description="Start time")
    day: datetime = Field(..., description="Task day")
    is_complete: bool = Field(False, description="Task completion status")
    total_pics: int = Field(..., description="Total number of pics")
    worker: str = Field(..., description="worker identifier")
    store: str = Field(..., description="store identifier")    
    brand_detected: Dict[str,int] = Field(..., description="Number of each category of the brand")