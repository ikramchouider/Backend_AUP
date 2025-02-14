from fastapi import APIRouter, HTTPException ,Query
from bson import ObjectId
from app.db.db import Consumer
from app.schemas.consumer import ConsumerCreate, ConsumerRead, ConsumerUpdate
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

router = APIRouter()

@router.post("/", response_model=ConsumerRead)
async def create_consumer(consumer: ConsumerCreate):
    hashed_password = hash_password(consumer.password)
    consumer_data = consumer.dict()
    consumer_data["password"] = hashed_password
    consumer_data["total_points"] = 0
    result = await Consumer.insert_one(consumer_data)
    consumer_data["id"] = str(result.inserted_id)
    consumer_data.pop("password")
    return ConsumerRead(**consumer_data)

@router.get("/", response_model=List[ConsumerRead])
async def get_all_consumers():
    consumers = await Consumer.find().to_list()
    if consumers:
        for consumer in consumers:
            consumer["id"] = str(consumer.pop("_id"))
            consumer.pop("password", None) 
        return [ConsumerRead(**consumer) for consumer in consumers]
    raise HTTPException(status_code=404, detail="No consumers found")

@router.get("/{consumer_id}", response_model=ConsumerRead)
async def get_consumer(consumer_id: str):
    if not ObjectId.is_valid(consumer_id):
        raise HTTPException(status_code=400, detail="Invalid consumer ID")

    consumer = await Consumer.find_one({"_id": ObjectId(consumer_id)})
    if consumer:
        consumer["id"] = str(consumer.pop("_id"))
        return ConsumerRead(**consumer)
    raise HTTPException(status_code=404, detail="Consumer not found")

@router.put("/{consumer_id}", response_model=ConsumerRead)
async def update_consumer(consumer_id: str, consumer: ConsumerUpdate):
    if not ObjectId.is_valid(consumer_id):
        raise HTTPException(status_code=400, detail="Invalid consumer ID")

    update_data = {k: v for k, v in consumer.dict().items() if v is not None}
    result = await Consumer.update_one({"_id": ObjectId(consumer_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_consumer = await Consumer.find_one({"_id": ObjectId(consumer_id)})
        updated_consumer["id"] = str(updated_consumer.pop("_id"))
        return ConsumerRead(**updated_consumer)

    raise HTTPException(status_code=404, detail="Consumer not found")

@router.delete("/{consumer_id}")
async def delete_consumer(consumer_id: str):
    if not ObjectId.is_valid(consumer_id):
        raise HTTPException(status_code=400, detail="Invalid consumer ID")

    result = await Consumer.delete_one({"_id": ObjectId(consumer_id)})

    if result.deleted_count == 1:
        return {"message": "Consumer deleted successfully"}

    raise HTTPException(status_code=404, detail="Consumer not found")

@router.get("/1/search", response_model=List[ConsumerRead])
async def search_consumer(full_name: str = Query(None), email: str = Query(None)):
    if not full_name and not email:
         raise HTTPException(status_code=400, detail="Either full name or email must be provided")
    print(f"Received full_name: {full_name}, email: {email}")
    query = {}
    if full_name:
         query["full_name"] = full_name
    if email:
         query["email"] = email
    print(f"Query: {query}")
    consumers = await Consumer.find(query).to_list()
    print(consumers)
    if consumers:
         for consumer in consumers:
            print(consumer)
            consumer.pop("password", None)  
            consumer["id"] = str(consumer.pop("_id")) 
         return [ConsumerRead(**consumer) for consumer in consumers]

    raise HTTPException(status_code=404, detail="No matching consumers found")