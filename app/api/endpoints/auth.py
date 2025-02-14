from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.services.auth_service import authenticate_user, create_access_token, verify_password
from app.db.session import get_db
from app.models.admin import Admin
from app.models.consumer import Consumer
from app.models.worker import Worker  
from datetime import timedelta
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from pymongo.database import Database
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/login")
async def login(email: str, password: str, db: Database = Depends(get_db)):
    user = await authenticate_user(db, email, password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Determine role
    if "total_points" in user:
        role = "consumer"
    elif "profile_image" in user:
        role = "worker" if await db["workers"].find_one({"email": email}) else "admin"
    else:
        raise HTTPException(status_code=500, detail="Role could not be determined")

    # Generate token
    access_token = create_access_token({"sub": user["email"], "role": role}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    return JSONResponse({"access_token": access_token, "token_type": "bearer"})


@router.post("/logout")
async def logout():
    return JSONResponse({"message": "Logout successful"})

@router.post("signup")
async def signup(
    role: str,
    full_name: str,
    phone: str,
    email: str,
    password: str,
    db: Database = Depends(get_db)
):
    # Ensure role is valid
    if role not in ["admin", "consumer", "worker"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Check if user already exists
    existing_user = await db["admins"].find_one({"email": email}) or \
                    await db["consumers"].find_one({"email": email}) or \
                    await db["workers"].find_one({"email": email})

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = pwd_context.hash(password)

    # Create user based on role
    user_data = {
        "full_name": full_name,
        "phone": phone,
        "email": email,
        "password": hashed_password
    }

    if role == "admin":
        await db["admins"].insert_one(user_data)
    elif role == "consumer":
        user_data["total_points"] = 0  # Consumers have points
        await db["consumers"].insert_one(user_data)
    elif role == "worker":
        user_data["profile_image"] = None  # Workers have profile images
        await db["workers"].insert_one(user_data)

    return JSONResponse({"message": f"{role.capitalize()} registered successfully"})


