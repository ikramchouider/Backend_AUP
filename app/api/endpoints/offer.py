from fastapi import APIRouter, HTTPException
from app.db.db import Offer
from app.utils.qr_generator import generate_qr_code
from bson import ObjectId

router = APIRouter()

@router.get("/{offer_id}/qr")
async def get_offer_qr(offer_id: str):
    """Generate a QR code when a user selects an offer."""

    if not ObjectId.is_valid(offer_id):
        raise HTTPException(status_code=400, detail="Invalid offer ID")

    offer = await Offer.find_one({"_id": ObjectId(offer_id)})
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    qr_code = generate_qr_code(
        offer_id=str(offer["_id"]),
        description=offer["description"],
        points_required=offer["points_required"]
    )

    return {"qr_code": qr_code} 
