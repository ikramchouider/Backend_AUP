from fastapi import FastAPI
from app.api.endpoints.admin import router as admin_router
from app.api.endpoints.visit import router as visit_router
#from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.consumer import router as consumer_router
from app.api.endpoints.offer import router as offer_router
from app.api.endpoints.store import router as store_router
from app.api.endpoints.worker import router as worker_router

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Organizer App API!"}

# Include all routers with appropriate prefixes and tags
app.include_router(admin_router, prefix="/admins", tags=["Admins"])
app.include_router(visit_router, prefix="/visits", tags=["Visits"])
#app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(consumer_router, prefix="/consumers", tags=["Consumers"])
app.include_router(offer_router, prefix="/offers", tags=["Offers"])
app.include_router(store_router, prefix="/stores", tags=["Stores"])
app.include_router(worker_router, prefix="/workers", tags=["Workers"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
