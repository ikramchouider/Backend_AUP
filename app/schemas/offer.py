from pydantic import BaseModel
from bson import ObjectId

class OfferBase(BaseModel):
    points_required: int
    description: str

class OfferCreate(OfferBase):
    pass

class OfferRead(OfferBase):
    id: str

