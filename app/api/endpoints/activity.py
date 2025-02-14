from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from bson import ObjectId
from app.db.db import Activity
from app.schemas.activity import ActivityCreate, ActivityRead
import aiofiles
import os
from PIL import Image, ImageFilter
import numpy as np
from datetime import datetime

router = APIRouter()

# Directory to store uploaded images
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/", response_model=ActivityRead)
async def create_activity(activity: ActivityCreate):
    activity_data = activity.dict()
    result = await Activity.insert_one(activity_data)
    activity_data["id"] = str(result.inserted_id)
    return ActivityRead(**activity_data)


def is_image_blurry(image_path: str) -> bool:
    """Check if the image is blurry using the Laplacian method."""
    img = Image.open(image_path)
    img_gray = img.convert("L")  # Convert to grayscale
    img_laplacian = np.array(img_gray.filter(ImageFilter.FIND_EDGES))
    variance = np.var(img_laplacian)  # Variance measures sharpness
    return variance < 100  # If variance is low, the image is blurry

@router.post("/{activity_id}/upload-image")
async def upload_image(activity_id: str, file: UploadFile = File(...)):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")
    
    # Save the file temporarily to check blurriness
    temp_file_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Check if the image is blurry
    if is_image_blurry(temp_file_path):
        os.remove(temp_file_path)  # Remove the blurry image
        raise HTTPException(status_code=400, detail="Uploaded image is blurry. Please upload a clearer image.")
    
    # If not blurry, save the image with proper naming
    file_path = os.path.join(UPLOAD_DIR, f"{activity_id}_{file.filename}")
    os.rename(temp_file_path, file_path)  # Move the image to its final location
    
    return {"message": "Image uploaded successfully", "file_path": file_path}

async def send_images_to_ai(activity_id: str, image_path: str):
    """Send the image to AI for processing."""
    # Here we send the image path to the AI processing function (you can replace this with actual AI processing code)
    ai_result = {"BrandA": 5, "BrandB": 2}  # Example response from AI
    now = datetime.utcnow()
    current_date = now.date() 
    current_time = now.time() 
    await Activity.update_one(
        {"_id": ObjectId(activity_id)},
        {"$set": {
            "brand_detected": ai_result,
            "completed": True,
            "day": current_date,  
            "time": current_time  
        }}  
    )

@router.post("/{activity_id}/process-images")
async def process_images(activity_id: str, background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")
    
    # Save the image with proper naming after blur check was done in upload-image 
    file_path = os.path.join(UPLOAD_DIR, f"{activity_id}_{file.filename}")
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    # Run AI processing in the background
    background_tasks.add_task(send_images_to_ai, activity_id, file_path)
    
    return {"message": "Images sent for AI processing", "file_path": file_path}

@router.get("/", response_model=List[ActivityRead])
async def get_all_activities():
    activities = await Activity.find().to_list()
    if activities:
        for activity in activities:
            activity["id"] = str(activity.pop("_id"))
        return [ActivityRead(**activity) for activity in activities]
    raise HTTPException(status_code=404, detail="No activities found")

@router.get("/{activity_id}", response_model=ActivityRead)
async def get_activity(activity_id: str):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")

    activity = await Activity.find_one({"_id": ObjectId(activity_id)})
    if activity:
        activity["id"] = str(activity.pop("_id"))
        return ActivityRead(**activity)
    raise HTTPException(status_code=404, detail="Activity not found")

@router.put("/{activity_id}", response_model=ActivityRead)
async def update_activity(activity_id: str, activity: ActivityUpdate):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")

    update_data = {k: v for k, v in activity.dict().items() if v is not None}
    result = await Activity.update_one({"_id": ObjectId(activity_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_activity = await Activity.find_one({"_id": ObjectId(activity_id)})
        updated_activity["id"] = str(updated_activity.pop("_id"))
        return ActivityRead(**updated_activity)

    raise HTTPException(status_code=404, detail="Activity not found")

@router.delete("/{activity_id}")
async def delete_activity(activity_id: str):
    if not ObjectId.is_valid(activity_id):
        raise HTTPException(status_code=400, detail="Invalid activity ID")

    result = await Activity.delete_one({"_id": ObjectId(activity_id)})

    if result.deleted_count == 1:
        return {"message": "Activity deleted successfully"}

    raise HTTPException(status_code=404, detail="Activity not found")

@router.get("/1/search", response_model=List[ActivityRead])
async def search_activity(name: str = Query(None), consumer: str = Query(None)):
    if not name and not consumer:
        raise HTTPException(status_code=400, detail="Either name or consumer must be provided")
    
    query = {}
    if name:
        query["name"] = name
    if consumer:
        query["consumer"] = consumer
    
    activities = await Activity.find(query).to_list()
    if activities:
        for activity in activities:
            activity["id"] = str(activity.pop("_id"))
        return [ActivityRead(**activity) for activity in activities]

    raise HTTPException(status_code=404, detail="No matching activities found")

@router.get("/1/not_completed", response_model=List[ActivityRead])
async def get_not_completed_activities():
    activities = await Activity.find({
        "is_complete": False,
    }).to_list()

    if activities:
        for activity in activities:
            activity["id"] = str(activity.pop("_id")) 
        return [ActivityRead(**activity) for activity in activities]

    raise HTTPException(status_code=404, detail="No avalaible activities found")
