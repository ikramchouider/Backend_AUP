from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Query
from bson import ObjectId
from app.db.db import Visit
from app.schemas.visit import VisitCreate, VisitRead, VisitUpdate
import aiofiles
import os
from PIL import Image, ImageFilter
import numpy as np
from datetime import datetime
from typing import List

router = APIRouter()

# Directory to store uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=VisitRead)
async def create_visit(visit: VisitCreate):
    visit_data = visit.dict()
    result = await Visit.insert_one(visit_data)
    visit_data["id"] = str(result.inserted_id)
    return VisitRead(**visit_data)

def is_image_blurry(image_path: str) -> bool:
    """Check if the image is blurry using the Laplacian method."""
    img = Image.open(image_path)
    img_gray = img.convert("L")  # Convert to grayscale
    img_laplacian = np.array(img_gray.filter(ImageFilter.FIND_EDGES))
    variance = np.var(img_laplacian)  # Variance measures sharpness
    return variance < 100  # If variance is low, the image is blurry

@router.post("/{visit_id}/upload-image")
async def upload_image(visit_id: str, file: UploadFile = File(...)):
    if not ObjectId.is_valid(visit_id):
        raise HTTPException(status_code=400, detail="Invalid visit ID")
    
    temp_file_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    if is_image_blurry(temp_file_path):
        os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail="Uploaded image is blurry. Please upload a clearer image.")
    
    file_path = os.path.join(UPLOAD_DIR, f"{visit_id}_{file.filename}")
    os.rename(temp_file_path, file_path)
    
    return {"message": "Image uploaded successfully", "file_path": file_path}

async def send_images_to_ai(visit_id: str, image_path: str):
    ai_result = {"BrandA": 5, "BrandB": 2}  # Example AI response
    now = datetime.utcnow()
    current_date = now.date()
    current_time = now.time()
    await Visit.update_one(
        {"_id": ObjectId(visit_id)},
        {"$set": {
            "brand_detected": ai_result,
            "completed": True,
            "day": current_date,  
            "time": current_time  
        },
        "$inc": {"gained_points": 10}}  
    )

@router.post("/{visit_id}/process-images")
async def process_images(visit_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not ObjectId.is_valid(visit_id):
        raise HTTPException(status_code=400, detail="Invalid visit ID")
    
    file_path = os.path.join(UPLOAD_DIR, f"{visit_id}_{file.filename}")
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    background_tasks.add_task(send_images_to_ai, visit_id, file_path)
    
    return {"message": "Images sent for AI processing", "file_path": file_path}

@router.get("/", response_model=List[VisitRead])
async def get_all_visits():
    visits = await Visit.find().to_list()
    if visits:
        for visit in visits:
            visit["id"] = str(visit.pop("_id"))
        return [VisitRead(**visit) for visit in visits]
    raise HTTPException(status_code=404, detail="No visits found")

@router.get("/{visit_id}", response_model=VisitRead)
async def get_visit(visit_id: str):
    if not ObjectId.is_valid(visit_id):
        raise HTTPException(status_code=400, detail="Invalid visit ID")

    visit = await Visit.find_one({"_id": ObjectId(visit_id)})
    if visit:
        visit["id"] = str(visit.pop("_id"))
        return VisitRead(**visit)
    raise HTTPException(status_code=404, detail="Visit not found")

@router.put("/{visit_id}", response_model=VisitRead)
async def update_visit(visit_id: str, visit: VisitUpdate):
    if not ObjectId.is_valid(visit_id):
        raise HTTPException(status_code=400, detail="Invalid visit ID")

    update_data = {k: v for k, v in visit.dict().items() if v is not None}
    result = await Visit.update_one({"_id": ObjectId(visit_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_visit = await Visit.find_one({"_id": ObjectId(visit_id)})
        updated_visit["id"] = str(updated_visit.pop("_id"))
        return VisitRead(**updated_visit)

    raise HTTPException(status_code=404, detail="Visit not found")

@router.delete("/{visit_id}")
async def delete_visit(visit_id: str):
    if not ObjectId.is_valid(visit_id):
        raise HTTPException(status_code=400, detail="Invalid visit ID")

    result = await Visit.delete_one({"_id": ObjectId(visit_id)})

    if result.deleted_count == 1:
        return {"message": "Visit deleted successfully"}

    raise HTTPException(status_code=404, detail="Visit not found")

@router.get("/1/search", response_model=List[VisitRead])
async def search_visit(name: str = Query(None), consumer: str = Query(None)):
    if not name and not consumer:
        raise HTTPException(status_code=400, detail="Either name or consumer must be provided")
    
    query = {}
    if name:
        query["name"] = name
    if consumer:
        query["consumer"] = consumer
    
    visits = await Visit.find(query).to_list()
    if visits:
        for visit in visits:
            visit["id"] = str(visit.pop("_id"))
        return [VisitRead(**visit) for visit in visits]

    raise HTTPException(status_code=404, detail="No matching visits found")

@router.get("/1/not_completed", response_model=List[VisitRead])
async def get_not_completed_visits():
    visits = await Visit.find({
        "is_complete": False,
    }).to_list()

    if visits:
        for visit in visits:
            visit["id"] = str(visit.pop("_id")) 
        return [VisitRead(**visit) for visit in visits]

    raise HTTPException(status_code=404, detail="No available visits found")
