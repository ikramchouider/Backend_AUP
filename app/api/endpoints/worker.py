from fastapi import APIRouter, HTTPException ,Query
from bson import ObjectId
from app.db.db import Worker
from app.schemas.worker import WorkerCreate, WorkerRead, WorkerUpdate
from passlib.context import CryptContext
from typing import List

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

router = APIRouter()

@router.post("/", response_model=WorkerRead)
async def create_worker(worker: WorkerCreate):
    hashed_password = hash_password(worker.password)
    worker_data = worker.dict()
    worker_data["password"] = hashed_password
    result = await Worker.insert_one(worker_data)
    worker_data["id"] = str(result.inserted_id)
    worker_data.pop("password")
    return WorkerRead(**worker_data)

@router.get("/", response_model=List[WorkerRead])
async def get_all_workers():
    workers = await Worker.find().to_list()
    if workers:
        for worker in workers:
            worker["id"] = str(worker.pop("_id"))
            worker.pop("password", None) 
        return [WorkerRead(**worker) for worker in workers]
    raise HTTPException(status_code=404, detail="No workers found")

@router.get("/{worker_id}", response_model=WorkerRead)
async def get_worker(worker_id: str):
    if not ObjectId.is_valid(worker_id):
        raise HTTPException(status_code=400, detail="Invalid worker ID")

    worker = await Worker.find_one({"_id": ObjectId(worker_id)})
    if worker:
        worker["id"] = str(worker.pop("_id"))
        return WorkerRead(**worker)
    raise HTTPException(status_code=404, detail="Worker not found")

@router.put("/{worker_id}", response_model=WorkerRead)
async def update_worker(worker_id: str, worker: WorkerUpdate):
    if not ObjectId.is_valid(worker_id):
        raise HTTPException(status_code=400, detail="Invalid worker ID")

    update_data = {k: v for k, v in worker.dict().items() if v is not None}
    result = await Worker.update_one({"_id": ObjectId(worker_id)}, {"$set": update_data})

    if result.modified_count == 1:
        updated_worker = await Worker.find_one({"_id": ObjectId(worker_id)})
        updated_worker["id"] = str(updated_worker.pop("_id"))
        return WorkerRead(**updated_worker)

    raise HTTPException(status_code=404, detail="Worker not found")

@router.delete("/{worker_id}")
async def delete_worker(worker_id: str):
    if not ObjectId.is_valid(worker_id):
        raise HTTPException(status_code=400, detail="Invalid worker ID")

    result = await Worker.delete_one({"_id": ObjectId(worker_id)})

    if result.deleted_count == 1:
        return {"message": "Worker deleted successfully"}

    raise HTTPException(status_code=404, detail="Worker not found")

@router.get("/1/search", response_model=List[WorkerRead])
async def search_worker(full_name: str = Query(None), email: str = Query(None)):
    if not full_name and not email:
         raise HTTPException(status_code=400, detail="Either full name or email must be provided")
    print(f"Received full_name: {full_name}, email: {email}")
    query = {}
    if full_name:
         query["full_name"] = full_name
    if email:
         query["email"] = email
    print(f"Query: {query}")
    workers = await Worker.find(query).to_list()
    print(workers)
    if workers:
         for worker in workers:
            print(worker)
            worker.pop("password", None)  
            worker["id"] = str(worker.pop("_id")) 
         return [WorkerRead(**worker) for worker in workers]

    raise HTTPException(status_code=404, detail="No matching workers found")
