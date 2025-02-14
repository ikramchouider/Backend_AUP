from fastapi import APIRouter, HTTPException, Query
from bson import ObjectId
from app.db.db import Store
from app.schemas.store import StoreCreate, StoreRead, StoreUpdate
from typing import List

router = APIRouter()

@router.post("/", response_model=StoreRead)
async def create_store(store: StoreCreate):
    store_data = store.dict()
    result = await Store.insert_one(store_data)
    store_data["id"] = str(result.inserted_id)
    return StoreRead(**store_data)

@router.get("/", response_model=List[StoreRead])
async def get_all_stores():
    stores = await Store.find().to_list()
    if stores:
        for store in stores:
            store["id"] = str(store.pop("_id"))
        return [StoreRead(**store) for store in stores]
    raise HTTPException(status_code=404, detail="No stores found")

@router.get("/{store_id}", response_model=StoreRead)
async def get_store(store_id: str):
    if not ObjectId.is_valid(store_id):
        raise HTTPException(status_code=400, detail="Invalid store ID")

    store = await Store.find_one({"_id": ObjectId(store_id)})
    if store:
        store["id"] = str(store.pop("_id"))
        return StoreRead(**store)
    raise HTTPException(status_code=404, detail="Store not found")

@router.put("/{store_id}", response_model=StoreRead)
async def update_store(store_id: str, store: StoreUpdate):
    if not ObjectId.is_valid(store_id):
        raise HTTPException(status_code=400, detail="Invalid store ID")

    update_data = {k: v for k, v in store.dict().items() if v is not None}
    result = await Store.update_one({"_id": ObjectId(store_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_store = await Store.find_one({"_id": ObjectId(store_id)})
        updated_store["id"] = str(updated_store.pop("_id"))
        return StoreRead(**updated_store)

    raise HTTPException(status_code=404, detail="Store not found")

@router.delete("/{store_id}")
async def delete_store(store_id: str):
    if not ObjectId.is_valid(store_id):
        raise HTTPException(status_code=400, detail="Invalid store ID")

    result = await Store.delete_one({"_id": ObjectId(store_id)})

    if result.deleted_count == 1:
        return {"message": "Store deleted successfully"}

    raise HTTPException(status_code=404, detail="Store not found")

@router.get("/1/search", response_model=List[StoreRead])
async def search_store(name: str = Query(None), location: str = Query(None)):
    if not name and not location:
        raise HTTPException(status_code=400, detail="Either name or location must be provided")
    
    query = {}
    if name:
        query["name"] = name
    if location:
        query["location"] = location
    
    stores = await Store.find(query).to_list()
    if stores:
        for store in stores:
            store["id"] = str(store.pop("_id"))
        return [StoreRead(**store) for store in stores]

    raise HTTPException(status_code=404, detail="No matching stores found")
